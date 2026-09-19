import { useState } from "react";

import {
  Leaf,
  Droplets,
  Sprout,
  TreePine,
  CloudRain,
  FlaskConical,
  Search,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  BookOpen,
  MessageCircle,
  Send,
} from "lucide-react";

import "./App.css";


function App() {

  // =========================================================
  // ENVIRONMENTAL INPUTS
  // =========================================================

  const [form, setForm] = useState({

    region: "semi-arid",

    rainfall_mm: 500,

    land_use: "monoculture wheat",

    ph: 6.5,

    organic_carbon_pct: 0.3,

    moisture_pct: 15,

    species_richness: 5,

    habitat_diversity: 1,

    pollution: "low",

    deforestation: "moderate",

  });


  // =========================================================
  // ANALYSIS STATE
  // =========================================================

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  // =========================================================
  // FOLLOW-UP CHAT STATE
  // =========================================================

  const [chatMessage, setChatMessage] =
    useState("");

  const [chatMessages, setChatMessages] =
    useState([]);

  const [chatLoading, setChatLoading] =
    useState(false);

  const [chatError, setChatError] =
    useState("");


  // =========================================================
  // UPDATE INPUT
  // =========================================================

  const updateField = (
    field,
    value
  ) => {

    setForm((previous) => ({

      ...previous,

      [field]: value,

    }));

  };


  // =========================================================
  // ANALYZE ENVIRONMENT
  // =========================================================

  const analyzeEnvironment =
    async () => {

      setLoading(true);

      setError("");

      setResult(null);

      // Clear previous conversation
      setChatMessages([]);

      setChatError("");


      // =====================================================
      // REQUEST PAYLOAD
      // =====================================================

      const payload = {

        text:
          "Biodiversity is declining on my farmland. " +
          "Please analyze the environmental conditions " +
          "and provide exactly three evidence-grounded " +
          "recommendations.",


        region:
          String(form.region),


        rainfall_mm:
          Number(form.rainfall_mm),


        land_use:
          String(form.land_use),


        soil: {

          ph:
            Number(form.ph),

          organic_carbon_pct:
            Number(
              form.organic_carbon_pct
            ),

          moisture_pct:
            Number(
              form.moisture_pct
            ),

        },


        biodiversity: {

          species_richness:
            String(
              form.species_richness
            ),

          habitat_diversity:
            String(
              form.habitat_diversity
            ),

        },


        human_impact: {

          pollution:
            String(form.pollution),

          deforestation:
            String(
              form.deforestation
            ),

        },

      };


      console.log(
        "Environmental request:",
        payload
      );


      // =====================================================
      // CALL FASTAPI
      // =====================================================

      try {

        const response =
          await fetch(
            "https://ecosense-ai-backend-7o1i.onrender.com/api/analyze",
            {

              method: "POST",

              headers: {

                "Content-Type":
                  "application/json",

                Accept:
                  "application/json",

              },

              body:
                JSON.stringify(
                  payload
                ),

            }
          );


        const responseText =
          await response.text();


        console.log(
          "FastAPI status:",
          response.status
        );


        console.log(
          "FastAPI response:",
          responseText
        );


        // =================================================
        // BACKEND ERROR
        // =================================================

        if (!response.ok) {

          throw new Error(
            `Backend returned HTTP ${response.status}: ${responseText}`
          );

        }


        // =================================================
        // PARSE RESPONSE
        // =================================================

        const data =
          JSON.parse(
            responseText
          );


        console.log(
          "Analysis result:",
          data
        );


        setResult(data);

        setError("");


      } catch (err) {

        console.error(
          "Environmental analysis error:",
          err
        );


        setError(
          err.message ||
          "Unable to connect to the FastAPI backend."
        );


      } finally {

        setLoading(false);

      }

    };


  // =========================================================
  // ASK FOLLOW-UP QUESTION
  // =========================================================

  const askFollowUp =
    async () => {

      // Don't send empty question
      if (
        !chatMessage.trim()
      ) {

        return;

      }


      const currentMessage =
        chatMessage.trim();


      // =====================================================
      // ADD USER MESSAGE
      // =====================================================

      setChatMessages(
        (previous) => [

          ...previous,

          {

            role: "user",

            content:
              currentMessage,

          },

        ]
      );


      setChatMessage("");

      setChatLoading(true);

      setChatError("");


      // =====================================================
      // SEND PREVIOUS ENVIRONMENTAL CONTEXT
      // =====================================================

      const payload = {

        message:
          currentMessage,


        // Previous environmental data

        region:
          form.region,


        rainfall_mm:
          Number(
            form.rainfall_mm
          ),


        land_use:
          form.land_use,


        ph:
          Number(
            form.ph
          ),


        organic_carbon_pct:
          Number(
            form.organic_carbon_pct
          ),


        moisture_pct:
          Number(
            form.moisture_pct
          ),


        species_richness:
          Number(
            form.species_richness
          ),


        habitat_diversity:
          Number(
            form.habitat_diversity
          ),


        pollution:
          form.pollution,


        deforestation:
          form.deforestation,


        // Previous recommendations

        recommendations:
          result?.recommendations ||
          [],

      };


      console.log(
        "Follow-up request:",
        payload
      );


      try {

        const response =
          await fetch(
            "https://ecosense-ai-backend-7o1i.onrender.com/api/chat",
            {

              method: "POST",

              headers: {

                "Content-Type":
                  "application/json",

                Accept:
                  "application/json",

              },

              body:
                JSON.stringify(
                  payload
                ),

            }
          );


        const responseText =
          await response.text();


        console.log(
          "Follow-up status:",
          response.status
        );


        console.log(
          "Follow-up response:",
          responseText
        );


        if (!response.ok) {

          throw new Error(
            `Backend returned HTTP ${response.status}: ${responseText}`
          );

        }


        const data =
          JSON.parse(
            responseText
          );


        // =================================================
        // ADD AI RESPONSE + RAG EVIDENCE
        // =================================================

        setChatMessages(
          (previous) => [

            ...previous,

            {

              role: "ai",

              content:
                data.answer ||
                "I could not generate a follow-up answer.",

              evidence:
                Array.isArray(
                  data.retrieved_evidence
                )
                  ? data.retrieved_evidence
                  : [],

            },

          ]
        );


      } catch (err) {

        console.error(
          "Follow-up error:",
          err
        );


        setChatError(
          err.message ||
          "Unable to connect to the AI."
        );


      } finally {

        setChatLoading(false);

      }

    };


  // =========================================================
  // HANDLE ENTER KEY
  // =========================================================

  const handleChatKeyDown =
    (event) => {

      if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !chatLoading
      ) {

        event.preventDefault();

        askFollowUp();

      }

    };


  // =========================================================
  // RESET FORM
  // =========================================================

  const resetForm = () => {

    setForm({

      region: "semi-arid",

      rainfall_mm: 500,

      land_use: "monoculture wheat",

      ph: 6.5,

      organic_carbon_pct: 0.3,

      moisture_pct: 15,

      species_richness: 5,

      habitat_diversity: 1,

      pollution: "low",

      deforestation: "moderate",

    });

    setResult(null);

    setError("");

    setChatMessages([]);

    setChatError("");

  };


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="app">

      <header className="site-header">

        <div className="brand">

          <div className="logo">
            <Leaf
              size={25}
              strokeWidth={2.2}
            />
          </div>

          <div>

            <h1>EcoSense AI</h1>

            <p>
              Environmental intelligence &amp;
              biodiversity reasoning
            </p>

          </div>

        </div>


        <div className="status">
          <span></span>
          Analysis engine online
        </div>

      </header>


      <main>

        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero-section">

          <div className="hero-copy">

            <div className="eyebrow">
              AI ENVIRONMENTAL SCIENTIST
            </div>

            <h2>
              Understand the relationships behind your{" "}
              <em>ecosystem.</em>
            </h2>

            <div className="accent-line"></div>

            <p>
              Combine soil, climate, land-use and
              biodiversity indicators to produce an
              evidence-grounded environmental diagnosis.
            </p>

          </div>


          <div className="relationship-wrap">

            <div className="relationship-orbit orbit-one"></div>

            <div className="relationship-orbit orbit-two"></div>

            <div className="relation-center">
              <Leaf size={36} />
            </div>

            <span className="relation-label soil">
              SOIL
            </span>

            <span className="relation-label land">
              LAND USE
            </span>

            <span className="relation-label climate">
              CLIMATE
            </span>

            <span className="relation-label habitat">
              HABITAT
            </span>

            <div className="hero-note">
              Data Insights
              <br />
              <strong>Action</strong> for a healthier planet.
            </div>

          </div>

        </section>


        {/* =================================================
            WORKSPACE
        ================================================= */}

        <section className="workspace">

          <div className="profile-card">

            <div className="card-heading">

              <div>

                <span className="section-number">
                  01 · SITE PROFILE
                </span>

                <h3>
                  Environmental inputs
                </h3>

              </div>

              <button
                className="reset-button"
                onClick={resetForm}
                type="button"
              >
                Reset
              </button>

            </div>


            <div className="context-row">

              <label className="context-field">

                <span>Region</span>

                <input
                  type="text"
                  value={form.region}
                  onChange={(e) =>
                    updateField(
                      "region",
                      e.target.value
                    )
                  }
                />

              </label>


              <label className="context-field">

                <span>Land use</span>

                <input
                  type="text"
                  value={form.land_use}
                  onChange={(e) =>
                    updateField(
                      "land_use",
                      e.target.value
                    )
                  }
                />

              </label>

            </div>


            <div className="input-grid">

              <div className="input-card">

                <div className="icon-box">
                  <Droplets size={18} />
                </div>

                <div>

                  <label>
                    Annual rainfall
                  </label>

                  <div className="value-input">

                    <input
                      type="number"
                      value={form.rainfall_mm}
                      onChange={(e) =>
                        updateField(
                          "rainfall_mm",
                          e.target.value
                        )
                      }
                    />

                    <span>mm</span>

                  </div>

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <FlaskConical size={18} />
                </div>

                <div>

                  <label>
                    Soil pH
                  </label>

                  <input
                    type="number"
                    step="0.1"
                    value={form.ph}
                    onChange={(e) =>
                      updateField(
                        "ph",
                        e.target.value
                      )
                    }
                  />

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <Leaf size={18} />
                </div>

                <div>

                  <label>
                    Organic carbon
                  </label>

                  <div className="value-input">

                    <input
                      type="number"
                      step="0.1"
                      value={
                        form.organic_carbon_pct
                      }
                      onChange={(e) =>
                        updateField(
                          "organic_carbon_pct",
                          e.target.value
                        )
                      }
                    />

                    <span>%</span>

                  </div>

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <Droplets size={18} />
                </div>

                <div>

                  <label>
                    Soil moisture
                  </label>

                  <div className="value-input">

                    <input
                      type="number"
                      value={
                        form.moisture_pct
                      }
                      onChange={(e) =>
                        updateField(
                          "moisture_pct",
                          e.target.value
                        )
                      }
                    />

                    <span>%</span>

                  </div>

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <TreePine size={18} />
                </div>

                <div>

                  <label>
                    Species richness
                  </label>

                  <input
                    type="number"
                    value={
                      form.species_richness
                    }
                    onChange={(e) =>
                      updateField(
                        "species_richness",
                        e.target.value
                      )
                    }
                  />

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <TreePine size={18} />
                </div>

                <div>

                  <label>
                    Habitat diversity
                  </label>

                  <input
                    type="number"
                    value={
                      form.habitat_diversity
                    }
                    onChange={(e) =>
                      updateField(
                        "habitat_diversity",
                        e.target.value
                      )
                    }
                  />

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <FlaskConical size={18} />
                </div>

                <div>

                  <label>
                    Pollution
                  </label>

                  <select
                    value={form.pollution}
                    onChange={(e) =>
                      updateField(
                        "pollution",
                        e.target.value
                      )
                    }
                  >

                    <option value="low">
                      Low
                    </option>

                    <option value="moderate">
                      Moderate
                    </option>

                    <option value="high">
                      High
                    </option>

                  </select>

                </div>

              </div>


              <div className="input-card">

                <div className="icon-box">
                  <TreePine size={18} />
                </div>

                <div>

                  <label>
                    Deforestation
                  </label>

                  <select
                    value={form.deforestation}
                    onChange={(e) =>
                      updateField(
                        "deforestation",
                        e.target.value
                      )
                    }
                  >

                    <option value="low">
                      Low
                    </option>

                    <option value="moderate">
                      Moderate
                    </option>

                    <option value="high">
                      High
                    </option>

                  </select>

                </div>

              </div>

            </div>


            <button
              className="analyze-button"
              onClick={analyzeEnvironment}
              disabled={loading}
              type="button"
            >

              <Search size={18} />

              {loading
                ? "Analysing environmental system..."
                : "Analyse environmental system"
              }

            </button>


            {error && (

              <div className="error-box">

                <AlertTriangle size={20} />

                <div>

                  <strong>
                    Analysis Error
                  </strong>

                  <div>
                    {error}
                  </div>

                </div>

              </div>

            )}

          </div>


          {/* =================================================
              LIVE PROFILE
          ================================================= */}

          <aside className="live-card">

            <div className="live-top">

              <div>

                <span className="section-number">
                  LIVE PROFILE
                </span>

                <h3>
                  What the engine sees
                </h3>

              </div>

              <span className="live-dot"></span>

            </div>


            <div className="profile-list">

              <div>
                <span>
                  Water availability
                </span>

                <strong>
                  {form.rainfall_mm} mm
                </strong>
              </div>

              <div>
                <span>
                  Soil carbon
                </span>

                <strong>
                  {form.organic_carbon_pct}%
                </strong>
              </div>

              <div>
                <span>
                  Soil moisture
                </span>

                <strong>
                  {form.moisture_pct}%
                </strong>
              </div>

              <div>
                <span>
                  Species richness
                </span>

                <strong>
                  {form.species_richness}
                </strong>
              </div>

              <div>
                <span>
                  Habitat diversity
                </span>

                <strong>
                  {form.habitat_diversity}
                </strong>
              </div>

              <div>
                <span>
                  Pollution level
                </span>

                <strong>
                  {form.pollution}
                </strong>
              </div>

              <div>
                <span>
                  Deforestation
                </span>

                <strong>
                  {form.deforestation}
                </strong>
              </div>

            </div>


            <div className="reasoning-note">

              <Leaf size={18} />

              <p>
                These variables are reasoned together.
                The engine does not treat them as
                independent scores.
              </p>

            </div>


            <div className="landscape-card">

              <div className="landscape-art">

                <span></span>
                <span></span>
                <span></span>
                <span></span>

              </div>

              <strong>
                HEALTHY ECOSYSTEMS
              </strong>

              <small>
                BRIGHTER TOMORROWS
              </small>

            </div>

          </aside>

        </section>


        {/* =================================================
            RESULTS
        ================================================= */}

        {result && (

          <section className="results">

            <div className="section-title">

              <CheckCircle2 />

              <div>

                <span className="section-number">
                  02 · SYSTEM ANALYSIS
                </span>

                <h2>
                  AI Environmental Diagnosis
                </h2>

                <p>
                  Multi-metric environmental reasoning
                </p>

              </div>

            </div>


            {/* =================================================
                DIAGNOSIS
            ================================================= */}

            <div className="diagnosis-card">

              <h3>
                Environmental Diagnosis
              </h3>

              <p className="preline">
                {result.diagnosis ||
                  "Environmental conditions have been analyzed using multiple environmental indicators."
                }
              </p>

            </div>


            {/* =================================================
                RECOMMENDATIONS
            ================================================= */}

            <h2 className="result-heading">
              🌱 Recommended Actions
            </h2>

            <div className="recommendations">

              {result.recommendations &&
              result.recommendations.length > 0
                ? result.recommendations.map(
                    (rec, index) => (

                      <article
                        className="recommendation-card"
                        key={index}
                      >

                        <div className="recommendation-index">
                          0{index + 1}
                        </div>

                        <h3>
                          {rec.action ||
                            rec.recommendation ||
                            `Recommendation ${index + 1}`
                          }
                        </h3>

                        {rec.reason && (
                          <p>
                            {rec.reason}
                          </p>
                        )}

                        {rec.scientific_reasoning && (
                          <p>
                            {rec.scientific_reasoning}
                          </p>
                        )}

                        {rec.why_it_works && (
                          <p>
                            <strong>
                              Why it works:
                            </strong>{" "}
                            {rec.why_it_works}
                          </p>
                        )}

                        {rec.impacted_metrics && (

                          <div className="metric-tags">

                            {(
                              Array.isArray(
                                rec.impacted_metrics
                              )
                                ? rec.impacted_metrics
                                : [
                                    rec.impacted_metrics
                                  ]
                            ).map(
                              (m, i) => (
                                <span key={i}>
                                  {m}
                                </span>
                              )
                            )}

                          </div>

                        )}

                        {rec.time_horizon && (

                          <div className="rec-meta">

                            <Clock3 size={15} />

                            {rec.time_horizon}

                          </div>

                        )}

                        {rec.confidence !== undefined && (

                          <div className="rec-meta">

                            Confidence:{" "}
                            {rec.confidence}

                          </div>

                        )}

                        {rec.reference && (

                          <div className="reference-line">

                            <BookOpen size={15} />

                            {rec.reference}

                          </div>

                        )}

                      </article>

                    )
                  )
                : (

                  <div className="diagnosis-card">

                    <p>
                      No recommendations were returned.
                    </p>

                  </div>

                )}

            </div>


            {/* =================================================
                CHAT
            ================================================= */}

            <section className="follow-up-chat">

              <div className="chat-heading">

                <div>

                  <span className="section-number">
                    03 · CONVERSATION
                  </span>

                  <h2>
                    Ask EcoSense AI
                  </h2>

                  <p>
                    Explore the diagnosis with a
                    contextual follow-up question.
                  </p>

                </div>

                <MessageCircle />

              </div>


              {chatMessages.length > 0 && (

                <div className="chat-messages">

                  {chatMessages.map(
                    (message, index) => (

                      <div
                        className={`chat-message ${message.role}`}
                        key={index}
                      >

                        <span>
                          {message.role === "user"
                            ? "You"
                            : "EcoSense AI"
                          }
                        </span>


                        <p className="chat-answer">
                          {message.content}
                        </p>


                        {/* =================================================
                            CHAT RAG EVIDENCE
                        ================================================= */}

                        {message.role === "ai" &&
                          message.evidence &&
                          message.evidence.length > 0 && (

                            <div className="chat-evidence">

                              <div className="chat-evidence-heading">

                                <BookOpen size={15} />

                                <strong>
                                  Scientific evidence
                                </strong>

                              </div>


                              <div className="chat-evidence-list">

                                {message.evidence
                                  .slice(0, 5)
                                  .map(
                                    (
                                      evidence,
                                      evidenceIndex
                                    ) => (

                                      <div
                                        className="chat-evidence-item"
                                        key={
                                          evidenceIndex
                                        }
                                      >

                                        <strong>
                                          {evidence.title ||
                                            evidence.name ||
                                            evidence.source ||
                                            `Evidence ${evidenceIndex + 1}`
                                          }
                                        </strong>


                                        {evidence.content && (

                                          <p>
                                            {evidence.content}
                                          </p>

                                        )}

                                        {evidence.text && !evidence.content && (

                                          <p>
                                            {evidence.text}
                                          </p>

                                        )}

                                        {evidence.source &&
                                          evidence.source !== evidence.title && (

                                            <small>
                                              {evidence.source}
                                            </small>

                                        )}

                                      </div>

                                    )
                                  )}

                              </div>

                            </div>

                          )}

                      </div>

                    )
                  )}

                </div>

              )}


              {chatLoading && (

                <div className="chat-message ai">

                  <span>
                    EcoSense AI
                  </span>

                  <p className="chat-answer">
                    Retrieving scientific evidence and
                    reasoning about your ecosystem...
                  </p>

                </div>

              )}


              {chatError && (

                <div className="error-box">

                  <AlertTriangle size={18} />

                  <div>
                    {chatError}
                  </div>

                </div>

              )}


              <div className="chat-input-row">

                <textarea
                  value={chatMessage}
                  onChange={(e) =>
                    setChatMessage(
                      e.target.value
                    )
                  }
                  onKeyDown={
                    handleChatKeyDown
                  }
                  placeholder="Ask about the relationships, recommendations, or next steps..."
                  rows={2}
                />


                <button
                  onClick={askFollowUp}
                  disabled={
                    chatLoading ||
                    !chatMessage.trim()
                  }
                  type="button"
                >

                  <Send size={17} />

                  {chatLoading
                    ? "Thinking..."
                    : "Ask"
                  }

                </button>

              </div>

            </section>


            {/* =================================================
                MAIN ANALYSIS EVIDENCE
            ================================================= */}

            <section className="evidence">

              <div className="section-title">

                <BookOpen />

                <div>

                  <span className="section-number">
                    04 · SCIENTIFIC GROUNDING
                  </span>

                  <h2>
                    Retrieved evidence
                  </h2>

                  <p>
                    Sources used to ground the
                    environmental reasoning.
                  </p>

                </div>

              </div>


              <div className="evidence-content">

                {result.retrieved_evidence &&
                result.retrieved_evidence.length > 0
                  ? result.retrieved_evidence.map(
                      (item, index) => (

                        <div
                          className="evidence-item"
                          key={index}
                        >

                          <strong>
                            {item.title ||
                              item.source ||
                              `Evidence ${index + 1}`
                            }
                          </strong>

                          <p>
                            {item.text ||
                              item.content ||
                              item.description ||
                              "Scientific evidence retrieved for this analysis."
                            }
                          </p>

                        </div>

                      )
                    )
                  : (

                    <div className="evidence-item">

                      Scientific evidence was not
                      returned for this analysis.

                    </div>

                  )}

              </div>

            </section>


            {/* =================================================
                SUMMARY
            ================================================= */}

            {result.conversation_summary && (

              <div className="diagnosis-card summary-card">

                <h3>
                  Analysis Summary
                </h3>

                <p className="preline">
                  {result.conversation_summary}
                </p>

              </div>

            )}

          </section>

        )}

      </main>


      {/* =================================================
          FOOTER
      ================================================= */}

      <footer>

        <Leaf size={17} />

        <span>
          EcoSense AI · Evidence-grounded
          environmental reasoning
        </span>

      </footer>

    </div>

  );

}


export default App;