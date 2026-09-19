from typing import Any, Dict, List

from backend.rag.retriever import retrieve


# =========================================================
# UNIVERSAL VALUE READER
# =========================================================

def read_value(data: Any, possible_names: List[str]):
    """
    Finds a value even when it is stored inside nested
    Pydantic models or dictionaries.

    This makes the reasoning engine compatible with the
    current EnvironmentalInput schema.
    """

    # -----------------------------------------------------
    # Convert Pydantic models to dictionaries when possible
    # -----------------------------------------------------

    if hasattr(data, "model_dump"):
        try:
            data = data.model_dump()
        except Exception:
            pass

    if hasattr(data, "dict") and not isinstance(data, dict):
        try:
            data = data.dict()
        except Exception:
            pass

    # -----------------------------------------------------
    # Recursive search
    # -----------------------------------------------------

    def search(obj):

        if obj is None:
            return None

        # Dictionary
        if isinstance(obj, dict):

            for key, value in obj.items():

                key_lower = str(key).lower()

                for name in possible_names:

                    if key_lower == name.lower():
                        return value

                result = search(value)

                if result is not None:
                    return result

        # List
        elif isinstance(obj, list):

            for item in obj:

                result = search(item)

                if result is not None:
                    return result

        return None

    return search(data)


# =========================================================
# TEXT CONVERSION
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# CHECK REQUIRED INFORMATION
# =========================================================

def find_missing_fields(data):

    missing = []

    # -----------------------------------------------------
    # Region
    # -----------------------------------------------------

    region = read_value(
        data,
        [
            "region",
            "location",
            "area",
            "climate_region",
        ],
    )

    if region is None or clean_text(region) == "":
        missing.append("region")

    # -----------------------------------------------------
    # Rainfall
    # -----------------------------------------------------

    rainfall = read_value(
        data,
        [
            "rainfall_mm",
            "annual_rainfall",
            "annual_rainfall_mm",
            "rainfall",
        ],
    )

    if rainfall is None or clean_text(rainfall) == "":
        missing.append("rainfall")

    # -----------------------------------------------------
    # Land use
    # -----------------------------------------------------

    land_use = read_value(
        data,
        [
            "land_use",
            "landuse",
            "land",
            "crop",
        ],
    )

    if land_use is None or clean_text(land_use) == "":
        missing.append("land use")

    # -----------------------------------------------------
    # Soil organic carbon
    # -----------------------------------------------------

    organic_carbon = read_value(
        data,
        [
            "organic_carbon_pct",
            "organic_carbon",
            "soil_organic_carbon",
            "soc",
        ],
    )

    if (
        organic_carbon is None
        or clean_text(organic_carbon) == ""
    ):
        missing.append("soil organic carbon")

    return missing


# =========================================================
# CLARIFICATION
# =========================================================

def clarification_question(missing):

    if not missing:
        return None

    return (
        "To provide a reliable biodiversity assessment, "
        "please provide: "
        + ", ".join(missing)
        + "."
    )


# =========================================================
# GET ENVIRONMENTAL VALUES
# =========================================================

def get_environmental_values(data):

    return {

        "region": read_value(
            data,
            [
                "region",
                "location",
                "area",
                "climate_region",
            ],
        ),

        "rainfall": read_value(
            data,
            [
                "rainfall_mm",
                "annual_rainfall",
                "annual_rainfall_mm",
                "rainfall",
            ],
        ),

        "land_use": read_value(
            data,
            [
                "land_use",
                "landuse",
                "land",
                "crop",
            ],
        ),

        "ph": read_value(
            data,
            [
                "ph",
                "soil_ph",
            ],
        ),

        "organic_carbon": read_value(
            data,
            [
                "organic_carbon_pct",
                "organic_carbon",
                "soil_organic_carbon",
                "soc",
            ],
        ),

        "moisture": read_value(
            data,
            [
                "moisture_pct",
                "soil_moisture",
                "moisture",
            ],
        ),

        "species_richness": read_value(
            data,
            [
                "species_richness",
            ],
        ),

        "habitat_diversity": read_value(
            data,
            [
                "habitat_diversity",
            ],
        ),

        "pollution": read_value(
            data,
            [
                "pollution",
            ],
        ),

        "deforestation": read_value(
            data,
            [
                "deforestation",
            ],
        ),
    }


# =========================================================
# MULTI-METRIC DIAGNOSIS
# =========================================================

