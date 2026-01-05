from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse

from ..schemas.tutorials import CreateNodeType, NodeBase, TutorialBase
from ..services.admin_service import AdminService
from .base_controller import BaseController


class AdminController(BaseController):
    def __init__(self):
        self.admin_service = AdminService()
        super().__init__()

    # Tutorial
    async def create_tutorial(self, session: AsyncSession, tutorial_data: TutorialBase):
        result = await self.admin_service.create_tutorial(session, tutorial_data)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"], data=result["data"])

    async def update_tutorial(
        self, session: AsyncSession, tutorial_slug: str, tutorial_data: TutorialBase
    ):
        result = await self.admin_service.update_tutorial(session, tutorial_slug, tutorial_data)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"])

    async def delete_tutorial(self, session: AsyncSession, tutorial_id: int):
        # pending
        result = await self.admin_service.delete_tutorial(session, tutorial_id)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"])

    # Nodes
    async def get_all_node_types(self, session: AsyncSession):
        result = await self.admin_service.get_all_node_types(session)

        return SuccessResponse(message="Node types fetched successfully", data=result)

    async def create_node_type(self, session: AsyncSession, node_type_data: CreateNodeType):
        result = await self.admin_service.create_node_type(session, node_type_data)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"], data=result["data"])

    async def get_node(self, session: AsyncSession, tutorial_slug: str, node_slug: str):
        result = await self.admin_service.get_node(session, tutorial_slug, node_slug)

        if not result:
            return ErrorResponse(message="Node not found")

        return SuccessResponse(message="Node fetched successfully", data=result)

    async def create_node(self, session: AsyncSession, tutorial_slug: str, node_data: NodeBase):
        result = await self.admin_service.create_node(session, tutorial_slug, node_data)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"], data=result["data"])

    async def delete_node(self, session: AsyncSession, tutorial_slug: str, node_id: int):
        result = await self.admin_service.delete_node_soft(session, tutorial_slug, node_id)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"])

    async def hard_delete_node(self, session: AsyncSession, tutorial_slug: str, node_id: int):
        result = await self.admin_service.delete_node_hard(session, tutorial_slug, node_id)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"])
