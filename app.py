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
    initial_sidebar_state="collapsed"
)

# Custom Dark Theme & Dropdown Styling (Fixing BaseWeb Popups & Text Contrast)
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

    /* Selectbox Input Box Styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1f2937 !important;
        border-radius: 10px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }
    .stSelectbox span, .stSelectbox div[data-baseweb="select"] span {
        color: #f8fafc !important;
    }

    /* Open Dropdown Popup List Container & Options Dark Theme Fix */
    div[data-baseweb="menu"] {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="menu"] ul {
        background-color: #111827 !important;
    }
    div[data-baseweb="menu"] li, div[data-baseweb="menu"] div {
        background-color: #111827 !important;
        color: #f8fafc !important;
    }
    div[data-baseweb="menu"] li:hover, div[data-baseweb="menu"] div[aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #60a5fa !important;
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
"""

# Navigation State Management
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "🏠 Study Dashboard"

nav_choice = st.session_state.nav_choice

# Helper function to render a top Back to Dashboard button on sub-pages
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
    st.write("Content removed.")
    st.markdown('</div>', unsafe_allow_html=True)