def diagnose(data):

    values = get_environmental_values(data)

    region = values["region"]
    rainfall = values["rainfall"]
    land_use = values["land_use"]
    ph = values["ph"]
    organic_carbon = values["organic_carbon"]
    moisture = values["moisture"]
    species_richness = values["species_richness"]
    habitat_diversity = values["habitat_diversity"]
    pollution = values["pollution"]
    deforestation = values["deforestation"]

    findings = []

    # -----------------------------------------------------
    # Soil organic carbon
    # -----------------------------------------------------

    try:

        carbon = float(organic_carbon)

        if carbon < 1:

            findings.append(
                f"Soil organic carbon is {carbon}%, "
                "which indicates a relatively low soil-carbon "
                "baseline and makes organic-matter management "
                "an important consideration."
            )

        elif carbon < 2:

            findings.append(
                f"Soil organic carbon is {carbon}%, "
                "indicating an intermediate carbon baseline "
                "that should be monitored over time."
            )

        else:

            findings.append(
                f"Soil organic carbon is {carbon}%, "
                "providing a stronger soil-carbon baseline."
            )

    except (TypeError, ValueError):

        pass

    # -----------------------------------------------------
    # Rainfall
    # -----------------------------------------------------

    try:

        rainfall_value = float(rainfall)

        if rainfall_value < 600:

            findings.append(
                f"Annual rainfall is approximately "
                f"{rainfall_value} mm, indicating relatively "
                "limited water availability and increasing "
                "the importance of moisture-conservation practices."
            )

        else:

            findings.append(
                f"Annual rainfall is approximately "
                f"{rainfall_value} mm, providing a larger "
                "water resource while seasonal availability "
                "should still be considered."
            )

    except (TypeError, ValueError):

        if clean_text(rainfall).lower() in [
            "low",
            "very low",
            "dry",
            "drought",
            "erratic",
        ]:

            findings.append(
                "Rainfall is reported as low or variable, "
                "so water availability should be considered "
                "when selecting biodiversity interventions."
            )

    # -----------------------------------------------------
    # Land use
    # -----------------------------------------------------

    land_text = clean_text(
        land_use
    ).lower()

    if (
        "monoculture" in land_text
        or "single crop" in land_text
        or "monocrop" in land_text
    ):

        findings.append(
            "The reported monoculture system has lower "
            "crop and structural diversity than a diversified "
            "production system."
        )

    elif land_text:

        findings.append(
            f"The reported land-use system is "
            f"'{land_use}'. Its interaction with soil, "
            "water and habitat conditions is included "
            "in the assessment."
        )

    # -----------------------------------------------------
    # Soil moisture
    # -----------------------------------------------------

    try:

        moisture_value = float(moisture)

        if moisture_value < 20:

            findings.append(
                f"Soil moisture is reported as "
                f"{moisture_value}%, indicating that "
                "water-retention and soil-cover practices "
                "may be particularly relevant."
            )

    except (TypeError, ValueError):

        pass

    # -----------------------------------------------------
    # pH
    # -----------------------------------------------------

    try:

        ph_value = float(ph)

        findings.append(
            f"Soil pH is approximately {ph_value}, "
            "which should be considered when selecting "
            "locally suitable vegetation and crops."
        )

    except (TypeError, ValueError):

        pass

    # -----------------------------------------------------
    # Biodiversity
    # -----------------------------------------------------

    if species_richness is not None:

        findings.append(
            f"Species richness is reported as "
            f"{species_richness}, providing a baseline "
            "for future biodiversity monitoring."
        )

    if habitat_diversity is not None:

        findings.append(
            f"Habitat diversity is reported as "
            f"{habitat_diversity}, providing a baseline "
            "for habitat monitoring."
        )

    # -----------------------------------------------------
    # Human impact
    # -----------------------------------------------------

    if pollution:

        findings.append(
            f"Reported pollution level: {pollution}."
        )

    if deforestation:

        findings.append(
            f"Reported deforestation level: {deforestation}."
        )

    # -----------------------------------------------------
    # FINAL DIAGNOSIS
    # -----------------------------------------------------

    if not findings:

        return (
            "The environmental conditions were received, "
            "but additional measurements are needed for "
            "a detailed diagnosis."
        )

    return (
        f"Multi-metric environmental assessment "
        f"for {region}:\n\n"
        + "\n\n".join(findings)
        + "\n\n"
        "The assessment considers soil condition, "
        "water availability, land-use structure and "
        "biodiversity together rather than treating "
        "each environmental variable independently."
    )


# =========================================================
# SCIENTIFIC EVIDENCE
# =========================================================

def retrieve_scientific_evidence(data):

    values = get_environmental_values(data)

    query = (
        "biodiversity conservation "
        "soil organic carbon "
        "soil moisture "
        "rainfall "
        "land use "
        "monoculture "
        "agroforestry "
        "crop diversification "
        "habitat diversity "
        "species richness "
        f"{values['region']} "
        f"{values['land_use']}"
    )

    try:

        evidence = retrieve(
            query,
            6
        )

        if evidence is None:
            return []

        return evidence

    except Exception as error:

        print(
            "Evidence retrieval warning:",
            error
        )

        return []


