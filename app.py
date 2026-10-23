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
    page_title="German A1 Learning Hub", 
    page_icon="🌻", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Glow Theme with Yellow, Pink, and Orange Neon Glow Accents
st.markdown("""
<style>
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

    [data-testid="stSidebar"] {
        display: none !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
        background: transparent !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.6rem !important;
    }

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
</style>
""", unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 **Missing Gemini API Key!** Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

SYSTEM_INSTRUCTION = """
You are Gem, an expert German tutor and official Goethe-Institut A1 examiner.
Provide comprehensive explanations based on the Schwert A1 German Class Handbook, plus expert insights, bullet points, and markdown tables.
When generating quiz questions, provide exactly a mix of multiple choice, fill-in-the-blank, sentence building, and translation. Always include detailed explanations for correct answers and feedback for incorrect answers.
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
    st.audio(b64_audio, format="audio/mp3")

# Exhaustive Schwert A1 Curriculum Lessons Database (40 Lessons from Handbook)
SCHWERT_A1_LESSONS_FULL = [
    "Lesson 1: Understanding German Alphabet, Pronunciation, and Article Recognition",
    "Lesson 2: Learning German Noun Gender and Everyday Word Patterns",
    "Lesson 3: Recognizing Singular and Plural Forms in Daily German",
    "Lesson 4: Reading Personal Introductions and Basic Identity Information",
    "Lesson 5: Building Simple German Sentences for Everyday Communication",
    "Lesson 6: Recognizing Present Tense Verb Patterns in Practical German",
    "Lesson 7: Working with sein and haben in Everyday Situations",
    "Lesson 8: Understanding Numbers, Prices, Dates, and Everyday Quantities",
    "Lesson 9: Reading Everyday Question Structures and Basic Information Requests",
    "Lesson 10: Recognizing Negation and Negative Sentences in Practical German",
    "Lesson 11: Exploring Object Sentences and Basic Accusative Structures",
    "Lesson 12: Reading Simple Descriptions of People, Places, and Things",
    "Lesson 13: Recognizing Possession, Ownership, and Family Relationships",
    "Lesson 14: Reading Time Expressions, Appointments, and Schedules",
    "Lesson 15: Understanding Daily Routine Patterns and Everyday Activities",
    "Lesson 16: Recognizing Commands, Requests, and Basic Instructions",
    "Lesson 17: Exploring Abilities, Obligations, and Everyday Modal Verbs",
    "Lesson 18: Reading Practical Sentences with Modal Verb Structures",
    "Lesson 19: Exploring Everyday Dative Structures and Indirect Objects",
    "Lesson 20: Reading Common Dative Expressions in Real-Life Communication",
    "Lesson 21: Understanding Location Expressions and Place Descriptions",
    "Lesson 22: Reading Movement and Position Patterns in Everyday German",
    "Lesson 23: Exploring Two-Way Prepositions and Directional Meaning",
    "Lesson 24: Reading Shopping, Money, and Price Communication",
    "Lesson 25: Connecting Simple Ideas with Basic German Connectors",
    "Lesson 26: Recognizing Reasons, Explanations, and Cause Structures",
    "Lesson 27: Reading Future Expressions and Everyday Planning Language",
    "Lesson 28: Exploring Past Events with haben and Perfekt Structures",
    "Lesson 29: Exploring Movement and Travel Narration with sein",
    "Lesson 30: Reading Everyday Past Narration and Simple Storytelling",
    "Lesson 31: Recognizing Separable Verb Patterns in Daily Communication",
    "Lesson 32: Exploring Comparisons, Preferences, and Basic Opinions",
    "Lesson 33: Reading Likes, Preferences, and Personal Interests",
    "Lesson 34: Recognizing Simple Subordinate Clauses and Verb-Final Patterns",
    "Lesson 35: Reading Simple Emails, Messages, and Digital Communication",
    "Lesson 36: Recognizing Everyday Conversation Patterns and Social Interaction",
    "Lesson 37: Recognizing and Correcting Common A1 Grammar Mistakes",
    "Lesson 38: Recognizing A1 Grammar in Authentic German Texts",
    "Lesson 39: Reading Everyday Public Signs, Instructions, and Survival German",
    "Lesson 40: CEFR A1 Mock Examination (Written Test)"
]

# Vocabulary Section Word Bank Side-by-Side (German - English)
A1_VOCABULARY_BANK = [
    ("gehen", "to go"),
    ("kommen", "to come"),
    ("sein", "to be"),
    ("haben", "to have"),
    ("arbeiten", "to work"),
    ("lernen", "to learn / study"),
    ("wohnen", "to live / reside"),
    ("sprechen", "to speak"),
    ("essen", "to eat"),
    ("trinken", "to drink"),
    ("lesen", "to read"),
    ("schreiben", "to write"),
    ("kaufen", "to buy"),
    ("verkaufen", "to sell"),
    ("verstehen", "to understand"),
    ("der Tisch", "the table"),
    ("die Lampe", "the lamp"),
    ("das Buch", "the book"),
    ("das Haus", "the house"),
    ("die Straße", "the street"),
    ("der Bahnhof", "the train station"),
    ("die Zeitung", "the newspaper"),
    ("das Handy", "the mobile phone"),
    ("der Computer", "the computer"),
    ("die Quittung", "the receipt"),
    ("das Wasser", "the water"),
    ("der Kaffee", "the coffee"),
    ("das Brot", "the bread"),
    ("die Milch", "the milk"),
    ("der Apfel", "the apple")
]

# State Initialization
if "selected_nav" not in st.session_state:
    st.session_state.selected_nav = "Core Grammar Practice & Exercises"
if "selected_lesson" not in st.session_state:
    st.session_state.selected_lesson = SCHWERT_A1_LESSONS_FULL[0]
if "grammar_quiz_active" not in st.session_state:
    st.session_state.grammar_quiz_active = False
if "grammar_quiz_questions" not in st.session_state:
    st.session_state.grammar_quiz_questions = []
if "grammar_quiz_index" not in st.session_state:
    st.session_state.grammar_quiz_index = 0
if "grammar_quiz_score" not in st.session_state:
    st.session_state.grammar_quiz_score = 0
if "grammar_quiz_complete" not in st.session_state:
    st.session_state.grammar_quiz_complete = False
if "user_quiz_answers" not in st.session_state:
    st.session_state.user_quiz_answers = {}

# Main Header Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">SCHWERT A1 GERMAN CLASS HANDBOOK & TUTOR</div>
    <div class="hero-title">Deutsch A1 Passive Fluency & Mastery</div>
    <div class="hero-subtitle">Natural Pattern Recognition, Comprehensive Grammar Explanations, Interactive Quizzes, and Memorized Word Bank</div>
</div>
""", unsafe_allow_html=True)

