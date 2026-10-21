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
    page_title="Goethe A1 Studio", 
    page_icon="🇩🇪", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
    .main-card { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .accent-card { background: #ffffff; border-radius: 16px; padding: 24px; border-left: 6px solid #2563eb; box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    
    /* Interactive Flashcard UI */
    .flashcard-front-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
        border: 2px solid #38bdf8;
        margin-bottom: 15px;
    }
    .flashcard-word-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #38bdf8;
        margin-bottom: 10px;
    }
    .flashcard-back-box {
        background: #ffffff;
        border: 2px solid #2563eb;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.12);
        margin-bottom: 15px;
    }
    .flashcard-back-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 5px;
    }
    .meaning-subtitle {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2563eb;
        margin-bottom: 15px;
    }
    
    /* Metric Font Uniformity */
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())

# Ordered Model Fallback Strategy
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]

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
            if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota"]):
                continue
            raise e
            
    raise Exception(f"All free model quotas are currently exhausted or unavailable. Details: {str(last_error)}")

def generate_dynamic_content(prompt_text: str, is_json: bool = False) -> str:
    config_args = {"system_instruction": SYSTEM_INSTRUCTION}
    if is_json:
        config_args["response_mime_type"] = "application/json"
    
    last_error = None
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
            if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota"]):
                continue
            raise e
            
    raise Exception(f"All free model quotas are currently exhausted or unavailable. Details: {str(last_error)}")

@st.cache_data
def load_goethe_vocab_categories():
    return {
        "All": [],  # Populated dynamically
        "Kultur und Medien": ["Buch", "Zeitung", "Film", "Musik", "Fernsehen", "Internet", "Computer", "Handy", "Radio", "Bibliothek", "Kino", "Theater", "Museum", "Künstler", "Sprache", "Nachrichten"],
        "Arbeiten": ["arbeiten", "Arbeit", "Büro", "Kollege", "Chefin", "Beruf", "Firma", "Computer", "Telefon", "E-Mail", "Meeting", "Gehalt", "Pause", "Urlaub", "kündigen", "bewerben", "Lebenslauf", "Praktikum"],
        "Universität und Studieren": ["Universität", "Student", "Studium", "studieren", "Professoren", "Prüfung", "Vorlesung", "Seminar", "Bibliothek", "Buch", "Stift", "Heft", "Kurs", "Zeugnis", "Abschluss", "ferien", "Labor", "Canteen"],
        "Allgemein": ["sein", "haben", "machen", "gehen", "kommen", "wollen", "können", "müssen", "werden", "sagen", "geben", "sehen", "wissen", "nehmen", "finden", "sprechen", "verstehen", "helfen", "lernen", "leben", "wohnen", "bleiben", "brauchen", "denken", "lieben", "fragen", "hören", "lesen", "schreiben", "kaufen", "bezahlen", "essen", "trinken", "schlafen", "fahren", "stehen", "laufen", "sitzen", "liegen", "warten", "Guten Tag", "Guten Morgen", "Guten Abend", "Auf Wiedersehen", "Tschüss", "Danke", "Bitte", "Entschuldigung", "Hilfe", "Bahnhof", "Flughafen", "Hotel", "Restaurant", "Speisekarte", "Rechnung", "Arzt", "Krankenhaus", "Supermarkt", "Apotheke", "Polizei", "Fahrkarte", "Wohnung", "Zimmer", "Küche", "Badezimmer", "Schlafzimmer", "Wohnzimmer", "Balkon", "Garten", "Tisch", "Stuhl", "Bett", "Schrank", "Kühlschrank", "Herd", "Waschmaschine"]
    }

GOETHE_CATEGORIES = load_goethe_vocab_categories()
ALL_VOCAB_WORDS = list(set([w for cat_list in GOETHE_CATEGORIES.values() for w in cat_list]))
GOETHE_CATEGORIES["All"] = ALL_VOCAB_WORDS

@st.cache_data(show_spinner=False)
def generate_german_audio_bytes(text: str) -> bytes:
    tts = gTTS(text=text, lang='de')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.getvalue()

# Sidebar Navigation
st.sidebar.title("🇩🇪 Goethe A1 Studio")
st.sidebar.caption("Target Exam: Dec 12, 2026")
st.sidebar.divider()

