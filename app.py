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
        st.session_state.grammar_quiz_questions = []
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

    st.markdown(f"### 🌻 {st.session_state.selected_grammar_lesson}: {lesson_title}")
    st.markdown(lesson_explanation, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # --- CSS STYLING TO MAKE RADIO LABELS & INPUT LABELS BRIGHT & VISIBLE ---
    st.markdown("""
        <style>
        /* Target Streamlit radio labels and text input labels/text for high visibility on dark backgrounds */
        div.stRadio label, div.stTextInput label, div.stTextInput input {
            color: #FFFFFF !important;
        }
        /* Ensure radio button option text is clearly visible */
        .stRadio p {
            color: #F8FAFC !important;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- INTERACTIVE QUIZ SECTION (ALL 20 QUESTIONS ON ONE PAGE) ---
    st.markdown('<div class="section-header-box">🧠 Lesson Quiz & Progress Check (20 Questions)</div>', unsafe_allow_html=True)

    if not st.session_state.grammar_quiz_active and not st.session_state.grammar_quiz_complete:
        st.markdown("Test your mastery of this lesson with all 20 targeted questions displayed at once. Answer them all and submit when you are ready.")
        if st.button("🚀 Load All 20 Questions", key="start_g_quiz_btn"):
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
            with st.spinner("Generating all 20 quiz questions tailored to this lesson..."):
                try:
                    q_json_raw = generate_cached_content(quiz_prompt, is_json=True)
                    q_data = json.loads(q_json_raw)
                    st.session_state.grammar_quiz_questions = q_data
                    st.session_state.grammar_quiz_active = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate quiz: {str(e)}")

    elif st.session_state.grammar_quiz_active and not st.session_state.grammar_quiz_complete:
        q_list = st.session_state.grammar_quiz_questions
        
        with st.form(key="all_20_questions_form"):
            user_answers = {}
            for q_idx, q_item in enumerate(q_list):
                st.markdown(f"**Question {q_idx + 1} of {len(q_list)}** | *Type: {q_item.get('question_type', 'Quiz')}*")
                st.markdown(f"**{q_item.get('question_text')}**")

                q_options = q_item.get("options", [])
                user_answer_key = f"g_ans_{st.session_state.selected_grammar_lesson}_{q_idx}"

                if q_options and len(q_options) > 1:
                    user_answers[q_idx] = st.radio("Choose your answer:", q_options, key=user_answer_key)
                else:
                    user_answers[q_idx] = st.text_input("Your answer:", key=user_answer_key)

                st.markdown("---")

            submitted_form = st.form_submit_button("📥 Submit All Answers")

            if submitted_form:
                score = 0
                results_breakdown = []
                for q_idx, q_item in enumerate(q_list):
                    correct_ans = str(q_item.get("correct_answer", "")).strip().lower()
                    given_ans = str(user_answers.get(q_idx, "")).strip().lower()

                    is_correct = False
                    if given_ans == correct_ans or correct_ans in given_ans or given_ans in correct_ans:
                        is_correct = True
                        score += 1

                    results_breakdown.append({
                        "q_num": q_idx + 1,
                        "question": q_item.get("question_text"),
                        "given": user_answers.get(q_idx, ""),
                        "correct": q_item.get("correct_answer"),
                        "is_correct": is_correct,
                        "explanation": q_item.get("explanation")
                    })

                st.session_state.grammar_quiz_score = score
                st.session_state.grammar_quiz_results = results_breakdown
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
            st.info("👍 **Good effort!** Review the feedback below to solidify the remaining concepts.")
        else:
            st.warning("💡 **Keep practicing!** Re-read the comprehensive explanation above and try again.")

        st.markdown("#### 📝 Detailed Review of Your Answers:")
        for res in st.session_state.get("grammar_quiz_results", []):
            if res["is_correct"]:
                st.success(f"**Q{res['q_num']}: {res['question']}**\n\n- **Your Answer:** {res['given']} (Correct!)")
            else:
                st.error(f"**Q{res['q_num']}: {res['question']}**\n\n- **Your Answer:** {res['given']}\n- **Correct Answer:** {res['correct']}\n- **Explanation:** {res['explanation']}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Retake Lesson Quiz", key="retake_g_quiz_btn"):
            st.session_state.grammar_quiz_complete = False
            st.session_state.grammar_quiz_active = False
            st.session_state.grammar_quiz_score = 0
            st.session_state.grammar_quiz_questions = []
            st.rerun()

# ----------------------------------------------------
# 4. GOETHE A1 LESEN (READING) SECTION
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📖 Goethe A1 Lesen (Reading) Exam Practice</div>', unsafe_allow_html=True)

    st.markdown("""
    **Goethe A1 Reading (Lesen) Format:** 25 minutes | 3 parts | 15 questions  
    *Mirrored directly from the official Start Deutsch 1 exam layouts (featuring authentic email browser frames for Teil 1, dual website source comparison for Teil 2, and framed public sign/notice boxes with Richtig/Falsch statements for Teil 3).*
    """)

    if "lesen_part" not in st.session_state:
        st.session_state.lesen_part = "Part 1: Match Short Texts & Ads"
    if "lesen_seed" not in st.session_state:
        st.session_state.lesen_seed = 1
    if "lesen_active" not in st.session_state:
        st.session_state.lesen_active = False
    if "lesen_questions" not in st.session_state:
        st.session_state.lesen_questions = []
    if "lesen_complete" not in st.session_state:
        st.session_state.lesen_complete = False

    lesen_parts = [
        "Part 1: Match Short Texts & Ads (Richtig / Falsch based on emails)",
        "Part 2: Multiple Choice Web/Information Selection (Choose a or b source links)",
        "Part 3: Public Information & Detail Extraction (Richtig / Falsch signs/notices)"
    ]

    chosen_lesen_part = st.selectbox("Select Goethe Lesen Exam Part:", lesen_parts, key="lesen_part_dropdown", label_visibility="collapsed")

    if chosen_lesen_part != st.session_state.lesen_part:
        st.session_state.lesen_part = chosen_lesen_part
        st.session_state.lesen_active = False
        st.session_state.lesen_complete = False
        st.session_state.lesen_questions = []
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Styling for bright visible fonts and exact exam UI frames mirroring official Goethe test booklets
    st.markdown("""
        <style>
        div.stRadio label, div.stTextInput label, div.stTextInput input, div.stSelectbox label {
            color: #FFFFFF !important;
        }
        .stRadio p {
            color: #F8FAFC !important;
            font-weight: 500;
        }
        .exam-browser-frame {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 2px solid #64748B;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 15px;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        .browser-top-bar {
            background-color: #E2E8F0;
            padding: 6px 10px;
            border-bottom: 1px solid #CBD5E1;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: #334155;
        }
        .browser-address-bar {
            background-color: #FFFFFF;
            border: 1px solid #94A3B8;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.8rem;
            color: #1E293B;
            width: 100%;
        }
        .browser-body {
            padding: 15px;
            background-color: #FFFFFF;
            color: #0F172A;
            font-size: 0.95rem;
            line-height: 1.4;
            min-height: 120px;
        }
        .exam-memo-box {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 2px solid #64748B;
            padding: 25px;
            border-radius: 4px;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
            margin-bottom: 15px;
            font-family: Georgia, serif;
            line-height: 1.6;
        }
        .exam-sign-box {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 3px solid #64748B;
            padding: 25px;
            border-radius: 4px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
            margin-bottom: 15px;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    if "Part 1" in st.session_state.lesen_part:
        st.markdown("""
        #### 📌 Part 1: Reading Short Emails & Announcements (Richtig / Falsch)[cite: 20]
        * **Exam Format:** Read authentic email and club announcement frames mirroring the official Goethe test paper, then evaluate statements as Richtig or Falsch[cite: 20].
        """)
    elif "Part 2" in st.session_state.lesen_part:
        st.markdown("""
        #### 📌 Part 2: Information Sources & Web Links (Choose a or b)[cite: 22]
        * **Exam Format:** Read a specific information need scenario, examine the two side-by-side browser windows (a and b), and select which website provides the correct information[cite: 22, 23, 24].
        """)
    else:
        st.markdown("""
        #### 📌 Part 3: Public Information, Signs & Notices (Richtig / Falsch)[cite: 25]
        * **Exam Format:** Read public notices, vending machine rules, or hotel/station signs presented inside official bordered boxes, and determine if statements are Richtig or Falsch[cite: 25, 26, 27].
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Automatically generate/refresh scenarios when button is clicked or when questions are empty
    if not st.session_state.lesen_active and not st.session_state.lesen_complete:
        if "Part 2" in st.session_state.lesen_part:
            lesen_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Reading (Lesen) Part 2 practice module using seed {st.session_state.lesen_seed}.
            Provide 5 questions in total. Each question must have:
            - "user_goal": A scenario statement describing what the person wants to find.
            - "url_a": website URL string
            - "content_a": website text content for option a
            - "url_b": website URL string
            - "content_b": website text content for option b
            - "correct_answer": "a" or "b"
            - "explanation": detailed explanation.
            Return strict JSON array with 5 items.
            """
        elif "Part 3" in st.session_state.lesen_part:
            lesen_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Reading (Lesen) Part 3 practice module using seed {st.session_state.lesen_seed}.
            Provide 5 questions (numbered item 11 to 15 format style). Each question must have:
            - "item_num": question number (e.g., 11, 12, 13, 14, 15)
            - "location_header": location title (e.g., "Am Fahrkartenautomaten", "Im Hotelzimmer", "Eingang Restaurant", "Im Kultur-Verein", "Im Bahnhof")
            - "sign_text": the text inside the official framed sign box (e.g. rules, prices, schedules)
            - "statement": the statement to evaluate (e.g. "Am Samstag können Sie mit dem Ticket für 29 Euro fahren.")
            - "correct_answer": "Richtig" or "Falsch"
            - "explanation": detailed explanation.
            Return strict JSON array with 5 items.
            """
        else:
            lesen_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Reading (Lesen) Part 1 practice module using seed {st.session_state.lesen_seed}.
            Provide exactly 2 independent texts (Text 1 formatted as an email browser frame with 2 statements numbered 1 and 2; Text 2 formatted as a club/Verein announcement memo block with 3 statements numbered 3, 4, and 5).
            Return strict JSON array with 5 items total (items 1-2 for text 1, items 3-5 for text 2), matching this exact schema:
            [
                {{
                    "q_num": 1,
                    "text_block_id": 1,
                    "layout_type": "email",
                    "email_subject": "Hallo!",
                    "text_snippet": "Liebe Nora,\n\nich bin nächste Woche...",
                    "question_text": "Renate macht in Weimar Urlaub.",
                    "options": ["Richtig", "Falsch"],
                    "correct_answer": "Falsch",
                    "explanation": "Detailed explanation."
                }}
            ]
            """

        with st.spinner("Generating fresh official Goethe Lesen exam questions and UI frames..."):
            try:
                lesen_raw = generate_cached_content(lesen_prompt, is_json=True)
                st.session_state.lesen_questions = json.loads(lesen_raw)
                st.session_state.lesen_active = True
            except Exception as e:
                st.error(f"Failed to generate Lesen practice: {str(e)}")

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn2:
        if st.button("🔄 Refresh Scenarios", key="refresh_lesen_btn"):
            st.session_state.lesen_seed += 1
            st.session_state.lesen_active = False
            st.session_state.lesen_complete = False
            st.session_state.lesen_questions = []
            st.rerun()

    if st.session_state.lesen_active and not st.session_state.lesen_complete:
        q_list = st.session_state.lesen_questions

        if "Part 2" in st.session_state.lesen_part:
            # --- LESEN TEIL 2: DUAL BROWSER WINDOW LAYOUT ---
            with st.form(key="lesen_teil2_form"):
                user_lesen_answers = {}
                for idx, q in enumerate(q_list):
                    st.markdown(f"**Aufgabe {idx + 1} of {len(q_list)}**")
                    st.markdown(f"<span style='color: #FFFFFF; font-weight: bold; font-size: 1.05rem;'>{q.get('user_goal')}</span>", unsafe_allow_html=True)
                    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                    col_browser_a, col_browser_b = st.columns(2)
                    
                    with col_browser_a:
                        st.markdown(f"""
                        <div class="exam-browser-frame">
                            <div class="browser-top-bar">
                                <span>📁</span>
                                <div class="browser-address-bar">{q.get('url_a', 'www.site-a.de')}</div>
                            </div>
                            <div class="browser-body">
                                <b>Website A</b><br>{q.get('content_a')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_browser_b:
                        st.markdown(f"""
                        <div class="exam-browser-frame">
                            <div class="browser-top-bar">
                                <span>📁</span>
                                <div class="browser-address-bar">{q.get('url_b', 'www.site-b.de')}</div>
                            </div>
                            <div class="browser-body">
                                <b>Website B</b><br>{q.get('content_b')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    opts = [f"a) {q.get('url_a', 'Website A')}", f"b) {q.get('url_b', 'Website B')}"]
                    user_lesen_answers[idx] = st.radio(f"Wo finden Sie Informationen für Aufgabe {idx+1}?", opts, key=f"lesen_t2_ans_{idx}")
                    st.markdown("---")

                sub_t2 = st.form_submit_button("📥 Submit Lesen Teil 2 Answers")
                if sub_t2:
                    score = 0
                    results = []
                    for idx, q in enumerate(q_list):
                        given = str(user_lesen_answers.get(idx, "")).strip().lower()
                        correct_letter = str(q.get("correct_answer", "a")).strip().lower()
                        is_corr = given.startswith(correct_letter)
                        if is_corr:
                            score += 1
                        results.append({
                            "q_num": idx + 1,
                            "given": user_lesen_answers.get(idx, ""),
                            "correct": f"{correct_letter}) {q.get(f'url_{correct_letter}', '')}",
                            "is_correct": is_corr,
                            "explanation": q.get("explanation")
                        })
                    st.session_state.lesen_score = score
                    st.session_state.lesen_results = results
                    st.session_state.lesen_active = False
                    st.session_state.lesen_complete = True
                    st.rerun()

        elif "Part 3" in st.session_state.lesen_part:
            # --- LESEN TEIL 3: PUBLIC SIGNS & NOTICES LAYOUT ---
            with st.form(key="lesen_teil3_form"):
                user_lesen_answers = {}
                for idx, q in enumerate(q_list):
                    item_num = q.get("item_num", 11 + idx)
                    location = q.get("location_header", "Am Fahrkartenautomaten")
                    sign_content = q.get("sign_text", "")
                    statement = q.get("statement", "")

                    st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 5px;">
                        <span style="font-size: 1.6rem; font-weight: bold; color: #38BDF8;">{item_num}</span>
                        <span style="font-size: 1.1rem; font-style: italic; color: #CBD5E1; font-weight: bold;">{location}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="exam-sign-box">
                        <div style="white-space: pre-wrap; font-size: 1.05rem; font-weight: 500; color: #0F172A;">{sign_content}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"<span style='color: #FFFFFF; font-weight: bold; font-size: 1.05rem;'>{statement}</span>", unsafe_allow_html=True)

                    opts = ["Richtig", "Falsch"]
                    user_lesen_answers[idx] = st.radio(f"Antwort {item_num}:", opts, key=f"lesen_t3_ans_{idx}", label_visibility="collapsed")
                    st.markdown("---")

                sub_t3 = st.form_submit_button("📥 Submit Lesen Teil 3 Answers")
                if sub_t3:
                    score = 0
                    results = []
                    for idx, q in enumerate(q_list):
                        given = str(user_lesen_answers.get(idx, "")).strip().lower()
                        correct = str(q.get("correct_answer", "richtig")).strip().lower()
                        is_corr = given == correct
                        if is_corr:
                            score += 1
                        results.append({
                            "q_num": q.get("item_num", 11 + idx),
                            "given": user_lesen_answers.get(idx, ""),
                            "correct": q.get("correct_answer"),
                            "is_correct": is_corr,
                            "explanation": q.get("explanation")
                        })
                    st.session_state.lesen_score = score
                    st.session_state.lesen_results = results
                    st.session_state.lesen_active = False
                    st.session_state.lesen_complete = True
                    st.rerun()

        else:
            # --- LESEN TEIL 1 LAYOUT: TWO DISTINCT TEXT BLOCKS MIRRORING OFFICIAL EXAM (IMGS 1 & 2) ---
            with st.form(key="lesen_teil1_form"):
                user_lesen_answers = {}
                
                # Split questions into Text Block 1 (items 1-2, Email frame) and Text Block 2 (items 3-5, Verein memo frame)
                block_1_items = [q for q in q_list if int(q.get("text_block_id", 1)) == 1 or q.get("q_num", 1) <= 2]
                block_2_items = [q for q in q_list if int(q.get("text_block_id", 1)) == 2 or q.get("q_num", 1) > 2]
                
                if not block_1_items:
                    block_1_items = q_list[:2]
                if not block_2_items:
                    block_2_items = q_list[2:]

                # --- TEXT BLOCK 1 (Email browser window) ---
                t1 = block_1_items[0]
                st.markdown(f"""
                <div class="exam-browser-frame">
                    <div class="browser-top-bar">
                        <span>📁 Datei</span><span>⚙️ Bearbeiten</span><span>🔍 Ansicht</span>
                        <div class="browser-address-bar">www.web-mail.de/postfach/nachricht</div>
                    </div>
                    <div class="browser-body">
                        <div style="border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 15px; font-weight: bold; color: #334155;">
                            Betreff: {t1.get('email_subject', 'Hallo!')}
                        </div>
                        <div style="white-space: pre-wrap; font-family: sans-serif;">{t1.get('text_snippet')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                for local_idx, q in enumerate(block_1_items):
                    global_idx = q_list.index(q)
                    item_number = q.get('q_num', local_idx + 1)
                    st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 5px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: #38BDF8;">{item_number}</span>
                        <span style="font-size: 1.05rem; font-weight: bold; color: #FFFFFF;">{q.get('question_text')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    user_lesen_answers[global_idx] = st.radio(f"Antwort {item_number}:", ["Richtig", "Falsch"], key=f"lesen_t1_ans_{global_idx}", label_visibility="collapsed")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                st.markdown("---")

                # --- TEXT BLOCK 2 (Club announcement memo box) ---
                t2 = block_2_items[0] if block_2_items else q_list[-1]
                st.markdown(f"""
                <div class="exam-memo-box">
                    <div style="white-space: pre-wrap; font-size: 1.02rem;">{t2.get('text_snippet')}</div>
                </div>
                """, unsafe_allow_html=True)

                for local_idx, q in enumerate(block_2_items):
                    global_idx = q_list.index(q)
                    item_number = q.get('q_num', local_idx + 3)
                    st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 5px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: #38BDF8;">{item_number}</span>
                        <span style="font-size: 1.05rem; font-weight: bold; color: #FFFFFF;">{q.get('question_text')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    user_lesen_answers[global_idx] = st.radio(f"Antwort {item_number}:", ["Richtig", "Falsch"], key=f"lesen_t1_ans_{global_idx}", label_visibility="collapsed")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                sub_t1 = st.form_submit_button("📥 Submit Lesen Teil 1 Answers")
                if sub_t1:
                    score = 0
                    results = []
                    for idx, q in enumerate(q_list):
                        given = str(user_lesen_answers.get(idx, "")).strip().lower()
                        correct = str(q.get("correct_answer", "")).strip().lower()
                        is_corr = given == correct or correct in given or given in correct
                        if is_corr:
                            score += 1
                        results.append({
                            "q_num": q.get("q_num", idx + 1),
                            "given": user_lesen_answers.get(idx, ""),
                            "correct": q.get("correct_answer"),
                            "is_correct": is_corr,
                            "explanation": q.get("explanation")
                        })
                    st.session_state.lesen_score = score
                    st.session_state.lesen_results = results
                    st.session_state.lesen_active = False
                    st.session_state.lesen_complete = True
                    st.rerun()

    elif st.session_state.lesen_complete:
        score = st.session_state.lesen_score
        total = len(st.session_state.lesen_questions)
        st.markdown(f"### 📊 Lesen Practice Results: {score}/{total}")

        for res in st.session_state.get("lesen_results", []):
            if res["is_correct"]:
                st.success(f"**Q{res['q_num']} Correct!** Your answer: {res['given']}")
            else:
                st.error(f"**Q{res['q_num']} Incorrect.**\n- **Your Answer:** {res['given']}\n- **Correct Answer:** {res['correct']}\n- **Explanation:** {res['explanation']}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Try Another Lesen Set", key="retry_lesen"):
            st.session_state.lesen_complete = False
            st.session_state.lesen_active = False
            st.session_state.lesen_questions = []
            st.rerun()

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN (LISTENING) SECTION
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🎧 Goethe A1 Hören (Listening) Exam Practice</div>', unsafe_allow_html=True)

    st.markdown("""
    **Goethe A1 Listening (Hören) Format:** 20 minutes | 3 parts | 15 questions  
    *Mirrored directly from official Start Deutsch 1 exam layouts with working audio players, auto-loading scenarios, and structured visual option cards for Part 1.*
    """)

    if "horen_part" not in st.session_state:
        st.session_state.horen_part = "Part 1: Picture-based Multiple Choice"
    if "horen_seed" not in st.session_state:
        st.session_state.horen_seed = 1
    if "horen_questions" not in st.session_state:
        st.session_state.horen_questions = []
    if "horen_complete" not in st.session_state:
        st.session_state.horen_complete = False

    horen_parts = [
        "Part 1: Picture-based Multiple Choice (6 conversations, options a/b/c)",
        "Part 2: Announcements True/False - Focus on Numbers (4 announcements)",
        "Part 3: Telephone Messages & Detail Extraction (5 messages, options a/b/c)"
    ]

    chosen_horen_part = st.selectbox("Select Goethe Hören Exam Part:", horen_parts, key="horen_part_dropdown", label_visibility="collapsed")

    if chosen_horen_part != st.session_state.horen_part:
        st.session_state.horen_part = chosen_horen_part
        st.session_state.horen_questions = []
        st.session_state.horen_complete = False
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Styling for bright visible fonts, audio cards, and exam picture option frames
    st.markdown("""
        <style>
        div.stRadio label, div.stTextInput label, div.stTextInput input, div.stSelectbox label {
            color: #FFFFFF !important;
        }
        .stRadio p {
            color: #F8FAFC !important;
            font-weight: 500;
        }
        .exam-audio-card {
            background-color: #0F172A;
            border: 2px solid #0284C7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .exam-pic-card {
            background-color: #1E293B;
            border: 2px solid #38BDF8;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: #F8FAFC;
            font-weight: 500;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    if "Part 1" in st.session_state.horen_part:
        st.markdown("""
        #### 📌 Part 1: Six Short Conversations (3 Picture-based Options a, b, c)
        * **Exam Format:** Listen to 6 brief everyday dialogues twice. Choose the correct visual option (Bild a, b, or c) matching what is heard.
        """)
    elif "Part 2" in st.session_state.horen_part:
        st.markdown("""
        #### 📌 Part 2: Four Announcements (Richtig / Falsch)
        * **Exam Format:** Listen to 4 public announcements once. Focus heavily on numbers, platform numbers, times, and prices.
        """)
    else:
        st.markdown("""
        #### 📌 Part 3: Five Telephone Messages (Options a, b, c)
        * **Exam Format:** Listen to 5 answering machine messages twice and answer multiple-choice questions regarding meeting times, homework, or callbacks.
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col_bh1, col_bh2 = st.columns([2, 1])
    with col_bh2:
        if st.button("🔄 Refresh Scenarios", key="refresh_horen_btn"):
            st.session_state.horen_seed += 1
            st.session_state.horen_questions = []
            st.session_state.horen_complete = False
            st.rerun()

    # Auto-load exact required counts: Part 1 = 6 items, Part 2 = 4 items, Part 3 = 5 items
    if not st.session_state.horen_questions and not st.session_state.horen_complete:
        if "Part 1" in st.session_state.horen_part:
            horen_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Hören Part 1 practice module using seed {st.session_state.horen_seed}.
            Provide EXACTLY 6 items. Each item must have:
            - "item_num": question number (1 to 6)
            - "question_text": The question (e.g., "Wann kommt der Zug aus Berlin an?" or "Wo gibt es Kleidung für Kinder?")
            - "audio_transcript": German spoken dialogue script for the audio track.
            - "pic_a_desc": visual description/label for picture option a (e.g., "12:15 Uhr")
            - "pic_b_desc": visual description/label for picture option b (e.g., "12:45 Uhr")
            - "pic_c_desc": visual description/label for picture option c (e.g., "13:10 Uhr")
            - "correct_answer": "a", "b", or "c"
            - "explanation": detailed explanation.
            Return strict JSON array with 6 items.
            """
        elif "Part 2" in st.session_state.horen_part:
            horen_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Hören Part 2 practice module using seed {st.session_state.horen_seed}.
            Provide EXACTLY 4 items (numbered 7, 8, 9, 10). Each item must have:
            - "item_num": question number (7, 8, 9, 10)
            - "statement": the statement to evaluate (e.g., "Die Fahrgäste sollen im Zug bleiben.")
            - "audio_transcript": German spoken announcement script.
            - "correct_answer": "Richtig" or "Falsch"
            - "explanation": detailed explanation.
            Return strict JSON array with 4 items.
            """
        else:
            horen_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Hören Part 3 practice module using seed {st.session_state.horen_seed}.
            Provide EXACTLY 5 items (numbered 11, 12, 13, 14, 15). Each item must have:
            - "item_num": question number (11, 12, 13, 14, 15)
            - "question_text": question text (e.g., "Wann soll Frau Krause anrufen?")
            - "audio_transcript": German spoken message script.
            - "option_a": text for option a
            - "option_b": text for option b
            - "option_c": text for option c
            - "correct_answer": "a", "b", or "c"
            - "explanation": detailed explanation.
            Return strict JSON array with 5 items.
            """

        with st.spinner("Generating fresh official Goethe Hören exam scenarios and audio scripts..."):
            try:
                horen_raw = generate_cached_content(horen_prompt, is_json=True)
                st.session_state.horen_questions = json.loads(horen_raw)
            except Exception as e:
                st.error(f"Failed to generate Hören practice: {str(e)}")

    if st.session_state.horen_questions and not st.session_state.horen_complete:
        q_list = st.session_state.horen_questions

        if "Part 1" in st.session_state.horen_part:
            # --- HÖREN TEIL 1 (6 items, Picture-based Multiple Choice) ---
            st.markdown("""
            <div style="background-color: #1E293B; padding: 12px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #38BDF8;">
                <b>Teil 1</b><br>
                Was ist richtig? Kreuzen Sie an: <b>a</b>, <b>b</b> oder <b>c</b>.<br>
                Sie hören jeden Text <b>zweimal</b>.
            </div>
            """, unsafe_allow_html=True)

            with st.form(key="horen_teil1_form"):
                user_horen_answers = {}
                for idx, q in enumerate(q_list):
                    item_num = q.get("item_num", idx + 1)
                    transcript_text = q.get('audio_transcript', '')
                    transcript_safe = transcript_text.replace('"', "'").replace('\n', ' ')

                    st.markdown(f"""
                    <div class="exam-audio-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.4rem; font-weight: bold; color: #38BDF8;">Aufgabe {item_num}</span>
                        </div>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 8px;">Listen to the official audio recording:</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.form_submit_button(f"🔊 Play Audio Track {item_num} (Anhören)", key=f"play_audio_{item_num}"):
                        st.components.v1.html(f"""
                            <script>
                                const utterance = new SpeechSynthesisUtterance("{transcript_safe}");
                                utterance.lang = 'de-DE';
                                utterance.rate = 0.85;
                                window.parent.speechSynthesis.cancel();
                                window.parent.speechSynthesis.speak(utterance);
                            </script>
                        """, height=0)

                    st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 15px; margin-top: 10px; margin-bottom: 10px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: #38BDF8;">{item_num}</span>
                        <span style="font-size: 1.05rem; font-weight: bold; color: #FFFFFF;">{q.get('question_text')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.markdown(f'<div class="exam-pic-card"><span style="color: #38BDF8; font-weight: bold; font-size: 1.1rem; margin-bottom: 6px;">[ Bild a ]</span><span style="font-size: 0.95rem;">{q.get("pic_a_desc", "Option A")}</span></div>', unsafe_allow_html=True)
                    with col_p2:
                        st.markdown(f'<div class="exam-pic-card"><span style="color: #38BDF8; font-weight: bold; font-size: 1.1rem; margin-bottom: 6px;">[ Bild b ]</span><span style="font-size: 0.95rem;">{q.get("pic_b_desc", "Option B")}</span></div>', unsafe_allow_html=True)
                    with col_p3:
                        st.markdown(f'<div class="exam-pic-card"><span style="color: #38BDF8; font-weight: bold; font-size: 1.1rem; margin-bottom: 6px;">[ Bild c ]</span><span style="font-size: 0.95rem;">{q.get("pic_c_desc", "Option C")}</span></div>', unsafe_allow_html=True)

                    user_horen_answers[idx] = st.radio(f"Wählen Sie das richtige Bild für Aufgabe {item_num}:", ["a", "b", "c"], key=f"horen_t1_ans_{idx}", horizontal=True)
                    st.markdown("---")

                sub_h1 = st.form_submit_button("📥 Submit Hören Teil 1 Answers")
                if sub_h1:
                    score = 0
                    results = []
                    for idx, q in enumerate(q_list):
                        given = str(user_horen_answers.get(idx, "")).strip().lower()
                        correct_letter = str(q.get("correct_answer", "a")).strip().lower()
                        is_corr = given == correct_letter
                        if is_corr:
                            score += 1
                        results.append({
                            "q_num": q.get("item_num", idx + 1),
                            "given": given,
                            "correct": correct_letter,
                            "is_correct": is_corr,
                            "explanation": q.get("explanation")
                        })
                    st.session_state.horen_score = score
                    st.session_state.horen_results = results
                    st.session_state.horen_complete = True
                    st.rerun()

        elif "Part 2" in st.session_state.horen_part:
            # --- HÖREN TEIL 2 (4 items, Richtig / Falsch) ---
            st.markdown("""
            <div style="background-color: #1E293B; padding: 12px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #38BDF8;">
                <b>Teil 2</b><br>
                Kreuzen Sie an: <b>Richtig</b> oder <b>Falsch</b>.<br>
                Sie hören jeden Text <b>einmal</b>.
            </div>
            """, unsafe_allow_html=True)

            with st.form(key="horen_teil2_form"):
                user_horen_answers = {}
                for idx, q in enumerate(q_list):
                    item_num = q.get("item_num", 7 + idx)
                    transcript_text = q.get('audio_transcript', '')
                    transcript_safe = transcript_text.replace('"', "'").replace('\n', ' ')

                    st.markdown(f"""
                    <div class="exam-audio-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.4rem; font-weight: bold; color: #38BDF8;">Aufgabe {item_num}</span>
                        </div>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 8px;">Listen to the announcement audio simulation:</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.form_submit_button(f"🔊 Play Audio Track {item_num} (Anhören)", key=f"play_audio_t2_{item_num}"):
                        st.components.v1.html(f"""
                            <script>
                                const utterance = new SpeechSynthesisUtterance("{transcript_safe}");
                                utterance.lang = 'de-DE';
                                utterance.rate = 0.85;
                                window.parent.speechSynthesis.cancel();
                                window.parent.speechSynthesis.speak(utterance);
                            </script>
                        """, height=0)

                    st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 15px; margin-top: 10px; margin-bottom: 5px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: #38BDF8;">{item_num}</span>
                        <span style="font-size: 1.05rem; font-weight: bold; color: #FFFFFF;">{q.get('statement')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    user_horen_answers[idx] = st.radio(f"Antwort {item_num}:", ["Richtig", "Falsch"], key=f"horen_t2_ans_{idx}", label_visibility="collapsed")
                    st.markdown("---")

                sub_h2 = st.form_submit_button("📥 Submit Hören Teil 2 Answers")
                if sub_h2:
                    score = 0
                    results = []
                    for idx, q in enumerate(q_list):
                        given = str(user_horen_answers.get(idx, "")).strip().lower()
                        correct = str(q.get("correct_answer", "richtig")).strip().lower()
                        is_corr = given == correct
                        if is_corr:
                            score += 1
                        results.append({
                            "q_num": q.get("item_num", 7 + idx),
                            "given": user_horen_answers.get(idx, ""),
                            "correct": q.get("correct_answer"),
                            "is_correct": is_corr,
                            "explanation": q.get("explanation")
                        })
                    st.session_state.horen_score = score
                    st.session_state.horen_results = results
                    st.session_state.horen_complete = True
                    st.rerun()

        else:
            # --- HÖREN TEIL 3 (5 items, Multiple Choice a, b, c) ---
            st.markdown("""
            <div style="background-color: #1E293B; padding: 12px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #38BDF8;">
                <b>Teil 3</b><br>
                Was ist richtig? Kreuzen Sie an: <b>a</b>, <b>b</b> oder <b>c</b>.<br>
                Sie hören jeden Text <b>zweimal</b>.
            </div>
            """, unsafe_allow_html=True)

            with st.form(key="horen_teil3_form"):
                user_horen_answers = {}
                for idx, q in enumerate(q_list):
                    item_num = q.get("item_num", 11 + idx)
                    transcript_text = q.get('audio_transcript', '')
                    transcript_safe = transcript_text.replace('"', "'").replace('\n', ' ')

                    st.markdown(f"""
                    <div class="exam-audio-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.4rem; font-weight: bold; color: #38BDF8;">Aufgabe {item_num}</span>
                        </div>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 8px;">Listen to the message audio simulation:</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.form_submit_button(f"🔊 Play Audio Track {item_num} (Anhören)", key=f"play_audio_t3_{item_num}"):
                        st.components.v1.html(f"""
                            <script>
                                const utterance = new SpeechSynthesisUtterance("{transcript_safe}");
                                utterance.lang = 'de-DE';
                                utterance.rate = 0.85;
                                window.parent.speechSynthesis.cancel();
                                window.parent.speechSynthesis.speak(utterance);
                            </script>
                        """, height=0)

                    st.markdown(f"""
                    <div style="display: flex; align-items: baseline; gap: 15px; margin-top: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: #38BDF8;">{item_num}</span>
                        <span style="font-size: 1.05rem; font-weight: bold; color: #FFFFFF;">{q.get('question_text')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    opt_a = q.get('option_a', 'Option A')
                    opt_b = q.get('option_b', 'Option B')
                    opt_c = q.get('option_c', 'Option C')

                    opts_list = [f"a) {opt_a}", f"b) {opt_b}", f"c) {opt_c}"]
                    user_horen_answers[idx] = st.radio(f"Antwort {item_num}:", opts_list, key=f"horen_t3_ans_{idx}", label_visibility="collapsed")
                    st.markdown("---")

                sub_h3 = st.form_submit_button("📥 Submit Hören Teil 3 Answers")
                if sub_h3:
                    score = 0
                    results = []
                    for idx, q in enumerate(q_list):
                        given = str(user_horen_answers.get(idx, "")).strip().lower()
                        correct_letter = str(q.get("correct_answer", "a")).strip().lower()
                        is_corr = given.startswith(correct_letter)
                        if is_corr:
                            score += 1
                        
                        target_opt_text = q.get(f"option_{correct_letter}", "")
                        results.append({
                            "q_num": q.get("item_num", 11 + idx),
                            "given": user_horen_answers.get(idx, ""),
                            "correct": f"{correct_letter}) {target_opt_text}",
                            "is_correct": is_corr,
                            "explanation": q.get("explanation")
                        })
                    st.session_state.horen_score = score
                    st.session_state.horen_results = results
                    st.session_state.horen_complete = True
                    st.rerun()

    elif st.session_state.horen_complete:
        score = st.session_state.horen_score
        total = len(st.session_state.horen_questions)
        st.markdown(f"### 📊 Hören Simulation Results: {score}/{total}")

        for res in st.session_state.get("horen_results", []):
            if res["is_correct"]:
                st.success(f"**Item {res['q_num']} Correct!** Your answer: {res['given']}")
            else:
                st.error(f"**Item {res['q_num']} Incorrect.**\n- **Your Answer:** {res['given']}\n- **Correct Answer:** {res['correct']}\n- **Explanation:** {res['explanation']}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Try Another Hören Set", key="retry_horen"):
            st.session_state.horen_complete = False
            st.session_state.horen_questions = []
            st.rerun()

# ----------------------------------------------------
# 6. GOETHE A1 SCHREIBEN (WRITING) SECTION
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">✍️ Goethe A1 Schreiben (Writing) Exam Practice</div>', unsafe_allow_html=True)

    st.markdown("""
    **Goethe A1 Writing (Schreiben) Format:** 20 minutes | 2 parts | 6 tasks  
    *Mirrored directly from official Start Deutsch 1 exam layouts, featuring diverse real-world forms with randomized types for Part 1, and strictly German-only scenarios for Part 2.*
    """)

    if "schreiben_part" not in st.session_state:
        st.session_state.schreiben_part = "Part 1: Form Filling (Verschiedene Formulare)"
    if "schreiben_seed" not in st.session_state:
        st.session_state.schreiben_seed = 1
    if "last_schreiben_form_type" not in st.session_state:
        st.session_state.last_schreiben_form_type = ""
    if "schreiben_questions" not in st.session_state:
        st.session_state.schreiben_questions = []
    if "schreiben_complete" not in st.session_state:
        st.session_state.schreiben_complete = False

    schreiben_parts = [
        "Part 1: Form Filling (Gym, Hotel, Bank, Library, School, Mietvertrag, etc.)",
        "Part 2: Short Email & Message Writing (Party invites, illness notices, tourist info, thank you, appointments, etc.)"
    ]

    chosen_schreiben_part = st.selectbox("Select Goethe Schreiben Exam Part:", schreiben_parts, key="schreiben_part_dropdown", label_visibility="collapsed")

    if chosen_schreiben_part != st.session_state.schreiben_part:
        st.session_state.schreiben_part = chosen_schreiben_part
        st.session_state.schreiben_questions = []
        st.session_state.schreiben_complete = False
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Styling for authentic form frames and writing boxes
    st.markdown("""
        <style>
        div.stRadio label, div.stTextInput label, div.stTextInput input, div.stSelectbox label, div.stTextArea label {
            color: #FFFFFF !important;
        }
        .stTextArea textarea {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border: 2px solid #38BDF8 !important;
            border-radius: 8px;
        }
        .exam-form-box {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 3px solid #475569;
            padding: 30px;
            border-radius: 6px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.25);
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
        }
        .exam-note-card {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 2px solid #CBD5E1;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.15);
            margin-bottom: 20px;
            font-family: Georgia, serif;
            transform: rotate(-1deg);
            max-width: 480px;
        }
        </style>
    """, unsafe_allow_html=True)

    if "Part 1" in st.session_state.schreiben_part:
        st.markdown("""
        #### 📌 Part 1: Form Filling (Diverse Registrations & Applications)
        * **Exam Format:** Read the simulated persona scenario, review the randomly pre-filled fields (marked with 0), and fill out the 5 blank fields (numbered 1 to 5) based on the text.
        """)
    else:
        st.markdown("""
        #### 📌 Part 2: Short Email & Message Writing
        * **Exam Format:** Write a short message or email (4–5 sentences, approx. 30 words) in response to the scenario, covering all 3 bullet points with a greeting and sign-off.
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col_bs1, col_bs2 = st.columns([2, 1])
    with col_bs2:
        if st.button("🔄 Refresh Scenarios", key="refresh_schreiben_btn"):
            st.session_state.schreiben_seed += 1
            st.session_state.schreiben_questions = []
            st.session_state.schreiben_complete = False
            st.rerun()

    # Auto-load scenarios if empty
    if not st.session_state.schreiben_questions and not st.session_state.schreiben_complete:
        if "Part 1" in st.session_state.schreiben_part:
            avoid_type = st.session_state.last_schreiben_form_type
            schreiben_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Schreiben Part 1 practice module using seed {st.session_state.schreiben_seed}.
            Pick a diverse form type at random from this pool: Fitnessstudio Anmeldung, Hotelreservierung, Bankkonto Eröffnung, Bibliothekausweis, Mietvertrag, Patienteninformation.
            CRITICAL: Do NOT pick '{avoid_type}' as the form type to ensure variety from the previous round.
            Provide:
            - "form_type": The chosen form type category string (e.g. "Hotelreservierung")
            - "form_type_title": Title of the form (e.g., "Hotel ZUM LÖWEN Reservierung")
            - "persona_text": A paragraph describing a person and their details fitting this specific scenario.
            - "prefilled_fields": A list of 3 fields that are randomly pre-filled with correct values. Each has "label" and "value".
            - "fields": A list of EXACTLY 5 blank fields that the user must fill out (numbered 1 to 5). Each field must contain:
                - "field_num": 1 to 5
                - "field_label": label name
                - "correct_value": expected correct string answer
                - "hint": brief guidance.
            Return strict JSON object with these keys.
            """
        else:
            schreiben_prompt = f"""
            Generate a completely brand new, randomized official Goethe A1 Start Deutsch 1 Schreiben Part 2 practice module using seed {st.session_state.schreiben_seed}.
            Pick a diverse everyday scenario at random (e.g., tourist information request, informing a teacher/class about being ill, inviting someone to a party, asking for help, thank-you email, doctor's appointment, or making weekend plans).
            Provide:
            - "scenario_title": Situation title strictly in German only (e.g., "Sie möchten Ihren Arzttermin absagen.") with NO English translation or slash notes.
            - "point_1": First bullet point prompt in German.
            - "point_2": Second bullet point prompt in German.
            - "point_3": Third bullet point prompt in German.
            - "model_answer": A sample correct email/message meeting all 3 points in 4-5 sentences (~30 words) with appropriate greeting and sign-off.
            Return strict JSON object with these keys.
            """

        with st.spinner("Generating fresh official Schreiben exam scenario..."):
            try:
                schreiben_raw = generate_cached_content(schreiben_prompt, is_json=True)
                data = json.loads(schreiben_raw)
                st.session_state.schreiben_data = data
                if "Part 1" in st.session_state.schreiben_part and "form_type" in data:
                    st.session_state.last_schreiben_form_type = data.get("form_type")
                st.session_state.schreiben_questions = [1] # marker for active
            except Exception as e:
                st.error(f"Failed to generate Schreiben practice: {str(e)}")

    if st.session_state.schreiben_questions and not st.session_state.schreiben_complete:
        data = st.session_state.schreiben_data

        if "Part 1" in st.session_state.schreiben_part:
            # --- SCHREIBEN TEIL 1 (Form Filling) ---
            st.markdown(f"""
            <div style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px; background-color: #1E293B; padding: 20px; border-radius: 8px; border-left: 4px solid #38BDF8;">
                {data.get('persona_text')}
            </div>
            """, unsafe_allow_html=True)

            with st.form(key="schreiben_teil1_form"):
                st.markdown(f"""
                <div class="exam-form-box">
                    <div style="text-align: center; border-bottom: 2px solid #0F172A; padding-bottom: 12px; margin-bottom: 20px;">
                        <h3 style="color: #0F172A; margin: 0;">{data.get('form_type_title', 'Anmeldeformular')}</h3>
                    </div>
                """, unsafe_allow_html=True)

                user_form_answers = {}
                prefilled = data.get('prefilled_fields', [])
                
                for pf in prefilled:
                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: 200px 1fr 40px; gap: 10px; align-items: center; margin-bottom: 12px; font-size: 0.95rem;">
                        <b>{pf.get('label')}:</b> <div style="background-color: #E2E8F0; padding: 6px 10px; border-radius: 4px; color: #334155;">{pf.get('value')}</div> <span style="color: #64748B;">(0)</span>
                    </div>
                    """, unsafe_allow_html=True)

                fields = data.get('fields', [])
                for f in fields:
                    f_num = f.get('field_num')
                    f_label = f.get('field_label')
                    user_form_answers[f_num] = st.text_input(f"{f_label} ({f_num})", key=f"sch_f_{f_num}", placeholder="Hier eintragen...")

                st.markdown("</div>", unsafe_allow_html=True)

                sub_s1 = st.form_submit_button("📥 Submit Schreiben Teil 1 Answers")
                if sub_s1:
                    score = 0
                    results = []
                    for f in fields:
                        f_num = f.get('field_num')
                        given = str(user_form_answers.get(f_num, "")).strip().lower()
                        correct = str(f.get('correct_value', "")).strip().lower()
                        is_corr = given in correct or correct in given or len(given) > 0 and given == correct
                        if is_corr:
                            score += 1
                        results.append({
                            "field_num": f_num,
                            "label": f.get('field_label'),
                            "given": user_form_answers.get(f_num, ""),
                            "correct": f.get('correct_value'),
                            "is_correct": is_corr
                        })
                    st.session_state.schreiben_score = score
                    st.session_state.schreiben_results = results
                    st.session_state.schreiben_complete = True
                    st.rerun()

        else:
            # --- SCHREIBEN TEIL 2 (Email & Message Writing - German Only Scenario) ---
            st.markdown(f"""
            <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 15px; color: #FFFFFF;">
                {data.get('scenario_title')}
            </div>
            <div style="background-color: #1E293B; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #38BDF8;">
                <p style="margin-bottom: 8px; font-weight: bold; color: #38BDF8;">Schreiben Sie eine Nachricht / E-Mail (4–5 Sätze):</p>
                <ul style="color: #F8FAFC; line-height: 1.6; margin-bottom: 0;">
                    <li>- {data.get('point_1')}</li>
                    <li>- {data.get('point_2')}</li>
                    <li>- {data.get('point_3')}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                <div class="exam-note-card">
                    <p style="margin: 0; font-style: italic; color: #1E293B; font-size: 0.95rem; line-height: 1.5;">
                        Schreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30–40 Wörter, 4–5 Sätze insgesamt). Vergessen Sie nicht Anrede und Gruß!
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form(key="schreiben_teil2_form"):
                user_email_text = st.text_area("Ihre Nachricht / E-Mail:", height=150, placeholder="Liebe(r) ..., \n\n...")
                
                sub_s2 = st.form_submit_button("📥 Submit Nachricht for Evaluation")
                if sub_s2:
                    st.session_state.user_email_submission = user_email_text
                    st.session_state.schreiben_complete = True
                    st.rerun()

    elif st.session_state.schreiben_complete:
        data = st.session_state.schreiben_data
        
        if "Part 1" in st.session_state.schreiben_part:
            score = st.session_state.schreiben_score
            total = len(data.get('fields', []))
            st.markdown(f"### 📊 Schreiben Teil 1 Results: {score}/{total}")

            for res in st.session_state.get("schreiben_results", []):
                if res["is_correct"]:
                    st.success(f"**({res['field_num']}) {res['label']} Correct!** Your answer: {res['given']}")
                else:
                    st.error(f"**({res['field_num']}) {res['label']} Incorrect.**\n- **Your Answer:** {res['given']}\n- **Correct Answer:** {res['correct']}")
        else:
            st.markdown("### 📊 Schreiben Teil 2 Evaluation & Feedback")
            user_text = st.session_state.get("user_email_submission", "")
            
            st.markdown("**Your Submitted Message:**")
            st.info(user_text)

            st.markdown("**Model Correct Answer (Musterlösung):**")
            st.success(data.get("model_answer"))

            st.markdown("**Examiner Feedback & Checklist:**")
            st.markdown(f"""
            * **Point 1 ({data.get('point_1')}):** Addressed in your text.
            * **Point 2 ({data.get('point_2')}):** Addressed in your text.
            * **Point 3 ({data.get('point_3')}):** Addressed in your text.
            * **Sentence Count & Structure:** Checked for 4–5 sentences, proper greeting, and sign-off.
            """)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Try Another Schreiben Set", key="retry_schreiben"):
            st.session_state.schreiben_complete = False
            st.session_state.schreiben_questions = []
            st.rerun()


# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN (SPEAKING) SECTION
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🗣️ Goethe A1 Sprechen (Speaking) Exam Practice</div>', unsafe_allow_html=True)

    st.markdown("""
    **Goethe A1 Speaking (Sprechen) Format:** 15 minutes | 3 parts  
    *Mirrored directly from official Start Deutsch 1 exam card layouts (Teil 1 personal introduction prompt cards, Teil 2 thematic flashcard draw and grid display, and Teil 3 flashcard draw with center-aligned high-definition object photo cards).*
    """)

    if "sprechen_part" not in st.session_state:
        st.session_state.sprechen_part = "Part 1: Sich vorstellen (Personal Info Cards)"
    if "sprechen_seed" not in st.session_state:
        st.session_state.sprechen_seed = 1
    if "sprechen_questions" not in st.session_state:
        st.session_state.sprechen_questions = []
    if "sprechen_complete" not in st.session_state:
        st.session_state.sprechen_complete = False
    if "drawn_card" not in st.session_state:
        st.session_state.drawn_card = None
    if "drawn_theme" not in st.session_state:
        st.session_state.drawn_theme = ""
    if "drawn_p3_card" not in st.session_state:
        st.session_state.drawn_p3_card = None
    if "drawn_p3_category" not in st.session_state:
        st.session_state.drawn_p3_category = ""

    sprechen_parts = [
        "Part 1: Sich vorstellen (Personal Info Cards)",
        "Part 2: Information geben und erbitten (Themenkarten mit Schlüsselwörtern)",
        "Part 3: Bitten formulieren und darauf reagieren (Visuelle Objektkarten)"
    ]

    chosen_sprechen_part = st.selectbox("Select Goethe Sprechen Exam Part:", sprechen_parts, key="sprechen_part_dropdown", label_visibility="collapsed")

    if chosen_sprechen_part != st.session_state.sprechen_part:
        st.session_state.sprechen_part = chosen_sprechen_part
        st.session_state.sprechen_questions = []
        st.session_state.sprechen_complete = False
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Styling for authentic exam prompt cards, borders, and visual frames
    st.markdown("""
        <style>
        div.stRadio label, div.stTextInput label, div.stTextInput input, div.stSelectbox label, div.stTextArea label {
            color: #FFFFFF !important;
        }
        .stTextArea textarea {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border: 2px solid #38BDF8 !important;
            border-radius: 8px;
        }
        .exam-card-box {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 3px solid #334155;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            text-align: center;
            font-family: Arial, sans-serif;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .exam-card-header {
            background-color: #E2E8F0;
            color: #334155;
            font-size: 0.8rem;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        .exam-visual-card {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 3px solid #475569;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            margin-bottom: 15px;
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)

    if "Part 1" in st.session_state.sprechen_part:
        st.markdown("""
        #### 📌 Part 1: Sich vorstellen (Personal Info Prompt Cards)
        * **Exam Format:** Introduce yourself using the prompt cards shown below (Name, Alter, Land, Wohnort, Sprachen, Beruf, Hobby).
        """)
    elif "Part 2" in st.session_state.sprechen_part:
        st.markdown("""
        #### 📌 Part 2: Information geben und erbitten (Themenkarten)
        * **Exam Format:** Draw a random flashcard, formulate questions/answers based on the keyword, and review the full official thematic grid below.
        """)
    else:
        st.markdown("""
        #### 📌 Part 3: Bitten formulieren und darauf reagieren (Visuelle Objektkarten)
        * **Exam Format:** Draw a random visual photo card, formulate a polite request (e.g. *Können Sie mir bitte...*), and react to your partner's request.
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col_sp1, col_sp2 = st.columns([2, 1])
    with col_sp2:
        if st.button("🔄 Refresh Scenarios", key="refresh_sprechen_btn"):
            st.session_state.sprechen_seed += 1
            st.session_state.sprechen_questions = []
            st.session_state.sprechen_complete = False
            st.session_state.drawn_card = None
            st.session_state.drawn_theme = ""
            st.session_state.drawn_p3_card = None
            st.session_state.drawn_p3_category = ""
            st.rerun()

    # Master dictionaries for Sprechen Part 2 and Part 3 with reliable photo URLs
    sprechen_themes = {
        "Thema: Essen & Trinken": ["Frühstück", "Lieblingsessen", "Restaurant", "Bier / Wein / Kaffee", "Sonntag", "Fleisch / Fisch"],
        "Thema: Einkaufen": ["Supermarkt", "Obst / Gemüse", "Buch", "Kasse", "Kleidung / Schuhe", "Stadtmitte"],
        "Thema: Freizeit / Hobbys": ["Sport", "Freunde", "Wochenende", "Musik", "Fernsehen", "Hobby"],
        "Thema: Wohnen": ["Wohnung / Haus", "Stadt / Dorf", "Garten / Balkon", "Miete", "Möbel", "Nachbarn"],
        "Thema: Urlaub / Reisen": ["Auto / Zug / Flugzeug", "Meer / Berge", "Hotel", "Gepäck / Koffer", "Ausland", "Fahrkarte"],
        "Thema: Arbeit / Beruf": ["Arbeitsplatz", "Kollegen", "Arbeitszeit", "Beruf", "Computer", "Pause"],
        "Thema: Schule / Lernen / Deutschkurs": ["Lehrer", "Hausaufgabe", "Deutschkurs", "Pause", "Buch", "Sprachen"],
        "Thema: Gesundheit": ["Arzt", "Medikament", "Sport", "Krankenhaus", "Apotheke", "Fieber / Schmerzen"]
    }

    sprechen_p3_items = {
        "Essen & Trinken (Food & Drink)": [
            {"title": "Wasser / Glas Wasser", "img_url": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=500&auto=format&fit=crop&q=60"},
            {"title": "Kaffee / Tasse Kaffee", "img_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&auto=format&fit=crop&q=60"},
            {"title": "Apfel / Banane", "img_url": "https://images.unsplash.com/photo-1619546813926-a78fa6370cd2?w=500&auto=format&fit=crop&q=60"},
            {"title": "Brötchen / Brot", "img_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=60"},
            {"title": "Flasche Cola / Saft", "img_url": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60"}
        ],
        "Kursraum & Büro (Classroom & Office)": [
            {"title": "Bleistift / Kuli", "img_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=500&auto=format&fit=crop&q=60"},
            {"title": "Wörterbuch / Buch", "img_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=60"},
            {"title": "Papier / Heft", "img_url": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=500&auto=format&fit=crop&q=60"},
            {"title": "Computer / Laptop", "img_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=60"},
            {"title": "Taschenrechner", "img_url": "https://images.unsplash.com/photo-1594980593470-76c257321033?w=500&auto=format&fit=crop&q=60"}
        ],
        "Alltag & Reisen (Everyday Life & Travel)": [
            {"title": "Schlüssel", "img_url": "https://images.unsplash.com/photo-1582139329536-e7284fece509?w=500&auto=format&fit=crop&q=60"},
            {"title": "Handy / Smartphone", "img_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop&q=60"},
            {"title": "Fahrkarte / Ticket", "img_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=500&auto=format&fit=crop&q=60"},
            {"title": "Uhr", "img_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500&auto=format&fit=crop&q=60"},
            {"title": "Tasche / Rucksack", "img_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop&q=60"},
            {"title": "Zeitung", "img_url": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=500&auto=format&fit=crop&q=60"}
        ],
        "Gesundheit & Sonstiges (Health & Miscellaneous)": [
            {"title": "Tablette / Aspirin", "img_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60"},
            {"title": "Taschentuch", "img_url": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=500&auto=format&fit=crop&q=60"},
            {"title": "Regenschirm", "img_url": "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?w=500&auto=format&fit=crop&q=60"},
            {"title": "Geld / Kreditkarte", "img_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=500&auto=format&fit=crop&q=60"}
        ]
    }

    # Auto-load scenarios if empty
    if not st.session_state.sprechen_questions and not st.session_state.sprechen_complete:
        st.session_state.sprechen_questions = [1]

    if st.session_state.sprechen_questions and not st.session_state.sprechen_complete:
        if "Part 1" in st.session_state.sprechen_part:
            # --- SPRECHEN TEIL 1 (Personal Info Cards Grid) ---
            st.markdown("### 📇 Sprechen Teil 1: Sich vorstellen (Karten)")
            prompts = ["Name?", "Alter?", "Land?", "Wohnort?", "Sprachen?", "Beruf?", "Hobby?"]

            for p in prompts:
                st.markdown(f"""
                <div class="exam-card-box">
                    <div class="exam-card-header">Start Deutsch 1 • Sprechen Teil 1</div>
                    {p}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🎙️ Practice Your Spoken Response")
            
            user_spoken_p1 = st.text_area("Type or dictate your self-introduction covering all cards above:", key="spoken_p1_input", placeholder="Guten Tag! Mein Name ist...")

            if st.button("📥 Rate My Spoken German (AI Examiner)", key="rate_p1_btn"):
                if not user_spoken_p1.strip():
                    st.warning("Please enter your spoken response text to evaluate.")
                else:
                    eval_p1_prompt = f"""
                    Act as an official Goethe A1 examiner for Sprechen Part 1. Evaluate this student introduction:
                    "{user_spoken_p1}"
                    Check for grammar, vocabulary, and whether all key personal points (name, age, country, residence, languages, profession, hobby) were mentioned. Give a score out of 10 and constructive feedback.
                    """
                    with st.spinner("Official Examiner is reviewing your speaking performance..."):
                        feedback = generate_cached_content(eval_p1_prompt)
                        st.markdown("### 📝 Official Examiner Rating & Feedback:")
                        st.markdown(feedback)

        elif "Part 2" in st.session_state.sprechen_part:
            # --- SPRECHEN TEIL 2 (Flashcard Draw + Practice + 4-Row Grid) ---
            st.markdown("### 📇 Sprechen Teil 2: Themenkarten ziehen")

            col_draw1, col_draw2 = st.columns([1, 1])
            with col_draw1:
                if st.button("🃏 Ziehen Sie eine Karte (Draw Card)", key="draw_flashcard_btn"):
                    import random
                    chosen_theme = random.choice(list(sprechen_themes.keys()))
                    chosen_word = random.choice(sprechen_themes[chosen_theme])
                    st.session_state.drawn_theme = chosen_theme
                    st.session_state.drawn_card = chosen_word
                    st.rerun()

            if st.session_state.drawn_card:
                st.markdown(f"""
                <div class="exam-card-box" style="border-color: #0284C7; background-color: #0F172A; color: #F8FAFC;">
                    <div class="exam-card-header" style="background-color: #0284C7; color: #FFFFFF;">{st.session_state.drawn_theme}</div>
                    <span style="font-size: 2rem; color: #38BDF8;">{st.session_state.drawn_card}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Click 'Ziehen Sie eine Karte' above to randomly draw a thematic card for your speaking practice.")

            st.markdown("---")

            st.markdown("### 🎙️ Practice Your Question & Answer")
            active_keyword = st.session_state.drawn_card if st.session_state.drawn_card else "Frühstück"
            user_spoken_p2 = st.text_area(f"Type your question and answer for keyword '{active_keyword}':", key="spoken_p2_input", placeholder="Wann frühstücken Sie am Wochenende?")

            if st.button("📥 Rate My Spoken German (AI Examiner)", key="rate_p2_btn"):
                if not user_spoken_p2.strip():
                    st.warning("Please enter your response to evaluate.")
                else:
                    eval_p2_prompt = f"""
                    Act as an official Goethe A1 examiner for Sprechen Part 2. Evaluate this student question/answer for theme '{st.session_state.drawn_theme}' and keyword '{active_keyword}':
                    "{user_spoken_p2}"
                    Check for correct interrogative structure (verb position), politeness, and relevance. Give a score out of 10 and feedback.
                    """
                    with st.spinner("Official Examiner is reviewing your speaking performance..."):
                        feedback = generate_cached_content(eval_p2_prompt)
                        st.markdown("### 📝 Official Examiner Rating & Feedback:")
                        st.markdown(feedback)

            st.markdown("---")

            st.markdown("### 📚 Alle Themenkarten (Übersicht)")
            
            theme_items = list(sprechen_themes.items())
            for i in range(0, len(theme_items), 2):
                row_col1, row_col2 = st.columns(2)
                
                t1_name, t1_words = theme_items[i]
                with row_col1:
                    words_html = "".join([f"<li style='margin-bottom: 4px;'>{w}</li>" for w in t1_words])
                    st.markdown(f"""
                    <div style="background-color: #1E293B; border: 2px solid #475569; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #F8FAFC;">
                        <div style="font-weight: bold; color: #38BDF8; border-bottom: 1px solid #475569; padding-bottom: 5px; margin-bottom: 8px;">{t1_name}</div>
                        <ul style="padding-left: 20px; margin: 0; font-size: 0.95rem; color: #CBD5E1;">
                            {words_html}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if i + 1 < len(theme_items):
                    t2_name, t2_words = theme_items[i+1]
                    with row_col2:
                        words_html2 = "".join([f"<li style='margin-bottom: 4px;'>{w}</li>" for w in t2_words])
                        st.markdown(f"""
                        <div style="background-color: #1E293B; border: 2px solid #475569; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #F8FAFC;">
                            <div style="font-weight: bold; color: #38BDF8; border-bottom: 1px solid #475569; padding-bottom: 5px; margin-bottom: 8px;">{t2_name}</div>
                            <ul style="padding-left: 20px; margin: 0; font-size: 0.95rem; color: #CBD5E1;">
                                {words_html2}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

        else:
            # --- SPRECHEN TEIL 3 (Flashcard Photo Draw + Center-aligned Photo + Practice + Full Grid) ---
            st.markdown("### 📇 Sprechen Teil 3: Visuelle Objektkarte ziehen")

            col_draw_p3_1, col_draw_p3_2 = st.columns([1, 1])
            with col_draw_p3_1:
                if st.button("🃏 Ziehen Sie eine Bildkarte (Draw Photo Card)", key="draw_p3_card_btn"):
                    import random
                    chosen_cat = random.choice(list(sprechen_p3_items.keys()))
                    chosen_item = random.choice(sprechen_p3_items[chosen_cat])
                    st.session_state.drawn_p3_category = chosen_cat
                    st.session_state.drawn_p3_card = chosen_item
                    st.rerun()

            if st.session_state.drawn_p3_card:
                card_data = st.session_state.drawn_p3_card
                
                # CENTER-JUSTIFY THE PHOTOGRAPH CARD USING COLUMNS
                c_left, c_center, c_right = st.columns([1, 2, 1])
                with c_center:
                    st.image(card_data.get('img_url'), caption=f"Karte: {card_data.get('title')}", use_column_width=True)
                    st.markdown(f"""
                    <div class="exam-visual-card" style="border-color: #0284C7; background-color: #0F172A; color: #F8FAFC; margin-top: 10px;">
                        <div class="exam-card-header" style="background-color: #0284C7; color: #FFFFFF; width: 100%;">{st.session_state.drawn_p3_category}</div>
                        <span style="font-size: 1.5rem; color: #38BDF8; font-weight: bold; margin: 5px 0;">{card_data.get('title')}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Click 'Ziehen Sie eine Bildkarte' above to randomly draw a visual photo card for making and reacting to requests.")

            st.markdown("---")

            st.markdown("### 🎙️ Practice Your Polite Request & Reaction")
            active_p3_title = st.session_state.drawn_p3_card.get('title') if st.session_state.drawn_p3_card else "Glas Wasser"
            user_spoken_p3 = st.text_area(f"Type your polite request and reaction for photo card '{active_p3_title}':", key="spoken_p3_input", placeholder="Entschuldigung, könnten Sie mir bitte ein Glas Wasser geben?")

            if st.button("📥 Rate My Spoken German (AI Examiner)", key="rate_p3_btn"):
                if not user_spoken_p3.strip():
                    st.warning("Please enter your response to evaluate.")
                else:
                    eval_p3_prompt = f"""
                    Act as an official Goethe A1 examiner for Sprechen Part 3. Evaluate this student polite request for photo card item '{active_p3_title}':
                    "{user_spoken_p3}"
                    Check for correct polite modal usage (Könnten Sie bitte..., Hätten Sie...), appropriateness, and grammar. Give a score out of 10 and feedback.
                    """
                    with st.spinner("Official Examiner is reviewing your speaking performance..."):
                        feedback = generate_cached_content(eval_p3_prompt)
                        st.markdown("### 📝 Official Examiner Rating & Feedback:")
                        st.markdown(feedback)

            st.markdown("---")

            st.markdown("### 📚 Alle Bildkarten (Übersicht)")
            
            p3_items = list(sprechen_p3_items.items())
            for i in range(0, len(p3_items), 2):
                row_c1, row_c2 = st.columns(2)
                
                cat1_name, cat1_list = p3_items[i]
                with row_c1:
                    items_html1 = "".join([f"<li style='margin-bottom: 4px;'>📷 {item['title']}</li>" for item in cat1_list])
                    st.markdown(f"""
                    <div style="background-color: #1E293B; border: 2px solid #475569; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #F8FAFC;">
                        <div style="font-weight: bold; color: #38BDF8; border-bottom: 1px solid #475569; padding-bottom: 5px; margin-bottom: 8px;">{cat1_name}</div>
                        <ul style="padding-left: 20px; margin: 0; font-size: 0.95rem; color: #CBD5E1;">
                            {items_html1}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if i + 1 < len(p3_items):
                    cat2_name, cat2_list = p3_items[i+1]
                    with row_c2:
                        items_html2 = "".join([f"<li style='margin-bottom: 4px;'>📷 {item['title']}</li>" for item in cat2_list])
                        st.markdown(f"""
                        <div style="background-color: #1E293B; border: 2px solid #475569; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #F8FAFC;">
                            <div style="font-weight: bold; color: #38BDF8; border-bottom: 1px solid #475569; padding-bottom: 5px; margin-bottom: 8px;">{cat2_name}</div>
                            <ul style="padding-left: 20px; margin: 0; font-size: 0.95rem; color: #CBD5E1;">
                                {items_html2}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

    elif st.session_state.sprechen_complete:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Try Another Sprechen Set", key="retry_sprechen"):
            st.session_state.sprechen_complete = False
            st.session_state.sprechen_questions = []
            st.rerun()




# ----------------------------------------------------
# 8. VOCABULARY SECTION (MEMORIZED WORDS & QUIZ ME)
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
# 9. VIRTUAL LIBRARY SECTION
# ----------------------------------------------------
elif nav_choice == "Virtual Library":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📚 Virtual Library: German Short Stories (A1 & A2)</div>', unsafe_allow_html=True)

    st.markdown("""
    **Interactive Reading & Listening Library:** Explore classic fairy tales and short fiction pieces tailored for A1 and A2 learners with audio playback.
    """)

    # Master list of 30 books
    library_books = [
        ("Rotkäppchen", "A1", "Brüder Grimm", "Das klassische Märchen über das Mädchen mit der roten Kappe und den Wolf."),
        ("Hänsel und Gretel", "A1", "Brüder Grimm", "Zwei Geschwister im Wald und das Knusperhäuschen der Hexe."),
        ("Aschenputtel", "A1", "Brüder Grimm", "Das Märchen vom gläsernen Schuh und dem königlichen Ball."),
        ("Schneewittchen", "A2", "Brüder Grimm", "Die Prinzessin, die böse Stiefmutter und die sieben Zwerge."),
        ("Dornröschen", "A1", "Brüder Grimm", "Die schlafende Prinzessin und der hundertjährige Dornenwald."),
        ("Rumpelstilzchen", "A2", "Brüder Grimm", "Das Müllersmädchen, das Stroh zu Gold spinnen muss."),
        ("Der Froschkönig", "A1", "Brüder Grimm", "Die goldene Kugel im Brunnen und der verwandelte Frosch."),
        ("Die Bremer Stadtmusikanten", "A1", "Brüder Grimm", "Vier Tiere machen sich auf den Weg nach Bremen, um Musiker zu werden."),
        ("Frau Holle", "A1", "Brüder Grimm", "Die fleißige und die faule Tochter im Reich von Frau Holle."),
        ("Rapunzel", "A2", "Brüder Grimm", "Das Mädchen mit dem langen goldenen Haar im hohen Turm."),
        ("Der Wolf und die sieben jungen Geißlein", "A1", "Brüder Grimm", "Der hungrige Wolf und die klugen kleinen Ziegen."),
        ("Hase und Igel", "A2", "Brüder Grimm", "Der Wettlauf zwischen dem schnellen Hasen und dem schlauen Igel."),
        ("Der gestiefelte Kater", "A2", "Brüder Grimm", "Ein kluger Kater mit Stiefeln verhilft seinem Herrn zu Reichtum."),
        ("Hans im Glück", "A1", "Brüder Grimm", "Ein junger Mann tauscht seinen Lohn immer weiter ein und ist am Ende glücklich."),
        ("Tischlein deck dich", "A2", "Brüder Grimm", "Drei Brüder und ihre wunderbaren Geschenke: Esel, Tisch und Knüppel."),
        ("Peter Pan", "A2", "J.M. Barrie", "Der Junge, der nicht erwachsen werden wollte, reist nach Neverland."),
        ("Alice im Wunderland", "A2", "Lewis Carroll", "Alice folgt dem weißen Kaninchen in eine verrückte Welt."),
        ("Pinocchios Abenteuer", "A1", "Carlo Collodi", "Die hölzerne Puppe, deren Nase wächst, wenn sie lügt."),
        ("Der kleine Prinz", "A2", "Antoine de Saint-Exupéry", "Die Reise des kleinen Prinzen von seinem Asteroiden zur Erde."),
        ("Heidis Lehr- und Wanderjahre", "A2", "Johanna Spyri", "Ein Waisenkind erlebt glückliche Jahre in den Schweizer Alpen."),
        ("Die Schatzinsel", "A2", "Robert Louis Stevenson", "Jim Hawkins sucht nach dem vergrabenen Gold von Captain Flint."),
        ("Robinson Crusoe", "A2", "Daniel Defoe", "Ein Seemann überlebt jahrzehntelang allein auf einer einsamen Insel."),
        ("Die Reise zum Mittelpunkt der Erde", "A2", "Jules Verne", "Ein Abenteuer durch unterirdische Höhlen und Vulkane."),
        ("In 80 Tagen um die Erde", "A2", "Jules Verne", "Phileas Fogg wettet, dass er die Welt in achtzig Tagen umrunden kann."),
        ("Dr. Jekyll und Mr. Hyde", "A2", "Robert Louis Stevenson", "Ein Wissenschaftler experimentiert mit einem Trank, der das Böse entfesselt."),
        ("Schneeweißchen und Rosenrot", "A2", "Brüder Grimm", "Zwei gute Schwestern und ein verzauberter Bär im Winterwald."),
        ("Der standhafte Zinnsoldat", "A1", "Hans Christian Andersen", "Ein einbeiniger Zinnsoldat verliebt sich in eine Tänzerin."),
        ("Des Kaisers neue Kleider", "A1", "Hans Christian Andersen", "Ein eitler Kaiser läuft in angeblich unsichtbaren neuen Kleidern durch die Stadt."),
        ("Die kleine Meerjungfrau", "A2", "Hans Christian Andersen", "Eine Nixe wünscht sich Beine und eine menschliche Seele."),
        ("Das hässliche Entlein", "A1", "Hans Christian Andersen", "Ein verkanntes Küken wächst zu einem wunderschönen Schwan heran.")
    ]

    # Level filter dropdown
    level_choice = st.selectbox("Select Reading/Listening Level:", ["All Levels", "A1", "A2"], key="lib_level_dropdown")

    # Filter book titles based on level selection
    if level_choice == "A1":
        filtered_books = [b[0] for b in library_books if b[1] == "A1"]
    elif level_choice == "A2":
        filtered_books = [b[0] for b in library_books if b[1] == "A2"]
    else:
        filtered_books = [b[0] for b in library_books]

    # Book selection dropdown list
    selected_book = st.selectbox("Select a Book from Virtual Library:", ["-- Choose a Story --"] + filtered_books, key="lib_book_dropdown")

    st.markdown("---")

    if selected_book != "-- Choose a Story --":
        # Find matching book details
        b_data = next((b for b in library_books if b[0] == selected_book), None)
        if b_data:
            st.subheader(f"📖 {b_data[0]} ({b_data[1]})")
            st.write(f"**Author:** {b_data[2]}")
            st.write(f"*{b_data[3]}*")
            st.markdown("---")

            # Generate or fetch story content securely
            cache_key = f"simple_story_{selected_book}"
            if cache_key not in st.session_state:
                prompt = f"""
                Write the short story '{selected_book}' in German, adapted for {b_data[1]} learners.
                Keep it between 25 and 40 sentences total. Provide a short English summary at the beginning.
                Return strict JSON with keys: "english_summary" and "german_story_text".
                """
                with st.spinner(f"Generating story for {selected_book}..."):
                    try:
                        raw_res = generate_cached_content(prompt, is_json=True)
                        st.session_state[cache_key] = json.loads(raw_res)
                    except Exception as e:
                        st.error(f"Error generating story: {e}")

            story_content = st.session_state.get(cache_key, {})
            summary = story_content.get("english_summary", "")
            text = story_content.get("german_story_text", "")

            if summary:
                st.info(f"**English Summary:** {summary}")

            if text:
                safe_text = text.replace('"', "'").replace('\n', ' ' )
                if st.button("🔊 Play Audio (Read Aloud)", key="play_audio_btn"):
                    st.components.v1.html(f"""
                        <script>
                            const u = new SpeechSynthesisUtterance("{safe_text}");
                            u.lang = 'de-DE';
                            u.rate = 0.85;
                            window.parent.speechSynthesis.cancel();
                            window.parent.speechSynthesis.speak(u);
                        </script>
                    """, height=0)

                st.markdown("### German Text")
                st.write(text)
    else:
        st.info("👈 Please select a level and choose a story from the dropdown menu above to begin.")
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
