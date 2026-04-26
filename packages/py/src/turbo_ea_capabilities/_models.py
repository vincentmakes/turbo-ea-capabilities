"""Pydantic v2 model for a Business Capability.

Mirrors `schema/capability.schema.json` in the source repo. The flat-form data
file (`capabilities.json`) stores `children` as a list of child ids; the nested
tree file (`tree.json`) stores it as a list of `Capability` objects. The model
accepts both shapes and the loader normalises them for you.

Translations are an additive overlay. Fields on `Capability` always carry the
English source values; call `Capability.localized(lang)` to get a copy with
the localised display fields swapped in. See `schema/i18n.schema.json` for
the translatable-field whitelist.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LocalizedFields(BaseModel):
    """Translatable subset of a capability for one locale.

    All fields optional — an omitted field falls back to the English source
    value for that field only. Mirrors the LocalizedFields definition in
    `schema/i18n.schema.json`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: Optional[str] = None
    description: Optional[str] = None
    aliases: tuple[str, ...] = ()
    in_scope: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()

    @field_validator("aliases", "in_scope", "out_of_scope", mode="before")
    @classmethod
    def _coerce_to_tuple(cls, v: Any) -> tuple[str, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")


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

    def localized(self, lang: str, *, fallback: str = "en") -> "Capability":
        """Return a copy with translatable fields swapped to `lang`.

        Missing per-field translations fall back to the source (English)
        value silently. `lang="en"` and unknown locales both return self
        unchanged. Children are recursively localized.

        This method dispatches to the loader's locale cache; callers do not
        need to touch the bundled data files directly.
        """
        # Local import to avoid a model->loader import cycle at module load.
        from ._loader import _localize  # noqa: PLC0415

        return _localize(self, lang, fallback)


# Forward-ref rebuild for Pydantic v2.
Capability.model_rebuild()
