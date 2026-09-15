"""Traditional Ecological Knowledge (TEK) and environmental intelligence analyzer."""

import re
from typing import List, Optional, Tuple
from app.config.logging import get_logger
from app.schemas.evidence import EvidenceType
from app.schemas.folklore import EnvironmentalCategory, EnvironmentalKnowledge

logger = get_logger("folklore.ecology")

# Curated pattern registry mapping concrete operational TEK practices to categories
TEK_PRACTICE_PATTERNS = [
    (
        EnvironmentalCategory.WATER_MANAGEMENT,
        r"\b(johad|tanka|khadin|baoli|stepwell|ahar[\s-]pyne|kund|beris|water harvesting|rainwater storage|check dam|bunding|bunds|irrigation canal|water reservoir)\b",
        "Traditional water conservation and storage infrastructure",
        ["water", "reservoirs", "catchment"],
    ),
    (
        EnvironmentalCategory.FOREST_MANAGEMENT,
        r"\b(sacred grove|oran|devrai|khejri protection|chipko|forest taboo|cutting trees forbidden|sacred tree|banyan protection|neem grove)\b",
        "Community-governed sacred grove and forest preservation practice",
        ["trees", "forest canopy", "sacred flora"],
    ),
    (
        EnvironmentalCategory.MEDICINAL_PLANTS,
        r"\b(medicinal|neem decoction|tulsi cure|ayurvedic herb|healing bark|crushed leaves for wound|herbal remedy|antidote for venom|fever concoction)\b",
        "Ethnobotanical medicinal application and herbal formulation",
        ["medicinal herbs", "flora", "healing plants"],
    ),
    (
        EnvironmentalCategory.AGRICULTURE,
        r"\b(crop rotation|mixed cropping|intercropping|monsoon sowing|kharif|rabi|zaid|millets cultivation|indigenous seed preservation|seed keeping|ploughing method)\b",
        "Indigenous agricultural cycle and crop husbandry method",
        ["seeds", "crops", "arable land"],
    ),
    (
        EnvironmentalCategory.ANIMAL_HUSBANDRY,
        r"\b(pastoral grazing route|camel breeding|livestock shelter|shepherd trail|cattle vaccination traditional|milk fermentation|grazing commons)\b",
        "Pastoralist livestock management and migration knowledge",
        ["livestock", "pasture", "grazing commons"],
    ),
    (
        EnvironmentalCategory.WEATHER_KNOWLEDGE,
        r"\b(monsoon cloud omen|ant behavior before rain|frog croaking indicates deluge|swallow flight height|wind direction predicts drought|nakshatra rain)\b",
        "Meteorological observation and seasonal weather forecasting",
        ["clouds", "winds", "rain omens"],
    ),
    (
        EnvironmentalCategory.SEASONAL_KNOWLEDGE,
        r"\b(ritu|solstice calendar|seasonal festival cycle|vernal equinox|autumn harvest timing|dry season preparation|winter migration)\b",
        "Cyclical seasonal calendar and ecological phenology",
        ["seasons", "phenology", "calendar"],
    ),
    (
        EnvironmentalCategory.SOIL_MANAGEMENT,
        r"\b(cow dung manure|composting|black soil retention|silt application from lake bed|green manure|terrace farming soil conservation)\b",
        "Soil fertility preservation and erosion control practice",
        ["soil", "manure", "silt"],
    ),
    (
        EnvironmentalCategory.BIODIVERSITY,
        r"\b(wildlife coexistence pact|totemic animal taboo|sparing nesting birds|fisheries breeding season taboo|mangrove protection pact)\b",
        "Customary biodiversity conservation and species taboo",
        ["species", "wildlife", "habitat"],
    ),
    (
        EnvironmentalCategory.FOOD_PRESERVATION,
        r"\b(sun drying vegetables|pickling with mustard oil|grain storage in clay bins|smokery|salting meat|curd fermentation in earthenware)\b",
        "Post-harvest food preservation and emergency grain storage",
        ["grains", "earthenware", "preserved foods"],
    ),
    (
        EnvironmentalCategory.ARCHITECTURE,
        r"\b(lime plaster cooling|thick mud walls for desert heat|jaali airflow screen|courtyard ventilation|earthquake-resistant kath-kuni)\b",
        "Vernacular climate-adapted architecture and passive cooling",
        ["mud", "limestone", "timber frames"],
    ),
    (
        EnvironmentalCategory.NAVIGATION,
        r"\b(pole star navigation|dune ridge orientation|river current reading|bird navigation at sea|constellation waypoint)\b",
        "Traditional astronomical and terrain-based navigation",
        ["stars", "terrain", "currents"],
    ),
    (
        EnvironmentalCategory.NATURAL_HAZARDS,
        r"\b(cyclone warning signs|flood escape route|drought reserve grain|tsunami sea retreat warning|forest fire back burning)\b",
        "Community disaster risk reduction and hazard preparedness",
        ["hazard warning", "safety reserves"],
    ),
    (
        EnvironmentalCategory.RESOURCE_MANAGEMENT,
        r"\b(common pool resource|shared pasture quota|rotational well usage|sustainable honey harvesting|firewood collection limit)\b",
        "Customary governance and quota allocation of common-pool resources",
        ["commons", "governance rules"],
    ),
]


class EcologyAnalyzer:
    """Analyzes Traditional Ecological Knowledge (TEK) requiring explicit practice evidence."""

    def analyze_ecology(self, text: str, source_url: Optional[str] = None) -> List[EnvironmentalKnowledge]:
        """Extract verified TEK records backed by direct passage evidence from source text."""
        records: List[EnvironmentalKnowledge] = []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

        for category, pattern, desc_template, default_resources in TEK_PRACTICE_PATTERNS:
            for sentence in sentences:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    matched_term = match.group(0)
                    knowledge_summary = f"{category.value.replace('_', ' ').title()}: {matched_term.title()} usage"
                    
                    records.append(
                        EnvironmentalKnowledge(
                            knowledge=knowledge_summary,
                            category=category,
                            description=f"{desc_template} identified via '{matched_term}'.",
                            resources=default_resources,
                            practice=matched_term,
                            source=source_url,
                            evidence=sentence,
                            evidence_type=EvidenceType.DIRECT,
                            confidence=0.90,
                        )
                    )
                    break  # Avoid duplicating the same category on multiple sentences

        logger.info("tek_analysis_completed", found_items=len(records))
        return records
