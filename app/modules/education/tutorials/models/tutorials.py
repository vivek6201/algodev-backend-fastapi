from datetime import datetime
from typing import List, Optional

from sqlalchemy import Index
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

    is_published: Optional[bool] = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class Node(SoftDeleteMixin, SQLModel, table=True):
    __table_args__ = (
        # 1️⃣ Unique slug per tutorial for ROOT nodes (chapters)
        Index(
            "uq_node_tutorial_slug_root",
            "tutorial_slug",
            "slug",
            unique=True,
            postgresql_where="parent_id IS NULL AND deleted_at IS NULL",
        ),
        # 2️⃣ Unique slug per parent for CHILD nodes (topics)
        Index(
            "uq_node_parent_slug",
            "parent_id",
            "slug",
            unique=True,
            postgresql_where="parent_id IS NOT NULL AND deleted_at IS NULL",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    slug: str = Field(index=True)
    order: int = Field(default=0, nullable=False)

    tutorial_slug: str = Field(foreign_key="tutorial.slug", index=True)
    tutorial: "Tutorial" = Relationship(back_populates="nodes")

    node_type_id: int = Field(foreign_key="nodetype.id", index=True)
    node_type: "NodeType" = Relationship(back_populates="nodes")

    parent_id: Optional[int] = Field(default=None, foreign_key="node.id")
    parent: Optional["Node"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Node.id"},
    )
    children: List["Node"] = Relationship(back_populates="parent")

    node_metadata: Optional["NodeMetadata"] = Relationship(back_populates="node")

    is_published: bool = Field(default=False, nullable=False, index=True)
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

    is_leaf: Optional[bool] = Field(default=False, nullable=False, index=True)

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
