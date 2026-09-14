"""Folklore domain schemas, entities, environmental knowledge, and variant models."""

import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.source import SourceInfo


class EvidenceType(str, Enum):
    """Classification of how knowledge was evidenced in source text."""
    EXPLICIT = "explicit"
    INFERENCE = "inference"
    SPECULATIVE = "speculative"


class EnvironmentalCategory(str, Enum):
    """Categorization of Traditional Ecological Knowledge."""
    WATER_MANAGEMENT = "water_management"
    AGRICULTURE = "agriculture"
    ANIMAL_HUSBANDRY = "animal_husbandry"
    FOREST_MANAGEMENT = "forest_management"
    MEDICINAL_PLANTS = "medicinal_plants"
    WEATHER_KNOWLEDGE = "weather_knowledge"
    SEASONAL_KNOWLEDGE = "seasonal_knowledge"
    SOIL_MANAGEMENT = "soil_management"
    BIODIVERSITY = "biodiversity"
    FOOD_PRESERVATION = "food_preservation"
    ARCHITECTURE = "architecture"
    NAVIGATION = "navigation"
    NATURAL_HAZARDS = "natural_hazards"
    RESOURCE_MANAGEMENT = "resource_management"
    LANDSCAPE = "landscape"
    OTHER = "other"


class FolkloreType(str, Enum):
    """Primary categorization of folklore genres."""
    FOLKTALE = "folktale"
    LEGEND = "legend"
    MYTH = "myth"
    FAIRY_TALE = "fairy_tale"
    FABLE = "fable"
    HEROIC_TALE = "heroic_tale"
    LOVE_STORY = "love_story"
    ORIGIN_STORY = "origin_story"
    GHOST_STORY = "ghost_story"
    RELIGIOUS_TALE = "religious_tale"
    TRICKSTER_TALE = "trickster_tale"
    ANIMAL_TALE = "animal_tale"
    CREATION_STORY = "creation_story"
    ETIOLOGICAL_TALE = "etiological_tale"
    FOLK_SONG = "folk_song"
    FOLK_POEM = "folk_poem"
    ORAL_HISTORY = "oral_history"
    PROVERB = "proverb"
    RIDDLE = "riddle"
    RITUAL_NARRATIVE = "ritual_narrative"
    OTHER = "other"


class Character(BaseModel):
    """Folklore character entity."""
    name: str
    aliases: List[str] = Field(default_factory=list)
    role: str = Field(default="protagonist", description="e.g. protagonist, antagonist, trickster, deity, supporting")
    gender: Optional[str] = None
    species: str = Field(default="human", description="e.g. human, animal, spirit, deity, mythical_creature")
    description: str = ""
    relationships: List[str] = Field(default_factory=list)


class Location(BaseModel):
    """Geographical or mythical location entity."""
    name: str
    type: str = Field(default="settlement", description="e.g. village, city, forest, river, mountain, sacred_site")
    region: Optional[str] = None
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mentioned_in_story: bool = True


class EnvironmentalKnowledge(BaseModel):
    """Traditional Ecological Knowledge (TEK) observation embedded in folklore."""
    knowledge: str = Field(description="Summary of the traditional knowledge or practice")
    category: EnvironmentalCategory = Field(default=EnvironmentalCategory.OTHER)
    description: str = ""
    resources: List[str] = Field(default_factory=list, description="e.g. water, neem, black soil, monsoon clouds")
    ecosystem: Optional[str] = Field(default=None, description="e.g. desert, western ghats, mangrove, gangetic plain")
    practice: Optional[str] = Field(default=None, description="Action or technique described")
    evidence: Optional[str] = Field(default=None, description="Direct quote or passage reference from text")
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    evidence_type: EvidenceType = Field(default=EvidenceType.EXPLICIT)


class ClassificationResult(BaseModel):
    """Classification assessment of folklore content."""
    is_folklore: bool = True
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    type: FolkloreType = Field(default=FolkloreType.FOLKTALE)
    subtype: Optional[str] = None
    tradition: Optional[str] = Field(default=None, description="e.g. Rajasthani, Bengali, Gondi, Santhali")
    oral_tradition: bool = True


class Variant(BaseModel):
    """Relationship model connecting a canonical folklore record to its cultural variants."""
    canonical_id: str
    variant_id: str
    variant_title: str
    region: Optional[str] = None
    language: Optional[str] = None
    differences: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source: Optional[SourceInfo] = None


class FolkloreDocument(BaseModel):
    """Complete canonical Folklore schema for Lokkatha."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    title: str
    alternate_titles: List[str] = Field(default_factory=list)

    category: str = Field(default="folktale")
    folklore_type: FolkloreType = Field(default=FolkloreType.FOLKTALE)

    story: str = Field(description="Full text or narrative description")
    summary: str = ""

    region: List[str] = Field(default_factory=list, description="States or cultural regions, e.g. ['Rajasthan', 'Marwar']")
    country: str = "India"

    language: List[str] = Field(default_factory=list)
    original_language: Optional[str] = None
    translated: bool = False

    characters: List[Character] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    communities: List[str] = Field(default_factory=list)

    themes: List[str] = Field(default_factory=list)
    motifs: List[str] = Field(default_factory=list)

    cultural_elements: List[str] = Field(default_factory=list)
    rituals: List[str] = Field(default_factory=list)
    festivals: List[str] = Field(default_factory=list)
    beliefs: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    foodways: List[str] = Field(default_factory=list)
    occupations: List[str] = Field(default_factory=list)

    environmental_knowledge: List[EnvironmentalKnowledge] = Field(default_factory=list)
    flora: List[str] = Field(default_factory=list)
    fauna: List[str] = Field(default_factory=list)
    landscape: List[str] = Field(default_factory=list)

    historical_context: Optional[str] = None
    social_context: Optional[str] = None

    oral_tradition: bool = False
    variants: List[Variant] = Field(default_factory=list)

    source: SourceInfo
    confidence: Dict[str, float] = Field(default_factory=lambda: {"overall": 0.85})
    copyright_status: str = Field(default="unknown", description="unknown, public_domain, copyrighted, creative_commons")
