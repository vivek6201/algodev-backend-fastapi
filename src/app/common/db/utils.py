from sqlmodel import Field
from sqlmodel import Column, Enum as SAEnum

def pg_enum(enum_cls, **kwargs):
    """
    Automatically creates a Field with a named SQLAlchemy Enum.
    The name is derived automatically from the class name.
    """
    return Field(
        sa_column=Column(
            # We auto-generate the name here using enum_cls.__name__
            SAEnum(enum_cls, name=enum_cls.__name__.lower()), 
            **kwargs
        )
    )