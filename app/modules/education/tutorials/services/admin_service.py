from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import invalidate_cache
from app.common.cache.redis import redis_client
from app.common.db.config import logger
from app.common.lib.slug_utils import create_slug
from app.modules.education.shared.model import EducationCategory

from ..models.tutorials import Node, NodeContent, NodeType, Tutorial
from ..schemas.tutorials import (
    CreateNodeType,
    NodeBase,
    NodeBaseUpdate,
    NodeOperationResponse,
    TutorialBase,
)
from .base_service import BaseService


class AdminService(BaseService):
    @invalidate_cache(tags=["tutorial_list"])
    async def create_tutorial(self, session: AsyncSession, tutorial_data: TutorialBase):
        data_dict = tutorial_data.model_dump(exclude={"categories"})
        data_dict["slug"] = create_slug(data_dict["title"])

        statement = select(Tutorial).where(Tutorial.slug == data_dict["slug"])
        result = await session.exec(statement)
        tutorial = result.first()

        if tutorial:
            return {
                "message": "Tutorial already exists",
                "status": False,
            }

        result = await session.exec(
            select(EducationCategory).where(EducationCategory.id.in_(tutorial_data.categories))
        )
        categories = result.all()

        tutorial = Tutorial(**data_dict)
        tutorial.categories = categories

        try:
            session.add(tutorial)
            await session.commit()
            await session.refresh(tutorial)
            return {
                "message": "Tutorial created successfully",
                "status": True,
                "data": tutorial,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    @invalidate_cache(tags=["tutorial_{tutorial_slug}", "tutorial_list"])
    async def publish_tutorial(self, session: AsyncSession, tutorial_slug: str, publish: bool):
        statement = select(Tutorial).where(
            Tutorial.slug == tutorial_slug, Tutorial.deleted_at.is_(None)
        )
        result = await session.exec(statement)
        tutorial = result.one_or_none()

        if not tutorial:
            return {
                "message": "Tutorial not found",
                "status": False,
            }

        tutorial.is_published = publish

        try:
            session.add(tutorial)
            await session.commit()
            await session.refresh(tutorial)
            return {
                "message": "Tutorial published successfully",
                "status": True,
                "data": tutorial,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    async def delete_tutorial(self, session: AsyncSession, tutorial_slug: str):
        statement = select(Tutorial).where(Tutorial.slug == tutorial_slug)
        result = await session.exec(statement)
        tutorial = result.one_or_none()

        if not tutorial:
            return {
                "message": "Tutorial not found",
                "status": False,
            }

        tutorial.deleted_at = Tutorial.soft_delete()

        try:
            session.add(tutorial)
            await session.commit()
            await session.refresh(tutorial)
            return {
                "message": "Tutorial deleted successfully",
                "status": True,
                "data": tutorial,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    async def _check_slug_collision(
        self,
        session: AsyncSession,
        slug: str,
        tutorial_slug: str,
        parent_id: Optional[int],
        exclude_node_id: Optional[int] = None,
    ) -> bool:
        """
        Check if a node slug collides with existing nodes in the same hierarchy level.
        Returns True if collision exists, False otherwise.
        """
        statement = select(Node).where(Node.slug == slug, Node.deleted_at.is_(None))

        if parent_id:
            statement = statement.where(Node.parent_id == parent_id)
        else:
            statement = statement.where(
                Node.tutorial_slug == tutorial_slug, Node.parent_id.is_(None)
            )

        if exclude_node_id:
            statement = statement.where(Node.id != exclude_node_id)

        result = await session.exec(statement)
        return result.first() is not None

    @invalidate_cache(tags=["node_types"])
    async def create_node_type(self, session: AsyncSession, node_type_data: CreateNodeType):
        data_dict = node_type_data.model_dump()
        node_type = NodeType(**data_dict)

        # Check for existing node type
        statement = select(NodeType).where(NodeType.name == data_dict["name"])
        result = await session.exec(statement)
        existing_node_type = result.first()

        if existing_node_type:
            return {
                "message": "Node type already exists",
                "status": False,
            }

        try:
            session.add(node_type)
            await session.commit()
            await session.refresh(node_type)
            return {
                "message": "Node type created successfully",
                "status": True,
                "data": node_type,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    async def update_node(
        self, session: AsyncSession, tutorial_slug: str, node_id: int, node_data: NodeBaseUpdate
    ):
        # Eager load content, node type
        statement = (
            select(Node)
            .where(Node.id == node_id)
            .options(selectinload(Node.content), selectinload(Node.node_type))
        )
        result = await session.exec(statement)
        node = result.one_or_none()

        if not node or node.deleted_at:
            return {
                "message": "Node not found",
                "status": False,
            }

        data_dict = node_data.model_dump(exclude={"node_type", "content"}, exclude_unset=True)
        # Handle Slug Change
        if ("title" in data_dict and data_dict["title"] != node.title) or (
            "parent_id" in data_dict and data_dict["parent_id"] != node.parent_id
        ):
            new_title = data_dict.get("title", node.title)
            new_parent_id = data_dict.get("parent_id", node.parent_id)

            base_slug = create_slug(new_title)
            if new_parent_id:
                new_slug = f"{base_slug}-{new_parent_id}"
            else:
                new_slug = base_slug

            # Check for collision
            is_collision = await self._check_slug_collision(
                session=session,
                slug=new_slug,
                tutorial_slug=tutorial_slug,
                parent_id=new_parent_id,
                exclude_node_id=node_id,
            )

            if is_collision:
                return {
                    "message": "Node with this title already exists in this level",
                    "status": False,
                }

            node.slug = new_slug

        # Update scalar fields
        for key, value in data_dict.items():
            setattr(node, key, value)

        # Handle content
        if node_data.content:
            if node.content:
                node.content.editorial = node_data.content.editorial
                node.content.video_url = node_data.content.video_url
                session.add(node.content)
            else:
                new_content = NodeContent(
                    node_id=node.id,
                    editorial=node_data.content.editorial,
                    video_url=node_data.content.video_url,
                )
                session.add(new_content)

        # Handle Type change
        if node.node_type_id != node_data.node_type:
            result = await session.exec(select(NodeType).where(NodeType.id == node_data.node_type))
            existing_node_type = result.one_or_none()
            if existing_node_type:
                node.node_type = existing_node_type

        try:
            session.add(node)
            await session.commit()
            await session.refresh(node)

            # Invalidate cache
            tags = [f"node_{tutorial_slug}_{node.slug}"]
            if node.parent_id:
                # We need to fetch parent to get its slug for cache tag
                parent_node = await session.get(Node, node.parent_id)
                if parent_node:
                    tags.append(f"node_{tutorial_slug}_{parent_node.slug}")

            await redis_client.invalidate_tags(tags)

            return {
                "message": "Node updated successfully",
                "status": True,
                "data": NodeOperationResponse.model_validate(node),
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    async def publish_node(
        self, session: AsyncSession, tutorial_slug: str, node_id: int, publish: bool
    ):
        statement = (
            select(Node)
            .where(
                Node.id == node_id,
                Node.tutorial_slug == tutorial_slug,
                Node.deleted_at.is_(None),
            )
            .options(selectinload(Node.content), selectinload(Node.node_type))
        )
        result = await session.exec(statement)
        node = result.one_or_none()

        if not node:
            return {
                "message": "Node not found",
                "status": False,
            }

        node.is_published = publish

        try:
            session.add(node)
            await session.commit()

            # Re-fetch node with options to ensure relationships are loaded
            result = await session.exec(statement)
            node = result.one()

            # Invalidate cache
            tags = [f"node_{tutorial_slug}_{node.slug}", f"tutorial_{tutorial_slug}"]
            if node.parent_id:
                parent_node = await session.get(Node, node.parent_id)
                if parent_node:
                    tags.append(f"node_{tutorial_slug}_{parent_node.slug}")
            await redis_client.invalidate_tags(tags)

            return {
                "message": "Node published successfully",
                "status": True,
                "data": NodeOperationResponse.model_validate(node),
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    @invalidate_cache(tags=["nodes_list", "tutorial_{tutorial_slug}"])
    async def create_node(self, session: AsyncSession, tutorial_slug: str, node_data: NodeBase):
        data_dict = node_data.model_dump(exclude={"node_type", "content"})

        base_slug = create_slug(data_dict["title"])
        if data_dict["parent_id"]:
            data_dict["slug"] = f"{base_slug}-{data_dict['parent_id']}"
        else:
            data_dict["slug"] = base_slug

        if data_dict["parent_id"]:
            # Verify parent exists
            parent_node = await session.get(Node, data_dict["parent_id"])
            if not parent_node or parent_node.deleted_at:
                return {
                    "message": "Parent node not found",
                    "status": False,
                }

        # Check for collision
        is_collision = await self._check_slug_collision(
            session=session,
            slug=data_dict["slug"],
            tutorial_slug=tutorial_slug,
            parent_id=data_dict["parent_id"],
        )

        if is_collision:
            return {
                "message": "Node with this title already exists in this level",
                "status": False,
            }

        result = await session.exec(select(NodeType).where(NodeType.id == node_data.node_type))
        existing_node_type = result.one_or_none()

        if not existing_node_type:
            return {
                "message": "Node type not found",
                "status": False,
            }

        node = Node(**data_dict)
        node.node_type = existing_node_type
        node.tutorial_slug = tutorial_slug  # Set the tutorial_slug

        try:
            session.add(node)
            await session.commit()
            await session.refresh(node)

            # Handle Metadata Creation
            if node_data.content:
                content = NodeContent(
                    node_id=node.id,
                    editorial=node_data.content.editorial,
                    video_url=node_data.content.video_url,
                )
                session.add(content)
                await session.commit()
                await session.refresh(node)

            # Invalidate parent node cache if it exists
            if node.parent_id and parent_node:
                await redis_client.invalidate_tags([f"node_{tutorial_slug}_{parent_node.slug}"])

            return {
                "message": "Node created successfully",
                "status": True,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    @invalidate_cache(tags=["nodes_list", "tutorial_{tutorial_slug}"])
    async def delete_node_soft(self, session: AsyncSession, tutorial_slug: str, node_id: int):
        statement = select(Node).where(Node.id == node_id).options(selectinload(Node.node_type))
        result = await session.exec(statement)
        node = result.one_or_none()

        if not node or node.deleted_at:
            return {
                "message": "Node not found",
                "status": False,
            }

        statement = select(Node).where(Node.parent_id == node_id, Node.deleted_at.is_(None))
        result = await session.exec(statement)
        children = result.all()

        if not node.node_type.is_leaf and children:
            return {
                "message": "Cannot delete a category that has children. Please delete children first.",
                "status": False,
            }

        try:
            node.soft_delete()
            session.add(node)
            await session.commit()

            # Invalidate parent node cache and self
            tags = [f"node_{tutorial_slug}_{node.slug}"]
            if node.parent_id:
                parent_node = await session.get(Node, node.parent_id)
                if parent_node:
                    tags.append(f"node_{tutorial_slug}_{parent_node.slug}")

            await redis_client.invalidate_tags(tags)

            return {
                "message": "Node deleted successfully",
                "status": True,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    @invalidate_cache(tags=["nodes_list", "tutorial_{tutorial_slug}"])
    async def delete_node_hard(self, session: AsyncSession, tutorial_slug: str, node_id: int):
        statement = select(Node).where(Node.id == node_id).options(selectinload(Node.node_type))
        result = await session.exec(statement)
        node = result.one_or_none()
        # For hard delete we might want to allow deleting already soft-deleted nodes too
        if not node:
            return {
                "message": "Node not found",
                "status": False,
            }

        # Check children (even soft deleted ones should be checked for consistent DB state
        # or we just rely on FK constraints? Better to check explicitly)
        statement = select(Node).where(Node.parent_id == node_id)
        result = await session.exec(statement)
        children = result.all()

        if not node.node_type.is_leaf and children:
            return {
                "message": "Cannot delete a category that has children. Please delete children first.",
                "status": False,
            }

        try:
            await session.delete(node)
            await session.commit()

            # Invalidate parent node cache and self
            tags = [f"node_{tutorial_slug}_{node.slug}", f"tutorial_{tutorial_slug}"]
            if node.parent_id:
                parent_node = await session.get(Node, node.parent_id)
                if parent_node:
                    tags.append(f"node_{tutorial_slug}_{parent_node.slug}")

            await redis_client.invalidate_tags(tags)

            return {"message": "Node permanently deleted", "status": True}
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": e.__str__(),
                "status": False,
            }
