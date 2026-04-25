"""Pydantic v2 model for a Business Capability.

Mirrors `schema/capability.schema.json` in the source repo. The flat-form data
file (`capabilities.json`) stores `children` as a list of child ids; the nested
tree file (`tree.json`) stores it as a list of `Capability` objects. The model
accepts both shapes and the loader normalises them for you.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Capability(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    level: int = Field(ge=1, le=4)
    parent_id: Optional[str] = None

    description: Optional[str] = None
    aliases: tuple[str, ...] = ()
    owner: Optional[str] = None
    tags: tuple[str, ...] = ()
    industry: Optional[str] = None
    references: tuple[str, ...] = ()
    in_scope: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()

    deprecated: bool = False
    deprecation_reason: Optional[str] = None
    successor_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    children: tuple["Capability", ...] = ()

    @field_validator("aliases", "tags", "references", "in_scope", "out_of_scope", mode="before")
    @classmethod
    def _coerce_to_tuple(cls, v: Any) -> tuple[str, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")

    @field_validator("children", mode="before")
    @classmethod
    def _coerce_children(cls, v: Any) -> Any:
        # Accept either a list of ids (from capabilities.json flat form), in
        # which case we strip them — the loader rebuilds children from the
        # full id->Capability map. Or a list of dicts/Capability objects from
        # tree.json, which we pass through.
        if v is None:
            return ()
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], str):
            return ()
        return v


# Forward-ref rebuild for Pydantic v2.
Capability.model_rebuild()
