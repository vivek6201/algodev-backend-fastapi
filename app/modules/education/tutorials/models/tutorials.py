from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.modules.common.model import SoftDeleteMixin
from app.modules.education.shared.model import TutorialCategoryLink


class Tutorial(SoftDeleteMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    slug: str = Field(index=True, unique=True)
    description: Optional[str] = None

    nodes: List["Node"] = Relationship(back_populates="tutorial")

    categories: List["EducationCategory"] = Relationship(  # noqa: F821
        back_populates="tutorials",
        link_model=TutorialCategoryLink,
    )

    is_published: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class Node(SoftDeleteMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    slug: str
    order: int = Field(default=0, nullable=False)

    tutorial_id: int = Field(foreign_key="tutorial.id", index=True)
    tutorial: Tutorial = Relationship(back_populates="nodes")

    node_type_id: int = Field(foreign_key="nodetype.id", index=True)
    node_type: "NodeType" = Relationship(back_populates="nodes")

    parent_id: Optional[int] = Field(default=None, foreign_key="node.id")
    parent: Optional["Node"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Node.id"},
    )
    children: List["Node"] = Relationship(back_populates="parent")

    node_metadata: Optional["NodeMetadata"] = Relationship(back_populates="node")

    is_published: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class NodeType(SoftDeleteMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    icon: Optional[str] = None

    is_leaf: bool = False

    nodes: List["Node"] = Relationship(back_populates="node_type")

    created_at: datetime = Field(default_factory=datetime.utcnow)


class NodeMetadata(SoftDeleteMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    node_id: int = Field(
        foreign_key="node.id",
        unique=True,
        index=True,
    )

    node: Node = Relationship(back_populates="node_metadata")

    content: str = Field(default="", nullable=False)
