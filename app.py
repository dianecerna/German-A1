import os
import json
import io
import random
import time
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS

# Streamlit Page Configuration
st.set_page_config(
    page_title="German A1 Learning", 
    page_icon="🌻", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Glow Theme with Yellow, Pink, and Orange Neon Glow Accents
st.markdown("""
<style>
    /* Global Dark Background with Subtle Glow Wallpaper */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.94), rgba(15, 23, 42, 0.94)), 
                    url("https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=2000&q=80") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    *, div, span, p, h1, h2, h3, h4, h5, h6, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Hide Sidebar Completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Relaxed Comfort Spacing & Eliminating Extra White Boxes */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
        background: transparent !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.8rem !important;
    }

    /* Dark Neon Glow Custom Button Styling with Yellow, Pink, and Orange Accents */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, rgba(254, 240, 138, 0.15) 0%, rgba(244, 114, 182, 0.2) 50%, rgba(251, 146, 60, 0.15) 100%) !important;
        border: 1px solid #f472b6 !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #fef08a !important;
        box-shadow: 0 0 15px rgba(244, 114, 182, 0.25) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 6px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fef08a 0%, #f472b6 50%, #fb923c 100%) !important;
        border-color: #fde047 !important;
        transform: translateY(-1px);
        box-shadow: 0 0 25px rgba(244, 114, 182, 0.5), 0 0 10px rgba(251, 146, 60, 0.4) !important;
        color: #0f172a !important;
    }

    /* Dark Glow Section Header Boxes */
    .section-header-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%) !important;
        backdrop-filter: blur(8px);
        border-left: 6px solid #f472b6;
        border-top: 1px solid rgba(244, 114, 182, 0.4);
        border-right: 1px solid rgba(251, 146, 60, 0.4);
        border-bottom: 1px solid rgba(254, 240, 138, 0.4);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 14px;
        color: #fef08a !important;
        font-size: 1.25rem;
        font-weight: 800;
        box-shadow: 0 0 20px rgba(244, 114, 182, 0.2);
    }

    /* Main Content Container Cards with Dark Glow */
    .main-card {
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(8px);
        border-radius: 14px;
        padding: 22px 26px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 14px;
        border: 1px solid rgba(244, 114, 182, 0.3);
        color: #f8fafc;
    }

    /* Hero Banner with Dark Neon Glow Border */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(8px);
        border-radius: 14px;
        padding: 26px;
        color: #f8fafc;
        margin-bottom: 16px;
        border: 2px solid #f472b6;
        box-shadow: 0 0 30px rgba(244, 114, 182, 0.25);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(244, 114, 182, 0.15);
        border: 1px solid #f472b6;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        color: #f472b6;
        box-shadow: 0 0 10px rgba(244, 114, 182, 0.2);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 4px;
        background: linear-gradient(90deg, #fef08a 0%, #f472b6 50%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.4;
        margin-bottom: 0px;
        font-weight: 500;
    }

    /* Clean Minimalist Dropdown Box Design for Dark Theme */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 10px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 2px solid #f472b6 !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        padding: 8px 14px !important;
        box-shadow: 0 0 15px rgba(244, 114, 182, 0.2) !important;
        min-height: 44px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #fb923c !important;
    }
    .stSelectbox span, .stSelectbox div[data-baseweb="select"] span {
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Open Dropdown Popup List Container & Options */
    div[data-baseweb="menu"] {
        background-color: #1e293b !important;
        border: 1px solid #f472b6 !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-baseweb="menu"] ul {
        background-color: #1e293b !important;
    }
    div[data-baseweb="menu"] li, div[data-baseweb="menu"] div {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
    }
    div[data-baseweb="menu"] li span, div[data-baseweb="menu"] div span {
        color: #f8fafc !important;
    }
    div[data-baseweb="menu"] li:hover, div[data-baseweb="menu"] div[aria-selected="true"] {
        background-color: rgba(244, 114, 182, 0.2) !important;
        color: #fef08a !important;
    }

    /* DYNAMIC FLASHCARD SECTION */
    .card-masculine-container {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        border: 2px solid #2563eb;
        color: #ffffff;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.4);
        margin-bottom: 12px;
    }
    .card-masculine-container * { color: #ffffff !important; }

    .card-feminine-container {
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
        border: 2px solid #dc2626;
        color: #ffffff;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.4);
        margin-bottom: 12px;
    }
    .card-feminine-container * { color: #ffffff !important; }

    .card-neuter-container {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        border: 2px solid #059669;
        color: #ffffff;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.4);
        margin-bottom: 12px;
    }
    .card-neuter-container * { color: #ffffff !important; }

    .card-verb-container {
        background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
        border: 2px solid #ea580c;
        color: #ffffff;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(249, 115, 22, 0.4);
        margin-bottom: 12px;
    }
    .card-verb-container * { color: #ffffff !important; }

    .card-other-container {
        background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%);
        border: 2px solid #9333ea;
        color: #ffffff;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.4);
        margin-bottom: 12px;
    }
    .card-other-container * { color: #ffffff !important; }

    .flashcard-word-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 4px;
        color: #ffffff !important;
    }

    /* Clean Dark Card Section Wrapper for Back Details */
    .detail-section-card {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(244, 114, 182, 0.4);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #f8fafc;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 **Missing Gemini API Key!** Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]

SYSTEM_INSTRUCTION = """
You are Gem, an expert German tutor and official Goethe-Institut examiner evaluating candidates for the Goethe-Zertifikat A1 exam.
Follow standard CEFR A1 learning objectives and exhaustive Goethe-Zertifikat A1 vocabulary standards (top 1000 essential words across nouns, verbs, prepositions, adjectives, pronouns).
Provide accurate grammatical breakdowns, exact plurals, case usages, conjugations, komparativ/superlative, and always provide sentences for each pronoun even for nouns or other parts of speech. Never leave fields as blank or N/A in conjugations. Clean and concise formatting.
"""

@st.cache_data(show_spinner=False)
def generate_cached_content(prompt_text: str, is_json: bool = False) -> str:
    config_args = {"system_instruction": SYSTEM_INSTRUCTION}
    if is_json:
        config_args["response_mime_type"] = "application/json"
    
    last_error = None
    for attempt in range(2):
        for model_name in FALLBACK_MODELS:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=types.GenerateContentConfig(**config_args)
                )
                return res.text
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota", "not_found"]):
                    time.sleep(1)
                    continue
                raise e
        time.sleep(1.5)
    raise Exception(f"All model quotas are currently exhausted or experiencing high demand. Details: {str(last_error)}")

@st.cache_data(show_spinner=False)
def generate_german_audio_bytes(text: str) -> bytes:
    tts = gTTS(text=text, lang='de')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.getvalue()

def play_direct_audio(text_to_speak, unique_key):
    audio_bytes = generate_german_audio_bytes(text_to_speak)
    b64_audio = io.BytesIO(audio_bytes).read()
    st.audio(b64_audio, format="audio/mp3", autoplay=True)

# Expanded Exhaustive A1 Vocabulary Database across Nouns, Verbs, Prepositions, Adjectives, Pronouns (Top Essential Words)
A1_VOCABULARY_DATABASE = {
    "ALL": [],
    "allgemein": ["sein", "haben", "werden", "gut", "ja", "nein", "nicht", "sehr", "und", "oder", "aber", "also", "hier", "da", "was", "wer", "wie", "wo", "woher", "wohin", "machen", "gehen", "kommen", "sehen", "geben", "nehmen", "stehen", "liegen", "finden", "bleiben", "sprechen", "sprechen", "fragen", "antworten", "kennen", "wissen", "denken", "glauben", "sollen", "wollen", "können", "müssen", "dürfen", "möchten", "mögen"],
    "arbeiten_und_beruf": ["arbeiten", "der Beruf", "die Firma", "das Büro", "der Kollege", "die Kollegin", "der Chef", "die Chefin", "die Arbeit", "der Job", "der Termin", "die Pause", "verdienen", "schreiben", "anrufen", "der Computer", "das Telefon", "die E-Mail", "der Brief", "die Besprechung", "der Vertrag", "die Bewerbung", "der Kollege", "die Arbeitszeit", "die Abteilung", "der Kunde", "das Gehalt", "kündigen", "planen", "organisieren"],
    "mensch_und_koerper": ["die Familie", "der Vater", "die Mutter", "der Sohn", "die Tochter", "der Bruder", "die Schwester", "die Eltern", "das Kind", "der Mensch", "der Freund", "die Freundin", "die Person", "der Name", "das Alter", "der Kopf", "das Auge", "das Ohr", "die Hand", "der Fuß", "der Rücken", "der Bauch", "das Haar", "die Nase", "der Mund", "der Zahn", "das Bein", "das Herz", "gesund", "krank"],
    "wohnen_und_haushalt": ["das Haus", "die Wohnung", "das Zimmer", "die Küche", "das Bad", "das Schlafzimmer", "das Wohnzimmer", "die Tür", "das Fenster", "der Tisch", "der Stuhl", "das Bett", "die Lampe", "wohnen", "mieten", "der Schlüssel", "der Garten", "das Balkon", "die Miete", "umziehen", "die Heizung", "die Treppe", "das Dach", "der Flur", "die Wand", "der Boden", "putzen", "aufräumen", "einrichten", "die Garage"],
    "essen_und_trinken": ["das Essen", "das Wasser", "der Kaffee", "der Tee", "die Milch", "das Brot", "das Fleisch", "der Fisch", "das Obst", "das Gemüse", "essen", "trinken", "kochen", "backen", "das Restaurant", "der Hunger", "der Durst", "das Frühstück", "das Mittagessen", "das Abendessen", "der Zucker", "das Salz", "das Ei", "der Käse", "die Butter", "der Apfel", "die Banane", "die Kartoffel", "die Tomate", "schmecken"],
    "freizeit_und_hobbys": ["das Hobby", "spielen", "lesen", "schwimmen", "reisen", "fotografieren", "der Sport", "das Buch", "die Musik", "tanzen", "singen", "malen", "der Film", "das Kino", "das Theater", "wandern", "joggen", "treffen", "lachen", "fernsehen", "das Konzert", "das Museum", "das Lied", "das Spiel", "entspannen", "interessieren", "feiern", "grillen", "paddeln", "fotografieren"],
    "einkaufen_und_geld": ["einkaufen", "das Geld", "der Euro", "der Cent", "kosten", "teuer", "billig", "der Laden", "das Geschäft", "der Markt", "der Supermarkt", "kaufen", "verkaufen", "bezahlen", "die Karte", "bar", "der Preis", "das Angebot", "die Kasse", "der Kunde", "die Rechnung", "das Kleingeld", "tauschen", "sparen", "umtauschen", "der Rabatt", "die Bank", "die Kreditkarte", "die Tüte", "öffnen"],
    "verkehr_und_reisen": ["fahren", "fliegen", "reisen", "der Urlaub", "das Ticket", "der Bahnhof", "der Zug", "das Auto", "das Flugzeug", "der Bus", "die Straßenbahn", "das Fahrrad", "die Haltestelle", "der Flughafen", "das Hotel", "ankommen", "abfahren", "die Reise", "der Fahrplan", "die Verspätung", "das Gepäck", "der Pass", "die Karte", "einsteigen", "aussteigen", "umsteigen", "mieten", "die Tour", "die Fahrt", "der Hafen"],
    "gesundheit_und_ernaehrung": ["der Arzt", "die Ärztin", "das Krankenhaus", "die Apotheke", "krank", "gesund", "der Schmerz", "die Medizin", "die Gesundheit", "helfen", "ruhig", "müde", "schlecht", "die Tablette", "der Notfall", "untersuchen", "das Rezept", "fühlen", "leben", "sterben", "die Praxis", "der Unfall", "verletzt", "atmen", "schlafen", "die Diät", "vitamin", "allergisch", "das Fieber", "der Husten"],
    "medien_und_kommunikation": ["sprechen", "sagen", "hören", "telefonieren", "das Handy", "das Internet", "die Zeitung", "das Fernsehen", "das Radio", "die Nachricht", "fragen", "antworten", "verstehen", "erklären", "zeigen", "bestellen", "kommunizieren", "schreiben", "lesen", "das Buch", "der Brief", "die Sprache", "rufen", "melden", "antworten", "diskutieren", "erzählen", "der Computer", "die Website", "online"],
    "zeit_und_wetter": ["die Zeit", "die Stunde", "die Minute", "der Tag", "die Woche", "der Monat", "das Jahr", "heute", "gestern", "morgen", "jetzt", "immer", "nie", "das Wetter", "die Sonne", "der Regen", "der Schnee", "kalt", "warm", "schön", "der Wind", "die Wolke", "heiß", "kühl", "der Frühling", "der Sommer", "der Herbst", "der Winter", "früh", "spät"],
    "praepositionen_und_grammatik": ["in", "an", "auf", "unter", "über", "vor", "hinter", "neben", "zwischen", "mit", "ohne", "für", "gegen", "durch", "um", "aus", "bei", "nach", "seit", "von", "zu", "und", "oder", "aber", "denn", "weil", "dass", "wenn", "als", "ob"]
}

# Populate ALL category dynamically with unique sorted words
all_words_set = set()
for cat, w_list in A1_VOCABULARY_DATABASE.items():
    if cat != "ALL":
        all_words_set.update(w_list)
A1_VOCABULARY_DATABASE["ALL"] = sorted(list(all_words_set))

# Persistent Memorized Word Bank Storage State
if "memorized_words_dict" not in st.session_state:
    st.session_state.memorized_words_dict = {}

# Quiz State Management
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_current_index" not in st.session_state:
    st.session_state.quiz_current_index = 0
if "quiz_round_score" not in st.session_state:
    st.session_state.quiz_round_score = 0
if "quiz_total_score" not in st.session_state:
    st.session_state.quiz_total_score = 0
if "quiz_total_answered" not in st.session_state:
    st.session_state.quiz_total_answered = 0
if "quiz_round_complete" not in st.session_state:
    st.session_state.quiz_round_complete = False
if "quiz_awaiting_next_round_prompt" not in st.session_state:
    st.session_state.quiz_awaiting_next_round_prompt = False

# Navigation State Management
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "🏠 Study Dashboard"

if "vocab_category" not in st.session_state:
    st.session_state.vocab_category = "ALL"

if "vocab_index" not in st.session_state:
    st.session_state.vocab_index = 0

if "is_card_flipped" not in st.session_state:
    st.session_state.is_card_flipped = False

nav_choice = st.session_state.nav_choice

def render_top_back_button():
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Dashboard", key="top_back_dash_btn"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. STUDY DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="section-header-box">🌻 Study Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">MY GERMAN STUDY BUDDY</div>
        <div class="hero-title">German A1 Learning</div>
        <div class="hero-subtitle">Master Goethe vocabulary effortlessly and build your path to A1 fluency.</div>
    </div>
    """, unsafe_allow_html=True)

    modules = [
        "📚 Master Goethe Word Engine",
        "📖 Core Grammar Practice & Exercises",
        "📖 Goethe A1 Lesen (Reading)",
        "🎧 Goethe A1 Hören (Listening)",
        "✍️ Goethe A1 Schreiben (Writing)",
        "🗣️ Goethe A1 Sprechen (Speaking)",
        "📖 A1 & A2 Short Stories",
        "📖 Vocabulary",
        "🐱 Gem AI Tutor"
    ]

    for mod_title in modules:
        if st.button(mod_title, key=f"dash_card_{mod_title}", use_container_width=True):
            st.session_state.nav_choice = mod_title
            st.rerun()

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🌻 Master Goethe Word Engine</div>', unsafe_allow_html=True)
    
    categories = list(A1_VOCABULARY_DATABASE.keys())
    cat_options = {"ALL (All Categories)": "ALL"}
    for cat in categories:
        if cat != "ALL":
            cat_options[cat.replace('_', ' ').title()] = cat

    current_display_name = [k for k, v in cat_options.items() if v == st.session_state.vocab_category][0]
    
    selected_display_name = st.selectbox("Select Category:", list(cat_options.keys()), index=list(cat_options.keys()).index(current_display_name), key="category_dropdown", label_visibility="collapsed")
    
    selected_cat_key = cat_options[selected_display_name]
    if selected_cat_key != st.session_state.vocab_category:
        st.session_state.vocab_category = selected_cat_key
        st.session_state.vocab_index = 0
        st.session_state.is_card_flipped = False
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    current_word_list = A1_VOCABULARY_DATABASE[st.session_state.vocab_category]
    if not current_word_list:
        current_word_list = ["sein"]

    # --- ALPHABETICALLY SORTED WORD DROPDOWN WITH "ALL" OPTION AS FIRST OPTION ---
    sorted_current_words = sorted(current_word_list)
    word_dropdown_options = ["ALL (Shuffle / Show All Words)"] + sorted_current_words

    active_word = current_word_list[st.session_state.vocab_index]

    selected_word_dropdown = st.selectbox("Select Word (Sorted Alphabetically):", word_dropdown_options, key="word_alpha_dropdown", label_visibility="collapsed")
    
    if selected_word_dropdown == "ALL (Shuffle / Show All Words)":
        # Keep current active word or shuffle if needed
        pass
    else:
        if selected_word_dropdown != active_word:
            st.session_state.vocab_index = current_word_list.index(selected_word_dropdown)
            st.session_state.is_card_flipped = False
            st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    if st.session_state.vocab_index >= len(current_word_list):
        st.session_state.vocab_index = 0

    active_word = current_word_list[st.session_state.vocab_index]

    # Fetch structured flashcard data from Gemini
    prompt = f"""
    Provide exhaustive Goethe A1 flashcard data for the German word/phrase '{active_word}' in category '{st.session_state.vocab_category}'.
    CRITICAL REQUIREMENT for conjugations: Always provide 6 items (for pronouns ich, du, er/sie/es, wir, ihr, sie/Sie). Even if the word is a noun, preposition, adjective, or non-conjugatable word, provide a natural sample sentence using that exact word with each nominative pronoun.
    Return strict JSON with this exact schema:
    {{
        "word": "{active_word}",
        "category": "{st.session_state.vocab_category}",
        "gender": "der / die / das / N/A",
        "plural_form": "Plural form or N/A",
        "english_meaning": "English translation",
        "word_type": "noun / verb / preposition / reflexive pronoun / adjective / etc.",
        "case_usage": "akkusativ / dativ / akkusativ und dativ / nominativ / N/A",
        "auxiliary_verb": "sein / haben / N/A",
        "partizip_ii": "Partizip II form or N/A",
        "aux_sentence_de": "Sample sentence using auxiliary verb and Partizip II (or usage sentence)",
        "aux_sentence_en": "English translation of auxiliary sentence",
        "komparativ": "Komparativ form or N/A",
        "superlative": "Superlative form or N/A",
        "conjugations": [
            {{"pronoun": "ich", "form": "...", "sentence": "...", "english_sentence": "..."}},
            {{"pronoun": "du", "form": "...", "sentence": "...", "english_sentence": "..."}},
            {{"pronoun": "er/sie/es", "form": "...", "sentence": "...", "english_sentence": "..."}},
            {{"pronoun": "wir", "form": "...", "sentence": "...", "english_sentence": "..."}},
            {{"pronoun": "ihr", "form": "...", "sentence": "...", "english_sentence": "..."}},
            {{"pronoun": "sie/Sie", "form": "...", "sentence": "...", "english_sentence": "..."}}
        ],
        "colloquial_phrases": [
            {{"phrase_de": "German phrase", "phrase_en": "English translation"}}
        ],
        "grammar_notes": "Important A1 grammar note for this word"
    }}
    """
    
    try:
        raw_json = generate_cached_content(prompt, is_json=True)
        data = json.loads(raw_json)
    except Exception as e:
        data = {
            "word": active_word,
            "category": st.session_state.vocab_category,
            "gender": "N/A",
            "plural_form": "N/A",
            "english_meaning": "Translation loading error",
            "word_type": "unknown",
            "case_usage": "N/A",
            "auxiliary_verb": "N/A",
            "partizip_ii": "N/A",
            "aux_sentence_de": "N/A",
            "aux_sentence_en": "N/A",
            "komparativ": "N/A",
            "superlative": "N/A",
            "conjugations": [],
            "colloquial_phrases": [],
            "grammar_notes": str(e)
        }

    # Determine Card Color Class based on exact user rules:
    # - blue for masculine ("der")
    # - red for feminine ("die")
    # - green for neuter ("das")
    # - orange for verbs
    # - purple for everything else
    gender_val = str(data.get("gender", "N/A")).strip().lower()
    word_type_val = str(data.get("word_type", "")).strip().lower()

    if gender_val == "der":
        container_class = "card-masculine-container"
    elif gender_val == "die":
        container_class = "card-feminine-container"
    elif gender_val == "das":
        container_class = "card-neuter-container"
    elif "verb" in word_type_val:
        container_class = "card-verb-container"
    else:
        container_class = "card-other-container"

    # --- FRONT & BACK FLASHCARD CONTAINER ---
    card_html_content = f'<div class="{container_class}">'
    if not st.session_state.is_card_flipped:
        card_html_content += f"""
        <div style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; color: #ffffff;">🌻 Category: {data.get('category', '').replace('_', ' ').title()}</div>
        <div class="flashcard-word-title">{data.get('word', active_word)}</div>
        <div style="font-size: 1rem; margin-top: 4px; color: #ffffff;">Gender / Article: <b>{data.get('gender', 'N/A')}</b></div>
        """
    else:
        card_html_content += f"""
        <div style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; color: #ffffff;">🌻 Category: {data.get('category', '').replace('_', ' ').title()}</div>
        <div class="flashcard-word-title" style="font-size: 2.2rem;">{data.get('word', active_word)}</div>
        <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0px; color: #ffffff;">Meaning: {data.get('english_meaning', '')}</div>
        """
    card_html_content += '</div>'
    st.markdown(card_html_content, unsafe_allow_html=True)

    # --- "LISTEN" BUTTON FOR FRONT CARD ---
    if not st.session_state.is_card_flipped:
        if st.button("Listen", key="audio_front_btn"):
            play_direct_audio(data.get("word", active_word), "front_audio")

    # --- BACK OF CARD ARRANGEMENT OF INFORMATION ---
    if st.session_state.is_card_flipped:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        
        # "Listen" button for Back Card Header
        if st.button("Listen", key="audio_back_word"):
            play_direct_audio(data.get("word", active_word), "back_audio")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 1. Plural Version with Audio (PLACED BEFORE WORD TYPE)
        plural = data.get("plural_form", "N/A")
        if plural and plural != "N/A":
            st.markdown(f'<div class="detail-section-card"><b>Plural Version:</b> {plural}</div>', unsafe_allow_html=True)
            if st.button("Listen (Plural)", key="audio_plural"):
                play_direct_audio(plural, "plural_audio")

        # 2. Word Type
        st.markdown(f'<div class="detail-section-card"><b>Word Type:</b> {data.get("word_type", "N/A")}</div>', unsafe_allow_html=True)

        # 3. Case Usage
        st.markdown(f'<div class="detail-section-card"><b>Case Usage:</b> {data.get("case_usage", "N/A")}</div>', unsafe_allow_html=True)

        # 4. Auxiliary Verb & Partizip 2
        aux_verb = data.get('auxiliary_verb', 'N/A')
        part_ii = data.get('partizip_ii', 'N/A')
        st.markdown(f'<div class="detail-section-card"><b>Auxiliary Verb & Partizip II:</b> {aux_verb} ({part_ii})</div>', unsafe_allow_html=True)

        # 5. Auxiliary Verb & Partizip 2 Sample Sentence with Audio & English Translation
        aux_sent = data.get('aux_sentence_de', '')
        if aux_sent and aux_sent != "N/A":
            st.markdown(f'''<div class="detail-section-card">
                <b>Auxiliary Verb & Partizip II Sample Sentence:</b><br>
                <em>{aux_sent}</em><br>
                <small style="color: #94a3b8;">({data.get('aux_sentence_en', '')})</small>
            </div>''', unsafe_allow_html=True)
            if st.button("Listen (Aux Sentence)", key="audio_aux_sent"):
                play_direct_audio(aux_sent, "aux_sent_audio")

        # 6. Komparativ and Superlative with Audio
        komp = data.get('komparativ', 'N/A')
        sup = data.get('superlative', 'N/A')
        if komp != "N/A" or sup != "N/A":
            st.markdown(f'<div class="detail-section-card"><b>Komparativ & Superlative:</b> {komp} | {sup}</div>', unsafe_allow_html=True)
            if st.button("Listen (Komparativ / Superlative)", key="audio_komp"):
                play_direct_audio(f"{komp} {sup}", "komp_audio")

        # 7. Conjugation and Sample Sentences for each pronoun with Audio
        conjugations = data.get("conjugations", [])
        if conjugations:
            conj_html = '<div class="detail-section-card"><b>Conjugation and Sample Sentences:</b><br><ul style="margin: 4px 0 0 16px; padding: 0;">'
            for conj in conjugations:
                conj_html += f'<li><b>{conj.get("pronoun", "")}</b> ({conj.get("form", "--")}): <em>{conj.get("sentence", "")}</em> <small>({conj.get("english_sentence", "")})</small></li>'
            conj_html += '</ul></div>'
            st.markdown(conj_html, unsafe_allow_html=True)
            if st.button("Listen (Conjugations)", key="audio_conj_all"):
                full_conj_text = ". ".join([c.get("sentence", "") for c in conjugations])
                play_direct_audio(full_conj_text, "conj_all_audio")

        # 8. Colloquial and Daily Phrases Sample Sentences with Audio
        phrases = data.get("colloquial_phrases", [])
        if phrases:
            ph_html = '<div class="detail-section-card"><b>Colloquial & Daily Phrases:</b><br><ul style="margin: 4px 0 0 16px; padding: 0;">'
            for ph in phrases:
                ph_html += f'<li><b>{ph.get("phrase_de", "")}</b> — <em>{ph.get("phrase_en", "")}</em></li>'
            ph_html += '</ul></div>'
            st.markdown(ph_html, unsafe_allow_html=True)
            if st.button("Listen (Colloquial Phrases)", key="audio_phrases_all"):
                full_ph_text = ". ".join([p.get("phrase_de", "") for p in phrases])
                play_direct_audio(full_ph_text, "ph_all_audio")

        # 9. Grammar Notes
        st.markdown(f'<div class="detail-section-card"><b>Grammar Notes:</b> {data.get("grammar_notes", "N/A")}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- BELOW FLASHCARD CONTROL BUTTONS ("Flip", "Back", "Shuffle", "Next") ---
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
    with col_ctrl1:
        if not st.session_state.is_card_flipped:
            if st.button("Flip", use_container_width=True, key="ctrl_flip_btn"):
                st.session_state.is_card_flipped = True
                st.rerun()
        else:
            if st.button("Flip", use_container_width=True, key="ctrl_flip_back_btn"):
                st.session_state.is_card_flipped = False
                st.rerun()
    with col_ctrl2:
        if st.button("Back", use_container_width=True, key="ctrl_back_btn"):
            st.session_state.vocab_index = (st.session_state.vocab_index - 1) % len(current_word_list)
            st.session_state.is_card_flipped = False
            st.rerun()
    with col_ctrl3:
        if st.button("Shuffle", use_container_width=True, key="ctrl_shuffle_btn"):
            st.session_state.vocab_index = random.randint(0, len(current_word_list) - 1)
            st.session_state.is_card_flipped = False
            st.rerun()
    with col_ctrl4:
        if st.button("Next", use_container_width=True, key="ctrl_next_btn"):
            st.session_state.vocab_index = (st.session_state.vocab_index + 1) % len(current_word_list)
            st.session_state.is_card_flipped = False
            st.rerun()

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # --- "MEMORIZED" BUTTON BELOW "NEXT" BUTTON TO TAG WORD ---
    word_key = active_word.strip()
    is_already_memorized = word_key in st.session_state.memorized_words_dict

    if not is_already_memorized:
        if st.button("Memorized", use_container_width=True, key="tag_memorized_btn"):
            st.session_state.memorized_words_dict[word_key] = data.get("english_meaning", "N/A")
            st.success(f"Successfully added '{word_key}' to your Vocabulary word bank!")
            time.sleep(0.6)
            st.rerun()
    else:
        st.markdown('<div style="text-align: center; color: #34d399; font-weight: 700; padding: 8px;">✅ This word is in your Vocabulary Word Bank</div>', unsafe_allow_html=True)
        if st.button("Remove from Memorized", use_container_width=True, key="remove_memorized_btn"):
            del st.session_state.memorized_words_dict[word_key]
            st.rerun()

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📖 Core Grammar Practice & Exercises</div>', unsafe_allow_html=True)

    # Handbook Lessons mapped accurately from the Table of Contents of German-A1-Passive-Fluency-Handbook.pdf
    handbook_lessons = {
        "Lesson 1": "Understanding German Alphabet, Pronunciation, and Article Recognition",
        "Lesson 2": "Learning German Noun Gender and Everyday Word Patterns",
        "Lesson 3": "Recognizing Singular and Plural Forms in Daily German",
        "Lesson 4": "Reading Personal Introductions and Basic Identity Information",
        "Lesson 5": "Building Simple German Sentences for Everyday Communication",
        "Lesson 6": "Recognizing Present Tense Verb Patterns in Practical German",
        "Lesson 7": "Working with sein and haben in Everyday Situations",
        "Lesson 8": "Understanding Numbers, Prices, Dates, and Everyday Quantities",
        "Lesson 9": "Reading Everyday Question Structures and Basic Information Requests",
        "Lesson 10": "Recognizing Negation and Negative Sentences in Practical German",
        "Lesson 11": "Exploring Object Sentences and Basic Accusative Structures",
        "Lesson 12": "Reading Simple Descriptions of People, Places, and Things",
        "Lesson 13": "Recognizing Possession, Ownership, and Family Relationships",
        "Lesson 14": "Reading Time Expressions, Appointments, and Schedules",
        "Lesson 15": "Understanding Daily Routine Patterns and Everyday Activities",
        "Lesson 16": "Recognizing Commands, Requests, and Basic Instructions",
        "Lesson 17": "Exploring Abilities, Obligations, and Everyday Modal Verbs",
        "Lesson 18": "Reading Practical Sentences with Modal Verb Structures",
        "Lesson 19": "Exploring Everyday Dative Structures and Indirect Objects",
        "Lesson 20": "Reading Common Dative Expressions in Real-Life Communication",
        "Lesson 21": "Understanding Location Expressions and Place Descriptions",
        "Lesson 22": "Reading Movement and Position Patterns in Everyday German",
        "Lesson 23": "Exploring Two-Way Prepositions and Directional Meaning",
        "Lesson 24": "Reading Shopping, Money, and Price Communication",
        "Lesson 25": "Connecting Simple Ideas with Basic German Connectors",
        "Lesson 26": "Recognizing Reasons, Explanations, and Cause Structures",
        "Lesson 27": "Reading Future Expressions and Everyday Planning Language",
        "Lesson 28": "Exploring Past Events with haben and Perfekt Structures",
        "Lesson 29": "Exploring Movement and Travel Narration with sein",
        "Lesson 30": "Reading Everyday Past Narration and Simple Storytelling",
        "Lesson 31": "Recognizing Separable Verb Patterns in Daily Communication",
        "Lesson 32": "Exploring Comparisons, Preferences, and Basic Opinions",
        "Lesson 33": "Reading Likes, Preferences, and Personal Interests",
        "Lesson 34": "Recognizing Simple Subordinate Clauses and Verb-Final Patterns",
        "Lesson 35": "Reading Simple Emails, Messages, and Digital Communication",
        "Lesson 36": "Recognizing Everyday Conversation Patterns and Social Interaction",
        "Lesson 37": "Recognizing and Correcting Common A1 Grammar Mistakes",
        "Lesson 38": "Recognizing A1 Grammar in Authentic German Texts",
        "Lesson 39": "Reading Everyday Public Signs, Instructions, and Survival German",
        "Lesson 40": "CEFR A1 Mock Examination (Written Test)"
    }

    # Initialize session state for selected lesson if missing
    if "selected_grammar_lesson" not in st.session_state:
        st.session_state.selected_grammar_lesson = "Lesson 1"

    # Initialize quiz state per lesson
    if "grammar_quiz_active" not in st.session_state:
        st.session_state.grammar_quiz_active = False
    if "grammar_quiz_questions" not in st.session_state:
        st.session_state.grammar_quiz_questions = []
    if "grammar_quiz_index" not in st.session_state:
        st.session_state.grammar_quiz_index = 0
    if "grammar_quiz_score" not in st.session_state:
        st.session_state.grammar_quiz_score = 0
    if "grammar_quiz_submitted" not in st.session_state:
        st.session_state.grammar_quiz_submitted = False
    if "grammar_quiz_complete" not in st.session_state:
        st.session_state.grammar_quiz_complete = False

    # Dropdown to choose lesson
    lesson_options = [f"{k}: {v}" for k, v in handbook_lessons.items()]
    current_selected_str = [opt for opt in lesson_options if opt.startswith(st.session_state.selected_grammar_lesson)][0]

    chosen_dropdown_val = st.selectbox("Select Lesson from Handbook:", lesson_options, index=lesson_options.index(current_selected_str), key="grammar_lesson_dropdown", label_visibility="collapsed")
    
    new_lesson_key = chosen_dropdown_val.split(":")[0].strip()
    if new_lesson_key != st.session_state.selected_grammar_lesson:
        st.session_state.selected_grammar_lesson = new_lesson_key
        st.session_state.grammar_quiz_active = False
        st.session_state.grammar_quiz_complete = False
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- TUTOR LESSON EXPLANATION FETCH ---
    lesson_title = handbook_lessons[st.session_state.selected_grammar_lesson]
    
    explain_prompt = f"""
    Act as an expert German tutor and study buddy inside the German A1 Core Grammar Practice section.
    Provide a comprehensive, highly engaging explanation for handbook lesson: '{st.session_state.selected_grammar_lesson}: {lesson_title}' based on the provided German A1 Passive Fluency Handbook.
    Provide more insight, professional study tips, and practical examples on top of what is in the handbook so the student fully masters the concept.
    Format your response cleanly using Markdown headings, bullet points, and tables where applicable.
    """

    with st.spinner(f"Gem is preparing comprehensive study materials for {st.session_state.selected_grammar_lesson}..."):
        try:
            lesson_explanation = generate_cached_content(explain_prompt)
        except Exception as e:
            lesson_explanation = f"Error loading lesson breakdown: {str(e)}"

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f"### 🌻 {st.session_state.selected_grammar_lesson}: {lesson_title}")
    st.markdown(lesson_explanation, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- INTERACTIVE QUIZ SECTION (20 QUESTIONS: Multiple Choice, Fill-in-the-blank, Sentence Building, Translation) ---
    st.markdown('<div class="section-header-box">🧠 Lesson Quiz & Progress Check (20 Questions)</div>', unsafe_allow_html=True)

    if not st.session_state.grammar_quiz_active and not st.session_state.grammar_quiz_complete:
        st.markdown("Test your mastery of this lesson with 20 targeted questions (Multiple Choice, Fill-in-the-blank, Sentence Building, and Translation). Detailed explanations will be provided for incorrect answers, and your score will be tracked.")
        if st.button("🚀 Start Lesson Quiz (20 Questions)", key="start_g_quiz_btn"):
            # Generate 20 questions via Gemini JSON
            quiz_prompt = f"""
            Generate a rigorous 20-question German A1 quiz for handbook lesson '{st.session_state.selected_grammar_lesson}: {lesson_title}'.
            Include a balanced mix of question types: Multiple Choice, Fill-in-the-blank, Sentence Building, and Translation.
            Return strict JSON array with this exact schema:
            [
                {{
                    "question_number": 1,
                    "question_type": "Multiple Choice / Fill-in-the-blank / Sentence Building / Translation",
                    "question_text": "Question statement here",
                    "options": ["Option A", "Option B", "Option C", "Option D"] (or empty list if open-ended),
                    "correct_answer": "Exact correct answer string",
                    "explanation": "Detailed pedagogical explanation why this is correct and common pitfalls."
                }}
            ]
            Ensure there are exactly 20 items in the array.
            """
            with st.spinner("Generating 20 quiz questions tailored to this lesson..."):
                try:
                    q_json_raw = generate_cached_content(quiz_prompt, is_json=True)
                    q_data = json.loads(q_json_raw)
                    st.session_state.grammar_quiz_questions = q_data
                    st.session_state.grammar_quiz_index = 0
                    st.session_state.grammar_quiz_score = 0
                    st.session_state.grammar_quiz_submitted = False
                    st.session_state.grammar_quiz_active = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate quiz: {str(e)}")

    elif st.session_state.grammar_quiz_active and not st.session_state.grammar_quiz_complete:
        q_list = st.session_state.grammar_quiz_questions
        q_idx = st.session_state.grammar_quiz_index

        if q_idx < len(q_list):
            q_item = q_list[q_idx]
            st.markdown(f"**Question {q_idx + 1} of {len(q_list)}** | *Type: {q_item.get('question_type', 'Quiz')}*")
            st.markdown(f"**{q_item.get('question_text')}**")

            q_options = q_item.get("options", [])
            user_answer_key = f"g_ans_{st.session_state.selected_grammar_lesson}_{q_idx}"

            if q_options and len(q_options) > 1:
                selected_opt = st.radio("Choose your answer:", q_options, key=user_answer_key)
                user_input = selected_opt
            else:
                user_input = st.text_input("Your answer:", key=user_answer_key)

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

            if not st.session_state.grammar_quiz_submitted:
                if st.button("Submit Answer", key=f"sub_g_{q_idx}", disabled=not user_input):
                    st.session_state.grammar_quiz_submitted = True
                    # Evaluate correctness
                    correct_ans = str(q_item.get("correct_answer", "")).strip().lower()
                    given_ans = str(user_input).strip().lower()

                    is_correct = False
                    if given_ans == correct_ans or correct_ans in given_ans or given_ans in correct_ans:
                        is_correct = True
                        st.session_state.grammar_quiz_score += 1
                        st.success("✅ **Correct! Excellent work.**")
                    else:
                        st.error(f"❌ **Incorrect.**\n\n**Correct Answer:** {q_item.get('correct_answer')}\n\n**Explanation:** {q_item.get('explanation')}")

                    st.rerun()
            else:
                # Show explanation if already submitted and button to next
                correct_ans = str(q_item.get("correct_answer", "")).strip().lower()
                given_ans = str(user_input).strip().lower()
                if given_ans == correct_ans or correct_ans in given_ans or given_ans in correct_ans:
                    st.success("✅ **Correct!**")
                else:
                    st.error(f"❌ **Incorrect.**\n\n**Correct Answer:** {q_item.get('correct_answer')}\n\n**Explanation:** {q_item.get('explanation')}")

                if st.button("Next Question ➡️", key=f"next_g_{q_idx}"):
                    st.session_state.grammar_quiz_submitted = False
                    st.session_state.grammar_quiz_index += 1
                    st.rerun()
        else:
            st.session_state.grammar_quiz_active = False
            st.session_state.grammar_quiz_complete = True
            st.rerun()

    elif st.session_state.grammar_quiz_complete:
        final_score = st.session_state.grammar_quiz_score
        total_q = len(st.session_state.grammar_quiz_questions)
        percentage = (final_score / total_q) * 100 if total_q > 0 else 0

        st.markdown(f"### 🎉 Quiz Complete for {st.session_state.selected_grammar_lesson}!")
        st.markdown(f"**Your Progress Score:** Scored **{final_score}/{total_q}** ({percentage:.1f}%)")

        if percentage >= 80:
            st.success("🌟 **Outstanding mastery!** You have thoroughly grasped this handbook lesson.")
        elif percentage >= 50:
            st.info("👍 **Good effort!** Review the handbook lesson explanations above to solidify the remaining concepts.")
        else:
            st.warning("💡 **Keep practicing!** Re-read the comprehensive explanation above and try the quiz again.")

        if st.button("🔄 Retake Lesson Quiz", key="retake_g_quiz_btn"):
            st.session_state.grammar_quiz_complete = False
            st.session_state.grammar_quiz_active = False
            st.session_state.grammar_quiz_score = 0
            st.session_state.grammar_quiz_index = 0
            st.rerun()

# ----------------------------------------------------
# 4. GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📖 Goethe A1 Lesen (Reading)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🎧 Goethe A1 Hören (Listening)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">✍️ Goethe A1 Schreiben (Writing)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🗣️ Goethe A1 Sprechen (Speaking)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. A1 & A2 SHORT STORIES
# ----------------------------------------------------
elif nav_choice == "📖 A1 & A2 Short Stories":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📖 A1 & A2 Short Stories</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 9. VOCABULARY SECTION (MEMORIZED WORDS & QUIZ ME)
# ----------------------------------------------------
elif nav_choice == "📖 Vocabulary":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📖 Vocabulary Word Bank</div>', unsafe_allow_html=True)
    
    # --- QUIZ ME INTERACTIVE WIDGET AT THE TOP (NO EXTRA WHITE BOXES) ---
    st.markdown("### 🧠 Quiz Me Challenge")
    
    memorized_items = list(st.session_state.memorized_words_dict.items())
    
    if len(memorized_items) < 3:
        st.info("💡 **Tip:** You need at least 3 words tagged as **Memorized** in the *Master Goethe Word Engine* section to start a meaningful quiz session. Explore words and tag them as memorized to build your vocabulary bank!")
    else:
        if not st.session_state.quiz_active and not st.session_state.quiz_awaiting_next_round_prompt:
            st.markdown("Test your translation and memory retention with an interactive flashcard quiz.")
            quiz_choice_mode = st.selectbox("Select Quiz Mode:", ["German to English", "English to German"], key="quiz_mode_select")
            if st.button("🚀 Start Quiz (10 Words)", key="start_quiz_btn"):
                st.session_state.quiz_mode = quiz_choice_mode
                selected_sample = random.sample(memorized_items, min(10, len(memorized_items)))
                st.session_state.quiz_questions = selected_sample
                st.session_state.quiz_current_index = 0
                st.session_state.quiz_round_score = 0
                st.session_state.quiz_round_complete = False
                st.session_state.quiz_active = True
                st.rerun()

        # Active Quiz Session Loop
        elif st.session_state.quiz_active and not st.session_state.quiz_round_complete:
            q_list = st.session_state.quiz_questions
            idx = st.session_state.quiz_current_index
            
            if idx < len(q_list):
                german_word, english_meaning = q_list[idx]
                st.markdown(f"**Question {idx + 1} of {len(q_list)}** (Mode: *{st.session_state.quiz_mode}*)")
                
                if st.session_state.quiz_mode == "German to English":
                    st.markdown(f"Translate this German word to English: **{german_word}**")
                    user_ans = st.text_input("Your English translation:", key=f"quiz_ans_{idx}")
                    submit_disabled = not user_ans.strip()
                    if st.button("Submit Answer", key=f"submit_q_{idx}", disabled=submit_disabled):
                        correct = english_meaning.strip().lower()
                        given = user_ans.strip().lower()
                        if given in correct or correct in given:
                            st.success(f"✅ Correct! '{german_word}' means '{english_meaning}'.")
                            st.session_state.quiz_round_score += 1
                        else:
                            st.error(f"❌ Incorrect. Correct translation for **{german_word}** is **{english_meaning}**.")
                        
                        time.sleep(1.2)
                        st.session_state.quiz_current_index += 1
                        st.rerun()
                else:
                    st.markdown(f"Translate this English word to German: **{english_meaning}**")
                    user_ans = st.text_input("Your German translation:", key=f"quiz_ans_{idx}")
                    submit_disabled = not user_ans.strip()
                    if st.button("Submit Answer", key=f"submit_q_{idx}", disabled=submit_disabled):
                        correct = german_word.strip().lower()
                        given = user_ans.strip().lower()
                        if given in correct or correct in given:
                            st.success(f"✅ Correct! '{english_meaning}' in German is '{german_word}'.")
                            st.session_state.quiz_round_score += 1
                        else:
                            st.error(f"❌ Incorrect. Correct German translation for **{english_meaning}** is **{german_word}**.")
                        
                        time.sleep(1.2)
                        st.session_state.quiz_current_index += 1
                        st.rerun()
            else:
                # Round finished
                r_score = st.session_state.quiz_round_score
                r_total = len(q_list)
                st.session_state.quiz_total_score += r_score
                st.session_state.quiz_total_answered += r_total
                st.session_state.quiz_round_complete = True
                st.session_state.quiz_awaiting_next_round_prompt = True
                st.session_state.quiz_active = False
                st.rerun()

        # Prompting for another round of 10 words
        elif st.session_state.quiz_awaiting_next_round_prompt:
            r_total = len(st.session_state.quiz_questions)
            r_score = st.session_state.quiz_round_score
            st.markdown(f"### 📊 Round Complete! Scored {r_score}/{r_total}")
            st.markdown(f"**Cumulative Score So Far:** {st.session_state.quiz_total_score}/{st.session_state.quiz_total_answered}")
            st.markdown("Would you like to go for another round of 10 words?")
            
            c_yes, c_no = st.columns(2)
            with c_yes:
                if st.button("Yes", key="quiz_yes_btn"):
                    selected_sample = random.sample(memorized_items, min(10, len(memorized_items)))
                    st.session_state.quiz_questions = selected_sample
                    st.session_state.quiz_current_index = 0
                    st.session_state.quiz_round_score = 0
                    st.session_state.quiz_round_complete = False
                    st.session_state.quiz_awaiting_next_round_prompt = False
                    st.session_state.quiz_active = True
                    st.rerun()
            with c_no:
                if st.button("No", key="quiz_no_btn"):
                    final_score = st.session_state.quiz_total_score
                    final_total = st.session_state.quiz_total_answered
                    st.success(f"🎉 Quiz finished! Total score tallied: **Scored {final_score}/{final_total}**.")
                    st.session_state.quiz_active = False
                    st.session_state.quiz_round_complete = False
                    st.session_state.quiz_awaiting_next_round_prompt = False
                    st.session_state.quiz_total_score = 0
                    st.session_state.quiz_total_answered = 0
                    time.sleep(1.5)
                    st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- MEMORIZED WORDS WORD BANK DISPLAY (ALPHABETICAL SORT, NO EXTRA WHITE BOXES) ---
    st.markdown("### 📚 Memorized Word Bank")
    st.markdown("Here are all the words you have tagged as **Memorized** in the *Master Goethe Word Engine*, sorted in alphabetical order:")
    
    if not st.session_state.memorized_words_dict:
        st.info("Your word bank is currently empty. Visit **Master Goethe Word Engine**, review flashcards, and click **Memorized** to build your vocabulary list.")
    else:
        sorted_memorized = sorted(st.session_state.memorized_words_dict.items(), key=lambda x: x[0].lower())
        
        col_h1, col_h2 = st.columns([1, 1])
        col_h1.markdown("**German Word**")
        col_h2.markdown("**English Translation**")
        st.markdown("<hr style='border-color: rgba(244, 114, 182, 0.3); margin: 6px 0;'>", unsafe_allow_html=True)
        
        for g_word, e_trans in sorted_memorized:
            rc1, rc2 = st.columns([1, 1])
            rc1.markdown(f"**{g_word}**")
            rc2.markdown(f"{e_trans}")
            st.markdown("<hr style='border-color: rgba(244, 114, 182, 0.15); margin: 4px 0;'>", unsafe_allow_html=True)

# ----------------------------------------------------
# 10. GEM AI TUTOR
# ----------------------------------------------------
elif nav_choice == "🐱 Gem AI Tutor":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🐱 Gem — AI German Tutor</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if "gem_chat_messages" not in st.session_state:
        st.session_state.gem_chat_messages = []
    for msg in st.session_state.gem_chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if user_prompt := st.chat_input("Ask Gem anything about German..."):
        st.session_state.gem_chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
        with st.chat_message("assistant"):
            with st.spinner("Gem is thinking..."):
                response = generate_cached_content(user_prompt)
                st.write(response)
                st.session_state.gem_chat_messages.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)
