from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Literal

ExchangeKind = Literal["production", "technosphere", "biosphere"]


@dataclass(frozen=True)
class ProviderKey:
    """Exact Brightway supplier identity.

    ``name``, ``product``, ``location`` and ``unit`` are intentionally all
    required. Calculation code is not allowed to silently fall back to a fuzzy
    match.
    """

    name: str
    product: str
    location: str
    unit: str
    database: str | None = None


@dataclass(frozen=True)
class Provenance:
    source_file: str
    source_sheet: str
    source_cell: str
    derivation: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class ExchangeSpec:
    name: str
    amount: float
    unit: str
    kind: ExchangeKind
    stage: str
    provider: ProviderKey | None = None
    categories: tuple[str, ...] | None = None
    temporal_profile: str = "same_year"
    temporal_offsets: tuple[int, ...] | None = None
    temporal_weights: tuple[float, ...] | None = None
    provenance: Provenance | None = None
    comment: str | None = None

    def __post_init__(self) -> None:
        if self.kind == "technosphere" and self.provider is None:
            raise ValueError(f"Technosphere exchange {self.name!r} has no provider")
        if self.kind == "biosphere" and not self.categories:
            raise ValueError(f"Biosphere exchange {self.name!r} has no categories")
        if self.kind == "production" and self.amount <= 0:
            raise ValueError("Production amount must be positive")
        if (self.temporal_offsets is None) != (self.temporal_weights is None):
            raise ValueError("Temporal offsets and weights must be supplied together")
        if self.temporal_offsets is not None:
            if len(self.temporal_offsets) != len(self.temporal_weights or ()):
                raise ValueError("Temporal offsets and weights must have equal length")
            if not self.temporal_offsets:
                raise ValueError("A custom temporal profile cannot be empty")
            if abs(sum(self.temporal_weights or ()) - 1.0) > 1e-9:
                raise ValueError("Custom temporal weights must sum to one")


@dataclass(frozen=True)
class ActivitySpec:
    code: str
    name: str
    product: str
    location: str
    unit: str
    exchanges: tuple[ExchangeSpec, ...]
    database: str = "ccus-webinar-foreground"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        production = [exc for exc in self.exchanges if exc.kind == "production"]
        if len(production) != 1:
            raise ValueError(
                f"Activity {self.code!r} must have exactly one production "
                f"exchange; found {len(production)}"
            )
        if len({exc.name for exc in production}) != 1:
            raise ValueError(f"Activity {self.code!r} has an invalid production")

    def canonical_dict(self) -> dict:
        return asdict(self)


def model_hash(activities: tuple[ActivitySpec, ...] | list[ActivitySpec]) -> str:
    """Return a stable hash independent of list construction order."""

    payload = [
        item.canonical_dict() for item in sorted(activities, key=lambda x: x.code)
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()
