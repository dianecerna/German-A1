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

# Custom Sunflower Wallpaper & Pastel Theme with Yellow, Pink, and Orange Gradient Accents on Main UI Elements
st.markdown("""
<style>
    /* Global Sunflower Wallpaper Background with Soft Light Overlay */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), 
                    url("https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=2000&q=80") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: #1e293b !important;
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

    /* Yellow, Pink, and Orange Pastel Gradient Accents on Main Buttons / UI Elements */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #fef08a 0%, #f472b6 50%, #fb923c 100%) !important;
        border: 1px solid rgba(244, 114, 182, 0.5) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #7c2d12 !important;
        box-shadow: 0 4px 15px rgba(251, 146, 60, 0.2) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 6px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fde047 0%, #ec4899 50%, #f97316 100%) !important;
        border-color: #ec4899 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(244, 63, 94, 0.3) !important;
        color: #ffffff !important;
    }

    /* Yellow, Pink, and Orange Pastel Gradient Accent on Section Header Boxes */
    .section-header-box {
        background: linear-gradient(135deg, rgba(254, 240, 138, 0.85) 0%, rgba(244, 114, 182, 0.75) 50%, rgba(251, 146, 60, 0.8) 100%) !important;
        backdrop-filter: blur(8px);
        border-left: 6px solid #db2777;
        border-top: 1px solid rgba(254, 240, 138, 0.9);
        border-right: 1px solid rgba(251, 146, 60, 0.9);
        border-bottom: 1px solid rgba(244, 114, 182, 0.9);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 14px;
        color: #7c2d12 !important;
        font-size: 1.25rem;
        font-weight: 800;
        box-shadow: 0 4px 18px rgba(244, 114, 182, 0.25);
    }

    /* Main Content Container Cards with Pastel Gradient Highlights */
    .main-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(8px);
        border-radius: 14px;
        padding: 22px 26px;
        box-shadow: 0 6px 20px rgba(244, 114, 182, 0.12);
        margin-bottom: 14px;
        border: 2px solid rgba(244, 114, 182, 0.4);
    }

    /* Hero Banner with Yellow, Pink, and Orange Pastel Gradient Glow Border */
    .hero-banner {
        background: linear-gradient(135deg, rgba(254, 240, 138, 0.3) 0%, rgba(244, 114, 182, 0.2) 50%, rgba(251, 146, 60, 0.25) 100%);
        backdrop-filter: blur(8px);
        border-radius: 14px;
        padding: 26px;
        color: #1e293b;
        margin-bottom: 16px;
        border: 2px solid #f472b6;
        box-shadow: 0 8px 25px rgba(244, 114, 182, 0.2);
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #fef08a 0%, #f472b6 100%);
        border: 1px solid #f472b6;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        color: #7c2d12;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 4px;
        background: linear-gradient(90deg, #ca8a04 0%, #db2777 50%, #ea580c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.4;
        margin-bottom: 0px;
        font-weight: 500;
    }

    /* Clean Minimalist Dropdown Box Design */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #f472b6 !important;
        border-radius: 10px !important;
        color: #1e293b !important;
        padding: 8px 14px !important;
        box-shadow: 0 4px 15px rgba(244, 114, 182, 0.15) !important;
        min-height: 44px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #fb923c !important;
    }
    .stSelectbox span, .stSelectbox div[data-baseweb="select"] span {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Open Dropdown Popup List Container & Options */
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #f472b6 !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-baseweb="menu"] ul {
        background-color: #ffffff !important;
    }
    div[data-baseweb="menu"] li, div[data-baseweb="menu"] div {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
    }
    div[data-baseweb="menu"] li span, div[data-baseweb="menu"] div span {
        color: #1e293b !important;
    }
    div[data-baseweb="menu"] li:hover, div[data-baseweb="menu"] div[aria-selected="true"] {
        background-color: #fef08a40 !important;
        color: #c2410c !important;
    }

    /* DYNAMIC FLASHCARD SECTION (EXACTLY UNTOUCHED COLOR RULES PER INSTRUCTION) */
    .card-masculine-container {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        border: 2px solid #2563eb;
        color: #ffffff;
        border-radius: 14px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.25);
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
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.25);
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
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
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
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.25);
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
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.25);
        margin-bottom: 12px;
    }
    .card-other-container * { color: #ffffff !important; }

    .flashcard-word-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 4px;
        color: #ffffff !important;
    }

    /* Clean Card Section Wrapper for Back Details */
    .detail-section-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(244, 114, 182, 0.4);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #1e293b;
        box-shadow: 0 2px 8px rgba(244, 114, 182, 0.08);
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
Follow standard CEFR A1 learning objectives and exhaustive Goethe-Zertifikat A1 vocabulary standards (top 1000 essential words).
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

# Exhaustive List of Applicable A1 Categories/Themes (Top 1000 Essential Vocabulary Database Expansion)
A1_VOCABULARY_DATABASE = {
    "ALL": [],
    "allgemein": ["sein", "haben", "werden", "gut", "ja", "nein", "nicht", "sehr", "und", "oder", "aber", "also", "hier", "da", "was", "wer", "wie", "wo", "woher", "wohin"],
    "arbeiten_und_beruf": ["arbeiten", "der Beruf", "die Firma", "das Büro", "der Kollege", "die Kollegin", "der Chef", "die Chefin", "die Arbeit", "der Job", "der Termin", "die Pause", "verdienen", "schreiben", "anrufen", "der Computer", "das Telefon", "die E-Mail", "der Brief", "die Besprechung"],
    "mensch_und_koerper": ["die Familie", "der Vater", "die Mutter", "der Sohn", "die Tochter", "der Bruder", "die Schwester", "die Eltern", "das Kind", "der Mensch", "der Freund", "die Freundin", "die Person", "der Name", "das Alter", "der Kopf", "das Auge", "das Ohr", "die Hand", "der Fuß"],
    "wohnen_und_haushalt": ["das Haus", "die Wohnung", "das Zimmer", "die Küche", "das Bad", "das Schlafzimmer", "das Wohnzimmer", "die Tür", "das Fenster", "der Tisch", "der Stuhl", "das Bett", "die Lampe", "wohnen", "mieten", "der Schlüssel", "der Garten", "das Balkon", "die Miete", "umziehen"],
    "essen_und_trinken": ["das Essen", "das Wasser", "der Kaffee", "der Tee", "die Milch", "das Brot", "das Fleisch", "der Fisch", "das Obst", "das Gemüse", "essen", "trinken", "kochen", "backen", "das Restaurant", "der Hunger", "der Durst", "das Frühstück", "das Mittagessen", "das Abendessen"],
    "freizeit_und_hobbys": ["das Hobby", "spielen", "lesen", "schwimmen", "reisen", "fotografieren", "der Sport", "das Buch", "die Musik", "tanzen", "singen", "malen", "der Film", "das Kino", "das Theater", "wandern", "joggen", "treffen", "lachen", "fernsehen"],
    "einkaufen_und_geld": ["einkaufen", "das Geld", "der Euro", "der Cent", "kosten", "teuer", "billig", "der Laden", "das Geschäft", "der Markt", "der Supermarkt", "kaufen", "verkaufen", "bezahlen", "die Karte", "bar", "der Preis", "das Angebot", "die Kasse", "der Kunde"],
    "verkehr_und_reisen": ["fahren", "fliegen", "reisen", "der Urlaub", "das Ticket", "der Bahnhof", "der Zug", "das Auto", "das Flugzeug", "der Bus", "die Straßenbahn", "das Fahrrad", "die Haltestelle", "der Flughafen", "das Hotel", "ankommen", "abfahren"],
    "gesundheit_und_ernaehrung": ["der Arzt", "die Ärztin", "das Krankenhaus", "die Apotheke", "krank", "gesund", "der Schmerz", "die Medizin", "die Gesundheit", "helfen", "ruhig", "müde", "schlecht", "die Tablette", "der Notfall", "untersuchen", "das Rezept", "fühlen", "leben"],
    "medien_und_kommunikation": ["sprechen", "sagen", "hören", "telefonieren", "das Handy", "das Internet", "die Zeitung", "das Fernsehen", "das Radio", "die Nachricht", "fragen", "antworten", "verstehen", "erklären", "zeigen", "bestellen", "kommunizieren"],
    "zeit_und_wetter": ["die Zeit", "die Stunde", "die Minute", "der Tag", "die Woche", "der Monat", "das Jahr", "heute", "gestern", "morgen", "jetzt", "immer", "nie", "das Wetter", "die Sonne", "der Regen", "der Schnee", "kalt", "warm", "schön"]
}

# Populate ALL category dynamically
all_words_set = set()
for cat, w_list in A1_VOCABULARY_DATABASE.items():
    if cat != "ALL":
        all_words_set.update(w_list)
A1_VOCABULARY_DATABASE["ALL"] = list(all_words_set)

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
    cat_options = {cat.replace('_', ' ').title(): cat for cat in categories}
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

    # Determine Card Color Class based on exact user rules (untouched flashcard section):
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

    # --- AUDIO & FLIP TO BACK BUTTON (FRONT ONLY) ---
    if not st.session_state.is_card_flipped:
        col_audio, col_flip = st.columns([1, 1])
        with col_audio:
            if st.button("🔊 Pronounce Word", key="audio_front_btn"):
                play_direct_audio(data.get("word", active_word), "front_audio")
        with col_flip:
            if st.button("Flip to See Details", key="front_flip_details_btn"):
                st.session_state.is_card_flipped = True
                st.rerun()

    # --- BACK OF CARD ARRANGEMENT OF INFORMATION ---
    if st.session_state.is_card_flipped:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        
        # Audio & Pronounce for Back Card Header
        col_baudio, col_bflip = st.columns([1, 1])
        with col_baudio:
            if st.button("🔊 Pronounce Word", key="audio_back_word"):
                play_direct_audio(data.get("word", active_word), "back_audio")
        with col_bflip:
            if st.button("Flip to Front", key="back_flip_front_btn"):
                st.session_state.is_card_flipped = False
                st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 1. Plural Version with Audio
        plural = data.get("plural_form", "N/A")
        if plural and plural != "N/A":
            st.markdown(f'<div class="detail-section-card"><b>Plural Version:</b> {plural}</div>', unsafe_allow_html=True)
            if st.button("🔊 Audio (Plural)", key="audio_plural"):
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
                <small style="color: #475569;">({data.get('aux_sentence_en', '')})</small>
            </div>''', unsafe_allow_html=True)
            if st.button("🔊 Audio (Aux Sentence)", key="audio_aux_sent"):
                play_direct_audio(aux_sent, "aux_sent_audio")

        # 6. Komparativ and Superlative with Audio
        komp = data.get('komparativ', 'N/A')
        sup = data.get('superlative', 'N/A')
        if komp != "N/A" or sup != "N/A":
            st.markdown(f'<div class="detail-section-card"><b>Komparativ & Superlative:</b> {komp} | {sup}</div>', unsafe_allow_html=True)
            if st.button("🔊 Audio (Komparativ / Superlative)", key="audio_komp"):
                play_direct_audio(f"{komp} {sup}", "komp_audio")

        # 7. Conjugation and Sample Sentences for each pronoun with Audio
        conjugations = data.get("conjugations", [])
        if conjugations:
            conj_html = '<div class="detail-section-card"><b>Conjugation and Sample Sentences:</b><br><ul style="margin: 4px 0 0 16px; padding: 0;">'
            for conj in conjugations:
                conj_html += f'<li><b>{conj.get("pronoun", "")}</b> ({conj.get("form", "--")}): <em>{conj.get("sentence", "")}</em> <small>({conj.get("english_sentence", "")})</small></li>'
            conj_html += '</ul></div>'
            st.markdown(conj_html, unsafe_allow_html=True)
            if st.button("🔊 Audio (Conjugations)", key="audio_conj_all"):
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
            if st.button("🔊 Audio (Colloquial Phrases)", key="audio_phrases_all"):
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

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    render_top_back_button()
    st.markdown('<div class="section-header-box">📖 Core Grammar Practice & Exercises</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)

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
# 9. GEM AI TUTOR
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