# =========================================================
# RECOMMENDATION 1
# =========================================================

def recommendation_soil_cover(evidence):

    return {

        "action": (
            "Introduce locally suitable cover crops "
            "or maintain crop residues to increase "
            "continuous soil cover."
        ),

        "why_it_works": (
            "Maintaining soil cover can reduce erosion "
            "and surface exposure while adding organic "
            "inputs and supporting soil moisture and "
            "biological activity."
        ),

        "impacted_metrics": [
            "Soil organic carbon",
            "Soil moisture",
            "Erosion",
            "Soil biodiversity",
        ],

        "time_horizon":
            "Short to medium term",

        "confidence": (
            "Medium — effectiveness depends on "
            "soil type, crop species, climate "
            "and management."
        ),

        "evidence":
            evidence[:3],

        "measurement_plan": [
            "Measure soil organic carbon periodically.",
            "Monitor soil moisture.",
            "Record percentage of soil covered.",
            "Monitor erosion indicators.",
        ],
    }


# =========================================================
# RECOMMENDATION 2
# =========================================================

def recommendation_habitat(evidence):

    return {

        "action": (
            "Increase habitat diversity using locally "
            "suitable native vegetation, field margins, "
            "flowering strips or compatible habitat features."
        ),

        "why_it_works": (
            "Increasing vegetation structure and habitat "
            "variety can provide food, shelter and ecological "
            "resources for a wider range of organisms."
        ),

        "impacted_metrics": [
            "Habitat diversity",
            "Species richness",
            "Pollinator abundance",
            "Ecosystem function",
        ],

        "time_horizon":
            "Medium term",

        "confidence": (
            "Medium — outcomes depend on species "
            "selection and landscape context."
        ),

        "evidence":
            evidence[:3],

        "measurement_plan": [
            "Record the number of habitat types.",
            "Monitor plant and insect species richness.",
            "Track vegetation establishment.",
            "Repeat biodiversity surveys.",
        ],
    }


# =========================================================
# RECOMMENDATION 3
# =========================================================

def recommendation_diversification(evidence):

    return {

        "action": (
            "Diversify the production system using "
            "compatible crop rotation, intercropping "
            "or agroforestry where locally appropriate."
        ),

        "why_it_works": (
            "Increasing plant diversity can provide "
            "additional habitat and biomass while supporting "
            "soil processes and reducing dependence on "
            "a single crop system."
        ),

        "impacted_metrics": [
            "Species richness",
            "Habitat diversity",
            "Soil organic carbon",
            "Water regulation",
        ],

        "time_horizon":
            "Medium to long term",

        "confidence": (
            "Medium — results depend on species "
            "compatibility, water availability "
            "and management."
        ),

        "evidence":
            evidence[:3],

        "measurement_plan": [
            "Record crop and plant diversity.",
            "Measure soil organic carbon periodically.",
            "Monitor species richness.",
            "Track establishment and survival of perennial vegetation.",
        ],
    }


# =========================================================
# GENERATE EXACTLY 3 RECOMMENDATIONS
# =========================================================

def generate_recommendations(
    data,
    evidence
):

    recommendations = [

        recommendation_soil_cover(
            evidence
        ),

        recommendation_habitat(
            evidence
        ),

        recommendation_diversification(
            evidence
        ),
    ]

    return recommendations[:3]


# =========================================================
# MAIN ANALYSIS FUNCTION
# =========================================================

def analyze(data):

    # -----------------------------------------------------
    # Check required information
    # -----------------------------------------------------

    missing = find_missing_fields(data)

    if missing:

        return {

            "status":
                "needs_clarification",

            "missing_fields":
                missing,

            "clarifying_question":
                clarification_question(
                    missing
                ),

            "diagnosis":
                None,

            "recommendations":
                [],

            "retrieved_evidence":
                [],

            "conversation_summary":
                "Additional environmental information "
                "is required before generating recommendations.",
        }

    # -----------------------------------------------------
    # Retrieve evidence
    # -----------------------------------------------------

    evidence = retrieve_scientific_evidence(
        data
    )

    # -----------------------------------------------------
    # Diagnose
    # -----------------------------------------------------

    diagnosis = diagnose(
        data
    )

    # -----------------------------------------------------
    # Generate exactly 3 recommendations
    # -----------------------------------------------------

    recommendations = generate_recommendations(
        data,
        evidence
    )

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {

        "status":
            "ok",

        "missing_fields":
            [],

        "clarifying_question":
            None,

        "diagnosis":
            diagnosis,

        "recommendations":
            recommendations,

        "retrieved_evidence":
            evidence,

        "conversation_summary":
            "The assessment combines soil health, "
            "water availability, land use and biodiversity "
            "indicators before producing exactly three "
            "evidence-grounded recommendations.",
    }