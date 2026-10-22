import os
import json
import io
import random
import time
import pypdf
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
    initial_sidebar_state="expanded"
)

# Custom Dark Theme Styling matching Exifa.net interface
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

    /* Dark Mode Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
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
    .main-card:hover {
        border-color: #3b82f6;
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

    /* Custom Sidebar Nav Link Button Styling */
    .stButton > button {
        width: 100%;
        background: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        text-align: left !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #374151 !important;
        border-color: #60a5fa !important;
        color: #ffffff !important;
    }

    /* Outlined Dropdown / Select Elements */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }
    
    /* Flashcard Front Container */
    .flashcard-front-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #111827 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        border: 1px solid #374151;
        margin-bottom: 15px;
    }
    .flashcard-word-title {
        font-size: 3rem;
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 10px;
    }
    .flashcard-back-box {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 15px;
    }
    .flashcard-back-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 5px;
    }
    .meaning-subtitle {
        font-size: 1.25rem;
        font-weight: 600;
        color: #60a5fa;
        margin-bottom: 15px;
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
Follow standard CEFR A1 learning objectives and handbook guidelines.
Ensure exact correctness, clear explanations, thorough lesson reviews, and strict JSON output formats when requested.
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

def generate_dynamic_content(prompt_text: str, is_json: bool = False) -> str:
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

# Scenarios Banks
HOREN_TEIL1_SCENARIOS = [
    {"title": "Jacke, Kino & Apotheke", "desc": "Short everyday dialogues about a jacket's price, the film start and directions to the pharmacy."},
    {"title": "Zug nach Köln, Markt & Hotel", "desc": "Short everyday dialogues about the train to Köln, market, weather and hotel room."}
]

LESEN_TEIL1_SCENARIOS = [
    {
        "title": "Flughafen & Grillfest",
        "desc": "Two short messages: airport pickup and garden barbecue — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail (Lena an Tom)",
        "text1": "BETREFF: Hallo Tom,\n\nvielen Dank für deine Nachricht! Ich hole dich am Sonntag vom Flughafen ab. Dein Flugzeug landet um 14.20 Uhr. Ich bin schon um 14 Uhr da und warte am Ausgang.\nRuf mich bitte an, wenn dein Flug später kommt.\nBis Sonntag!\nLena",
        "text2_label": "BRIEF (Einladung zum Grillfest)",
        "text2": "Liebe Sofia,\n\nnächsten Samstag mache ich ein Grillfest bei mir im Garten. Wir beginnen um 17 Uhr. Kommst du auch? Bitte bring etwas zu trinken mit. Fleisch und Salate habe ich schon genug.\nLiebe Grüße,\nAnna",
        "questions": [
            {"id": "lt1_1", "statement": "Lena holt Tom am Samstag vom Flughafen ab.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Im Text steht, dass sie ihn am Sonntag abholt."},
            {"id": "lt1_2", "statement": "Tom landet um 14.20 Uhr.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Text bestätigt: 'Dein Flugzeug landet um 14.20 Uhr.'"},
            {"id": "lt1_3", "statement": "Lena wartet am Ausgang.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Lena schreibt: '...und warte am Ausgang.'"},
            {"id": "lt1_4", "statement": "Sofia soll Fleisch und Salate mitbringen.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Fleisch und Salate sind genug da; Sofia soll etwas zu trinken mitbringen."},
            {"id": "lt1_5", "statement": "Bei Regen findet das Grillfest in der Wohnung statt.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Brief steht: 'Wenn es regnet, feiern wir in der Wohnung.'"}
        ]
    }
]

SCHREIBEN_TEIL1_SCENARIOS = [
    {
        "title": "Bodensee-Rundfahrt — Anmeldung",
        "desc": "Registration for a Bodensee tour with Eva Kadavy – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Ihre Freundin, Eva Kadavy, macht mit ihrem Mann und ihren beiden Söhnen (8 und 11 Jahre alt) Urlaub in Seeheim. Sie bucht eine Busfahrt.",
        "form_title": "BODENSEE-RUNDFAHRT — Anmeldung",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Kadavy, Eva", "is_gap": False},
            {"id": "sf2", "label": "1. Anzahl der Personen:", "answer": "4", "is_gap": True, "placeholder": "z. B. 4"},
            {"id": "sf3", "label": "2. Davon Kinder:", "answer": "2", "is_gap": True, "placeholder": "z. B. 2"},
            {"id": "sf4", "label": "Urlaubsadresse:", "default": "Hotel Schönblick", "is_gap": False},
            {"id": "sf5", "label": "Straße, Hausnummer:", "default": "Burgstraße 34", "is_gap": False},
            {"id": "sf6", "label": "3. PLZ, Urlaubsort:", "answer": "78014 Seeheim", "is_gap": True, "placeholder": "PLZ und Ort"},
            {"id": "sf7", "label": "4. Zahlungsweise:", "answer": "Bar", "is_gap": True, "placeholder": "Bar oder Kreditkarte", "options": ["Bar", "Kreditkarte"]},
            {"id": "sf8", "label": "5. Reisetermin:", "answer": "nächsten Sonntag", "is_gap": True, "placeholder": "z. B. nächsten Sonntag"},
            {"id": "sf9", "label": "Unterschrift:", "default": "Eva Kadavy", "is_gap": False}
        ]
    }
]

