import os
import json
import io
import random
import time
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# Streamlit Page Configuration
st.set_page_config(
    page_title="German A1 Learning", 
    page_icon="🍳", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Warm Minimalist Kitchen Aesthetic Theme matching the Quickbite reference
st.markdown("""
<style>
    /* Global Soft Cream Background & Clean Sans-Serif Fonts */
    .stApp {
        background-color: #fcf9f6 !important; /* Soft warm cream */
        color: #2d3748 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background-attachment: fixed !important;
    }
    
    *, div, span, p, h1, h2, h3, h4, h5, h6, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #2d3748;
    }

    /* Hide Sidebar Completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Relaxed Top Spacing for Comfort */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.6rem !important;
    }

    /* Clean Warm Minimalist Custom Button Styling */
    .stButton > button {
        width: 100% !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        text-align: left !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 6px !important;
    }
    
    .stButton > button:hover {
        background-color: #f8fafc !important;
        border-color: #94a3b8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        color: #0f172a !important;
    }

    /* Compact Main Content Cards / Containers */
    .main-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        margin-bottom: 12px;
        border: 1px solid #e2e8f0;
    }
    
    /* Compact Hero Banner / Header Box matching Quickbite style */
    .hero-banner {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        color: #2d3748;
        margin-bottom: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .hero-badge {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        color: #475569;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 4px;
        color: #1e293b;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        line-height: 1.4;
        margin-bottom: 0px;
        font-weight: 500;
    }

    /* Section Header Box */
    .section-header-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 12px;
        color: #1e293b;
        font-size: 1.2rem;
        font-weight: 800;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }

    /* Clean Minimalist Dropdown Box Design matching Warm Aesthetic */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        padding: 8px 14px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        min-height: 44px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #94a3b8 !important;
    }
    .stSelectbox span, .stSelectbox div[data-baseweb="select"] span {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Open Dropdown Popup List Container & Options */
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
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
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    div[data-baseweb="menu"] li:hover span, div[data-baseweb="menu"] div[aria-selected="true"] span {
        color: #0f172a !important;
    }

    /* Detailed Back Card Separated Sections Style */
    .detail-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }

    /* Gender-based Flashcard Containers (Warm Minimalist Palette) */
    .flashcard-masculine {
        background: #eff6ff;
        border: 2px solid #3b82f6;
        color: #1e3a8a;
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
        margin-bottom: 12px;
    }
    .flashcard-feminine {
        background: #fff1f2;
        border: 2px solid #f43f5e;
        color: #881337;
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.1);
        margin-bottom: 12px;
    }
    .flashcard-neuter {
        background: #f0fdf4;
        border: 2px solid #10b981;
        color: #064e3b;
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
        margin-bottom: 12px;
    }
    .flashcard-other {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        color: #78350f;
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.1);
        margin-bottom: 12px;
    }
    .flashcard-word-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 4px;
        color: #1e293b;
    }

    /* Metric & Text Uniformity */
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
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
Follow standard CEFR A1 learning objectives and exhaustive Goethe-Zertifikat A1 vocabulary standards.
Provide accurate grammatical breakdowns, exact plurals, case usages, conjugations, and always provide sentences for each pronoun even for nouns or other parts of speech. Never leave fields as blank or N/A in conjugations.
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

# Exhaustive A1 Categories & Representative Word Banks
A1_VOCABULARY_DATABASE = {
    "ALL": [],
    "allgemein": ["sein", "haben", "werden", "gut", "ja", "nein", "nicht", "sehr", "und", "oder", "aber", "also", "hier", "da", "was", "wer", "wie", "wo", "woher", "wohin"],
    "arbeit_und_beruf": ["arbeiten", "der Beruf", "die Firma", "das Büro", "der Kollege", "die Kollegin", "der Chef", "die Chefin", "die Arbeit", "der Job", "der Termin", "die Pause", "verdienen", "schreiben", "anrufen", "der Computer", "das Telefon", "die E-Mail", "der Brief", "die Besprechung"],
    "mensch_und_koerper": ["die Familie", "der Vater", "die Mutter", "der Sohn", "die Tochter", "der Bruder", "die Schwester", "die Eltern", "das Kind", "der Mensch", "der Freund", "die Freundin", "die Person", "der Name", "das Alter", "der Kopf", "das Auge", "das Ohr", "die Hand", "der Fuß"],
    "wohnen_und_haushalt": ["das Haus", "die Wohnung", "das Zimmer", "das Küche", "das Bad", "das Schlafzimmer", "das Wohnzimmer", "die Tür", "das Fenster", "der Tisch", "der Stuhl", "das Bett", "die Lampe", "wohnen", "mieten", "der Schlüssel", "der Garten", "der Balkon", "die Miete", "umziehen"],
    "essen_und_trinken": ["das Essen", "das Wasser", "der Kaffee", "der Tee", "die Milch", "das Brot", "das Fleisch", "der Fisch", "das Obst", "das Gemüse", "essen", "trinken", "kochen", "backen", "das Restaurant", "der Hunger", "der Durst", "das Frühstück", "das Mittagessen", "das Abendessen"],
    "freizeit_und_hobbys": ["das Hobby", "spielen", "lesen", "schwimmen", "reisen", "fotografieren", "der Sport", "das Buch", "die Musik", "tanzen", "singen", "malen", "der Film", "das Kino", "das Theater", "wandern", "joggen", "treffen", "lachen", "fernsehen"],
    "einkaufen_und_geld": ["einkaufen", "das Geld", "der Euro", "der Cent", "kosten", "teuer", "billig", "der Laden", "das Geschäft", "der Markt", "der Supermarkt", "kaufen", "verkaufen", "bezahlen", "die Karte", "bar", "der Preis", "das Angebot", "die Kasse", "der Kunde"],
    "verkehr_und_reisen": ["fahren", "fliegen", "reisen", "der Urlaub", "das Ticket", "der Bahnhof", "der Zug", "das Auto", "das Flugzeug", "das Bus", "die Straßenbahn", "das Fahrrad", "die Haltestelle", "der Flughafen", "das Hotel", "das Zimmer", "das Karte", "das Reise", "ankommen", "abfahren"],
    "gesundheit_und_ernaehrung": ["der Arzt", "die Ärztin", "das Krankenhaus", "die Apotheke", "krank", "gesund", "der Schmerz", "die Medizin", "die Gesundheit", "helfen", "ruhig", "müde", "gut", "schlecht", "die Tablette", "der Notfall", "untersuchen", "das Rezept", "fühlen", "leben"],
    "medien_und_kommunikation": ["sprechen", "sagen", "hören", "lesen", "schreiben", "telefonieren", "das Handy", "der Computer", "das Internet", "die Zeitung", "das Fernsehen", "das Radio", "das Nachricht", "fragen", "antworten", "verstehen", "erklären", "zeigen", "bestellen", "kommunizieren"],
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
    st.markdown('<div class="section-header-box">🍳 Study Dashboard</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header-box">🍳 Master Goethe Word Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("##### 🍳 Categories")
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

    # Fetch structured flashcard data from Gemini ensuring sample sentences for EVERY pronoun even for nouns/other words
    prompt = f"""
    Provide exhaustive Goethe A1 flashcard data for the German word/phrase '{active_word}' in category '{st.session_state.vocab_category}'.
    CRITICAL REQUIREMENT for conjugations: Always provide 6 items (for pronouns ich, du, er/sie/es, wir, ihr, sie/Sie). Even if the word is a noun, preposition, adjective, or non-conjugatable word, provide a natural sample sentence using that exact word with each pronoun (e.g. for noun 'das Haus': 'ich' -> form: '', sentence: 'Ich baue ein Haus', english: 'I am building a house'). Never leave conjugation form blank if it's a verb, but for nouns/other words leave conjugation form blank or put '--' and always provide a valid sentence for every pronoun.
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
            "conjugations": [],
            "colloquial_phrases": [],
            "grammar_notes": str(e)
        }

    gender_val = str(data.get("gender", "N/A")).strip().lower()
    if gender_val == "der":
        card_class = "flashcard-masculine"
    elif gender_val == "die":
        card_class = "flashcard-feminine"
    elif gender_val == "das":
        card_class = "flashcard-neuter"
    else:
        card_class = "flashcard-other"

    # --- FRONT OF CARD ---
    if not st.session_state.is_card_flipped:
        st.markdown(f"""
        <div class="{card_class}">
            <p style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">🍳 Category: {data.get("category", "").replace('_', ' ').title()}</p>
            <div class="flashcard-word-title">{data.get("word", active_word)}</div>
            <p style="font-size: 1rem; margin-top: 4px;">Gender / Article: <b>{data.get("gender", "N/A")}</b></p>
            <p style="font-size: 0.85rem; margin-top: 10px; opacity: 0.8;">Click below to listen or flip card for separated detail boxes.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔊 Play Pronunciation", key="audio_front_btn"):
            play_direct_audio(data.get("word", active_word), "front_audio")

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Flip to Back (Show Details)", type="primary", use_container_width=True):
            st.session_state.is_card_flipped = True
            st.rerun()

    # --- BACK OF CARD WITH SEPARATED BOXES ---
    else:
        st.markdown(f"""
        <div class="{card_class}">
            <p style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">📖 Detailed Breakdown</p>
            <div class="flashcard-word-title" style="font-size: 2.2rem;">{data.get("word", active_word)}</div>
            <p style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0px;">Meaning: {data.get("english_meaning", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔊 Pronounce Word", key="audio_back_word"):
            play_direct_audio(data.get("word", active_word), "back_audio")

        # 1. Plural Version Box
        plural = data.get("plural_form", "N/A")
        if plural and plural != "N/A":
            st.markdown('<div class="detail-box">', unsafe_allow_html=True)
            col_pl1, col_pl2 = st.columns([4, 1])
            col_pl1.markdown(f"**Plural Version:** `{plural}`")
            with col_pl2:
                if st.button("🔊 Audio", key="audio_plural"):
                    play_direct_audio(plural, "plural_audio")
            st.markdown('</div>', unsafe_allow_html=True)

        # 2. Word Type and Case Usage Box
        st.markdown('<div class="detail-box">', unsafe_allow_html=True)
        wt_col, cu_col = st.columns(2)
        wt_col.markdown(f"**Word Type:** `{data.get('word_type', 'N/A')}`")
        cu_col.markdown(f"**Case Usage:** `{data.get('case_usage', 'N/A')}`")
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. Auxiliary Verb and Sample Sentence with Audio Box
        aux_verb = data.get('auxiliary_verb', 'N/A')
        part_ii = data.get('partizip_ii', 'N/A')
        aux_sent = data.get('aux_sentence_de', '')
        st.markdown('<div class="detail-box">', unsafe_allow_html=True)
        st.markdown(f"**Auxiliary Verb & Partizip II:** `{aux_verb} ({part_ii})`")
        if aux_sent and aux_sent != "N/A":
            as_col1, as_col2 = st.columns([4, 1])
            as_col1.markdown(f"Sample: *{aux_sent}* <br><small style='color:#64748b;'>({data.get('aux_sentence_en', '')})</small>", unsafe_allow_html=True)
            with as_col2:
                if st.button("🔊 Audio", key="audio_aux_sent"):
                    play_direct_audio(aux_sent, "aux_sent_audio")
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. Conjugation & Sample Sentences Box (4 Columns)
        st.markdown('<div class="detail-box">', unsafe_allow_html=True)
        st.markdown("#### 📝 Conjugation & Sample Sentences")
        conjugations = data.get("conjugations", [])
        if conjugations:
            for conj in conjugations:
                c1, c2, c3, c4 = st.columns([1, 1, 2.5, 0.8])
                c1.markdown(f"**{conj.get('pronoun', '')}**")
                c2.markdown(f"`{conj.get('form', '--')}`")
                c3.markdown(f"*{conj.get('sentence', '')}*<br><small style='color:#64748b;'>({conj.get('english_sentence', '')})</small>", unsafe_allow_html=True)
                with c4:
                    if st.button("🔊", key=f"audio_conj_{conj.get('pronoun', '')}"):
                        play_direct_audio(conj.get('sentence', ''), f"conj_{conj.get('pronoun', '')}")
                st.markdown("<hr style='border-color: #e2e8f0; margin: 4px 0;'>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. Colloquial & Daily Phrases Box with Audio
        phrases = data.get("colloquial_phrases", [])
        if phrases:
            st.markdown('<div class="detail-box">', unsafe_allow_html=True)
            st.markdown("#### 💬 Colloquial & Daily Phrases")
            for idx, ph in enumerate(phrases):
                p_de = ph.get("phrase_de", "")
                p_en = ph.get("phrase_en", "")
                ph_c1, ph_c2 = st.columns([4, 1])
                ph_c1.markdown(f"• **{p_de}** — *{p_en}*")
                with ph_c2:
                    if st.button("🔊 Audio", key=f"audio_phrase_{idx}"):
                        play_direct_audio(p_de, f"phrase_audio_{idx}")
            st.markdown('</div>', unsafe_allow_html=True)

        # 6. Grammar Notes Box
        st.markdown(f'<div class="detail-box">🍳 <b>Grammar Notes:</b> {data.get("grammar_notes", "N/A")}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Flip back to Front", type="primary", use_container_width=True):
            st.session_state.is_card_flipped = False
            st.rerun()

    st.divider()

    # --- NAVIGATION CONTROLS BELOW FLASHCARD ---
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("◀ Previous Word", use_container_width=True):
            st.session_state.vocab_index = (st.session_state.vocab_index - 1) % len(current_word_list)
            st.session_state.is_card_flipped = False
            st.rerun()
    with col_nav2:
        if st.button("🔀 Shuffle Card", use_container_width=True):
            st.session_state.vocab_index = random.randint(0, len(current_word_list) - 1)
            st.session_state.is_card_flipped = False
            st.rerun()
    with col_nav3:
        if st.button("Next Word ▶", use_container_width=True):
            st.session_state.vocab_index = (st.session_state.vocab_index + 1) % len(current_word_list)
            st.session_state.is_card_flipped = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

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
                response = generate_dynamic_content(user_prompt)
                st.write(response)
                st.session_state.gem_chat_messages.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)
