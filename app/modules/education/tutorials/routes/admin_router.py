from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.common.lib.formatter import ErrorResponse, TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.users.models.admin import AdminRole

from ..controller.admin_controller import AdminController
from ..schemas.tutorials import CreateNodeType, NodeBase, NodeBaseUpdate, TutorialBase

admin_router = APIRouter()
admin_controller = AdminController()


# Tutorials
@admin_router.get("/")
async def get_all_tutorials(
    request: Request,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    query_params = request.query_params
    limit = int(query_params.get("limit", 10))
    page = int(query_params.get("page", 1))
    search = query_params.get("search", "")

    if limit < 1 or limit > 50:
        return ErrorResponse(message="Limit must be between 1 and 50", status_code=400)

    params = {
        "page": page,
        "limit": limit,
        "search": search,
    }

    return await admin_controller.get_tutorials(session=session, params=params)


@admin_router.get("/one/{tutorial_slug}")
async def get_tutorial(
    tutorial_slug: str,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.get_tutorial(session=session, tutorial_slug=tutorial_slug)


@admin_router.post("/")
async def create_tutorial(
    data: TutorialBase,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.create_tutorial(session=session, tutorial_data=data)


@admin_router.patch("/one/{tutorial_slug}")
async def update_tutorial(
    tutorial_slug: str,
    data: TutorialBase,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.update_tutorial(
        session=session, tutorial_slug=tutorial_slug, tutorial_data=data
    )


@admin_router.patch("/{tutorial_slug}/publish")
async def publish_tutorial(
    tutorial_slug: str,
    publish: bool,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(
        RoleChecker([AdminRole.SUPER_ADMIN.value, AdminRole.ADMIN.value], user_type="admin")
    ),
):
    return await admin_controller.publish_tutorial(
        session=session, tutorial_slug=tutorial_slug, publish=publish
    )


# Nodes
@admin_router.get("/node_type")
async def get_all_node_types(
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.get_all_node_types(session=session)


@admin_router.post("/node_type")
async def create_node_type(
    data: CreateNodeType,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.create_node_type(session=session, node_type_data=data)


@admin_router.post("/{tutorial_slug}/node")
async def create_node(
    tutorial_slug: str,
    data: NodeBase,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.create_node(
        session=session, tutorial_slug=tutorial_slug, node_data=data
    )


@admin_router.patch("/{tutorial_slug}/node/{node_id}")
async def update_node(
    tutorial_slug: str,
    node_id: int,
    data: NodeBaseUpdate,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.update_node(
        session=session,
        tutorial_slug=tutorial_slug,
        node_id=node_id,
        node_data=data,
    )


@admin_router.patch("/{tutorial_slug}/node/{node_id}/publish")
async def publish_node(
    tutorial_slug: str,
    node_id: int,
    publish: bool,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(
        RoleChecker([AdminRole.SUPER_ADMIN.value, AdminRole.ADMIN.value], user_type="admin")
    ),
):
    return await admin_controller.publish_node(
        session=session, tutorial_slug=tutorial_slug, node_id=node_id, publish=publish
    )


@admin_router.get("/{tutorial_slug}/node/{node_slug}")
async def get_node(
    tutorial_slug: str,
    node_slug: str,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.get_node(
        session=session, tutorial_slug=tutorial_slug, node_slug=node_slug
    )


@admin_router.delete("/one/{tutorial_slug}")
async def delete_tutorial(
    tutorial_slug: str,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(
        RoleChecker([AdminRole.SUPER_ADMIN.value], user_type="admin")
    ),
):
    return await admin_controller.delete_tutorial(session=session, tutorial_slug=tutorial_slug)


@admin_router.delete("/{tutorial_slug}/node/{node_id}")
async def delete_node(
    tutorial_slug: str,
    node_id: int,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.delete_node(
        session=session, tutorial_slug=tutorial_slug, node_id=node_id
    )


@admin_router.delete("/{tutorial_slug}/node/{node_id}/hard")
async def hard_delete_node(
    tutorial_slug: str,
    node_id: int,
    session: AsyncSession = Depends(get_session),
    # Only Super Admin can hard delete
    curr_admin: TokenPayload = Depends(
        RoleChecker([AdminRole.SUPER_ADMIN.value], user_type="admin")
    ),
):
    return await admin_controller.hard_delete_node(
        session=session, tutorial_slug=tutorial_slug, node_id=node_id
    )
