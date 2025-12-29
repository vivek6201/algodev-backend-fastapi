from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import invalidate_cache
from app.common.db.config import logger
from app.common.lib.slug_utils import create_slug
from app.modules.education.shared.model import EducationCategory

from ..models.tutorials import Node, NodeType, Tutorial
from ..schemas.tutorials import CreateNodeType, NodeBase, TutorialBase
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

    @invalidate_cache(tags=["nodes_list", "tutorial_{tutorial_slug}"])
    async def create_node(self, session: AsyncSession, tutorial_slug: str, node_data: NodeBase):
        data_dict = node_data.model_dump(exclude={"node_type"})
        data_dict["slug"] = create_slug(data_dict["title"])

        # Check for existing node based on hierarchy
        statement = select(Node).where(Node.slug == data_dict["slug"], Node.deleted_at.is_(None))

        if data_dict["parent_id"]:
            # If child node, check uniqueness under same parent
            statement = statement.where(Node.parent_id == data_dict["parent_id"])
        else:
            # If root node, check uniqueness under same tutorial
            statement = statement.where(
                Node.tutorial_slug == tutorial_slug, Node.parent_id.is_(None)
            )

        result = await session.exec(statement)
        existing_node = result.first()

        if existing_node:
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
            return {
                "message": "Node created successfully",
                "status": True,
                "data": node,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }

    @invalidate_cache(tags=["nodes_list"])
    async def update_node(self, session: AsyncSession, node_id: int, node_data: NodeBase):
        pass
