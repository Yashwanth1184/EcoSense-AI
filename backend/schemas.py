from typing import Optional, List
from pydantic import BaseModel, Field

class Soil(BaseModel):
    ph: Optional[float] = Field(None, ge=0, le=14)
    organic_carbon: Optional[float] = Field(None, ge=0)
    moisture: Optional[float] = Field(None, ge=0)

class Land(BaseModel):
    use: Optional[str] = None
    cover: Optional[str] = None

class Biodiversity(BaseModel):
    species_richness: Optional[str] = None
    habitat_diversity: Optional[str] = None

class Climate(BaseModel):
    temperature: Optional[float] = None
    rainfall: Optional[str] = None

class HumanImpact(BaseModel):
    pollution: Optional[str] = None
    deforestation: Optional[str] = None

class EnvironmentalInput(BaseModel):
    text: Optional[str] = None
    soil: Soil = Soil()
    land: Land = Land()
    biodiversity: Biodiversity = Biodiversity()
    climate: Climate = Climate()
    human_impact: HumanImpact = HumanImpact()
    region: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[EnvironmentalInput] = None
