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
    page_icon="🇩🇪", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Theme, Gender-Based Flashcard Styling & Fully Black Rounded Dropdown Styling
st.markdown("""
<style>
    /* Global Dark Theme & Modern Sans-Serif Font */
    .stApp {
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    *, div, span, p, h1, h2, h3, h4, h5, h6, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #f8fafc;
    }

    /* Hide Sidebar Completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Smooth Custom Button Styling */
    .stButton > button {
        width: 100% !important;
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        text-align: left !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 12px !important;
    }
    
    .stButton > button:hover {
        background-color: #1f2937 !important;
        border-color: #60a5fa !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35) !important;
        color: #ffffff !important;
    }

    /* Main Content Cards / Containers */
    .main-card {
        background: #111827;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
        border: 1px solid #1f2937;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border-radius: 20px;
        padding: 32px;
        color: #ffffff;
        margin-bottom: 24px;
        border: 1px solid #312e81;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        color: #60a5fa;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 8px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 0px;
    }

    /* Section Header Box */
    .section-header-box {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* Fully Black Rounded Dropdown Styling Matching Reference Design */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #000000 !important;
        border-radius: 14px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        border: 1px solid #374151 !important;
        border-radius: 14px !important;
        color: #f8fafc !important;
        padding: 6px 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #60a5fa !important;
    }
    .stSelectbox span, .stSelectbox div[data-baseweb="select"] span {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    /* Open Dropdown Popup List Container & Options Black Theme */
    div[data-baseweb="menu"] {
        background-color: #000000 !important;
        border: 1px solid #374151 !important;
        border-radius: 14px !important;
    }
    div[data-baseweb="menu"] ul {
        background-color: #000000 !important;
    }
    div[data-baseweb="menu"] li, div[data-baseweb="menu"] div {
        background-color: #000000 !important;
        color: #f8fafc !important;
    }
    div[data-baseweb="menu"] li:hover, div[data-baseweb="menu"] div[aria-selected="true"] {
        background-color: #111827 !important;
        color: #60a5fa !important;
    }

    /* Gender-based Flashcard Containers */
    .flashcard-masculine {
        background: linear-gradient(135deg, #1e3a8a 0%, #111827 100%);
        border: 2px solid #3b82f6;
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .flashcard-feminine {
        background: linear-gradient(135deg, #7f1d1d 0%, #111827 100%);
        border: 2px solid #ef4444;
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .flashcard-neuter {
        background: linear-gradient(135deg, #064e3b 0%, #111827 100%);
        border: 2px solid #10b981;
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .flashcard-other {
        background: linear-gradient(135deg, #7c2d12 0%, #111827 100%);
        border: 2px solid #f97316;
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .flashcard-word-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Metric & Text Uniformity */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
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
Provide accurate grammatical breakdowns, exact plurals, case usages, conjugations, and natural sample sentences.
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
    "wohnen_und_haushalt": ["das Haus", "die Wohnung", "das Zimmer", "die Küche", "das Bad", "das Schlafzimmer", "das Wohnzimmer", "die Tür", "das Fenster", "der Tisch", "der Stuhl", "das Bett", "die Lampe", "wohnen", "mieten", "der Schlüssel", "der Garten", "der Balkon", "die Miete", "umziehen"],
    "essen_und_trinken": ["das Essen", "das Wasser", "der Kaffee", "der Tee", "die Milch", "das Brot", "das Fleisch", "der Fisch", "das Obst", "das Gemüse", "essen", "trinken", "kochen", "backen", "das Restaurant", "der Hunger", "der Durst", "das Frühstück", "das Mittagessen", "das Abendessen"],
    "freizeit_und_hobbys": ["das Hobby", "spielen", "lesen", "schwimmen", "reisen", "fotografieren", "der Sport", "das Buch", "die Musik", "tanzen", "singen", "malen", "der Film", "das Kino", "das Theater", "wandern", "joggen", "treffen", "lachen", "fernsehen"],
    "einkaufen_und_geld": ["einkaufen", "das Geld", "der Euro", "der Cent", "kosten", "teuer", "billig", "der Laden", "das Geschäft", "der Markt", "der Supermarkt", "kaufen", "verkaufen", "bezahlen", "die Karte", "bar", "der Preis", "das Angebot", "die Kasse", "der Kunde"],
    "verkehr_und_reisen": ["fahren", "fliegen", "reisen", "der Urlaub", "das Ticket", "der Bahnhof", "der Zug", "das Auto", "das Flugzeug", "das Bus", "die Straßenbahn", "das Fahrrad", "die Haltestelle", "der Flughafen", "das Hotel", "das Zimmer", "die Karte", "die Reise", "ankommen", "abfahren"],
    "gesundheit_und_ernaehrung": ["der Arzt", "die Ärztin", "das Krankenhaus", "die Apotheke", "krank", "gesund", "der Schmerz", "die Medizin", "die Gesundheit", "helfen", "ruhig", "müde", "gut", "schlecht", "die Tablette", "der Notfall", "untersuchen", "das Rezept", "fühlen", "leben"],
    "medien_und_kommunikation": ["sprechen", "sagen", "hören", "lesen", "schreiben", "telefonieren", "das Handy", "der Computer", "das Internet", "die Zeitung", "das Fernsehen", "das Radio", "die Nachricht", "fragen", "antworten", "verstehen", "erklären", "zeigen", "bestellen", "kommunizieren"],
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
    if st.button("⬅️ Back to Dashboard", key="top_back_dash_btn"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. STUDY DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="section-header-box">🏠 Study Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">✨ GERMAN A1 LEARNING HUB</div>
        <div class="hero-title">Master Goethe-Zertifikat A1</div>
        <div class="hero-subtitle">Select an option below to start practicing.</div>
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
    st.markdown('<div class="section-header-box">📚 Master Goethe Word Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("### 📁 Categories")
    categories = list(A1_VOCABULARY_DATABASE.keys())
    
    # Map display names to internal keys
    cat_options = {cat.replace('_', ' ').title(): cat for cat in categories}
    current_display_name = [k for k, v in cat_options.items() if v == st.session_state.vocab_category][0]
    
    selected_display_name = st.selectbox("Select Category:", list(cat_options.keys()), index=list(cat_options.keys()).index(current_display_name), key="category_dropdown", label_visibility="collapsed")
    
    selected_cat_key = cat_options[selected_display_name]
    if selected_cat_key != st.session_state.vocab_category:
        st.session_state.vocab_category = selected_cat_key
        st.session_state.vocab_index = 0
        st.session_state.is_card_flipped = False
        st.rerun()

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    current_word_list = A1_VOCABULARY_DATABASE[st.session_state.vocab_category]
    if not current_word_list:
        current_word_list = ["sein"]

    if st.session_state.vocab_index >= len(current_word_list):
        st.session_state.vocab_index = 0

    active_word = current_word_list[st.session_state.vocab_index]

    # Fetch structured flashcard data from Gemini
    prompt = f"""
    Provide exhaustive Goethe A1 flashcard data for the German word/phrase '{active_word}' in category '{st.session_state.vocab_category}'.
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
        card_class = "flashcard-other" # Orange for other words

    # --- FRONT OF CARD ---
    if not st.session_state.is_card_flipped:
        st.markdown(f"""
        <div class="{card_class}">
            <p style="color: #94a3b8; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">📁 Category: {data.get("category", "").replace('_', ' ').title()}</p>
            <div class="flashcard-word-title">{data.get("word", active_word)}</div>
            <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 5px;">Gender / Article: <b>{data.get("gender", "N/A")}</b></p>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 15px;">Click button below to listen to pronunciation, or flip card for full details.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔊 Play Pronunciation", key="audio_front_btn"):
            play_direct_audio(data.get("word", active_word), "front_audio")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Flip to Back (Show Details)", type="primary", use_container_width=True):
            st.session_state.is_card_flipped = True
            st.rerun()

    # --- BACK OF CARD ---
    else:
        st.markdown(f"""
        <div class="{card_class}">
            <p style="color: #94a3b8; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">📖 Detailed Breakdown</p>
            <div class="flashcard-word-title" style="font-size: 2.4rem;">{data.get("word", active_word)}</div>
            <p style="color: #60a5fa; font-size: 1.3rem; font-weight: 700; margin-bottom: 0px;">Meaning: {data.get("english_meaning", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔊 Pronounce Word", key="audio_back_word"):
            play_direct_audio(data.get("word", active_word), "back_audio")

        # Plural version if applicable
        plural = data.get("plural_form", "N/A")
        if plural and plural != "N/A":
            col_pl1, col_pl2 = st.columns([3, 1])
            col_pl1.metric("Plural Version", plural)
            with col_pl2:
                if st.button("🔊 Plural Audio", key="audio_plural"):
                    play_direct_audio(plural, "plural_audio")

        st.divider()

        # Word Type, Case, Auxiliary verb & Partizip II
        c1, c2, c3 = st.columns(3)
        c1.metric("Word Type", data.get("word_type", "N/A"))
        c2.metric("Case Usage", data.get("case_usage", "N/A"))
        c3.metric("Auxiliary Verb", f"{data.get('auxiliary_verb', 'N/A')} ({data.get('partizip_ii', 'N/A')})")

        # Auxiliary verb sample sentence + audio
        aux_sent = data.get("aux_sentence_de", "")
        if aux_sent and aux_sent != "N/A":
            st.markdown("##### 📌 Auxiliary Verb / Usage Sample Sentence")
            s_col_a, s_col_b = st.columns([4, 1])
            s_col_a.markdown(f"`{aux_sent}`<br><small style='color:#94a3b8;'>({data.get('aux_sentence_en', '')})</small>", unsafe_allow_html=True)
            with s_col_b:
                if st.button("🔊 Audio", key="audio_aux_sent"):
                    play_direct_audio(aux_sent, "aux_sent_audio")

        st.markdown("### 📝 Conjugation & Sample Sentences")
        conjugations = data.get("conjugations", [])
        if conjugations:
            for conj in conjugations:
                p_col, s_col, a_col = st.columns([1, 3, 1])
                p_col.markdown(f"**{conj.get('pronoun', '')}**")
                s_col.markdown(f"`{conj.get('form', '')}` — *{conj.get('sentence', '')}*<br><small style='color:#94a3b8;'>({conj.get('english_sentence', '')})</small>", unsafe_allow_html=True)
                with a_col:
                    if st.button("🔊 Audio", key=f"audio_conj_{conj.get('pronoun', '')}"):
                        play_direct_audio(conj.get('sentence', ''), f"conj_{conj.get('pronoun', '')}")
                st.markdown("<hr style='border-color: #1f2937; margin: 5px 0;'>", unsafe_allow_html=True)

        st.markdown("### 💬 Colloquial & Daily Phrases")
        phrases = data.get("colloquial_phrases", [])
        if phrases:
            for idx, ph in enumerate(phrases):
                p_de = ph.get("phrase_de", "")
                p_en = ph.get("phrase_en", "")
                ph_col1, ph_col2 = st.columns([4, 1])
                ph_col1.markdown(f"• **{p_de}** — *{p_en}*")
                with ph_col2:
                    if st.button("🔊 Audio", key=f"audio_phrase_{idx}"):
                        play_direct_audio(p_de, f"phrase_audio_{idx}")

        st.info(f"💡 **Grammar Notes:** {data.get('grammar_notes', 'N/A')}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
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
