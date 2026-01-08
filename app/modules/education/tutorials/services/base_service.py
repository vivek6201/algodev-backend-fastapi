import math
from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached
from app.common.lib.formatter import ListResponse
from app.modules.education.tutorials.schemas.tutorials import (
    NodeContent,
    NodeResponse,
    NodeTypeResponse,
    TutorialResponse,
)

from ..models.tutorials import Node, NodeType, Tutorial


class BaseService:
    @cached(
        key_prefix="tutorials",
        tags=["tutorial_list"],
        response_model=ListResponse[TutorialResponse],
    )
    async def get_tutorials(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        search: str,
        is_published: Optional[bool] = None,
    ) -> ListResponse[TutorialResponse]:
        search = search.strip()
        page = int(page)
        limit = int(limit)

        # Build filters
        filters = [Tutorial.deleted_at.is_(None)]

        if search:
            filters.append(Tutorial.title.contains(f"%{search}%"))

        if is_published is not None:
            filters.append(Tutorial.is_published == is_published)

        # Count total items
        count_statement = select(func.count()).select_from(Tutorial).where(*filters)
        total_items = (await session.exec(count_statement)).one()

        # Get paginated data
        statement = (
            select(Tutorial)
            .where(*filters)
            .offset((page - 1) * limit)
            .limit(limit)
            .options(selectinload(Tutorial.categories))
        )

        result = await session.exec(statement)

        data: List[TutorialResponse] = []
        for t in result.all():
            t_data = t.model_dump()
            categories = t.categories
            data.append(TutorialResponse(**t_data, categories=categories))

        total_pages = math.ceil(total_items / limit) if limit > 0 else 1

        return ListResponse[TutorialResponse](
            data=data, total_items=total_items, total_pages=total_pages
        )

    def _to_node_dto(self, node: Node) -> NodeResponse:
        """Helper to convert Node ORM to NodeResponse DTO."""
        node_data = node.model_dump()
        node_data["node_type"] = node.node_type
        return NodeResponse(**node_data)

    def _build_node_tree_and_map(self, nodes: List[Node], is_published: Optional[bool] = None):
        """
        Manually build the tree from flat list of nodes.
        Returns both the list of root nodes and the map of all nodes.
        Filters out non-root nodes from the top level list.
        """
        node_map = {}
        roots = []

        # 1. Convert all ORM nodes to Pydantic models (without children yet)
        sorted_nodes = sorted(nodes, key=lambda x: x.order)

        # Create a map for quick access
        nodes_dto = []
        for node_orm in sorted_nodes:
            if node_orm.deleted_at:
                continue

            # Filtering logic
            if is_published is not None and node_orm.is_published != is_published:
                continue

            dto = self._to_node_dto(node_orm)
            nodes_dto.append(dto)
            node_map[dto.id] = dto

        # 2. Stitch the tree
        for dto in nodes_dto:
            if dto.parent_id and dto.parent_id in node_map:
                node_map[dto.parent_id].children.append(dto)
            elif dto.parent_id is None:
                roots.append(dto)

        return roots, node_map

    def _build_node_tree(
        self, nodes: List[Node], is_published: Optional[bool] = None
    ) -> List[NodeResponse]:
        roots, _ = self._build_node_tree_and_map(nodes, is_published)
        return roots

    @cached(key_prefix="node_types", tags=["node_types"], response_model=List[NodeTypeResponse])
    async def get_all_node_types(self, session: AsyncSession):
        statement = select(NodeType).where(NodeType.deleted_at.is_(None))
        result = await session.exec(statement)
        node_types = result.all()

        return [NodeTypeResponse.model_validate(node_type) for node_type in node_types]

    @cached(
        key_prefix="tutorials",
        tags=["tutorial_{tutorial_slug}"],
        response_model=TutorialResponse,
    )
    async def get_tutorial(
        self, session: AsyncSession, tutorial_slug: str, is_published: Optional[bool] = None
    ) -> Optional[TutorialResponse]:
        statement = select(Tutorial).where(
            Tutorial.slug == tutorial_slug, Tutorial.deleted_at.is_(None)
        )

        if is_published is not None:
            statement = statement.where(
                Tutorial.is_published == is_published,
            )

        statement = statement.options(
            selectinload(Tutorial.nodes).selectinload(Node.node_type),
            selectinload(Tutorial.categories),
        )

        result = await session.exec(statement)
        tutorial = result.one_or_none()
        if tutorial:
            roots = self._build_node_tree(tutorial.nodes, is_published=is_published)

            # 3. Create TutorialResponse
            # validata/dump tutorial fields
            tut_data = tutorial.model_dump()
            response = TutorialResponse(**tut_data)

            response.nodes = roots

            if tutorial.categories:
                response.categories = tutorial.categories

            return response
        return None

    @cached(
        key_prefix="tutorials",
        tags=["node_{tutorial_slug}_{node_slug}"],
        response_model=NodeResponse,
    )
    async def get_node(
        self,
        session: AsyncSession,
        tutorial_slug: str,
        node_slug: str,
        is_published: Optional[bool] = None,
    ):
        # Fetch the target node and its direct children
        statement = select(Node).where(Node.slug == node_slug, Node.deleted_at.is_(None))
        statement = statement.where(Node.tutorial_slug == tutorial_slug)
        statement = statement.options(selectinload(Node.node_type), selectinload(Node.content))

        if is_published is not None:
            statement = statement.where(Node.is_published == is_published)

        result = await session.exec(statement)
        node = result.first()

        if not node:
            return None

        # Fetch direct children
        children_stmt = (
            select(Node)
            .where(Node.parent_id == node.id, Node.deleted_at.is_(None))
            .options(selectinload(Node.node_type))
            .order_by(Node.order)
        )

        if is_published is not None:
            children_stmt = children_stmt.where(Node.is_published == is_published)

        children_res = await session.exec(children_stmt)
        children = children_res.all()

        # 1. Target Node DTO
        target_dto = self._to_node_dto(node)
        if node.content:
            target_dto.content = NodeContent.model_validate(node.content)

        # 2. Children DTOs (with empty children)
        children_dtos = []
        for child in children:
            child_dto = self._to_node_dto(child)
            # Explicitly set children to empty list to stop recursion/lazy loading
            child_dto.children = []
            children_dtos.append(child_dto)

        target_dto.children = children_dtos

        return target_dto
