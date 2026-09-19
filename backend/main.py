from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from backend.ai.reasoning import analyze
from backend.rag.retriever import retrieve


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="EcoSense AI",
    description="AI-powered biodiversity and environmental reasoning system",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Existing deployment
        "https://biodiversity-intelligence-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "service": "EcoSense AI",
        "status": "running",
        "message": "Environmental intelligence API is running.",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "EcoSense AI",
    }


# =========================================================
# ANALYZE ENVIRONMENT
# =========================================================

@app.post("/api/analyze")
def analyze_environment(
    environmental_data: Dict[str, Any]
):

    print("\n========================================")
    print("NEW ENVIRONMENTAL ANALYSIS REQUEST")
    print("========================================")

    print(environmental_data)

    try:

        result = analyze(
            environmental_data
        )

        print("\nAnalysis result:")
        print(result)

        return result

    except Exception as error:

        print(
            "ERROR:",
            repr(error)
        )

        return {
            "status": "error",

            "diagnosis":
                "The environmental analysis encountered an internal error.",

            "recommendations": [],

            "retrieved_evidence": [],

            "conversation_summary":
                str(error),

            "error":
                str(error),
        }


# =========================================================
# BUILD CHAT RAG QUERY
# =========================================================

def build_chat_query(
    user_question: str,
    region: Any,
    rainfall: Any,
    land_use: Any,
    ph: Any,
    organic_carbon: Any,
    moisture: Any,
    species_richness: Any,
    habitat_diversity: Any,
    pollution: Any,
    deforestation: Any,
):
    """
    Build a scientific retrieval query using both the user's
    question and the current environmental context.
    """

    return (
        f"Environmental question: {user_question}. "

        f"Region: {region}. "

        f"Annual rainfall: {rainfall} mm. "

        f"Land use: {land_use}. "

        f"Soil pH: {ph}. "

        f"Soil organic carbon: {organic_carbon}%. "

        f"Soil moisture: {moisture}%. "

        f"Species richness: {species_richness}. "

        f"Habitat diversity: {habitat_diversity}. "

        f"Pollution: {pollution}. "

        f"Deforestation: {deforestation}. "

        "Relevant scientific topics include biodiversity, "
        "ecosystem services, habitat diversity, species richness, "
        "soil health, soil organic carbon, soil moisture, "
        "conservation agriculture, agroforestry, land degradation "
        "and sustainable land management."
    )


# =========================================================
# FORMAT RETRIEVED EVIDENCE
# =========================================================

def format_evidence(evidence):
    """
    Convert retrieved ChromaDB records into a simple structure
    that can be returned to the frontend.
    """

    formatted = []

    if not evidence:
        return formatted

    for item in evidence:

        if not isinstance(item, dict):
            formatted.append({
                "title": str(item),
                "source": "",
                "content": str(item),
            })
            continue

        title = (
            item.get("title")
            or item.get("name")
            or item.get("document")
            or "Scientific evidence"
        )

        source = (
            item.get("source")
            or item.get("reference")
            or item.get("url")
            or ""
        )

        content = (
            item.get("content")
            or item.get("text")
            or item.get("document")
            or ""
        )

        formatted.append({
            "title": str(title),
            "source": str(source),
            "content": str(content),
        })

    return formatted


# =========================================================
# FOLLOW-UP CHAT
# =========================================================