SCHREIBEN_TEIL2_SCENARIOS = [
    {
        "title": "Dresden besuchen — Touristeninformation",
        "desc": "Message to the tourist information office about visiting Dresden – E-mail, approx. 30 words.",
        "aufgabe_text": "Sie möchten im August Dresden besuchen. Schreiben Sie an die Touristeninformation.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).",
        "points": [
            "1. Warum schreiben Sie?",
            "2. Bitten Sie: Informationen über Filme, Museen usw. (Kulturprogramm).",
            "3. Fragen Sie: Hoteladressen?"
        ]
    }
]

# Navigation State Management
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "🏠 Study Dashboard"

nav_options = [
    "🏠 Study Dashboard", 
    "📚 Master Goethe Word Engine",
    "📖 Core Grammar Practice & Exercises",
    "📖 Goethe A1 Lesen (Reading)",
    "🎧 Goethe A1 Hören (Listening)",
    "✍️ Goethe A1 Schreiben (Writing)", 
    "🗣️ Goethe A1 Sprechen (Speaking)",
    "📖 A1 & A2 Short Stories",
    "🐱 Gem AI Tutor"
]

# Sidebar Rendering (With native collapse arrow preserved)
with st.sidebar:
    st.markdown("<h2 style='margin:0; font-size:1.35rem; color:#f8fafc;'>🇩🇪 Exifa.net (German A1)</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#94a3b8; margin-bottom:10px;'>Navigation</p>", unsafe_allow_html=True)
    
    for opt in nav_options:
        if st.button(opt, key=f"nav_btn_{opt}", use_container_width=True):
            st.session_state.nav_choice = opt
            st.rerun()

nav_choice = st.session_state.nav_choice

