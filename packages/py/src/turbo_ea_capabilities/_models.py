"""Pydantic v2 models for the catalogue artefacts (capabilities, business
processes, value streams).

Mirrors the JSON schemas under `schema/` in the source repo. The flat-form
data files (`capabilities.json`, `business-processes.json`) store `children`
as a list of child ids; the nested tree files (`tree.json`, `bp-tree.json`)
store it as a list of objects. The models accept both shapes and the loader
normalises them for you.

Translations are an additive overlay. Fields on `Capability`/`BusinessProcess`
always carry the English source values; call `.localized(lang)` to get a copy
with the localised display fields swapped in. See `schema/i18n.schema.json`
for the translatable-field whitelist.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LocalizedFields(BaseModel):
    """Translatable subset of a capability/process/value-stream entry for one
    locale. All fields optional — an omitted field falls back to the English
    source value. Mirrors the union of `CapabilityFields` and
    `ValueStreamFields` in `schema/i18n.schema.json`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: Optional[str] = None
    stage_name: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
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

    # Reverse indices populated by build_api.ts (empty when no backlinks exist).
    realizes_processes: tuple[str, ...] = ()
    value_stream_stages: tuple[str, ...] = ()

    children: tuple["Capability", ...] = ()

    @field_validator("aliases", "tags", "references", "in_scope", "out_of_scope",
                     "realizes_processes", "value_stream_stages", mode="before")
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

        Missing per-field translations fall back silently to the English
        source. `lang="en"` and unknown locales both return self unchanged.
        Children are recursively localized.
        """
        from ._loader import _localize_capability  # noqa: PLC0415

        return _localize_capability(self, lang, fallback)


class FrameworkRef(BaseModel):
    """Structured cross-reference to an external process/capability framework."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    framework: Literal["APQC-PCF", "BIAN", "eTOM", "ITIL", "SCOR"]
    external_id: str
    version: Optional[str] = None
    url: Optional[str] = None


class BusinessProcess(BaseModel):
    """A node in the business-process catalogue (BP- ids).

    Mirrors `schema/business-process.schema.json`. Anchored on APQC PCF's
    Category → Process Group → Process → Activity hierarchy.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    level: int = Field(ge=1, le=4)
    parent_id: Optional[str] = None

    description: Optional[str] = None
    aliases: tuple[str, ...] = ()
    industry: Optional[str] = None
    references: tuple[str, ...] = ()
    framework_refs: tuple[FrameworkRef, ...] = ()
    realizes_capability_ids: tuple[str, ...] = ()
    in_scope: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()

    deprecated: bool = False
    deprecation_reason: Optional[str] = None
    successor_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Reverse index populated by build_api.ts.
    realized_in_value_streams: tuple[str, ...] = ()

    children: tuple["BusinessProcess", ...] = ()

    @field_validator("aliases", "references", "realizes_capability_ids",
                     "in_scope", "out_of_scope", "realized_in_value_streams",
                     mode="before")
    @classmethod
    def _coerce_to_tuple(cls, v: Any) -> tuple[str, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")

    @field_validator("framework_refs", mode="before")
    @classmethod
    def _coerce_framework_refs(cls, v: Any) -> tuple[Any, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")

    @field_validator("children", mode="before")
    @classmethod
    def _coerce_children(cls, v: Any) -> Any:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], str):
            return ()
        return v

    def localized(self, lang: str, *, fallback: str = "en") -> "BusinessProcess":
        from ._loader import _localize_business_process  # noqa: PLC0415

        return _localize_business_process(self, lang, fallback)


class ValueStreamStage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    stage_order: int = Field(ge=1)
    stage_name: str
    capability_ids: tuple[str, ...]
    process_ids: tuple[str, ...]
    industries: tuple[str, ...] = ()
    industry_variant: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("capability_ids", "process_ids", "industries", mode="before")
    @classmethod
    def _coerce_to_tuple(cls, v: Any) -> tuple[str, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")


class ValueStream(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    description: Optional[str] = None
    industries: tuple[str, ...]
    deprecated: bool = False
    deprecation_reason: Optional[str] = None
    successor_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    stages: tuple[ValueStreamStage, ...] = ()

    @field_validator("industries", mode="before")
    @classmethod
    def _coerce_industries(cls, v: Any) -> tuple[str, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")

    @field_validator("stages", mode="before")
    @classmethod
    def _coerce_stages(cls, v: Any) -> tuple[Any, ...]:
        if v is None:
            return ()
        if isinstance(v, (list, tuple)):
            return tuple(v)
        raise TypeError(f"Expected list/tuple, got {type(v).__name__}")


# Forward-ref rebuild for Pydantic v2.
Capability.model_rebuild()
BusinessProcess.model_rebuild()
