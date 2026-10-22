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

# Custom Styling: Pastel Blue background, Dark Navy headers, Pastel Framed Elements
st.markdown("""
<style>
    /* Global Clean Modern Sans-Serif Font & Pastel Blue Background */
    .stApp {
        background-color: #e0f2fe !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    *, div, span, p, h1, h2, h3, h4, h5, h6, label, button {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

/* Hide raw icon text in the sidebar collapse control while keeping the button clickable */
[data-testid="collapsedControl"] span, 
[data-testid="collapsedControl"] p,
button[kind="header"] span {
    font-size: 0px !important;
}

    /* Cards Styling with Vibrant Backgrounds & Subtle Hover Micro-Interactions */
    .main-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
        margin-bottom: 20px;
        border: 1px solid #bae6fd;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .main-card:hover {
        box-shadow: 0 6px 24px rgba(15, 23, 42, 0.09);
    }
    
    .accent-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 24px;
        border-left: 6px solid #1e3a8a;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.08);
        margin-bottom: 20px;
        border: 1px solid #bae6fd;
    }
    
    /* Hero Banner with Vibrant Dark Blue & Navy Headers */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        border-radius: 24px;
        padding: 36px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 15px;
        color: #7dd3fc;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #e2e8f0;
        line-height: 1.6;
        max-width: 800px;
        margin-bottom: 0px;
    }

    /* Section Header framed inside a darker pastel border with black font */
    .section-header-box {
        background: #f0f9ff;
        border: 2px solid #7dd3fc;
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 20px;
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 700;
    }

    /* Sophisticated Sidebar Navigation Styling with Vibrant Dark Blue */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Custom Sidebar Nav Link Button Styling: Left justified, pastel frames, black font */
    .stButton > button.nav-btn {
        width: 100%;
        background: #e0f2fe !important;
        border: 1.5px solid #7dd3fc !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        text-align: left !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton > button.nav-btn:hover {
        background: #bae6fd !important;
        border-color: #38bdf8 !important;
        transform: translateY(-1px);
    }
    .stButton > button.nav-btn-active {
        width: 100%;
        background: #7dd3fc !important;
        border: 1.5px solid #0284c7 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        text-align: left !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        box-shadow: 0 4px 12px rgba(125, 211, 252, 0.4);
    }

    /* Outlined & Framed Dropdown / Select Elements with Pastel Borders */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #7dd3fc !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
        transition: border-color 0.2s ease;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #0284c7 !important;
    }

    /* Interactive Flashcard UI */
    .flashcard-front-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 2px solid #7dd3fc;
        margin-bottom: 15px;
    }
    .flashcard-word-title {
        font-size: 3.2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #7dd3fc;
        margin-bottom: 10px;
    }
    .flashcard-back-box {
        background: #ffffff;
        border: 2px solid #1e3a8a;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.15);
        margin-bottom: 15px;
    }
    .flashcard-back-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .meaning-subtitle {
        font-size: 1.35rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 15px;
    }

    /* Metric Font Uniformity & Bold Key Items */
    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    strong, b {
        font-weight: 700 !important;
        color: #0f172a;
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

# Hören Teil 1 Official Scenarios Bank
HOREN_TEIL1_SCENARIOS = [
    {
        "title": "Jacke, Kino & Apotheke",
        "desc": "Short everyday dialogues about a jacket's price, the film start and directions to the pharmacy – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Zug nach Köln, Markt & Hotel",
        "desc": "Short everyday dialogues about the train to Köln, the market, weather and a hotel room – 6 tasks, a/b/c (played twice)."
    }
]

# Hören Teil 2 Official Scenarios Bank
HOREN_TEIL2_SCENARIOS = [
    {
        "title": "Markt-, Bahn- & Flughafendurchsagen",
        "desc": "Short announcements at a market, railway station and airport – 4 tasks, Richtig/Falsch (played once)."
    }
]

# Lesen Teil 1 Official Scenarios Bank
LESEN_TEIL1_SCENARIOS = [
    {
        "title": "Flughafen & Grillfest",
        "desc": "Two short messages: airport pickup and a garden barbecue — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail (Lena an Tom)",
        "text1": "BETREFF: Hallo Tom,\n\nvielen Dank für deine Nachricht! Ich hole dich am Sonntag vom Flughafen ab. Dein Flugzeug landet um 14.20 Uhr. Ich bin schon um 14 Uhr da und warte am Ausgang.\nRuf mich bitte an, wenn dein Flug später kommt. Meine Nummer hast du ja.\nBis Sonntag!\nLena",
        "text2_label": "BRIEF (Einladung zum Grillfest)",
        "text2": "Liebe Sofia,\n\nnächsten Samstag mache ich ein Grillfest bei mir im Garten. Wir beginnen um 17 Uhr. Kommst du auch? Es kommen noch andere Freunde, die du kennst. Bitte bring etwas zu trinken mit. Fleisch und Salate habe ich schon genug. Wenn es regnet, feiern wir in der Wohnung.",
        "questions": [
            {"id": "lt1_1", "statement": "Lena holt Tom am Samstag vom Flughafen ab.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Im Text steht, dass sie ihn am *Sonntag* abholt."},
            {"id": "lt1_2", "statement": "Tom landet um 14.20 Uhr.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Text bestätigt: 'Dein Flugzeug landet um 14.20 Uhr.'"},
            {"id": "lt1_3", "statement": "Lena wartet am Ausgang.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Lena schreibt: '...und warte am Ausgang.'"},
            {"id": "lt1_4", "statement": "Sofia soll Fleisch und Salate mitbringen.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Fleisch und Salate sind genug da; Sofia soll *etwas zu trinken* mitbringen."},
            {"id": "lt1_5", "statement": "Bei Regen findet das Grillfest in der Wohnung statt.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Brief steht: 'Wenn es regnet, feiern wir in der Wohnung.'"}
        ]
    },
    {
        "title": "Krankmeldung & Vereinsausflug",
        "desc": "Two short messages: a sick note and a club outing — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail an die Arbeit",
        "text1": "Sehr geehrte Frau Braun,\nich kann heute leider nicht ins Büro kommen, da ich starkes Fieber und Husten habe. Ich gehe heute Nachmittag zum Arzt und bringe morgen die Krankmeldung mit.\nMit freundlichen Grüßen,\nMarkus Weber",
        "text2_label": "Aushang (Sportverein)",
        "text2": "Liebe Vereinsmitglieder,\nserer Jahresausflug findet am Samstag, den 14. Juli, statt. Wir fahren mit dem Bus in die Berge zum Wandern. Anmeldung bitte bis Mittwoch bei Trainer Klaus.",
        "questions": [
            {"id": "lt1_21", "statement": "Markus hat Fieber und Husten.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Markus schreibt, dass er starkes Fieber und Husten hat."},
            {"id": "lt1_22", "statement": "Markus bringt die Krankmeldung erst nächste Woche.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Er bringt sie *morgen* mit."},
            {"id": "lt1_23", "statement": "Der Vereinsausflug ist am Sonntag.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Der Ausflug findet am *Samstag*, den 14. Juli, statt."},
            {"id": "lt1_24", "statement": "Man fährt mit dem Bus in die Berge.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Aushang steht: 'Wir fahren mit dem Bus in die Berge.'"},
            {"id": "lt1_25", "statement": "Man muss sich bis Mittwoch bei Klaus anmelden.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Anmeldung bitte bis Mittwoch bei Trainer Klaus."}
        ]
    }
]

# Lesen Teil 2 Official Scenarios Bank
LESEN_TEIL2_SCENARIOS = [
    {
        "title": "Fahrrad, Schwimmbad & Pizza",
        "desc": "Information about buying a bicycle, swimming pools, paediatricians and ordering pizza — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_t1",
                "situation": "6. Sie möchten ein gebrauchtes Fahrrad kaufen.",
                "site_a_url": "www.fahrrad-neu.de",
                "site_a": "Neue Fahrräder und E-Bikes\nNur Neuware vom Fachhändler\n• Modelle • Preise • Service",
                "site_b_url": "www.radmarkt-leipzig.de",
                "site_b": "Radmarkt Leipzig\nGebrauchte Fahrräder günstig kaufen und verkaufen\n• Angebote • Kontakt",
                "answer": "Website B",
                "explanation": "Sie suchen ein *gebrauchtes* Fahrrad. Website B bietet gebrauchte Fahrräder an."
            },
            {
                "id": "lt2_t2",
                "situation": "7. Sie möchten am Wochenende ins Schwimmbad gehen.",
                "site_a_url": "www.stadtbad-erfurt.de",
                "site_a": "Stadtbad Erfurt\nHallenbad mit Sauna\nÖffnungszeiten und Preise\nAuch am Wochenende geöffnet!",
                "site_b_url": "www.schwimmverein-erfurt.de",
                "site_b": "Schwimmverein Erfurt\nSchwimmkurse und Training nur für Mitglieder",
                "answer": "Website A",
                "explanation": "Website A ist ein öffentliches Bad mit Wochenendöffnung, während Website B nur für Mitglieder ist."
            }
        ]
    }
]

# Lesen Teil 3 Official Scenarios Bank
LESEN_TEIL3_SCENARIOS = [
    {
        "title": "Bäckerei, Markt & Parkhaus",
        "desc": "Signs and notices about a bakery, market, museum, library and car park — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Zum Deutsch Lernen gehen Sie in die Beethovenstraße 23.",
            "sign_title": "AN DER TÜR DER SPRACHSCHULE",
            "sign_text": "SPRACHZENTRUM\nDas Sprachzentrum ist umgezogen.\nSie finden uns jetzt in der Beethovenstr. 23",
            "answer": "richtig",
            "explanation": "Das Schild bestätigt, dass das Sprachzentrum jetzt in der Beethovenstr. 23 ist."
        },
        "tasks": [
            {
                "id": "lt3_1",
                "statement": "Im August ist die Bäckerei zwei Wochen geschlossen.",
                "sign_title": "AN DER BÄCKEREI",
                "sign_text": "Liebe Kunden!\nWegen Urlaub bleibt unsere Bäckerei vom 1. bis 14. August geschlossen.\nAb dem 15. August sind wir wieder für Sie da.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Der Zettel besagt, dass die Bäckerei vom 1. bis 14. August (zwei Wochen) wegen Urlaub geschlossen ist."
            }
        ]
    }
]

# Schreiben Teil 1 Official Scenarios Bank
SCHREIBEN_TEIL1_SCENARIOS = [
    {
        "title": "Bodensee-Rundfahrt — Anmeldung",
        "desc": "Registration for a Bodensee tour with Eva Kadavy – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Ihre Freundin, Eva Kadavy, macht mit ihrem Mann und ihren beiden Söhnen (8 und 11 Jahre alt) Urlaub in Seeheim.\n\nIm Reisebüro bucht sie für den nächsten Sonntag eine Busfahrt um den Bodensee.\n\nFrau Kadavy hat keine Kreditkarte.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie Ihrer Freundin und schreiben Sie die fünf fehlenden Informationen in das Formular.",
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

# Schreiben Teil 2 Official Scenarios Bank
SCHREIBEN_TEIL2_SCENARIOS = [
    {
        "title": "Dresden besuchen — Touristeninformation",
        "desc": "Message to the tourist information office about visiting Dresden – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie möchten im August Dresden besuchen. Schreiben Sie an die Touristeninformation.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Warum schreiben Sie?",
            "2. Bitten Sie: Informationen über Filme, Museen usw. (Kulturprogramm).",
            "3. Fragen Sie: Hoteladressen?"
        ],
        "prompt": "Sehr geehrte Damen und Herren,\n\nich möchte im August Dresden besuchen und plane eine Reise. Könnten Sie mir bitte Informationen über das Kulturprogramm (Museen, Filme usw.) schicken? Haben Sie auch Empfehlungen für Hoteladressen?\n\nMit freundlichen Grüßen,\n[Dein Name]"
    }
]

# Sidebar Navigation State Management
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

# Sidebar Rendering
with st.sidebar:
    st.markdown("<h3 style='margin:0; font-size:1.30rem; color:#ffffff;'>German A1 Learning</h3>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.1rem; font-weight:700; color:#e2e8f0; margin-bottom:12px;'>Navigation</p>", unsafe_allow_html=True)
    
    # Custom Framed Left-Justified Navigation Buttons with Pastel Frames & Black Font
    for opt in nav_options:
        is_active = (st.session_state.nav_choice == opt)
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
        <div class="hero-badge">✨ MY GERMAN STUDY BUDDY</div>
        <div class="hero-title">German A1 Learning Dashboard</div>
        <div class="hero-subtitle">Explore interactive modules, practice materials, and master the Goethe A1 curriculum.</div>
    </div>
    """, unsafe_allow_html=True)

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
        if st.button("🎲 Shuffle Random Word", use_container_width=True):
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
        "conjugations": [
            {{"pronoun": "ich", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}}
        ],
        "perfekt_tense": {{
            "formula": "hat/ist + Partizip II",
            "sample_sentence_de": "German Perfekt sentence",
            "sample_sentence_en": "English Perfekt sentence"
        }},
        "comparative_superlative": "N/A",
        "common_phrases": [
            {{"phrase_de": "German phrase", "phrase_en": "English translation"}}
        ],
        "grammar_notes": "Important A1 grammar note"
    }}
    """

    try:
        raw_json = generate_cached_content(prompt, is_json=True)
        data = json.loads(raw_json)

        if not st.session_state.get("show_card_back", False):
            st.markdown(f"""
            <div class="flashcard-front-box">
                <p style="color: #7dd3fc; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 8px;">⭐ {selected_main_cat} / {selected_sub_cat} ⭐</p>
                <div class="flashcard-word-title">{data.get("word", active_word)}</div>
                <p style="color: #e2e8f0; font-size: 1rem; margin-bottom: 0px;">Click speaker icon for instant audio playback, or flip card for details.</p>
            </div>
            """, unsafe_allow_html=True)
            
            c_aud_front = st.columns([0.5, 10])
            with c_aud_front[0]:
                if st.button("🔊", key="audio_front_btn"):
                    play_direct_audio(active_word, "front_word")
            with c_aud_front[1]:
                st.caption(f"Listen to pronunciation of **{active_word}**")

        else:
            st.markdown(f"""
            <div class="flashcard-back-box">
                <p style="color: #1e3a8a; font-weight: 700; font-size: 0.95rem; letter-spacing: 0.05em; margin-bottom: 2px;">⭐ {selected_main_cat} / {selected_sub_cat}</p>
                <div class="flashcard-back-title">{data.get("word", active_word)}</div>
                <div class="meaning-subtitle">Meaning: <b>{data.get("english_meaning", "")}</b></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Part of Speech", data.get("part_of_speech", "N/A"))
            c2.metric("Gender", data.get("gender", "N/A"))
            c3.metric("Plural Form", data.get("plural_form", "N/A"))
            c4.metric("Comp. / Superlative", data.get("comparative_superlative", "N/A"))

            perf = data.get("perfekt_tense", {})
            st.success(f"⏳ **Perfekt Tense:** `{perf.get('formula', 'N/A')}`")

            st.info(f"💡 **Grammar Notes & Rules:** {data.get('grammar_notes', 'N/A')}")

    except Exception as e:
        st.error(f"Error compiling flashcard details: {str(e)}")

    st.divider()

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        if st.button("🔄 Flip Flashcard (Front / Back)", use_container_width=True, type="primary"):
            st.session_state.show_card_back = not st.session_state.get("show_card_back", False)
            st.rerun()

    with col_f2:
        if st.button("🎲 Random Word in Deck", use_container_width=True):
            actual_pool = [w for w in available_words if w != "ALL"]
            st.session_state.current_flashcard_word = random.choice(actual_pool) if actual_pool else "sein"
            st.session_state.show_card_back = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    st.markdown('<div class="section-header-box">📖 Core Grammar Practice & Exercises</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Core Grammar Practice & Exercises")
    st.write("Review class handbook modules with rigorous bullet points and targeted practice questions.")

    handbook_lessons = [
        "Lesson 1: German Alphabet, Pronunciation, and Article Recognition",
        "Lesson 2: German Noun Gender and Everyday Word Patterns",
        "Lesson 3: Singular and Plural Forms in Daily German",
        "Lesson 4: Personal Introductions and Basic Identity Information"
    ]

    selected_lesson = st.selectbox("Select Handbook Lesson to Review & Practice:", handbook_lessons, key="grammar_lesson_sel")

    if st.button("📖 Load Rigorous Review & Practice Exercises", type="primary"):
        with st.spinner("Gem is compiling clean bulleted notes and practice exercises..."):
            prompt = f"""
            Create a detailed study review & 5-exercise package for '{selected_lesson}'.
            Return strict JSON with this exact schema:
            {{
                "lesson_title": "{selected_lesson}",
                "lesson_explanation": "Provide a clean bulleted guide explaining '{selected_lesson}'.",
                "exercises_mc": [
                    {{"id": "mc1", "question": "Question 1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct and why other options are incorrect..."}}
                ]
            }}
            """
            try:
                json_str = generate_cached_content(prompt, is_json=True)
                st.session_state.active_grammar_module = json.loads(json_str)
            except Exception as e:
                st.error(f"Error generating grammar module: {str(e)}")

    if "active_grammar_module" in st.session_state:
        mod = st.session_state.active_grammar_module
        st.markdown(f"### 📘 Comprehensive Lesson Review: {mod['lesson_title']}")
        st.markdown(mod["lesson_explanation"])

        st.divider()
        st.subheader("📝 Practice Exercises")

        mc_user_answers = {}
        for idx, q in enumerate(mod.get("exercises_mc", []), start=1):
            st.markdown(f"**Q{idx}. {q['question']}**")
            mc_user_answers[q['id']] = st.radio(f"Select answer for Q{idx}:", q['options'], key=f"rad_grammar_{q['id']}")

        if st.button("🚀 Submit Answers & View Explanations", type="primary"):
            st.markdown("### 📊 Correct Answers & Detailed Explanations")
            for idx, q in enumerate(mod.get("exercises_mc", []), start=1):
                u_ans = mc_user_answers.get(q['id'])
                if u_ans == q['correct']:
                    st.success(f"**Q{idx}: Correct!** (`{q['correct']}`) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['correct']}`\n\n💡 **Explanation / Correction:** {q['explanation']}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="section-header-box">📖 Goethe A1 Lesen (Reading)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Goethe A1 Lesen Practice (Reading)")

    l_tab1, l_tab2, l_tab3 = st.tabs([
        "Teil 1: Short Messages", 
        "Teil 2: Classified Ads", 
        "Teil 3: Public Signs"
    ])

    with l_tab1:
        st.markdown("**Teil 1 (Kurze Mitteilungen):** Select scenario or refresh to generate brand-new alternative scenarios and questions.")
        
        if "dyn_lesen_t1" not in st.session_state or not isinstance(st.session_state.dyn_lesen_t1, list):
            st.session_state.dyn_lesen_t1 = list(LESEN_TEIL1_SCENARIOS)

        valid_lesen_t1 = [s for s in st.session_state.dyn_lesen_t1 if isinstance(s, dict) and "title" in s]
        
        col_lt1_sel, col_lt1_ref = st.columns([4, 1])
        with col_lt1_sel:
            selected_lesen_t1_title = st.selectbox("📂 **Select Lesen Teil 1 Scenario Set:**", [s["title"] for s in valid_lesen_t1], key="lesen_t1_sel")
        with col_lt1_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_lesen_t1", use_container_width=True):
                with st.spinner("Generating fresh alternative Lesen Teil 1 scenario and updated questions via AI..."):
                    try:
                        prompt = "Generate a completely new Goethe A1 Lesen Teil 1 scenario set containing a title, desc, text1_label, text1, text2_label, text2, and 3 questions (each with id, statement, options ['richtig', 'falsch'], answer, and explanation). Return strict JSON format as a single object: {\"title\": \"...\", \"desc\": \"...\", \"text1_label\": \"...\", \"text1\": \"...\", \"text2_label\": \"...\", \"text2\": \"...\", \"questions\": [...]}"
                        res = generate_dynamic_content(prompt, is_json=True)
                        new_scen = json.loads(res)
                        if isinstance(new_scen, dict) and "title" in new_scen:
                            st.session_state.dyn_lesen_t1.append(new_scen)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to refresh: {str(e)}")

        selected_lesen_t1_obj = next((s for s in valid_lesen_t1 if s["title"] == selected_lesen_t1_title), valid_lesen_t1[0])
        
        st.info(f"📌 **Description:** {selected_lesen_t1_obj['desc']}")

        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #bae6fd; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 8px;">✉️ {selected_lesen_t1_obj.get('text1_label', 'E-Mail')}</div>
            <p style="white-space: pre-line; color: #334155; margin-bottom: 0px;">{selected_lesen_t1_obj['text1']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #bae6fd; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 8px;">📄 {selected_lesen_t1_obj.get('text2_label', 'Brief')}</div>
            <p style="white-space: pre-line; color: #334155; margin-bottom: 0px;">{selected_lesen_t1_obj['text2']}</p>
        </div>
        """, unsafe_allow_html=True)

        ans_lt1 = {}
        for idx, q in enumerate(selected_lesen_t1_obj["questions"], start=1):
            st.markdown(f"**Task {idx}: {q['statement']}**")
            ans_lt1[q["id"]] = st.radio("Wählen Sie:", q["options"], key=f"rad_lt1_{selected_lesen_t1_title}_{q['id']}")

        if st.button("✔ Submit Lesen Teil 1 & View Corrections", type="primary", key="sub_lt1"):
            score = 0
            for idx, q in enumerate(selected_lesen_t1_obj["questions"], start=1):
                u_ans = ans_lt1.get(q["id"])
                if u_ans == q["answer"]:
                    score += 1
                    st.success(f"**Task {idx}: Correct!** (`{q['answer']}`) — {q['explanation']}")
                else:
                    st.error(f"**Task {idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['answer']}`\n\n💡 **Explanation:** {q['explanation']}")
            st.metric("Score", f"{score} / {len(selected_lesen_t1_obj['questions'])}")

    with l_tab2:
        st.markdown("**Teil 2 (Zuordnung):** Classified Ads matching.")
        selected_lesen_t2_obj = LESEN_TEIL2_SCENARIOS[0]
        ans_lt2 = {}
        for idx, task in enumerate(selected_lesen_t2_obj["tasks"], start=1):
            st.markdown(f"**{task['situation']}**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"🌐 **{task['site_a_url']}**\n{task['site_a']}")
            with col_b:
                st.markdown(f"🌐 **{task['site_b_url']}**\n{task['site_b']}")
            ans_lt2[task["id"]] = st.radio(f"Select website for task {idx}:", ["Website A", "Website B"], key=f"rad_lt2_{task['id']}")

        if st.button("✔ Submit Lesen Teil 2 & View Corrections", type="primary", key="sub_lt2"):
            for idx, t in enumerate(selected_lesen_t2_obj["tasks"], start=1):
                u_ans = ans_lt2.get(t["id"])
                if u_ans == t["answer"]:
                    st.success(f"**Task {idx}: Correct!** (`{t['answer']}`) — {t['explanation']}")
                else:
                    st.error(f"**Task {idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{t['answer']}`\n\n💡 **Explanation:** {t['explanation']}")

    with l_tab3:
        st.markdown("**Teil 3 (Öffentliche Hinweise):** Public Signs.")
        selected_lesen_t3_obj = LESEN_TEIL3_SCENARIOS[0]
        ans_lt3 = {}
        for idx, task in enumerate(selected_lesen_t3_obj["tasks"], start=1):
            st.markdown(f"**{idx}. {task['statement']}**")
            st.markdown(f"**{task['sign_title']}**\n> {task['sign_text']}")
            ans_lt3[task["id"]] = st.radio(f"Antwort {idx}:", task["options"], key=f"rad_lt3_{task['id']}")

        if st.button("✔ Submit Lesen Teil 3 & View Corrections", type="primary", key="sub_lt3"):
            for idx, t in enumerate(selected_lesen_t3_obj["tasks"], start=1):
                u_ans = ans_lt3.get(t["id"])
                if u_ans == t["answer"]:
                    st.success(f"**Task {idx}: Correct!** (`{t['answer']}`) — {t['explanation']}")
                else:
                    st.error(f"**Task {idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['answer']}`\n\n💡 **Explanation:** {t['explanation']}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="section-header-box">🎧 Goethe A1 Hören (Listening)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Goethe A1 Hören Practice (Listening)")

    h_tab1, h_tab2 = st.tabs(["Teil 1: Dialogues", "Teil 2: Announcements"])

    with h_tab1:
        st.markdown("**Teil 1:** Short everyday dialogues.")
        selected_scenario_title = st.selectbox("Select Hören Teil 1 Scenario:", [s["title"] for s in HOREN_TEIL1_SCENARIOS])
        sample_script = "Kunde: Guten Tag, was kostet diese Jacke?\nVerkäuferin: Guten Tag, die Jacke kostet 49 Euro.\nKunde: Danke schön."
        st.audio(generate_german_audio_bytes(sample_script), format="audio/mp3")
        ans_h1 = st.radio("Was kostet die Jacke?", ["a) 39 Euro", "b) 49 Euro", "c) 59 Euro"], key="h1_rad")
        if st.button("Submit Hören Teil 1", type="primary"):
            if "49 Euro" in ans_h1:
                st.success("Correct! The jacket costs 49 Euro.")
            else:
                st.error("Incorrect. Correct answer is 49 Euro as heard in the dialogue.")

    with h_tab2:
        st.markdown("**Teil 2:** Station and airport announcements.")
        sample_ann = "Achtung am Gleis 3. Der ICE nach München hat 10 Minuten Verspätung."
        st.audio(generate_german_audio_bytes(sample_ann), format="audio/mp3")
        ans_h2 = st.radio("Der Zug nach München fährt pünktlich ab.", ["richtig", "falsch"], key="h2_rad")
        if st.button("Submit Hören Teil 2", type="primary"):
            if ans_h2 == "falsch":
                st.success("Correct! The announcement stated it has 10 minutes delay.")
            else:
                st.error("Incorrect. The train has a delay.")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="section-header-box">✍️ Goethe A1 Schreiben (Writing)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Goethe A1 Schreiben Practice")

    s_tab1, s_tab2 = st.tabs(["Teil 1: Formular", "Teil 2: Mitteilung"])

    with s_tab1:
        st.markdown("**Teil 1 (Formular):** Fill out forms.")
        if "dyn_schreiben_t1" not in st.session_state or not isinstance(st.session_state.dyn_schreiben_t1, list):
            st.session_state.dyn_schreiben_t1 = list(SCHREIBEN_TEIL1_SCENARIOS)

        valid_schreiben_t1 = [s for s in st.session_state.dyn_schreiben_t1 if isinstance(s, dict) and "title" in s]
        selected_schreiben_t1_title = st.selectbox("Select Schreiben Teil 1 Scenario:", [s["title"] for s in valid_schreiben_t1], key="schreiben_t1_select")
        selected_schreiben_t1_obj = next((s for s in valid_schreiben_t1 if s["title"] == selected_schreiben_t1_title), valid_schreiben_t1[0])

        st.info(selected_schreiben_t1_obj['aufgabe'])
        user_form_inputs = {}
        for field in selected_schreiben_t1_obj["fields"]:
            if not field.get("is_gap", False):
                st.text_input(field["label"], value=field.get("default", ""), disabled=True, key=f"dis_{field['id']}")
            else:
                if "options" in field:
                    user_form_inputs[field["id"]] = st.radio(field["label"], field["options"], key=f"gap_rad_{field['id']}")
                else:
                    user_form_inputs[field["id"]] = st.text_input(field["label"], placeholder=field.get("placeholder", "..."), key=f"gap_inp_{field['id']}")

        if st.button("✔ Check Form & View Corrections", type="primary", key="check_form_btn"):
            for field in selected_schreiben_t1_obj["fields"]:
                if field.get("is_gap", False):
                    u_val = str(user_form_inputs.get(field["id"], "")).strip().lower()
                    c_val = str(field["answer"]).strip().lower()
                    if c_val in u_val:
                        st.success(f"**{field['label']}** Correct! (`{field['answer']}`)")
                    else:
                        st.error(f"**{field['label']}** Incorrect. Your answer: `{user_form_inputs.get(field['id'], '')}` | Correct: `{field['answer']}`\n\n💡 **Correction guidance:** Ensure exact information from the prompt is entered.")

    with s_tab2:
        st.markdown("**Teil 2 (Mitteilung):** Write a short email.")
        selected_schreiben_t2_obj = SCHREIBEN_TEIL2_SCENARIOS[0]
        st.info(selected_schreiben_t2_obj['aufgabe_text'])
        for pt in selected_schreiben_t2_obj["points"]:
            st.markdown(f"• {pt}")

        u_email = st.text_area("Write your text here...", height=140, key="email_writing_area")
        if st.button("✔ Analyze text & View Corrections", type="primary", key="analyze_email_btn"):
            if u_email.strip():
                with st.spinner("Gem is analyzing your text..."):
                    try:
                        eval_prompt = f"TASK: {selected_schreiben_t2_obj['aufgabe_text']}\nSTUDENT TEXT: {u_email}\nEvaluate for A1 level, check if points are covered, and provide detailed corrections and explanations for any mistakes."
                        res = generate_dynamic_content(eval_prompt)
                        st.success("Evaluation & Corrections:")
                        st.write(res)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please write something first.")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="section-header-box">🗣️ Goethe A1 Sprechen (Speaking)</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Goethe A1 Sprechen Practice")
    st.write("Practice your speaking skills for Teil 1, Teil 2, and Teil 3 based on Goethe A1 exam standards.")

    sp_tab1, sp_tab2, sp_tab3 = st.tabs(["Teil 1 — Sich vorstellen", "Teil 2 — Fragen & Antworten", "Teil 3 — Bitten formulieren"])

    with sp_tab1:
        st.markdown("### Teil 1 — Sich vorstellen")
        st.markdown("Sich mit Stichwörtern vorstellen: Name, Alter, Land, Wohnort, Sprachen, Beruf und Hobby, dann einen Namen buchstabieren und eine Nummer...")
        rec_t1 = mic_recorder(start_prompt="Record Self-Introduction 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t1")
        if rec_t1:
            st.audio(rec_t1['bytes'], format='audio/wav')
            if st.button("Evaluate Introduction"):
                st.success("Audio recorded successfully! Keep practicing clear pronunciation.")

    with sp_tab2:
        st.markdown("### Teil 2 — Um Informationen bitten und Informationen geben")
        st.markdown("Mit Themenkarten zu zwei Themen je eine Frage stellen und die Fragen des Partners beantworten.")
        if st.button("Draw Topic Card"):
            st.info("Thema: **Einkaufen** | Stichwort: **Supermarkt**")
        rec_t2 = mic_recorder(start_prompt="Record Question 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t2")
        if rec_t2:
            st.audio(rec_t2['bytes'], format='audio/wav')

    with sp_tab3:
        st.markdown("### Teil 3 — Bitten formulieren und darauf reagieren")
        st.markdown("Mit Bildkarten zwei Bitten formulieren und auf die Bitten des Partners reagieren.")
        st.info("🎴 Bildkarte: **Regenschirm leihen**")
        rec_t3 = nag_rec = mic_recorder(start_prompt="Record Request 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t3")
        if rec_t3:
            st.audio(rec_t3['bytes'], format='audio/wav')

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. A1 & A2 SHORT STORIES
# ----------------------------------------------------
elif nav_choice == "📖 A1 & A2 Short Stories":
    st.markdown('<div class="section-header-box">📖 A1 & A2 Short Stories</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Enchanted Storybook Reader")
    st.write("Immerse yourself in A1 fairy tales and A2 classic fictions with complete audio narration.")

    story_level = st.radio("Select CEFR Level:", ["A1 Level (Fairy Tales)", "A2 Level (Classic Fictions)"], horizontal=True)

    if story_level == "A1 Level (Fairy Tales)":
        story_title = st.selectbox("Select Story:", ["Aschenputtel (Cinderella)", "Rotkäppchen (Little Red Riding Hood)"])
    else:
        story_title = st.selectbox("Select Story:", ["Moby Dick", "Die Schatzinsel (Treasure Island)"])

    if st.button("📖 Load Story", type="primary"):
        st.session_state.active_story_text = f"Es war einmal in einer wunderschönen Stadt... ({story_title})"

    if "active_story_text" in st.session_state:
        st.info(st.session_state.active_story_text)
        col_s_aud, _ = st.columns([0.5, 10])
        with col_s_aud:
            if st.button("🔊", key="story_audio_btn"):
                play_direct_audio(st.session_state.active_story_text, "story_audio")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 9. GEM AI TUTOR
# ----------------------------------------------------
elif nav_choice == "🐱 Gem AI Tutor":
    st.markdown('<div class="section-header-box">🐱 Gem — Your AI German Tutor</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Chat with Gem")
    st.write("Ask Gem any questions about German grammar, vocabulary, exam preparation, or general explanations.")

    if "gem_chat_messages" not in st.session_state:
        st.session_state.gem_chat_messages = []

    for msg in st.session_state.gem_chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_prompt := st.chat_input("Ask Gem a question about German..."):
        st.session_state.gem_chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Gem is thinking..."):
                try:
                    response_text = generate_dynamic_content(user_prompt)
                    st.write(response_text)
                    st.session_state.gem_chat_messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
