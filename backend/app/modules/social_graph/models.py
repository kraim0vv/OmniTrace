"""
OmniTrace Social Graph Mapping — Domain Models
===============================================
Type-safe Pydantic data schemas representing OSINT social graph entities,
relationships, heuristic match results, and extraction payloads.
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, computed_field


class PlatformType(str, Enum):
    """Enumeration of supported OSINT target platforms."""
    VK = "vk"
    TELEGRAM = "telegram"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    GENERIC = "generic"


class RelationType(str, Enum):
    """Enumeration of graph edge relationship semantics."""
    FRIEND = "friend"
    FOLLOWER = "follower"
    FOLLOWING = "following"
    MUTUAL = "mutual_friend"
    RELATIVE_CONFIRMED = "relative_confirmed"
    RELATIVE_CANDIDATE = "relative_candidate"
    SAME_LOCATION = "same_location"
    SAME_SURNAME = "same_surname"
    INTERACTION = "interaction"
    SHARED_MEMBERSHIP = "shared_membership"


class NodeClassification(str, Enum):
    """Forensic relevance category for nodes in the social graph."""
    SEED_TARGET = "seed_target"
    PRIMARY_TARGET = "primary_target"
    HIGH_PROBABILITY_RELATIVE = "high_probability_relative"
    CLOSE_ASSOCIATE = "close_associate"
    PERIPHERAL = "peripheral"


class ProfileNode(BaseModel):
    """
    Represents an entity/person profile in the social graph.
    Serves as an immutable node structure inside NetworkX.
    """
    id: str = Field(
        ...,
        description="Globally unique node ID, formatted as '{platform}:{platform_user_id}'."
    )
    platform: PlatformType = Field(
        ...,
        description="The social network or protocol where this account was discovered."
    )
    raw_id: str = Field(
        ...,
        description="The platform-native identifier (numeric ID or primary unique handle)."
    )
    username: Optional[str] = Field(
        default=None,
        description="Public username or display handle (e.g. '@durov')."
    )
    first_name: Optional[str] = Field(default=None, description="Extracted given name.")
    last_name: Optional[str] = Field(default=None, description="Extracted family name/surname.")
    birth_date: Optional[str] = Field(
        default=None,
        description="Birth date string in ISO YYYY-MM-DD or partial DD.MM format."
    )
    birth_year: Optional[int] = Field(default=None, description="Resolved birth year if available.")
    hometown: Optional[str] = Field(default=None, description="Reported birthplace / hometown.")
    current_city: Optional[str] = Field(default=None, description="Reported current residence city.")
    profile_url: Optional[str] = Field(default=None, description="Direct web URL to profile.")
    avatar_url: Optional[str] = Field(default=None, description="URL of primary profile avatar.")
    bio: Optional[str] = Field(default=None, description="User biography / status statement.")
    classification: NodeClassification = Field(
        default=NodeClassification.PERIPHERAL,
        description="Investigation classification level assigned by the heuristic engine."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary platform-specific attributes (phone hints, emails, groups, etc.)."
    )

    @computed_field
    @property
    def display_name(self) -> str:
        """Returns a synthesized human-readable label for graph visualization."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.username:
            return f"@{self.username}"
        return f"{self.platform.value}:{self.raw_id}"

    class Config:
        frozen = False
        validate_assignment = True


class RelationshipEdge(BaseModel):
    """
    Represents a directed or undirected connection between two ProfileNodes.
    """
    source_id: str = Field(..., description="ID of source ProfileNode.")
    target_id: str = Field(..., description="ID of target ProfileNode.")
    relation_type: RelationType = Field(..., description="Semantic type of the relationship.")
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence weight or intimacy metric of the connection (0.0 to 1.0)."
    )
    discovered_at: float = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).timestamp(),
        description="Unix timestamp when this relationship was observed."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Auxiliary relationship metadata (e.g. mutual friends count, interaction date)."
    )


class HeuristicMatchResult(BaseModel):
    """
    Evaluation output from the heuristic correlation engine indicating
    high-probability relatives or close targets.
    """
    source_id: str
    target_id: str
    surname_score: float = Field(ge=0.0, le=1.0)
    location_score: float = Field(ge=0.0, le=1.0)
    age_score: float = Field(ge=0.0, le=1.0)
    structural_score: float = Field(ge=0.0, le=1.0)
    composite_probability: float = Field(ge=0.0, le=1.0)
    inferred_relation: str = Field(
        ...,
        description="Inferred classification: e.g., 'IMMEDIATE_FAMILY', 'SIBLING', 'PARENT_CHILD', 'CLOSE_ASSOCIATE'."
    )
    justification: List[str] = Field(
        default_factory=list,
        description="Human-readable audit trail explaining the score computation."
    )


class ExtractionResult(BaseModel):
    """
    Standard output payload returned by any concrete BaseExtractor implementation.
    """
    seed_profile: ProfileNode
    connections: List[ProfileNode] = Field(default_factory=list)
    relationships: List[RelationshipEdge] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