@app.post("/api/chat")
def follow_up_chat(
    message: Dict[str, Any]
):

    user_message = str(
        message.get(
            "message",
            ""
        )
    ).strip()

    # =====================================================
    # PREVIOUS ENVIRONMENTAL CONTEXT
    # =====================================================

    region = message.get(
        "region",
        "unknown"
    )

    rainfall = message.get(
        "rainfall_mm",
        500
    )

    land_use = message.get(
        "land_use",
        "unknown"
    )

    ph = message.get(
        "ph",
        6.5
    )

    organic_carbon = message.get(
        "organic_carbon_pct",
        1.0
    )

    moisture = message.get(
        "moisture_pct",
        20
    )

    species_richness = message.get(
        "species_richness",
        5
    )

    habitat_diversity = message.get(
        "habitat_diversity",
        1
    )

    pollution = message.get(
        "pollution",
        "low"
    )

    deforestation = message.get(
        "deforestation",
        "low"
    )

    recommendations = message.get(
        "recommendations",
        []
    )

    # =====================================================
    # NORMALIZE QUESTION
    # =====================================================

    question = user_message.lower().strip()


    # =====================================================
    # RETRIEVE SCIENTIFIC EVIDENCE
    # =====================================================

    retrieved_evidence = []

    try:

        rag_query = build_chat_query(
            user_message,
            region,
            rainfall,
            land_use,
            ph,
            organic_carbon,
            moisture,
            species_richness,
            habitat_diversity,
            pollution,
            deforestation,
        )

        retrieved_evidence = retrieve(
            rag_query,
            5
        )

        if retrieved_evidence is None:
            retrieved_evidence = []

    except Exception as error:

        print(
            "Chat evidence retrieval warning:",
            repr(error)
        )

        retrieved_evidence = []


    # =====================================================
    # FORMAT EVIDENCE
    # =====================================================

    evidence_for_response = format_evidence(
        retrieved_evidence
    )


    # =====================================================
    # CREATE EVIDENCE SUMMARY
    # =====================================================

    evidence_titles = []

    for item in evidence_for_response:

        title = item.get(
            "title",
            ""
        )

        if title and title not in evidence_titles:
            evidence_titles.append(title)

    evidence_text = ""

    if evidence_titles:

        evidence_text = (
            "\n\nScientific evidence considered:\n"
            + "\n".join(
                f"• {title}"
                for title in evidence_titles[:5]
            )
        )


    # =====================================================
    # FOLLOW-UP: HABITAT DIVERSITY
    # =====================================================

    if (
        "habitat diversity" in question
        or "habitat-diversity" in question
        or "habitats" in question
        or "habitat" in question
        or "increase habitat" in question
        or "more habitat" in question
        or "diverse habitat" in question
    ):

        answer = (
            f"Habitat diversity is important in your ecosystem "
            f"because your current habitat-diversity value is "
            f"{habitat_diversity}, while species richness is "
            f"{species_richness}.\n\n"

            f"A low variety of habitats can limit the range of "
            f"food, shelter and breeding opportunities available "
            f"to different organisms. Increasing habitat variety "
            f"can create more ecological niches and provide "
            f"resources for a wider range of plants, insects, "
            f"birds and other organisms.\n\n"

            f"This is particularly relevant to your current "
            f"'{land_use}' system. Locally suitable native "
            f"vegetation, field margins, flowering strips, "
            f"hedgerows or other compatible habitat features "
            f"can increase structural diversity without requiring "
            f"a complete change in land use.\n\n"

            f"Your ecosystem has {rainfall} mm annual rainfall "
            f"and {moisture}% soil moisture. Therefore, habitat "
            f"improvements should use vegetation that is suitable "
            f"for the available water conditions.\n\n"

            f"To measure progress, track the number of habitat "
            f"types, species richness and vegetation establishment "
            f"over time. The goal is not simply to add vegetation, "
            f"but to increase the variety of suitable ecological "
            f"resources."
        )


    # =====================================================
    # FOLLOW-UP: LOW RAINFALL / WATER
    # =====================================================

    elif (
        "rainfall" in question
        or "rain" in question
        or "dry" in question
        or "water" in question
        or "drought" in question
    ):

        answer = (
            f"Based on your current environmental conditions "
            f"({rainfall} mm annual rainfall and {moisture}% "
            f"soil moisture), water availability is an important "
            f"constraint.\n\n"

            f"For this situation, prioritize practices that "
            f"retain soil moisture and improve soil cover. "
            f"Cover crops or retained crop residues can help "
            f"protect the soil surface, while diversified "
            f"vegetation should be selected according to local "
            f"water availability.\n\n"

            f"Your current land-use system is '{land_use}', "
            f"so diversification should be introduced in a "
            f"way that does not create excessive competition "
            f"for limited water."
        )


    # =====================================================
    # FOLLOW-UP: SOIL / CARBON / MOISTURE
    # =====================================================

    elif (
        "soil" in question
        or "carbon" in question
        or "organic matter" in question
        or "organic carbon" in question
        or "moisture" in question
    ):

        answer = (
            f"Your current soil indicators are: "
            f"pH {ph}, organic carbon {organic_carbon}% "
            f"and soil moisture {moisture}%.\n\n"

            f"The current organic-carbon value makes soil "
            f"organic-matter management particularly relevant. "
            f"Maintaining crop residues, suitable cover crops "
            f"and diversified plant inputs can support soil "
            f"carbon and moisture-related functions over time.\n\n"

            f"Because your soil moisture is currently {moisture}%, "
            f"soil-cover practices may also help protect the "
            f"soil surface and support moisture retention.\n\n"

            f"Measure soil organic carbon and soil moisture "
            f"periodically so changes can be compared against "
            f"your current baseline."
        )


    # =====================================================
    # FOLLOW-UP: SPECIES / BIODIVERSITY
    # =====================================================

    elif (
        "species" in question
        or "biodiversity" in question
        or "animals" in question
        or "birds" in question
        or "insects" in question
        or "pollinator" in question
        or "wildlife" in question
    ):

        answer = (
            f"Your current species-richness value is "
            f"{species_richness} and habitat-diversity value "
            f"is {habitat_diversity}.\n\n"

            f"To improve biodiversity, focus on increasing "
            f"habitat variety rather than relying on a single "
            f"intervention. Locally suitable native vegetation, "
            f"field margins, flowering strips and diversified "
            f"cropping can provide additional food and shelter "
            f"resources.\n\n"

            f"Your current '{land_use}' system can be diversified "
            f"gradually so additional habitats are introduced "
            f"without creating unnecessary pressure on available "
            f"water resources.\n\n"

            f"Track species richness and habitat types over "
            f"time so the effect of the intervention can be "
            f"measured."
        )


    # =====================================================
    # FOLLOW-UP: WHY / IMPORTANCE / BENEFITS
    # =====================================================

    elif (
        "why" in question
        or "important" in question
        or "importance" in question
        or "benefit" in question
        or "benefits" in question
        or "help" in question
    ):

        answer = (
            f"Your ecosystem should be considered as an "
            f"interacting environmental system rather than "
            f"as separate indicators.\n\n"

            f"Your current conditions include {rainfall} mm "
            f"annual rainfall, {organic_carbon}% soil organic "
            f"carbon, {moisture}% soil moisture, species "
            f"richness of {species_richness}, and habitat "
            f"diversity of {habitat_diversity}.\n\n"

            f"Changes in one part of the system can influence "
            f"other parts. For example, vegetation and habitat "
            f"structure can provide resources for species, "
            f"while vegetation cover can also contribute to "
            f"soil protection and moisture-related functions.\n\n"

            f"The useful approach is to select interventions "
            f"that address multiple environmental constraints "
            f"and then monitor the relevant indicators over time."
        )


    # =====================================================
    # FOLLOW-UP: WHICH RECOMMENDATION / PRIORITY
    # =====================================================

    elif (
        "which" in question
        or "best" in question
        or "start" in question
        or "first" in question
        or "priority" in question
        or "recommendation" in question
    ):

        answer = (
            "The starting point should depend on the main "
            "environmental constraint you want to address.\n\n"

            f"For your current conditions — {organic_carbon}% "
            f"soil organic carbon, {rainfall} mm rainfall, "
            f"{moisture}% soil moisture and '{land_use}' "
            f"land use — soil-cover and moisture-conservation "
            f"measures are a logical first intervention to "
            f"consider.\n\n"

            "After establishing soil cover, you can progressively "
            "increase habitat and crop diversity."
        )


    # =====================================================
    # FOLLOW-UP: HOW TO IMPROVE / ACTION
    # =====================================================

    elif (
        "how can i" in question
        or "how do i" in question
        or "how to" in question
        or "improve" in question
        or "increase" in question
        or "reduce" in question
        or "what should i do" in question
    ):

        answer = (
            f"Based on your current ecosystem profile, focus "
            f"on actions that address soil condition, water "
            f"availability and biodiversity together.\n\n"

            f"Your current values are {rainfall} mm rainfall, "
            f"{organic_carbon}% soil organic carbon, "
            f"{moisture}% soil moisture, species richness "
            f"{species_richness}, and habitat diversity "
            f"{habitat_diversity}.\n\n"

            f"Practical actions include maintaining soil cover, "
            f"retaining suitable crop residues, introducing "
            f"locally suitable vegetation, increasing habitat "
            f"variety and gradually diversifying the "
            f"'{land_use}' system.\n\n"

            f"After implementing an intervention, track the "
            f"same environmental indicators so that changes "
            f"can be compared with your current baseline."
        )


    # =====================================================
    # FOLLOW-UP: TIME / MONITORING
    # =====================================================

    elif (
        "how long" in question
        or "time" in question
        or "months" in question
        or "measure" in question
        or "monitor" in question
        or "6 month" in question
        or "6 months" in question
    ):

        answer = (
            "Use the current environmental measurements as "
            "your baseline.\n\n"

            "For soil moisture and visible vegetation changes, "
            "monitor more frequently during the growing season. "
            "For soil organic carbon and biodiversity indicators, "
            "use repeated measurements over a longer period "
            "because these indicators generally change more "
            "slowly.\n\n"

            "Useful indicators to track include soil organic "
            "carbon, soil moisture, species richness, habitat "
            "diversity and vegetation cover."
        )


    # =====================================================
    # FOLLOW-UP: POLLUTION
    # =====================================================

    elif (
        "pollution" in question
        or "contamination" in question
        or "pollutant" in question
        or "polluted" in question
    ):

        answer = (
            f"Your current pollution level is recorded as "
            f"'{pollution}'.\n\n"

            f"Even when the recorded pollution level is low, "
            f"continued monitoring is useful because pollutants "
            f"can affect soil organisms, plants, water quality "
            f"and biodiversity.\n\n"

            f"Track relevant local pollution indicators and "
            f"compare them with changes in species richness, "
            f"vegetation and soil conditions over time."
        )


    # =====================================================
    # FOLLOW-UP: DEFORESTATION / LAND DEGRADATION
    # =====================================================

    elif (
        "deforestation" in question
        or "forest" in question
        or "land degradation" in question
        or "degradation" in question
        or "tree" in question
        or "trees" in question
    ):

        answer = (
            f"Your current deforestation level is recorded as "
            f"'{deforestation}'.\n\n"

            f"Changes in vegetation cover can influence habitat "
            f"availability, soil protection, water regulation "
            f"and species diversity.\n\n"

            f"For your '{land_use}' system, maintaining or "
            f"restoring native vegetation in suitable areas "
            f"can help increase habitat structure while reducing "
            f"pressure on the surrounding ecosystem."
        )


    # =====================================================
    # GENERAL FOLLOW-UP
    # =====================================================

    else:

        answer = (
            f"I can continue the environmental assessment using "
            f"your current ecosystem context: {region}, "
            f"{rainfall} mm rainfall, '{land_use}' land use, "
            f"{organic_carbon}% soil organic carbon, "
            f"{moisture}% soil moisture, species richness "
            f"{species_richness}, and habitat diversity "
            f"{habitat_diversity}.\n\n"

            f"Your question is: \"{user_message}\"\n\n"

            f"I can explain it in relation to this ecosystem. "
            f"You can ask about habitat diversity, soil carbon, "
            f"rainfall, moisture, biodiversity, pollution, "
            f"deforestation, recommendations or monitoring."
        )


    # =====================================================
    # ADD SCIENTIFIC EVIDENCE TO ANSWER
    # =====================================================

    if evidence_titles:

        answer += evidence_text


    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "status": "ok",

        "answer": answer,

        "context": {
            "region": region,
            "rainfall_mm": rainfall,
            "land_use": land_use,
            "ph": ph,
            "organic_carbon_pct": organic_carbon,
            "moisture_pct": moisture,
            "species_richness": species_richness,
            "habitat_diversity": habitat_diversity,
            "pollution": pollution,
            "deforestation": deforestation
        },

        "retrieved_evidence": evidence_for_response,

        "conversation": True,
    }