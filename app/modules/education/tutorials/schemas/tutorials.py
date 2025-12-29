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


class NodeBase(BaseModel):
    title: str
    order: int
    parent_id: Optional[int] = None
    node_type: int


class CreateNodeType(BaseModel):
    name: str
    is_leaf: Optional[bool] = False


class NodeTypeResponse(BaseModel):
    name: str
    is_leaf: Optional[bool] = False
    model_config = ConfigDict(from_attributes=True)


class NodeResponse(BaseModel):
    id: int
    title: str
    slug: str
    order: int
    node_type: NodeTypeResponse
    parent_id: Optional[int] = None
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
    nodes: List[NodeResponse] = []

    model_config = ConfigDict(from_attributes=True)
