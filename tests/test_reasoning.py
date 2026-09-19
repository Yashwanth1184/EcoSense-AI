from backend.schemas import EnvironmentalInput
from backend.ai.reasoning import missing_fields, diagnose

def test_missing_fields():
    data = EnvironmentalInput()
    missing = missing_fields(data)
    assert "soil organic carbon (%)" in missing
    assert "land use / crop type" in missing
    assert "rainfall pattern" in missing

def test_multimetric_diagnosis():
    data = EnvironmentalInput(
        soil={"organic_carbon":0.3,"moisture":18},
        land={"use":"monoculture wheat"},
        biodiversity={"species_richness":"low","habitat_diversity":"low"},
        climate={"rainfall":"low"},
        region="semi-arid"
    )
    assert len(diagnose(data)) >= 4
