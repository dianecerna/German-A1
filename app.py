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

# Custom Sunflower Wallpaper & Pastel Theme with Dynamic Flashcard Styling
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

    /* Relaxed Comfort Spacing */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.8rem !important;
    }

    /* Pastel Yellow, Pink & Orange Gradient Custom Button Styling */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #fef08a 0%, #f472b6 50%, #fb923c 100%) !important;
        border: 1px solid rgba(244, 114, 182, 0.5) !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #7c2d12 !important;
        box-shadow: 0 4px 15px rgba(251, 146, 60, 0.2) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 4px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fde047 0%, #ec4899 50%, #f97316 100%) !important;
        border-color: #ec4899 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(244, 63, 94, 0.3) !important;
        color: #ffffff !important;
    }

    /* Compact Main Content Cards / Containers */
    .main-card {
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        margin-bottom: 12px;
        border: 1px solid rgba(251, 146, 60, 0.3);
    }
    
    /* Hero Banner with Pastel Gradient Glow Border */
    .hero-banner {
        background: linear-gradient(135deg, rgba(254, 240, 138, 0.2) 0%, rgba(244, 114, 182, 0.15) 50%, rgba(251, 146, 60, 0.2) 100%);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 24px;
        color: #1e293b;
        margin-bottom: 16px;
        border: 2px solid #f472b6;
        box-shadow: 0 8px 25px rgba(244, 114, 182, 0.2);
    }
    .hero-badge {
        display: inline-block;
        background: #fdf2f8;
        border: 1px solid #f472b6;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        color: #db2777;
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

    /* Section Header Box */
    .section-header-box {
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(8px);
        border-left: 5px solid #f472b6;
        border-top: 1px solid #fed7aa;
        border-right: 1px solid #fed7aa;
        border-bottom: 1px solid #fed7aa;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 12px;
        color: #c2410c;
        font-size: 1.2rem;
        font-weight: 800;
        box-shadow: 0 4px 15px rgba(251, 146, 60, 0.15);
    }

    /* Clean Minimalist Dropdown Box Design */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #f472b6 !important;
        border-radius: 8px !important;
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
        background-color: #fef08a40 !important;
        color: #c2410c !important;
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

# Navigation State Management
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "🏠 Study Dashboard"

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
# 2. MASTER GOETHE WORD ENGINE (CONTENT REMOVED AS REQUESTED)
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    render_top_back_button()
    st.markdown('<div class="section-header-box">🌻 Master Goethe Word Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Content removed.")
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
                response = generate_cached_content(user_prompt)
                st.write(response)
                st.session_state.gem_chat_messages.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)
