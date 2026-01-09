from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TutorialBase(BaseModel):
    title: str
    description: str
    categories: List[int]


class TutorialUpdate(TutorialBase):
    title: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[int]] = None


class NodeContent(BaseModel):
    editorial: str
    video_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class NodeBase(BaseModel):
    title: str
    order: int
    parent_id: Optional[int] = None
    node_type: int
    content: Optional[NodeContent] = None


class NodeBaseUpdate(NodeBase):
    title: Optional[str] = None
    order: Optional[int] = None
    node_type: Optional[int] = None


class CreateNodeType(BaseModel):
    name: str
    is_leaf: Optional[bool] = False


class NodeTypeResponse(BaseModel):
    id: int
    name: str
    is_leaf: Optional[bool] = False
    model_config = ConfigDict(from_attributes=True)


class NodeOperationResponse(NodeBase):
    id: int
    slug: str
    node_type: NodeTypeResponse
    parent_id: Optional[int] = None
    is_published: Optional[bool] = False
    content: Optional[NodeContent] = None

    model_config = ConfigDict(from_attributes=True)


class NodeResponse(NodeOperationResponse):
    children: List["NodeResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TutorialResponse(TutorialBase):
    id: int
    slug: str
    is_published: bool
    categories: List[CategoryResponse] = []
    nodes: Optional[List[NodeResponse]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