# ----------------------------------------------------
# 1. STUDY DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="section-header-box">🏠 Study Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">✨ GERMAN A1 LEARNING HUB</div>
        <div class="hero-title">Master Goethe-Zertifikat A1</div>
        <div class="hero-subtitle">Explore interactive modules, practice materials, and master the curriculum with dark theme fidelity.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Study Modules & Practice Centers")
    
    col1, col2 = st.columns(2)
    modules = [
        ("📚 Master Goethe Word Engine", "Interactive flashcard engine with Goethe A1 vocabulary categories and audio pronunciation."),
        ("📖 Core Grammar Practice & Exercises", "Handbook review modules with bulleted guides and multiple-choice practice."),
        ("📖 Goethe A1 Lesen (Reading)", "Practice Lesen Teil 1, Teil 2, and Teil 3 exam tasks with instant feedback."),
        ("🎧 Goethe A1 Hören (Listening)", "Listen to dialogues and station/airport announcements with audio playback."),
        ("✍️ Goethe A1 Schreiben (Writing)", "Practice form filling (Teil 1) and short email writing (Teil 2)."),
        ("🗣️ Goethe A1 Sprechen (Speaking)", "Record and evaluate your self-introductions, Q&A, and polite requests."),
        ("📖 A1 & A2 Short Stories", "Immerse yourself in fairy tales and classic fictions with built-in audio narration."),
        ("🐱 Gem AI Tutor", "Ask Gem any questions about German grammar, vocabulary, or exam prep.")
    ]

    for i, (mod_title, mod_desc) in enumerate(modules):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f'<div class="main-card">', unsafe_allow_html=True)
            if st.button(mod_title, key=f"dash_card_{i}", use_container_width=True):
                st.session_state.nav_choice = mod_title
                st.rerun()
            st.markdown(f"<p style='color: #94a3b8; font-size: 0.9rem; margin-top: 10px; margin-bottom: 0px;'>{mod_desc}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="section-header-box">📚 Master Goethe Word Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Interactive Flashcard Engine (Complete Vocabulary)")
    st.write("Browse through the complete Goethe A1 vocabulary list categorized into thematic groups.")

    TOP_1000_VOCAB_CATEGORIES = {
        "1. Person & Alltag (Personal & Daily Life)": {
            "Verben": ["heißen", "heiraten", "wohnen", "leben", "kennen", "kennenlernen", "schlafen", "aufstehen", "baden", "duschen"],
            "Nomen": ["die Familie", "der Vater", "die Mutter", "der Sohn", "die Tochter", "der Bruder", "die Schwester"]
        },
        "2. Essen & Trinken (Food & Drink)": {
            "Verben": ["essen", "trinken", "kochen", "backen", "frühstücken"],
            "Nomen": ["das Essen", "das Frühstück", "das Wasser", "der Kaffee", "der Tee", "das Brot"]
        }
    }

    vocab_tree = TOP_1000_VOCAB_CATEGORIES
    main_cats = ["ALL"] + list(vocab_tree.keys())
    selected_main_cat = st.selectbox("📂 **Select Main Category:**", main_cats, key="vocab_main_cat")

    if selected_main_cat == "ALL":
        sub_cats = ["ALL"]
        selected_sub_cat = "ALL"
        all_pool = []
        for cat, subdict in vocab_tree.items():
            for sub, wlist in subdict.items():
                all_pool.extend(wlist)
        available_words = ["ALL"] + list(set(all_pool))
    else:
        sub_dict = vocab_tree[selected_main_cat]
        sub_cats = ["ALL"] + list(sub_dict.keys())
        selected_sub_cat = st.selectbox("📁 **Select Subcategory:**", sub_cats, key="vocab_sub_cat")
        if selected_sub_cat == "ALL":
            all_sub_pool = []
            for sub, wlist in sub_dict.items():
                all_sub_pool.extend(wlist)
            available_words = ["ALL"] + list(set(all_sub_pool))
        else:
            available_words = ["ALL"] + sub_dict[selected_sub_cat]

    selected_word_dropdown = st.selectbox("🔤 **Select specific word (or ALL):**", available_words, key="vocab_word_sel")

    col_w1, col_w2 = st.columns([3, 1])
    with col_w1:
        if selected_word_dropdown == "ALL":
            actual_pool = [w for w in available_words if w != "ALL"]
            active_word = random.choice(actual_pool) if actual_pool else "sein"
        else:
            active_word = selected_word_dropdown
    with col_w2:
        if st.button("🎲 Shuffle Word", use_container_width=True):
            actual_pool = [w for w in available_words if w != "ALL"]
            st.session_state.current_flashcard_word = random.choice(actual_pool) if actual_pool else "sein"
            st.session_state.show_card_back = False
            st.rerun()

    if "current_flashcard_word" not in st.session_state or st.session_state.current_flashcard_word not in available_words:
        st.session_state.current_flashcard_word = active_word

    if selected_word_dropdown != "ALL" and selected_word_dropdown != st.session_state.current_flashcard_word:
        st.session_state.current_flashcard_word = selected_word_dropdown
        st.session_state.show_card_back = False

    active_word = st.session_state.current_flashcard_word

    prompt = f"""
    Generate an exhaustive A1 study card JSON for '{active_word}'.
    Return strict JSON with this exact schema:
    {{
        "word": "{active_word}",
        "is_goethe_word": true,
        "part_of_speech": "Verb / Noun / Adjective",
        "english_meaning": "English translation",
        "gender": "der / die / das / N/A",
        "plural_form": "Plural form or N/A",
        "perfekt_tense": {{"formula": "hat/ist + Partizip II"}},
        "grammar_notes": "Important A1 grammar note"
    }}
    """
    try:
        raw_json = generate_cached_content(prompt, is_json=True)
        data = json.loads(raw_json)

        if not st.session_state.get("show_card_back", False):
            st.markdown(f"""
            <div class="flashcard-front-box">
                <p style="color: #60a5fa; font-weight: 700; margin-bottom: 8px;">⭐ {selected_main_cat}</p>
                <div class="flashcard-word-title">{data.get("word", active_word)}</div>
                <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0px;">Click speaker icon for audio, or flip card for details.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔊 Play Pronunciation", key="audio_front_btn"):
                play_direct_audio(active_word, "front_word")
        else:
            st.markdown(f"""
            <div class="flashcard-back-box">
                <div class="flashcard-back-title">{data.get("word", active_word)}</div>
                <div class="meaning-subtitle">Meaning: <b>{data.get("english_meaning", "")}</b></div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Part of Speech", data.get("part_of_speech", "N/A"))
            c2.metric("Gender", data.get("gender", "N/A"))
            c3.metric("Plural Form", data.get("plural_form", "N/A"))
            st.info(f"💡 **Grammar Notes:** {data.get('grammar_notes', 'N/A')}")
    except Exception as e:
        st.error(f"Error loading flashcard: {str(e)}")

    st.divider()
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        if st.button("🔄 Flip Flashcard", use_container_width=True):
            st.session_state.show_card_back = not st.session_state.get("show_card_back", False)
            st.rerun()
    with col_f2:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state.nav_choice = "🏠 Study Dashboard"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    st.markdown('<div class="section-header-box">📖 Core Grammar Practice & Exercises</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    handbook_lessons = [
        "Lesson 1: German Alphabet, Pronunciation, and Article Recognition",
        "Lesson 2: German Noun Gender and Everyday Word Patterns"
    ]
    selected_lesson = st.selectbox("Select Handbook Lesson:", handbook_lessons, key="grammar_lesson_sel")
    if st.button("📖 Load Review & Practice", type="primary"):
        with st.spinner("Compiling notes..."):
            prompt = f"Create a detailed study guide & 3 MC exercises for '{selected_lesson}' in strict JSON: {{\"lesson_title\": \"...\", \"lesson_explanation\": \"...\", \"exercises_mc\": [{{\"id\": \"mc1\", \"question\": \"...\", \"options\": [\"A\",\"B\",\"C\",\"D\"], \"correct\": \"A\", \"explanation\": \"...\"}}]}}"
            st.session_state.active_grammar_module = json.loads(generate_cached_content(prompt, is_json=True))

    if "active_grammar_module" in st.session_state:
        mod = st.session_state.active_grammar_module
        st.markdown(f"### {mod['lesson_title']}")
        st.markdown(mod["lesson_explanation"])
        for idx, q in enumerate(mod.get("exercises_mc", []), start=1):
            st.markdown(f"**Q{idx}. {q['question']}**")
            st.radio("Options:", q['options'], key=f"rad_grammar_{q['id']}")
    
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="section-header-box">📖 Goethe A1 Lesen (Reading)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    scen = LESEN_TEIL1_SCENARIOS[0]
    st.info(scen['desc'])
    st.markdown(f"**{scen['text1_label']}**\n> {scen['text1']}")
    st.markdown(f"**{scen['text2_label']}**\n> {scen['text2']}")
    
    ans_lt1 = {}
    for idx, q in enumerate(scen["questions"], start=1):
        st.markdown(f"**Task {idx}: {q['statement']}**")
        ans_lt1[q["id"]] = st.radio("Wählen Sie:", q["options"], key=f"rad_lt1_{q['id']}")
    
    if st.button("✔ Submit Lesen Answers", type="primary"):
        for idx, q in enumerate(scen["questions"], start=1):
            if ans_lt1.get(q["id"]) == q["answer"]:
                st.success(f"Task {idx}: Correct! — {q['explanation']}")
            else:
                st.error(f"Task {idx}: Incorrect. Correct: `{q['answer']}` — {q['explanation']}")
    
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="section-header-box">🎧 Goethe A1 Hören (Listening)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Listen to sample dialogue and answer questions.")
    sample_script = "Kunde: Guten Tag, was kostet diese Jacke?\nVerkäuferin: Guten Tag, die Jacke kostet 49 Euro."
    st.audio(generate_german_audio_bytes(sample_script), format="audio/mp3")
    ans = st.radio("Was kostet die Jacke?", ["39 Euro", "49 Euro", "59 Euro"])
    if st.button("Submit Answer", type="primary"):
        if ans == "49 Euro":
            st.success("Correct!")
        else:
            st.error("Incorrect. It costs 49 Euro.")
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="section-header-box">✍️ Goethe A1 Schreiben (Writing)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    scen = SCHREIBEN_TEIL1_SCENARIOS[0]
    st.info(scen['aufgabe'])
    user_inputs = {}
    for field in scen["fields"]:
        if not field.get("is_gap", False):
            st.text_input(field["label"], value=field.get("default", ""), disabled=True)
        else:
            user_inputs[field["id"]] = st.text_input(field["label"], placeholder=field.get("placeholder", "..."))
    
    if st.button("✔ Check Form", type="primary"):
        for field in scen["fields"]:
            if field.get("is_gap", False):
                if field["answer"].lower() in str(user_inputs.get(field["id"], "")).lower():
                    st.success(f"{field['label']} Correct!")
                else:
                    st.error(f"{field['label']} Incorrect. Expected: {field['answer']}")
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="section-header-box">🗣️ Goethe A1 Sprechen (Speaking)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### Teil 1 — Sich vorstellen")
    rec = mic_recorder(start_prompt="Record Audio 🎙️", stop_prompt="Stop 🛑", key="rec_sp")
    if rec:
        st.audio(rec['bytes'], format='audio/wav')
        st.success("Recording captured successfully.")
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. A1 & A2 SHORT STORIES
# ----------------------------------------------------
elif nav_choice == "📖 A1 & A2 Short Stories":
    st.markdown('<div class="section-header-box">📖 A1 & A2 Short Stories</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Enchanted Storybook Reader")
    story = "Es war einmal in einer wunderschönen Stadt..."
    st.info(story)
    if st.button("🔊 Read Story Aloud"):
        play_direct_audio(story, "story")
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 9. GEM AI TUTOR
# ----------------------------------------------------
elif nav_choice == "🐱 Gem AI Tutor":
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
    if st.button("🏠 Back to Dashboard"):
        st.session_state.nav_choice = "🏠 Study Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