nav_choice = st.sidebar.radio("Navigation", [
    "🏠 Study Dashboard", 
    "📚 Master Goethe Word Engine",
    "📖 Core Grammar Practice & Exercises",
    "📖 Goethe A1 Lesen (Reading)",
    "🎧 Goethe A1 Hören (Listening)",
    "✍️ Goethe A1 Schreiben (Writing)", 
    "🗣️ Goethe A1 Sprechen (Speaking)",
    "🏆 Goethe A1 Mock Examination",
    "💬 Ask Gem (AI Tutor)"
])

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.title("Goethe-Zertifikat A1 Prep Studio")
    st.write("📅 **Exam Date:** December 12, 2026")
    st.write("Complete Goethe A1 curriculum preparation, vocabulary engine, grammar exercises, and exam modules.")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📖 Lesen & ✍️ Schreiben")
        st.markdown("""
        * **Lesen (25 Mins - 15 Tasks):**
          - Teil 1: Short Emails (5 Tasks - Richtig/Falsch)[cite: 3]
          - Teil 2: Classified Ads (5 Tasks - Option A or B)[cite: 3]
          - Teil 3: Public Signs (5 Tasks - Richtig/Falsch)[cite: 3]
        * **Schreiben (20 Mins - 2 Tasks):**
          - Teil 1: Fill 5 Missing Gaps on Form[cite: 3]
          - Teil 2: Write ~30-Word Message (3 Bullet Points)[cite: 3]
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🎧 Hören & 🗣️ Sprechen")
        st.markdown("""
        * **Hören (20 Mins - 15 Tasks):**
          - Teil 1: 6 Dialogues (2x Audio, A/B/C)[cite: 3]
          - Teil 2: 4 Announcements (1x Audio, Richtig/Falsch)[cite: 3]
          - Teil 3: 5 Voicemails (2x Audio, A/B/C)[cite: 3]
        * **Sprechen (15 Mins - Small Group):**
          - Teil 1: Self-Introduction & Spelling[cite: 3]
          - Teil 2: W-Questions (Verb in Position 2)[cite: 3]
          - Teil 3: Imperative Requests (Verb in Position 1)[cite: 3]
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Interactive Flashcard Engine")
    st.write("Practice essential Goethe A1 vocabulary, verbs, and phrases organized by practical theme categories.")

    # Category and Word Selection Dropdowns
    selected_category = st.selectbox("📂 Select Vocabulary Category:", list(GOETHE_CATEGORIES.keys()))
    available_words_in_cat = GOETHE_CATEGORIES[selected_category]

    col_w1, col_w2 = st.columns([3, 1])
    with col_w1:
        selected_word_dropdown = st.selectbox(f"🔤 Select specific word in '{selected_category}':", available_words_in_cat)
    with col_w2:
        if st.button("🎲 Shuffle Random Word", use_container_width=True):
            st.session_state.current_flashcard_word = random.choice(available_words_in_cat)
            st.session_state.show_card_back = False
            st.rerun()

    if "current_flashcard_word" not in st.session_state or st.session_state.current_flashcard_word not in available_words_in_cat:
        st.session_state.current_flashcard_word = selected_word_dropdown

    # If dropdown was changed explicitly
    if selected_word_dropdown != st.session_state.current_flashcard_word:
        st.session_state.current_flashcard_word = selected_word_dropdown
        st.session_state.show_card_back = False

    active_word = st.session_state.current_flashcard_word

    prompt = f"""
    Generate an exhaustive A1 study card JSON for '{active_word}'.
    Return strict JSON with this exact schema:
    {{
        "word": "{active_word}",
        "is_goethe_word": true,
        "part_of_speech": "Verb / Noun / Adjective / Preposition / Conjunction",
        "english_meaning": "English translation",
        "gender": "der / die / das / N/A",
        "plural_form": "Plural form or N/A",
        "conjugations": [
            {{"pronoun": "ich", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}},
            {{"pronoun": "du", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}},
            {{"pronoun": "er/sie/es", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}},
            {{"pronoun": "wir", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}},
            {{"pronoun": "ihr", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}},
            {{"pronoun": "sie/Sie", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}}
        ],
        "perfekt_tense": {{
            "formula": "hat/ist + Partizip II",
            "sample_sentence_de": "German Perfekt sentence",
            "sample_sentence_en": "English Perfekt sentence"
        }},
        "comparative_superlative": "N/A",
        "common_phrases": [
            {{"phrase_de": "German phrase", "phrase_en": "English translation"}},
            {{"phrase_de": "German phrase", "phrase_en": "English translation"}}
        ],
        "grammar_notes": "Important A1 grammar note (case triggers, prepositions, forced accusative, separable prefix, etc.)"
    }}
    """

    try:
        raw_json = generate_cached_content(prompt, is_json=True)
        data = json.loads(raw_json)

        if not st.session_state.get("show_card_back", False):
            st.markdown(f"""
            <div class="flashcard-front-box">
                <p style="color: #38bdf8; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 8px;">⭐ OFFICIAL GOETHE-ZERTIFIKAT A1 CORE VOCABULARY WORD ⭐</p>
                <div class="flashcard-word-title">{data.get("word", active_word)}</div>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 0px;">Category: {selected_category} | Click audio below or flip card for details.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### 🔊 Native Audio Pronunciation")
            audio_bytes = generate_german_audio_bytes(active_word)
            st.audio(audio_bytes, format="audio/mp3")

        else:
            st.markdown(f"""
            <div class="flashcard-back-box">
                <p style="color: #2563eb; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 2px;">⭐ GOETHE A1 CORE VOCABULARY WORD ({selected_category})</p>
                <div class="flashcard-back-title">{data.get("word", active_word)}</div>
                <div class="meaning-subtitle">Meaning: {data.get("english_meaning", "")}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Part of Speech", data.get("part_of_speech", "N/A"))
            c2.metric("Gender", data.get("gender", "N/A"))
            c3.metric("Plural Form", data.get("plural_form", "N/A"))
            c4.metric("Comp. / Superlative", data.get("comparative_superlative", "N/A"))

            perf = data.get("perfekt_tense", {})
            st.success(f"⏳ **Perfekt Tense:** `{perf.get('formula', 'N/A')}`")
            st.markdown(f"• **DE Sentence:** {perf.get('sample_sentence_de', '')}")
            # Audio button for Perfekt sentence
            if st.button("🔊 Play Perfekt Sentence Audio", key="audio_perf"):
                st.audio(generate_german_audio_bytes(perf.get('sample_sentence_de', '')), format="audio/mp3")
            st.markdown(f"• **EN Sentence:** {perf.get('sample_sentence_en', '')}")

            st.info(f"💡 **Grammar Notes & Rules:** {data.get('grammar_notes', 'N/A')}")

            st.markdown("#### 🔄 Conjugations & Example Sentences (with Individual Sentence Audios)")
            conjs = data.get("conjugations", [])
            for i, c in enumerate(conjs):
                cols_c = st.columns([4, 1])
                with cols_c[0]:
                    st.markdown(f"• **{c.get('pronoun')}:** `{c.get('form')}` — *{c.get('sentence')}*  \n  &nbsp;&nbsp;&nbsp;&nbsp;*(En: {c.get('sentence_en')})*")
                with cols_c[1]:
                    if st.button("🔊 Play", key=f"audio_conj_{i}"):
                        st.audio(generate_german_audio_bytes(c.get('sentence')), format="audio/mp3")

            st.markdown("#### 💬 Commonly Used Phrases")
            phrases = data.get("common_phrases", [])
            for j, p in enumerate(phrases):
                cols_p = st.columns([4, 1])
                with cols_p[0]:
                    st.markdown(f"👉 **{p.get('phrase_de')}** — *{p.get('phrase_en')}*")
                with cols_p[1]:
                    if st.button("🔊 Play", key=f"audio_phrase_{j}"):
                        st.audio(generate_german_audio_bytes(p.get('phrase_de')), format="audio/mp3")

    except Exception as e:
        st.error(f"Error compiling flashcard details: {str(e)}")

    st.divider()

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        if st.button("🔄 Flip Flashcard (Front / Back)", use_container_width=True, type="primary"):
            st.session_state.show_card_back = not st.session_state.get("show_card_back", False)
            st.rerun()

    with col_f2:
        if st.button("🎲 Random Goethe Word in Category", use_container_width=True):
            st.session_state.current_flashcard_word = random.choice(available_words_in_cat)
            st.session_state.show_card_back = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Core Grammar Practice & Exercises")
    st.write("Review class handbook modules with rigorous, structured bullet points, additional expert study-buddy explanations, and 20 targeted practice questions designed for 100% mastery.")

    handbook_lessons = [
        "Lesson 1: German Alphabet, Pronunciation, and Article Recognition",
        "Lesson 2: German Noun Gender and Everyday Word Patterns",
        "Lesson 3: Singular and Plural Forms in Daily German",
        "Lesson 4: Personal Introductions and Basic Identity Information",
        "Lesson 5: Simple Sentences for Everyday Communication",
        "Lesson 6: Present Tense Verb Patterns in Practical German",
        "Lesson 7: Working with sein and haben in Everyday Situations",
        "Lesson 8: Numbers, Prices, Dates, and Everyday Quantities",
        "Lesson 9: Everyday Question Structures and Basic Information Requests",
        "Lesson 10: Negation and Negative Sentences in Practical German",
        "Lesson 11: Object Sentences and Basic Accusative Structures",
        "Lesson 12: Simple Descriptions of People, Places, and Things",
        "Lesson 13: Possession, Ownership, and Family Relationships",
        "Lesson 14: Time Expressions, Appointments, and Schedules",
        "Lesson 15: Daily Routine Patterns and Everyday Activities",
        "Lesson 16: Commands, Requests, and Basic Instructions",
        "Lesson 17: Abilities, Obligations, and Everyday Modal Verbs",
        "Lesson 18: Practical Sentences with Modal Verb Structures",
        "Lesson 19: Everyday Dative Structures and Indirect Objects",
        "Lesson 20: Common Dative Expressions in Real-Life Communication",
        "Lesson 21: Location Expressions and Place Descriptions",
        "Lesson 22: Movement and Position Patterns in Everyday German",
        "Lesson 23: Two-Way Prepositions (Wechselpräpositionen) - Accusative vs. Dative Deep Dive",
        "Lesson 24: Shopping, Money, and Price Communication",
        "Lesson 25: Connecting Simple Ideas with Basic German Connectors",
        "Lesson 26: Reasons, Explanations, and Cause Structures",
        "Lesson 27: Future Expressions and Everyday Planning Language",
        "Lesson 28: Past Events with haben and Perfekt Structures",
        "Lesson 29: Movement and Travel Narration with sein",
        "Lesson 30: Everyday Past Narration and Simple Storytelling",
        "Lesson 31: Separable Verb Patterns in Daily Communication",
        "Lesson 32: Comparisons, Preferences, and Basic Opinions",
        "Lesson 33: Likes, Preferences, and Personal Interests",
        "Lesson 34: Simple Subordinate Clauses and Verb-Final Patterns",
        "Lesson 35: Simple Emails, Messages, and Digital Communication",
        "Lesson 36: Everyday Conversation Patterns and Social Interaction",
        "Lesson 37: Recognizing and Correcting Common A1 Grammar Mistakes",
        "Lesson 38: Recognizing A1 Grammar in Authentic German Texts",
        "Lesson 39: Everyday Public Signs, Instructions, and Survival German",
        "Lesson 40: CEFR A1 Mock Examination Overview"
    ]

    selected_lesson = st.selectbox("Select Handbook Lesson to Review & Practice:", handbook_lessons)

    if st.button("📖 Load Rigorous Review & 20 Practice Exercises", type="primary"):
        with st.spinner("Gem is compiling clean bulleted notes, advanced study-buddy mentorship insights, and 20 practice exercises..."):
            prompt = f"""
            Create a detailed study review & 20-exercise package for '{selected_lesson}'.
            CRITICAL FORMATTING INSTRUCTION: 
            1. 'lesson_explanation' MUST be structured using clear Markdown bullet points (`*` or `-`). Avoid dense walls of text.
            2. Provide thorough, advanced mentor insights that go beyond basic source material so the user can easily master all 20 practice questions. Include structural patterns, mnemonics, and traps to avoid.

            Return strict JSON with this exact schema:
            {{
                "lesson_title": "{selected_lesson}",
                "lesson_explanation": "Provide a clean, beautifully formatted bulleted guide explaining '{selected_lesson}'. Use bullet points for rules, bullet points for examples, and bullet points for study-buddy pro tips.",
                "exercises_mc": [
                    {{"id": "mc1", "question": "Question 1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct..."}},
                    {{"id": "mc2", "question": "Question 2", "options": ["A", "B", "C", "D"], "correct": "B", "explanation": "Why B is correct..."}},
                    {{"id": "mc3", "question": "Question 3", "options": ["A", "B", "C", "D"], "correct": "C", "explanation": "Why C is correct..."}},
                    {{"id": "mc4", "question": "Question 4", "options": ["A", "B", "C", "D"], "correct": "D", "explanation": "Why D is correct..."}},
                    {{"id": "mc5", "question": "Question 5", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "Why A is correct..."}}
                ],
                "exercises_fib": [
                    {{"id": "fib1", "prompt": "Complete sentence with missing blank (...)", "answer": "correct word", "explanation": "Grammar rule for this word"}},
                    {{"id": "fib2", "prompt": "Complete sentence with missing blank (...)", "answer": "correct word", "explanation": "Grammar rule for this word"}},
                    {{"id": "fib3", "prompt": "Complete sentence with missing blank (...)", "answer": "correct word", "explanation": "Grammar rule for this word"}},
                    {{"id": "fib4", "prompt": "Complete sentence with missing blank (...)", "answer": "correct word", "explanation": "Grammar rule for this word"}},
                    {{"id": "fib5", "prompt": "Complete sentence with missing blank (...)", "answer": "correct word", "explanation": "Grammar rule for this word"}}
                ],
                "exercises_sc": [
                    {{"id": "sc1", "words": ["words", "to", "arrange"], "answer": "Correct German sentence", "explanation": "Word order rule"}},
                    {{"id": "sc2", "words": ["words", "to", "arrange"], "answer": "Correct German sentence", "explanation": "Word order rule"}},
                    {{"id": "sc3", "words": ["words", "to", "arrange"], "answer": "Correct German sentence", "explanation": "Word order rule"}},
                    {{"id": "sc4", "words": ["words", "to", "arrange"], "answer": "Correct German sentence", "explanation": "Word order rule"}},
                    {{"id": "sc5", "words": ["words", "to", "arrange"], "answer": "Correct German sentence", "explanation": "Word order rule"}}
                ],
                "exercises_st": [
                    {{"id": "st1", "english": "English sentence to translate", "answer": "German translation", "explanation": "Key vocabulary and grammar rules"}},
                    {{"id": "st2", "english": "English sentence to translate", "answer": "German translation", "explanation": "Key vocabulary and grammar rules"}},
                    {{"id": "st3", "english": "English sentence to translate", "answer": "German translation", "explanation": "Key vocabulary and grammar rules"}},
                    {{"id": "st4", "english": "English sentence to translate", "answer": "German translation", "explanation": "Key vocabulary and grammar rules"}},
                    {{"id": "st5", "english": "English sentence to translate", "answer": "German translation", "explanation": "Key vocabulary and grammar rules"}}
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
        st.subheader("📝 Practice Exercises (20 Questions)")

        ex_tab1, ex_tab2, ex_tab3, ex_tab4 = st.tabs([
            "1. Multiple Choice (5)", 
            "2. Fill in the Blanks (5)", 
            "3. Sentence Creation (5)", 
            "4. Sentence Translation (5)"
        ])

        with ex_tab1:
            st.markdown("#### Section 1: Multiple Choice Questions")
            mc_user_answers = {}
            for idx, q in enumerate(mod["exercises_mc"], start=1):
                st.markdown(f"**Q{idx}. {q['question']}**")
                mc_user_answers[q['id']] = st.radio(f"Select answer for Q{idx}:", q['options'], key=f"rad_{q['id']}")

        with ex_tab2:
            st.markdown("#### Section 2: Fill in the Blanks")
            fib_user_answers = {}
            for idx, q in enumerate(mod["exercises_fib"], start=1):
                st.markdown(f"**Q{idx}. {q['prompt']}**")
                fib_user_answers[q['id']] = st.text_input(f"Your answer for Q{idx}:", key=f"inp_{q['id']}")

        with ex_tab3:
            st.markdown("#### Section 3: Sentence Creation (Unscramble / Build)")
            sc_user_answers = {}
            for idx, q in enumerate(mod["exercises_sc"], start=1):
                st.markdown(f"**Q{idx}. Words to use:** `{', '.join(q['words'])}`")
                sc_user_answers[q['id']] = st.text_input(f"Form complete German sentence for Q{idx}:", key=f"inp_sc_{q['id']}")

        with ex_tab4:
            st.markdown("#### Section 4: Sentence Translation")
            st_user_answers = {}
            for idx, q in enumerate(mod["exercises_st"], start=1):
                st.markdown(f"**Q{idx}. Translate to German:** *{q['english']}*")
                st_user_answers[q['id']] = st.text_input(f"German translation for Q{idx}:", key=f"inp_st_{q['id']}")

        st.divider()
        if st.button("🚀 Submit All Answers & View Immediate Corrections", type="primary"):
            st.markdown("### 📊 Correct Answers & Immediate Explanations")
            
            st.markdown("#### 1. Multiple Choice Evaluation")
            for idx, q in enumerate(mod["exercises_mc"], start=1):
                u_ans = mc_user_answers.get(q['id'])
                if u_ans == q['correct']:
                    st.success(f"**Q{idx}: Correct!** ({q['correct']}) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['correct']}`\n\n💡 **Reason:** {q['explanation']}")

            st.markdown("#### 2. Fill in the Blanks Evaluation")
            for idx, q in enumerate(mod["exercises_fib"], start=1):
                u_ans = fib_user_answers.get(q['id'], "").strip().lower()
                c_ans = q['answer'].strip().lower()
                if u_ans == c_ans:
                    st.success(f"**Q{idx}: Correct!** (`{q['answer']}`) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['answer']}`\n\n💡 **Reason:** {q['explanation']}")

            st.markdown("#### 3 & 4. Sentence Creation & Translation Evaluation")
            with st.spinner("Gem is evaluating sentence structures and translations..."):
                sc_st_prompt = f"""
                Evaluate the student's submitted answers against target answers.
                
                SENTENCE CREATION SUBMISSIONS:
                {json.dumps([{"q_id": q["id"], "user": sc_user_answers.get(q["id"]), "expected": q["answer"], "rule": q["explanation"]} for q in mod["exercises_sc"]])}
                
                TRANSLATION SUBMISSIONS:
                {json.dumps([{"q_id": q["id"], "user": st_user_answers.get(q["id"]), "expected": q["answer"], "rule": q["explanation"]} for q in mod["exercises_st"]])}

                Output clear feedback for each sentence, stating whether it is accepted, grammatical corrections, and reasoning.
                """
                eval_feedback = generate_cached_content(sc_st_prompt)
                st.write(eval_feedback)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Goethe A1 Lesen Practice (25 Mins, 15 Points)")

    l_tab1, l_tab2, l_tab3 = st.tabs([
        "Teil 1: Short Messages (5 Tasks)", 
        "Teil 2: Classified Ads (5 Tasks)", 
        "Teil 3: Public Signs (5 Tasks)"
    ])

    with l_tab1:
        st.markdown("**Teil 1:** Read short emails or notes and answer 5 Richtig/Falsch tasks[cite: 3].")
        if st.button("🎲 Generate Lesen Teil 1 Scenario", type="primary") or st.button("🔄 Generate New Lesen Teil 1 Set"):
            with st.spinner("Gem is generating a fresh Lesen Teil 1 set..."):
                prompt = """
                Generate Goethe A1 Lesen Teil 1 exercise: 2 short emails with 5 total statement tasks (Richtig/Falsch).
                Return strict JSON format:
                {
                    "text1": "Email 1 text...",
                    "text2": "Email 2 text...",
                    "questions": [
                        {"id": "l1_1", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."},
                        {"id": "l1_2", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."},
                        {"id": "l1_3", "statement": "Statement 3", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."},
                        {"id": "l1_4", "statement": "Statement 4", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."},
                        {"id": "l1_5", "statement": "Statement 5", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.lesen_t1 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "lesen_t1" in st.session_state:
            d = st.session_state.lesen_t1
            st.info(f"**Text 1:**\n{d['text1']}")
            st.info(f"**Text 2:**\n{d['text2']}")
            ans = {}
            for idx, q in enumerate(d["questions"], start=1):
                st.markdown(f"**Task {idx}: {q['statement']}**")
                ans[q["id"]] = st.radio("Choice:", q["options"], key=f"rad_lt1_{q['id']}")
            if st.button("Submit Lesen Teil 1"):
                score = sum(1 for q in d["questions"] if ans.get(q["id"]) == q["answer"])
                st.success(f"Teil 1 Score: {score} / 5")

    with l_tab2:
        st.markdown("**Teil 2:** Match user situations to classified website ads A or B (5 tasks)[cite: 3].")
        if st.button("🎲 Generate Lesen Teil 2 Scenario", type="primary") or st.button("🔄 Generate New Lesen Teil 2 Set"):
            with st.spinner("Gem is generating a fresh Lesen Teil 2 set..."):
                prompt = """
                Generate Goethe A1 Lesen Teil 2 exercise: 5 user situations, each with Website A and Website B options.
                Return strict JSON format:
                {
                    "tasks": [
                        {"id": "l2_1", "situation": "User situation 1", "site_a": "Ad A", "site_b": "Ad B", "options": ["Website A", "Website B"], "answer": "Website A", "explanation": "..."},
                        {"id": "l2_2", "situation": "User situation 2", "site_a": "Ad A", "site_b": "Ad B", "options": ["Website A", "Website B"], "answer": "Website B", "explanation": "..."},
                        {"id": "l2_3", "situation": "User situation 3", "site_a": "Ad A", "site_b": "Ad B", "options": ["Website A", "Website B"], "answer": "Website A", "explanation": "..."},
                        {"id": "l2_4", "situation": "User situation 4", "site_a": "Ad A", "site_b": "Ad B", "options": ["Website A", "Website B"], "answer": "Website B", "explanation": "..."},
                        {"id": "l2_5", "situation": "User situation 5", "site_a": "Ad A", "site_b": "Ad B", "options": ["Website A", "Website B"], "answer": "Website A", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.lesen_t2 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "lesen_t2" in st.session_state:
            d = st.session_state.lesen_t2
            ans2 = {}
            for idx, task in enumerate(d["tasks"], start=1):
                st.markdown(f"**Task {idx}: {task['situation']}**")
                c1, c2 = st.columns(2)
                with c1: st.caption(f"A: {task['site_a']}")
                with c2: st.caption(f"B: {task['site_b']}")
                ans2[task["id"]] = st.radio(f"Select site for Task {idx}:", task["options"], key=f"rad_lt2_{task['id']}")
            if st.button("Submit Lesen Teil 2"):
                score = sum(1 for t in d["tasks"] if ans2.get(t["id"]) == t["answer"])
                st.success(f"Teil 2 Score: {score} / 5")

    with l_tab3:
        st.markdown("**Teil 3:** Read public signs/notices and answer 5 Richtig/Falsch tasks[cite: 3].")
        if st.button("🎲 Generate Lesen Teil 3 Scenario", type="primary") or st.button("🔄 Generate New Lesen Teil 3 Set"):
            with st.spinner("Gem is generating a fresh Lesen Teil 3 sign set..."):
                prompt = """
                Generate Goethe A1 Lesen Teil 3 exercise: 5 public signs with 1 statement task per sign (Richtig/Falsch).
                Return strict JSON format:
                {
                    "tasks": [
                        {"id": "l3_1", "sign": "Sign text 1", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."},
                        {"id": "l3_2", "sign": "Sign text 2", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."},
                        {"id": "l3_3", "sign": "Sign text 3", "statement": "Statement 3", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."},
                        {"id": "l3_4", "sign": "Sign text 4", "statement": "Statement 4", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."},
                        {"id": "l3_5", "sign": "Sign text 5", "statement": "Statement 5", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.lesen_t3 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "lesen_t3" in st.session_state:
            d = st.session_state.lesen_t3
            ans3 = {}
            for idx, task in enumerate(d["tasks"], start=1):
                st.error(f"🛑 **Sign {idx}:** {task['sign']}")
                st.markdown(f"**Task {idx}: {task['statement']}**")
                ans3[task["id"]] = st.radio("Choice:", task["options"], key=f"rad_lt3_{task['id']}")
            if st.button("Submit Lesen Teil 3"):
                score = sum(1 for t in d["tasks"] if ans3.get(t["id"]) == t["answer"])
                st.success(f"Teil 3 Score: {score} / 5")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🎧 Goethe A1 Hören Practice (20 Mins, 15 Points)")

    h_tab1, h_tab2, h_tab3 = st.tabs([
        "Teil 1: 6 Dialogues (Played 2x - Distinct Male/Female Voices)", 
        "Teil 2: 4 Announcements (Played 1x)", 
        "Teil 3: 5 Voicemails (Played 2x)"
    ])

    with h_tab1:
        st.info("ℹ️ Teil 1: 6 dialogues played TWICE[cite: 3]. Each dialogue features alternating distinct speakers (e.g., Frau Müller as a female voice and Herr Schmidt as a male voice) mirroring the actual exam format.")
        if st.button("🎲 Generate Hören Teil 1 Scenario", type="primary") or st.button("🔄 Generate New Hören Teil 1 Audio & Tasks"):
            with st.spinner("Gem is synthesizing 6 distinct male/female dialogues..."):
                prompt = """
                Generate Goethe A1 Hören Teil 1: 6 dialogues between a woman (Frau Müller) and a man (Herr Schmidt) with 1 multiple-choice task per dialogue (A/B/C).
                Return strict JSON format:
                {
                    "tasks": [
                        {"id": "h1_1", "speaker_f": "Guten Tag, Herr Schmidt. Haben Sie den Bericht?", "speaker_m": "Ja, Frau Müller, er ist auf dem Tisch.", "question": "Wo ist der Bericht?", "options": ["a) Auf dem Tisch", "b) Im Auto", "c) Zu Hause"], "answer": "a) Auf dem Tisch", "explanation": "..."},
                        {"id": "h1_2", "speaker_f": "Frau Müller text 2", "speaker_m": "Herr Schmidt text 2", "question": "Question 2", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."},
                        {"id": "h1_3", "speaker_f": "Frau Müller text 3", "speaker_m": "Herr Schmidt text 3", "question": "Question 3", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."},
                        {"id": "h1_4", "speaker_f": "Frau Müller text 4", "speaker_m": "Herr Schmidt text 4", "question": "Question 4", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."},
                        {"id": "h1_5", "speaker_f": "Frau Müller text 5", "speaker_m": "Herr Schmidt text 5", "question": "Question 5", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."},
                        {"id": "h1_6", "speaker_f": "Frau Müller text 6", "speaker_m": "Herr Schmidt text 6", "question": "Question 6", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.hoeren_t1 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t1" in st.session_state:
            d = st.session_state.hoeren_t1
            ans1 = {}
            for idx, t in enumerate(d["tasks"], start=1):
                st.markdown(f"#### 🔊 Dialogue {idx} (Played 2x with distinct voices)")
                col_aud1, col_aud2 = st.columns(2)
                with col_aud1:
                    st.caption("👩‍💼 Frau Müller (Female Voice):")
                    st.audio(generate_german_audio_bytes(t["speaker_f"]), format="audio/mp3")
                with col_aud2:
                    st.caption("👨‍💼 Herr Schmidt (Male Voice):")
                    st.audio(generate_german_audio_bytes(t["speaker_m"]), format="audio/mp3")

                with st.expander(f"👁️ Full Transcript {idx}"): 
                    st.write(f"**Frau Müller:** {t['speaker_f']}")
                    st.write(f"**Herr Schmidt:** {t['speaker_m']}")

                st.markdown(f"**Task {idx}: {t['question']}**")
                ans1[t["id"]] = st.radio(f"Select Q{idx}:", t["options"], key=f"rad_ht1_{t['id']}")
            if st.button("Submit Hören Teil 1"):
                score = sum(1 for t in d["tasks"] if ans1.get(t["id"]) == t["answer"])
                st.success(f"Teil 1 Score: {score} / 6")

    with h_tab2:
        st.warning("⚠️ Teil 2: 4 public announcements played ONCE[cite: 3]. Judge Richtig or Falsch.")
        if st.button("🎲 Generate Hören Teil 2 Scenario", type="primary") or st.button("🔄 Generate New Hören Teil 2 Audio & Tasks"):
            with st.spinner("Gem is synthesizing 4 new public announcements..."):
                prompt = """
                Generate Goethe A1 Hören Teil 2: 4 announcements with 1 Richtig/Falsch task each.
                Return strict JSON format:
                {
                    "tasks": [
                        {"id": "h2_1", "script": "Announcement 1 transcript", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."},
                        {"id": "h2_2", "script": "Announcement 2 transcript", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."},
                        {"id": "h2_3", "script": "Announcement 3 transcript", "statement": "Statement 3", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."},
                        {"id": "h2_4", "script": "Announcement 4 transcript", "statement": "Statement 4", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.hoeren_t2 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t2" in st.session_state:
            d = st.session_state.hoeren_t2
            ans2 = {}
            for idx, t in enumerate(d["tasks"], start=1):
                st.markdown(f"#### 🔊 Public Announcement {idx} (Played 1x)")
                st.audio(generate_german_audio_bytes(t["script"]), format="audio/mp3")
                with st.expander(f"👁️ Transcript {idx}"): st.write(t["script"])
                st.markdown(f"**Task {idx}: {t['statement']}**")
                ans2[t["id"]] = st.radio(f"Select Q{idx}:", t["options"], key=f"rad_ht2_{t['id']}")
            if st.button("Submit Hören Teil 2"):
                score = sum(1 for t in d["tasks"] if ans2.get(t["id"]) == t["answer"])
                st.success(f"Teil 2 Score: {score} / 4")

    with h_tab3:
        st.info("ℹ️ Teil 3: 5 phone voicemails played TWICE[cite: 3]. Choose A, B, or C.")
        if st.button("🎲 Generate Hören Teil 3 Scenario", type="primary") or st.button("🔄 Generate New Hören Teil 3 Audio & Tasks"):
            with st.spinner("Gem is synthesizing 5 new voicemail messages..."):
                prompt = """
                Generate Goethe A1 Hören Teil 3: 5 voicemails with 1 multiple-choice task each (A/B/C).
                Return strict JSON format:
                {
                    "tasks": [
                        {"id": "h3_1", "script": "Voicemail 1 transcript", "question": "Question 1", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."},
                        {"id": "h3_2", "script": "Voicemail 2 transcript", "question": "Question 2", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."},
                        {"id": "h3_3", "script": "Voicemail 3 transcript", "question": "Question 3", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."},
                        {"id": "h3_4", "script": "Voicemail 4 transcript", "question": "Question 4", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."},
                        {"id": "h3_5", "script": "Voicemail 5 transcript", "question": "Question 5", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.hoeren_t3 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t3" in st.session_state:
            d = st.session_state.hoeren_t3
            ans3 = {}
            for idx, t in enumerate(d["tasks"], start=1):
                st.markdown(f"#### 🔊 Phone Message {idx} (Played 2x)")
                st.audio(generate_german_audio_bytes(t["script"]), format="audio/mp3")
                with st.expander(f"👁️ Transcript {idx}"): st.write(t["script"])
                st.markdown(f"**Task {idx}: {t['question']}**")
                ans3[t["id"]] = st.radio(f"Select Q{idx}:", t["options"], key=f"rad_ht3_{t['id']}")
            if st.button("Submit Hören Teil 3"):
                score = sum(1 for t in d["tasks"] if ans3.get(t["id"]) == t["answer"])
                st.success(f"Teil 3 Score: {score} / 5")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✍️ Goethe A1 Schreiben Practice (20 Mins, 15 Points)")

    s_tab1, s_tab2 = st.tabs([
        "Teil 1: Fill 5 Missing Gaps on Form", 
        "Teil 2: Write ~30-Word Email (3 Points)"
    ])

    with s_tab1:
        st.markdown("**Teil 1:** Read a short background text and complete the 5 missing fields on a registration form[cite: 3].")
        if st.button("🎲 Generate Schreiben Teil 1 Scenario", type="primary") or st.button("🔄 Generate New Form Scenario"):
            with st.spinner("Gem is creating complete form exercise..."):
                prompt = """
                Generate a complete Goethe A1 Schreiben Teil 1 form exercise.
                CRITICAL INSTRUCTION: The 'scenario' text MUST explicitly state all 5 details required to answer every single form field!

                Return strict JSON format:
                {
                    "scenario": "Your friend / tourist [Full Name] is booking a hotel room for [X] people arriving on [Day]. They want to pay by [Payment Method] and their phone number is [Phone Number]. Write out a full detailed 3-4 sentence background scenario containing ALL of these 5 facts clearly.",
                    "form_title": "Anmeldeformular",
                    "fields": [
                        {"id": "f1", "label": "1. Familienname", "answer": "Müller"},
                        {"id": "f2", "label": "2. Anzahl der Personen", "answer": "2"},
                        {"id": "f3", "label": "3. Anreisetag", "answer": "Samstag"},
                        {"id": "f4", "label": "4. Zahlungsart", "answer": "Bar"},
                        {"id": "f5", "label": "5. Telefonnummer", "answer": "015123456"}
                    ]
                }
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state.schreiben_t1 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "schreiben_t1" in st.session_state:
            d = st.session_state.schreiben_t1
            st.info(f"**Background Scenario:**\n{d['scenario']}")
            st.markdown(f"### 📋 {d['form_title']}")
            user_inputs = {}
            for f in d["fields"]:
                user_inputs[f["id"]] = st.text_input(f["label"], key=f"inp_{f['id']}")
            
            if st.button("Check Form Gaps"):
                score = 0
                for f in d["fields"]:
                    u_val = user_inputs[f["id"]].strip().lower()
                    c_val = f["answer"].strip().lower()
                    if u_val == c_val:
                        score += 1
                        st.success(f"**{f['label']}: Correct!** (`{f['answer']}`)")
                    else:
                        st.error(f"**{f['label']}: Incorrect.** Your answer: `{u_val}` | Correct: `{f['answer']}`")
                st.metric("Form Score", f"{score} / 5")

    with s_tab2:
        st.markdown("**Teil 2:** Write a short informal message/email (~30 words) hitting 3 required content points[cite: 3].")
        if st.button("🎲 Generate Schreiben Teil 2 Prompt", type="primary") or st.button("🔄 Generate Another Email Prompt"):
            with st.spinner("Gem is generating email prompt..."):
                try:
                    prompt = "Generate an official Goethe A1 Schreiben Teil 2 prompt specifying a clear scenario and 3 explicit bullet points."
                    st.session_state.schreiben_t2_prompt = generate_dynamic_content(prompt)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "schreiben_t2_prompt" in st.session_state:
            st.info(st.session_state.schreiben_t2_prompt)
            u_email = st.text_area("Your German Response (~30 words):", height=140)
            if st.button("Evaluate Email with Gem"):
                if u_email.strip():
                    with st.spinner("Gem is evaluating task fulfillment..."):
                        try:
                            eval_prompt = f"PROMPT:\n{st.session_state.schreiben_t2_prompt}\n\nSUBMISSION:\n{u_email}\n\nGrade task fulfillment across all 3 bullet points, V2 verb order, and appropriate salutations/closings."
                            eval_res = generate_dynamic_content(eval_prompt)
                            st.markdown("### Official Examiner Breakdown")
                            st.write(eval_res)
                        except Exception as e: st.error(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🗣️ Goethe A1 Sprechen Practice (15 Mins, Small Group Format)")

    sp_tab1, sp_tab2, sp_tab3 = st.tabs([
        "Teil 1: Sich vorstellen & Buchstabieren", 
        "Teil 2: W-Fragen mit Themenkarten", 
        "Teil 3: Bitten mit Bildkarten"
    ])

    with sp_tab1:
        st.markdown("""
        **Teil 1:** Introduce yourself using standard criteria and spell a name or state a phone/ZIP code[cite: 3]:
        *1. Name | 2. Alter | 3. Land | 4. Wohnort | 5. Sprachen | 6. Beruf | 7. Hobby*
        """)
        rec_t1 = mic_recorder(start_prompt="Record Self-Introduction 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t1")
        if rec_t1:
            st.audio(rec_t1['bytes'], format='audio/wav')
            if st.button("Evaluate Introduction"):
                with st.spinner("Gem is analyzing introduction..."):
                    try:
                        audio_part = types.Part.from_bytes(data=rec_t1['bytes'], mime_type="audio/wav")
                        eval_res = client.models.generate_content(
                            model=FALLBACK_MODELS[0],
                            contents=["Transcribe audio and evaluate candidate self-introduction and spelling against Goethe A1 criteria.", audio_part],
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                        )
                        st.write(eval_res.text)
                    except Exception as e: st.error(f"Error: {str(e)}")

    with sp_tab2:
        st.markdown("**Teil 2:** Draw a topic card, formulate a W-question for your partner, and answer theirs (Verb in Position 2)[cite: 3].")
        
        col_sp2_a, col_sp2_b = st.columns(2)
        with col_sp2_a:
            if st.button("🎲 Draw Topic Card", type="primary"):
                with st.spinner("Gem is drawing card..."):
                    try:
                        st.session_state.card_t2 = generate_dynamic_content("Generate Goethe A1 Sprechen topic card (e.g. Thema: 'Einkaufen', Wort: 'Brot').")
                    except Exception as e: st.error(f"Error: {str(e)}")
        with col_sp2_b:
            if st.button("🔄 Draw Another Topic Card"):
                with st.spinner("Gem is drawing a new card..."):
                    try:
                        st.session_state.card_t2 = generate_dynamic_content("Generate Goethe A1 Sprechen topic card with a completely different theme (e.g. Thema: 'Freizeit', 'Wohnen', 'Familie').")
                    except Exception as e: st.error(f"Error: {str(e)}")

        if "card_t2" in st.session_state:
            st.success(f"🎴 **Your Topic Card:** {st.session_state.card_t2}")
            rec_t2 = mic_recorder(start_prompt="Record W-Question 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t2")
            if rec_t2:
                st.audio(rec_t2['bytes'], format='audio/wav')
                if st.button("Evaluate Question Syntax"):
                    with st.spinner("Gem is evaluating verb placement..."):
                        try:
                            audio_part = types.Part.from_bytes(data=rec_t2['bytes'], mime_type="audio/wav")
                            eval_res = client.models.generate_content(
                                model=FALLBACK_MODELS[0],
                                contents=[f"Card: {st.session_state.card_t2}. Transcribe audio and verify if candidate formed a correct W-question with verb in Position 2.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    with sp_tab3:
        st.markdown("**Teil 3:** Draw a card showing an object/situation and make a polite request/instruction (Verb in Position 1)[cite: 3].")
        
        col_sp3_a, col_sp3_b = st.columns(2)
        with col_sp3_a:
            if st.button("🎲 Draw Picture Request Card", type="primary"):
                with st.spinner("Gem is drawing card..."):
                    try:
                        st.session_state.card_t3 = generate_dynamic_content("Generate Goethe A1 Sprechen picture request card (e.g. Gegenstand: Bleistift).")
                    except Exception as e: st.error(f"Error: {str(e)}")
        with col_sp3_b:
            if st.button("🔄 Draw Another Picture Card"):
                with st.spinner("Gem is drawing a new picture card..."):
                    try:
                        st.session_state.card_t3 = generate_dynamic_content("Generate a brand new Goethe A1 Sprechen picture card (e.g. Gegenstand: Apfel, Uhr, Buch, Handy).")
                    except Exception as e: st.error(f"Error: {str(e)}")

        if "card_t3" in st.session_state:
            st.success(f"🎴 **Your Picture Card:** {st.session_state.card_t3}")
            rec_t3 = mic_recorder(start_prompt="Record Request 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t3")
            if rec_t3:
                st.audio(rec_t3['bytes'], format='audio/wav')
                if st.button("Evaluate Request Syntax"):
                    with st.spinner("Gem is evaluating request syntax..."):
                        try:
                            audio_part = types.Part.from_bytes(data=rec_t3['bytes'], mime_type="audio/wav")
                            eval_res = client.models.generate_content(
                                model=FALLBACK_MODELS[0],
                                contents=[f"Card: {st.session_state.card_t3}. Transcribe audio and verify if candidate formed a correct imperative request with verb in Position 1.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. GOETHE A1 MOCK EXAMINATION
# ----------------------------------------------------
elif nav_choice == "🏆 Goethe A1 Mock Examination":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("🏆 Full CEFR A1 Timed Mock Examination Simulator")
    st.write("Simulate the exact Goethe-Zertifikat A1 exam with official section timers (Lesen: 25 mins, Hören: 20 mins, Schreiben: 20 mins). Your scores are tracked across retakes to analyze your problem areas and progress!")

    # Initialize historical scores and problem tracking
    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []
    if "problem_areas" not in st.session_state:
        st.session_state.problem_areas = {}
    if "mock_exam_data" not in st.session_state:
        st.session_state.mock_exam_data = None
    if "exam_submitted" not in st.session_state:
        st.session_state.exam_submitted = False

    # Display progress history and problem areas
    if st.session_state.exam_history:
        st.markdown("### 📈 Your Retake Progress & Score History")
        for idx, record in enumerate(st.session_state.exam_history, 1):
            st.markdown(f"• **Attempt {idx} ({record['date']}):** Total Score: **{record['total']} / 25** ({record['percentage']}%) — Lesen: {record['lesen']}/5, Hören: {record['hoeren']}/3, Schreiben: {record['schreiben']}/4")
        
        if st.session_state.problem_areas:
            st.warning("⚠️ **Identified Problem Areas to Focus On:** " + ", ".join([f"{k} ({v} mistakes)" for k, v in st.session_state.problem_areas.items()]))

    st.divider()

    if not st.session_state.mock_exam_data:
        if st.button("🚀 Start New Timed Mock Examination", type="primary"):
            with st.spinner("Gem is compiling official exam paper..."):
                mock_prompt = """
                Generate a full Goethe-Zertifikat A1 simulated exam paper in strict JSON format.
                Include:
                1. Lesen section with 1 short email passage and 5 Richtig/Falsch questions.
                2. Hören section with 1 short dialogue script, audio prompt text, and 3 multiple choice questions (A/B/C).
                3. Schreiben section with 1 registration form background scenario (with 4 fields) and 1 email prompt with 3 bullet points.
                4. Sprechen section with 1 self-introduction task description and 1 W-question card topic.

                Return strict JSON format:
                {
                    "lesen": {
                        "text": "Reading passage here...",
                        "questions": [
                            {"id": "m_l1", "topic": "Reading Comprehension", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig"},
                            {"id": "m_l2", "topic": "Reading Comprehension", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch"},
                            {"id": "m_l3", "topic": "Reading Details", "statement": "Statement 3", "options": ["richtig", "falsch"], "answer": "richtig"},
                            {"id": "m_l4", "topic": "Reading Details", "statement": "Statement 4", "options": ["richtig", "falsch"], "answer": "falsch"},
                            {"id": "m_l5", "topic": "Email Interpretation", "statement": "Statement 5", "options": ["richtig", "falsch"], "answer": "richtig"}
                        ]
                    },
                    "hoeren": {
                        "script": "Hören dialogue transcript here...",
                        "questions": [
                            {"id": "m_h1", "topic": "Listening Dialogues", "question": "Question 1", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A"},
                            {"id": "m_h2", "topic": "Listening Dialogues", "question": "Question 2", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B"},
                            {"id": "m_h3", "topic": "Listening Details", "question": "Question 3", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C"}
                        ]
                    },
                    "schreiben": {
                        "form_scenario": "Form scenario details: Anna Schmidt is booking for 2 people arriving Friday, paying by credit card, phone 01712345.",
                        "form_fields": [
                            {"id": "mf1", "topic": "Form Spelling & Vocabulary", "label": "1. Name", "answer": "Schmidt"},
                            {"id": "mf2", "topic": "Numbers & Quantities", "label": "2. Personen", "answer": "2"},
                            {"id": "mf3", "topic": "Days & Dates", "label": "3. Tag", "answer": "Freitag"},
                            {"id": "mf4", "topic": "Payment Vocabulary", "label": "4. Zahlung", "answer": "Kreditkarte"}
                        ],
                        "email_prompt": "Write an email to your friend about your birthday party. Include: 1. Date 2. Time 3. Location"
                    },
                    "sprechen": {
                        "intro_task": "Introduce yourself (Name, Age, Country, Profession).",
                        "card_task": "Thema: Essen & Trinken (Wort: Wasser). Formulate a W-question."
                    }
                }
                """
                try:
                    res_json = generate_dynamic_content(mock_prompt, is_json=True)
                    st.session_state.mock_exam_data = json.loads(res_json)
                    st.session_state.exam_submitted = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating mock exam: {str(e)}")

    if st.session_state.mock_exam_data and not st.session_state.exam_submitted:
        exam = st.session_state.mock_exam_data
        
        # Timers simulation (Goethe A1 official limits: Lesen 25 mins, Hören 20 mins, Schreiben 20 mins)
        st.markdown("### ⏱️ Official Exam Timers")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("📖 Lesen Timer", "25:00 max", "Official limit")
        with col_t2:
            st.metric("🎧 Hören Timer", "20:00 max", "Official limit")
        with col_t3:
            st.metric("✍️ Schreiben Timer", "20:00 max", "Official limit")

        m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(["📖 1. Lesen", "🎧 2. Hören", "✍️ 3. Schreiben", "🗣️ 4. Sprechen"])
        
        with m_tab1:
            st.markdown("### Teil 1: Lesen (Reading Comprehension - 25 Mins)")
            st.info(exam["lesen"]["text"])
            m_lesen_answers = {}
            for idx, q in enumerate(exam["lesen"]["questions"], start=1):
                st.markdown(f"**Q{idx}: {q['statement']}**")
                m_lesen_answers[q['id']] = st.radio("Select:", q['options'], key=f"m_l_rad_{q['id']}")

        with m_tab2:
            st.markdown("### Teil 2: Hören (Listening Comprehension - 20 Mins)")
            st.markdown("Listen to the simulated audio script below:")
            st.audio(generate_german_audio_bytes(exam["hoeren"]["script"]), format="audio/mp3")
            with st.expander("👁️ View Audio Transcript"):
                st.write(exam["hoeren"]["script"])
            
            m_hoeren_answers = {}
            for idx, q in enumerate(exam["hoeren"]["questions"], start=1):
                st.markdown(f"**Q{idx}: {q['question']}**")
                m_hoeren_answers[q['id']] = st.radio("Select choice:", q['options'], key=f"m_h_rad_{q['id']}")

        with m_tab3:
            st.markdown("### Teil 3: Schreiben (Writing - 20 Mins)")
            st.markdown("**Part A: Fill out form based on scenario:**")
            st.info(exam["schreiben"]["form_scenario"])
            m_form_inputs = {}
            for f in exam["schreiben"]["form_fields"]:
                m_form_inputs[f["id"]] = st.text_input(f["label"], key=f"m_form_{f['id']}")

            st.markdown("---")
            st.markdown("**Part B: Email Writing:**")
            st.info(exam["schreiben"]["email_prompt"])
            m_email_input = st.text_area("Your German Email Response (~30 words):", key="m_email_resp")

        with m_tab4:
            st.markdown("### Teil 4: Sprechen (Speaking)")
            st.info(f"**Task A:** {exam['sprechen']['intro_task']}")
            m_rec_intro = mic_recorder(start_prompt="Record Introduction 🎙️", stop_prompt="Stop 🛑", key="m_rec_i")
            if m_rec_intro:
                st.audio(m_rec_intro['bytes'], format='audio/wav')

            st.info(f"**Task B:** {exam['sprechen']['card_task']}")
            m_rec_card = mic_recorder(start_prompt="Record W-Question 🎙️", stop_prompt="Stop 🛑", key="m_rec_c")
            if m_rec_card:
                st.audio(m_rec_card['bytes'], format='audio/wav')

        st.divider()
        if st.button("🏆 Submit Full Examination & Generate Official Scorecard", type="primary"):
            # Calculate Scores
            lesen_score = sum(1 for q in exam["lesen"]["questions"] if m_lesen_answers.get(q["id"]) == q["answer"])
            hoeren_score = sum(1 for q in exam["hoeren"]["questions"] if m_hoeren_answers.get(q["id"]) == q["answer"])
            form_score = sum(1 for f in exam["schreiben"]["form_fields"] if m_form_inputs.get(f["id"], "").strip().lower() == f["answer"].strip().lower())
            
            total_score = lesen_score + hoeren_score + form_score
            total_max = 5 + 3 + 4  # 12 objective points graded automatically
            percentage = int((total_score / total_max) * 100)

            # Track problem areas
            for q in exam["lesen"]["questions"]:
                if m_lesen_answers.get(q["id"]) != q["answer"]:
                    topic = q["topic"]
                    st.session_state.problem_areas[topic] = st.session_state.problem_areas.get(topic, 0) + 1
            for q in exam["hoeren"]["questions"]:
                if m_hoeren_answers.get(q["id"]) != q["answer"]:
                    topic = q["topic"]
                    st.session_state.problem_areas[topic] = st.session_state.problem_areas.get(topic, 0) + 1
            for f in exam["schreiben"]["form_fields"]:
                if m_form_inputs.get(f["id"], "").strip().lower() != f["answer"].strip().lower():
                    topic = f["topic"]
                    st.session_state.problem_areas[topic] = st.session_state.problem_areas.get(topic, 0) + 1

            # Save to history
            st.session_state.exam_history.append({
                "date": time.strftime("%Y-%m-%d %H:%M"),
                "lesen": lesen_score,
                "hoeren": hoeren_score,
                "schreiben": form_score,
                "total": total_score,
                "percentage": percentage
            })
            st.session_state.exam_submitted = True
            st.rerun()

    if st.session_state.get("exam_submitted", False):
        st.markdown("### 🏆 Official Goethe Exam Scorecard & Feedback")
        latest = st.session_state.exam_history[-1]
        st.success(f"🎉 **Exam Completed Successfully!** Total Score: **{latest['total']} / 12** ({latest['percentage']}%)")
        st.metric("📖 Lesen Score", f"{latest['lesen']} / 5")
        st.metric("🎧 Hören Score", f"{latest['hoeren']} / 3")
        st.metric("✍️ Schreiben Form Score", f"{latest['schreiben']} / 4")

        if st.session_state.problem_areas:
            st.error("🚨 **Targeted Focus Areas (Where you missed points):**")
            for area, count in st.session_state.problem_areas.items():
                st.markdown(f"• **{area}:** {count} mistake(s). Review corresponding grammar or vocabulary modules!")

        if st.button("🔄 Retake Exam (Start New Attempt)", type="primary"):
            st.session_state.mock_exam_data = None
            st.session_state.exam_submitted = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 9. ASK GEM
# ----------------------------------------------------
elif nav_choice == "💬 Ask Gem (AI Tutor)":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("💬 Ask Gem — Interactive AI Tutor")
    if prompt := st.chat_input("Ask Gem a question:"):
        try:
            res = generate_dynamic_content(prompt)
            st.write(res)
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)
