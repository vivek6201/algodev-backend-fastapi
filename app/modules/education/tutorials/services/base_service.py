import math
from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached
from app.common.lib.formatter import ListResponse
from app.modules.education.tutorials.schemas.tutorials import (
    NodeResponse,
    TutorialResponse,
)

from ..models.tutorials import Node, Tutorial


class BaseService:
    @cached(
        key_prefix="tutorials",
        tags=["tutorial_list"],
        response_model=ListResponse[Tutorial],
    )
    async def get_tutorials(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        search: str,
        is_published: Optional[bool] = None,
    ) -> ListResponse[Tutorial]:
        search = search.strip()

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
        statement = select(Tutorial).where(*filters).offset((page - 1) * limit).limit(limit)

        result = await session.exec(statement)
        data = result.all()

        total_pages = math.ceil(total_items / limit) if limit > 0 else 1

        return ListResponse[Tutorial](data=data, total_items=total_items, total_pages=total_pages)

    def _build_node_tree(self, nodes: List[Node]) -> List[NodeResponse]:
        """
        Manually build the tree from flat list of nodes.
        Filters out non-root nodes from the top level list.
        """
        node_map = {}
        roots = []

        # 1. Convert all ORM nodes to Pydantic models (without children yet)
        # Use sorted to ensure order is respected
        sorted_nodes = sorted(nodes, key=lambda x: x.order)

        # Create a map for quick access
        # We rely on NodeResponse for the structure
        nodes_dto = []
        for node_orm in sorted_nodes:
            # model_dump on SQLModel excludes relationships by default, which is what we want
            node_data = node_orm.model_dump()
            # Explicitly add node_type since it's required by NodeResponse
            node_data["node_type"] = node_orm.node_type
            dto = NodeResponse(**node_data)
            nodes_dto.append(dto)
            node_map[dto.id] = dto

        # 2. Stitch the tree
        for dto in nodes_dto:
            if dto.parent_id and dto.parent_id in node_map:
                node_map[dto.parent_id].children.append(dto)
            else:
                roots.append(dto)

        return roots

    @cached(
        key_prefix="tutorials", tags=["tutorial_{tutorial_slug}"], response_model=TutorialResponse
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
            roots = self._build_node_tree(tutorial.nodes)

            # 3. Create TutorialResponse
            # validata/dump tutorial fields
            tut_data = tutorial.model_dump()
            response = TutorialResponse(**tut_data)

            # 4. Assign constructed hierarchy
            response.nodes = roots

            # 5. Handle categories explicitly if needed (or rely on from_attributes if validation works)
            # Since we manually constructed response, we need to populate categories
            if tutorial.categories:
                response.categories = tutorial.categories

            return response
        return None