# Navigation Buttons
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("📖 Core Grammar Practice & Exercises", use_container_width=True):
        st.session_state.selected_nav = "Core Grammar Practice & Exercises"
        st.rerun()
with col_nav2:
    if st.button("🔤 Vocabulary Section (Word Bank)", use_container_width=True):
        st.session_state.selected_nav = "Vocabulary Section"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 1: CORE GRAMMAR PRACTICE & EXERCISES
# ---------------------------------------------------------
if st.session_state.selected_nav == "Core Grammar Practice & Exercises":
    st.markdown('<div class="section-header-box">Core Grammar Practice & Exercises Section</div>', unsafe_allow_html=True)
    
    # Dropdown List of Lessons
    selected_lesson_dropdown = st.selectbox(
        "Select A1 Lesson from Schwert Handbook:",
        SCHWERT_A1_LESSONS_FULL,
        index=SCHWERT_A1_LESSONS_FULL.index(st.session_state.selected_lesson) if st.session_state.selected_lesson in SCHWERT_A1_LESSONS_FULL else 0
    )
    
    if selected_lesson_dropdown != st.session_state.selected_lesson:
        st.session_state.selected_lesson = selected_lesson_dropdown
        st.session_state.grammar_quiz_active = False
        st.session_state.grammar_quiz_complete = False
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate Comprehensive Explanation using Gemini
    with st.spinner(f"Gem is preparing comprehensive explanations and expert insights for {st.session_state.selected_lesson}..."):
        explanation_prompt = f"""
        Act as an expert German tutor and Goethe-Institut examiner. Provide a comprehensive explanation for the A1 lesson: '{st.session_state.selected_lesson}' based on theSchwers A1 German Class Handbook.
        Include:
        - Thorough core grammar rules with bullet points.
        - Detailed examples and markdown comparison/rule tables.
        - Expert insights on top of the handbook so the student fully understands the concept.
        Keep formatting clean, professional, and structured.
        """
        lesson_explanation = generate_cached_content(explanation_prompt, is_json=False)

    st.markdown(f"""
    <div class="main-card">
        <h3>📚 Comprehensive Tutoring & Handbook Insights: {st.session_state.selected_lesson}</h3>
        <hr style="border-color: rgba(244,114,182,0.3);">
        {lesson_explanation}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quiz Section below each lesson (Total 20 questions: MC, Fill-in-blank, Sentence building, Translation)
    st.markdown('<div class="section-header-box">Interactive Mastery Quiz (20 Questions)</div>', unsafe_allow_html=True)
    
    if not st.session_state.grammar_quiz_active and not st.session_state.grammar_quiz_complete:
        if st.button("🚀 Start 20-Question Quiz for this Lesson", use_container_width=True):
            with st.spinner("Generating 20 targeted quiz questions (Multiple Choice, Fill-in-the-Blank, Sentence Building, Translation)..."):
                quiz_prompt = f"""
                Generate exactly 20 German A1 quiz questions for the lesson: '{st.session_state.selected_lesson}'.
                Use a combination of multiple choice, fill-in-the-blank, sentence building, and translation.
                Return ONLY valid JSON format matching this schema:
                [
                  {{
                    "id": 1,
                    "type": "Multiple Choice",
                    "question": "Question text here",
                    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
                    "correct_answer": "A) ...",
                    "explanation": "Detailed explanation why this is correct."
                  }},
                  ... (20 total questions)
                ]
                """
                quiz_json_str = generate_cached_content(quiz_prompt, is_json=True)
                try:
                    # Clean json string if wrapped in markdown code blocks
                    cleaned_json = quiz_json_str.strip()
                    if cleaned_json.startswith("```json"):
                        cleaned_json = cleaned_json[7:]
                    if cleaned_json.endswith("```"):
                        cleaned_json = cleaned_json[:-3]
                    
                    questions_data = json.loads(cleaned_json.strip())
                    st.session_state.grammar_quiz_questions = questions_data
                    st.session_state.grammar_quiz_active = True
                    st.session_state.grammar_quiz_index = 0
                    st.session_state.grammar_quiz_score = 0
                    st.session_state.user_quiz_answers = {}
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error parsing quiz data: {ex}\nRaw output: {quiz_json_str}")
    
    elif st.session_state.grammar_quiz_active and not st.session_state.grammar_quiz_complete:
        q_idx = st.session_state.grammar_quiz_index
        questions = st.session_state.grammar_quiz_questions
        
        if q_idx < len(questions):
            q = questions[q_idx]
            st.markdown(f"""
            <div class="main-card">
                <h4>Question {q_idx + 1} of {len(questions)} ({q.get('type', 'Quiz')})</h4>
                <p style="font-size: 1.15rem; font-weight: 600; color: #fef08a;">{q['question']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Answer input based on question type
            q_type = q.get('type', 'Multiple Choice')
            user_ans = None
            
            if "Multiple Choice" in q_type or 'options' in q:
                options = q.get('options', [])
                user_ans = st.radio("Select your answer:", options, key=f"q_radio_{q_idx}")
            else:
                user_ans = st.text_input("Type your answer:", key=f"q_text_{q_idx}")
            
            col_submit, col_skip = st.columns([2, 1])
            with col_submit:
                if st.button("Submit Answer", key=f"submit_{q_idx}", use_container_width=True):
                    if not user_ans:
                        st.warning("Please provide an answer before submitting.")
                    else:
                        correct = q['correct_answer'].strip().lower()
                        chosen = str(user_ans).strip().lower()
                        
                        # Evaluate correctness
                        is_correct = False
                        if chosen == correct or chosen.startswith(correct[:3]):
                            is_correct = True
                        
                        if is_correct:
                            st.success("✅ Correct! Excellent work.")
                            st.session_state.grammar_quiz_score += 1
                        else:
                            st.error(f"❌ Incorrect. The correct answer is: **{q['correct_answer']}**")
                            st.info(f"💡 Explanation: {q['explanation']}")
                        
                        st.session_state.user_quiz_answers[q_idx] = {
                            "question": q['question'],
                            "chosen": user_ans,
                            "correct": q['correct_answer'],
                            "is_correct": is_correct,
                            "explanation": q['explanation']
                        }
                        
                        time.sleep(1.5)
                        if q_idx + 1 < len(questions):
                            st.session_state.grammar_quiz_index += 1
                        else:
                            st.session_state.grammar_quiz_complete = True
                            st.session_state.grammar_quiz_active = False
                        st.rerun()

        progress_pct = (q_idx) / len(questions)
        st.progress(progress_pct)
        st.caption(f"Progress: Question {q_idx + 1} of {len(questions)} | Current Score: {st.session_state.grammar_quiz_score}/{q_idx}")

    elif st.session_state.grammar_quiz_complete:
        final_score = st.session_state.grammar_quiz_score
        total_q = len(st.session_state.grammar_quiz_questions)
        
        st.markdown(f"""
        <div class="main-card" style="text-align: center;">
            <h2>🎉 Quiz Completed for {st.session_state.selected_lesson}!</h2>
            <h1 style="font-size: 3rem; color: #fef08a; margin: 15px 0;">Scored {final_score}/{total_q}</h1>
            <p style="font-size: 1.1rem; color: #94a3b8;">Review your performance below and continue mastering your A1 German fluency!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.grammar_quiz_active = False
            st.session_state.grammar_quiz_complete = False
            st.session_state.grammar_quiz_index = 0
            st.session_state.grammar_quiz_score = 0
            st.rerun()

# ---------------------------------------------------------
# SECTION 2: VOCABULARY SECTION (MEMORIZED WORD BANK)
# ---------------------------------------------------------
elif st.session_state.selected_nav == "Vocabulary Section":
    st.markdown('<div class="section-header-box">Vocabulary Section — Memorized Word Bank</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-card">
        <p style="font-size: 1.05rem; color: #f8fafc; margin-bottom: 15px;">
            Here is your exhaustive Schwert A1 Memorized Word Bank. German and English translations are placed side-by-side with pronunciation audio support for fast retention and Passive Fluency mastery.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display Side-by-Side Word Bank Table
    for idx, (ger_word, eng_trans) in enumerate(A1_VOCABULARY_BANK):
        col_w1, col_w2, col_w3 = st.columns([3, 3, 1])
        with col_w1:
            st.markdown(f"<div class='main-card' style='padding: 12px; margin-bottom: 6px; font-weight: 700; color: #fef08a;'>🇩🇪 {ger_word}</div>", unsafe_allow_html=True)
        with col_w2:
            st.markdown(f"<div class='main-card' style='padding: 12px; margin-bottom: 6px; font-weight: 600; color: #f8fafc;'>🇬🇧 {eng_trans}</div>", unsafe_allow_html=True)
        with col_w3:
            if st.button("🔊", key=f"audio_word_{idx}", use_container_width=True):
                play_direct_audio(ger_word, f"word_{idx}")

# Footer
st.markdown("<br><hr style='border-color: rgba(244,114,182,0.2);'><p style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>CB Language and Review Academy — German Passive Fluency A1 Handbook & Tutor Hub</p>", unsafe_allow_html=True)
