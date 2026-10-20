import os
import json
import io
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

# CSS for Flip Flashcard Styling & Custom Layout
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
    .main-card { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .accent-card { background: #ffffff; border-radius: 16px; padding: 24px; border-left: 6px solid #2563eb; box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    
    /* Interactive Flashcard Front UI */
    .flashcard-front-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 50px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
        border: 2px solid #38bdf8;
        margin-bottom: 20px;
    }
    .flashcard-word-title {
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #38bdf8;
        margin-bottom: 15px;
    }
    
    /* Interactive Flashcard Back UI */
    .flashcard-back-box {
        background: #ffffff;
        border: 2px solid #2563eb;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.12);
        margin-bottom: 20px;
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
</style>
""", unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())
MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = """
You are Gem, an expert German tutor and official Goethe-Institut examiner evaluating candidates for the Goethe-Zertifikat A1 exam.

You follow standard CEFR A1 learning objectives and handbook guidelines.
When generating structured content, exercise sets, or JSON flashcards, ensure exact correctness, clear explanations, and strict output formats.
"""

@st.cache_data(show_spinner=False)
def generate_cached_content(prompt_text: str, is_json: bool = False) -> str:
    config_args = {"system_instruction": SYSTEM_INSTRUCTION}
    if is_json:
        config_args["response_mime_type"] = "application/json"
    
    res = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_text,
        config=types.GenerateContentConfig(**config_args)
    )
    return res.text

@st.cache_data
def load_goethe_vocab():
    try:
        with open("goethe_vocab.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "🍎 Essen & Trinken": ["einkaufen", "das Brot", "der Apfel", "die Milch", "das Wasser"],
            "🚗 Reisen & Verkehr": ["die Fahrkarte", "der Bahnhof", "der Flughafen", "abholen"],
            "🏠 Wohnen & Alltag": ["die Wohnung", "der Schlüssel", "das Zimmer", "aufstehen"]
        }

GOETHE_WORD_BANK = load_goethe_vocab()

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
          - Teil 1: Short Emails (5 Tasks - Richtig/Falsch)
          - Teil 2: Classified Ads (5 Tasks - Option A or B)
          - Teil 3: Public Signs (5 Tasks - Richtig/Falsch)
        * **Schreiben (20 Mins - 2 Tasks):**
          - Teil 1: Fill 5 Missing Gaps on Form
          - Teil 2: Write ~30-Word Message (3 Bullet Points)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🎧 Hören & 🗣️ Sprechen")
        st.markdown("""
        * **Hören (20 Mins - 15 Tasks):**
          - Teil 1: 6 Dialogues (2x Audio, A/B/C)
          - Teil 2: 4 Announcements (1x Audio, Richtig/Falsch)
          - Teil 3: 5 Voicemails (2x Audio, A/B/C)
        * **Sprechen (15 Mins - Small Group):**
          - Teil 1: Self-Introduction & Spelling
          - Teil 2: W-Questions (Verb in Position 2)
          - Teil 3: Imperative Requests (Verb in Position 1)
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE (UPDATED FLASHCARD)
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Interactive Flashcard Engine")
    st.write("Front features center word and native audio. Flip to reveal complete grammatical breakdowns.")

    cat_col, word_col = st.columns(2)
    with cat_col:
        selected_cat = st.selectbox("Select Category:", list(GOETHE_WORD_BANK.keys()))
    with word_col:
        selected_word = st.selectbox("Select Keyword:", GOETHE_WORD_BANK[selected_cat])
    
    custom_word = st.text_input("Or type any German word directly:")
    active_word = custom_word.strip() if custom_word.strip() else selected_word

    if "show_card_back" not in st.session_state:
        st.session_state.show_card_back = False

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button(f"🔍 Load Card for '{active_word}'", type="primary", use_container_width=True):
            st.session_state.show_card_back = False
    with col_b2:
        if st.button("🔄 Flip Flashcard (Front / Back)", use_container_width=True):
            st.session_state.show_card_back = not st.session_state.show_card_back

    prompt = f"""
    Generate an exhaustive A1 study card JSON for '{active_word}'.
    Return strict JSON with this exact schema:
    {{
        "word": "{active_word}",
        "part_of_speech": "Noun / Verb / Adjective / Preposition / Conjunction",
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
        "comparative_superlative": "Comparative / Superlative or N/A",
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

        # FRONT OF FLASHCARD
        if not st.session_state.show_card_back:
            st.markdown(f"""
            <div class="flashcard-front-box">
                <p style="color: #94a3b8; font-weight: 600; letter-spacing: 0.05em;">GERMAN A1 FLASHCARD (FRONT)</p>
                <div class="flashcard-word-title">{data.get("word", active_word)}</div>
                <p style="color: #cbd5e1; font-size: 0.95rem;">Listen to pronunciation below, then click 'Flip Flashcard 🔄' to view full details.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🔊 Native Audio Pronunciation")
            audio_bytes = generate_german_audio_bytes(active_word)
            st.audio(audio_bytes, format="audio/mp3")

        # BACK OF FLASHCARD
        else:
            st.markdown(f"""
            <div class="flashcard-back-box">
                <div class="flashcard-back-title">{data.get("word", active_word)}</div>
                <div class="meaning-subtitle">Meaning: {data.get("english_meaning", "")}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Part of Speech", data.get("part_of_speech", "-"))
            c2.metric("Gender", data.get("gender", "-"))
            c3.metric("Plural Form", data.get("plural_form", "-"))
            c4.metric("Comp. / Superlative", data.get("comparative_superlative", "-"))

            perf = data.get("perfekt_tense", {})
            st.success(f"⏳ **Perfekt Tense:** `{perf.get('formula', 'N/A')}`\n\n• **DE:** {perf.get('sample_sentence_de', '')}\n• **EN:** {perf.get('sample_sentence_en', '')}")

            st.info(f"💡 **Grammar Notes & Rules:** {data.get('grammar_notes', '')}")

            st.markdown("#### 🔄 Conjugations & Example Sentences")
            conjs = data.get("conjugations", [])
            for c in conjs:
                st.markdown(f"• **{c.get('pronoun')}:** `{c.get('form')}` — *{c.get('sentence')}*  \n  &nbsp;&nbsp;&nbsp;&nbsp;*(En: {c.get('sentence_en')})*")

            st.markdown("#### 💬 Commonly Used Phrases")
            phrases = data.get("common_phrases", [])
            for p in phrases:
                st.markdown(f"👉 **{p.get('phrase_de')}** — *{p.get('phrase_en')}*")

    except Exception as e:
        st.error(f"Error compiling flashcard details: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES (HANDBOOK MATCHED)
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Core Grammar Modules & Practice Exercises")
    st.write("Review class handbook modules and complete 20 practice exercises per lesson with instant evaluations and explanations.")

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
        "Lesson 23: Two-Way Prepositions and Directional Meaning",
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

    selected_lesson = st.selectbox("Select Handbook Lesson to Study:", handbook_lessons)

    if st.button("🎲 Generate Lesson Summary & 20 Targeted Practice Exercises", type="primary"):
        with st.spinner("Gem is summarizing module and constructing 20 targeted practice exercises..."):
            prompt = f"""
            Create a complete study & exercise package for '{selected_lesson}'.
            Return strict JSON with this exact schema:
            {{
                "lesson_title": "{selected_lesson}",
                "lesson_summary": "Detailed, highly practical explanation of core grammar rules and handbook concepts for this lesson.",
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
        st.markdown(f"### 📘 {mod['lesson_title']}")
        st.info(mod["lesson_summary"])

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
            
            # Grade Section 1
            st.markdown("#### 1. Multiple Choice Evaluation")
            score_mc = 0
            for idx, q in enumerate(mod["exercises_mc"], start=1):
                u_ans = mc_user_answers.get(q['id'])
                if u_ans == q['correct']:
                    score_mc += 1
                    st.success(f"**Q{idx}: Correct!** ({q['correct']}) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['correct']}`\n\n💡 **Reason:** {q['explanation']}")

            # Grade Section 2
            st.markdown("#### 2. Fill in the Blanks Evaluation")
            score_fib = 0
            for idx, q in enumerate(mod["exercises_fib"], start=1):
                u_ans = fib_user_answers.get(q['id'], "").strip().lower()
                c_ans = q['answer'].strip().lower()
                if u_ans == c_ans:
                    score_fib += 1
                    st.success(f"**Q{idx}: Correct!** (`{q['answer']}`) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['answer']}`\n\n💡 **Reason:** {q['explanation']}")

            # Grade Section 3 & 4 with AI verification
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
        st.markdown("**Teil 1:** Read short emails or notes and answer 5 Richtig/Falsch tasks.")
        if st.button("🎲 Generate Lesen Teil 1 (5 Tasks)", type="primary"):
            with st.spinner("Gem is generating 5 Teil 1 tasks..."):
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
                    json_str = generate_cached_content(prompt, is_json=True)
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
        st.markdown("**Teil 2:** Match user situations to classified website ads A or B (5 tasks).")
        if st.button("🎲 Generate Lesen Teil 2 (5 Tasks)", type="primary"):
            with st.spinner("Gem is generating 5 Teil 2 tasks..."):
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
                    json_str = generate_cached_content(prompt, is_json=True)
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
        st.markdown("**Teil 3:** Read public signs/notices and answer 5 Richtig/Falsch tasks.")
        if st.button("🎲 Generate Lesen Teil 3 (5 Tasks)", type="primary"):
            with st.spinner("Gem is generating 5 Teil 3 sign tasks..."):
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
                    json_str = generate_cached_content(prompt, is_json=True)
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
        "Teil 1: 6 Dialogues (Played 2x)", 
        "Teil 2: 4 Announcements (Played 1x)", 
        "Teil 3: 5 Voicemails (Played 2x)"
    ])

    with h_tab1:
        st.info("ℹ️ Teil 1: 6 dialogues played TWICE. Choose A, B, or C.")
        if st.button("🎲 Generate Hören Teil 1 (6 Tasks + Audio)", type="primary"):
            with st.spinner("Gem is synthesizing 6 audio dialogues..."):
                prompt = """
                Generate Goethe A1 Hören Teil 1: 6 short dialogues with 1 multiple-choice task per dialogue (A/B/C).
                Return strict JSON format:
                {
                    "tasks": [
                        {"id": "h1_1", "script": "Dialogue 1 German transcript", "question": "Question 1", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."},
                        {"id": "h1_2", "script": "Dialogue 2 German transcript", "question": "Question 2", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."},
                        {"id": "h1_3", "script": "Dialogue 3 German transcript", "question": "Question 3", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."},
                        {"id": "h1_4", "script": "Dialogue 4 German transcript", "question": "Question 4", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."},
                        {"id": "h1_5", "script": "Dialogue 5 German transcript", "question": "Question 5", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."},
                        {"id": "h1_6", "script": "Dialogue 6 German transcript", "question": "Question 6", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."}
                    ]
                }
                """
                try:
                    json_str = generate_cached_content(prompt, is_json=True)
                    st.session_state.hoeren_t1 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t1" in st.session_state:
            d = st.session_state.hoeren_t1
            ans1 = {}
            for idx, t in enumerate(d["tasks"], start=1):
                st.markdown(f"#### 🔊 Audio Dialogue {idx} (Played 2x)")
                st.audio(generate_german_audio_bytes(t["script"]), format="audio/mp3")
                with st.expander(f"👁️ Transcript {idx}"): st.write(t["script"])
                st.markdown(f"**Task {idx}: {t['question']}**")
                ans1[t["id"]] = st.radio(f"Select Q{idx}:", t["options"], key=f"rad_ht1_{t['id']}")
            if st.button("Submit Hören Teil 1"):
                score = sum(1 for t in d["tasks"] if ans1.get(t["id"]) == t["answer"])
                st.success(f"Teil 1 Score: {score} / 6")

    with h_tab2:
        st.warning("⚠️ Teil 2: 4 public announcements played ONCE. Judge Richtig or Falsch.")
        if st.button("🎲 Generate Hören Teil 2 (4 Tasks + Audio)", type="primary"):
            with st.spinner("Gem is synthesizing 4 public announcements..."):
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
                    json_str = generate_cached_content(prompt, is_json=True)
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
        st.info("ℹ️ Teil 3: 5 phone voicemails played TWICE. Choose A, B, or C.")
        if st.button("🎲 Generate Hören Teil 3 (5 Tasks + Audio)", type="primary"):
            with st.spinner("Gem is synthesizing 5 voicemail messages..."):
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
                    json_str = generate_cached_content(prompt, is_json=True)
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
        st.markdown("**Teil 1:** Read a short background text and complete the 5 missing fields on a registration form.")
        if st.button("🎲 Generate Schreiben Teil 1 Scenario", type="primary"):
            with st.spinner("Gem is creating form exercise..."):
                prompt = """
                Generate Goethe A1 Schreiben Teil 1 form exercise.
                Return strict JSON format:
                {
                    "scenario": "Short travel/booking scenario text...",
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
                    json_str = generate_cached_content(prompt, is_json=True)
                    st.session_state.schreiben_t1 = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "schreiben_t1" in st.session_state:
            d = st.session_state.schreiben_t1
            st.info(f"**Scenario:** {d['scenario']}")
            st.markdown(f"### 📋 {d['form_title']}")
            user_inputs = {}
            for f in d["fields"]:
                user_inputs[f["id"]] = st.text_input(f["label"], key=f"inp_{f['id']}")
            
            if st.button("Check Form Gaps"):
                score = sum(1 for f in d["fields"] if user_inputs[f["id"]].strip().lower() == f["answer"].strip().lower())
                st.metric("Form Score", f"{score} / 5")

    with s_tab2:
        st.markdown("**Teil 2:** Write a short informal message/email (~30 words) hitting 3 required content points.")
        if st.button("🎲 Generate Schreiben Teil 2 Prompt", type="primary"):
            with st.spinner("Gem is generating email prompt..."):
                try:
                    prompt = "Generate an official Goethe A1 Schreiben Teil 2 prompt specifying a scenario and 3 explicit bullet points."
                    st.session_state.schreiben_t2_prompt = generate_cached_content(prompt)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "schreiben_t2_prompt" in st.session_state:
            st.info(st.session_state.schreiben_t2_prompt)
            u_email = st.text_area("Your German Response (~30 words):", height=140)
            if st.button("Evaluate Email with Gem"):
                if u_email.strip():
                    with st.spinner("Gem is evaluating task fulfillment..."):
                        try:
                            eval_prompt = f"PROMPT:\n{st.session_state.schreiben_t2_prompt}\n\nSUBMISSION:\n{u_email}\n\nGrade task fulfillment across all 3 bullet points, V2 verb order, and appropriate salutations/closings."
                            eval_res = client.models.generate_content(
                                model=MODEL_NAME, contents=eval_prompt,
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.markdown("### Official Examiner Breakdown")
                            st.write(eval_res.text)
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
        **Teil 1:** Introduce yourself using standard criteria and spell a name or state a phone/ZIP code:
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
                            model=MODEL_NAME,
                            contents=["Transcribe audio and evaluate candidate self-introduction and spelling against Goethe A1 criteria.", audio_part],
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                        )
                        st.write(eval_res.text)
                    except Exception as e: st.error(f"Error: {str(e)}")

    with sp_tab2:
        st.markdown("**Teil 2:** Draw a topic card, formulate a W-question for your partner, and answer theirs (Verb in Position 2).")
        if st.button("🎲 Draw Topic Card", type="primary"):
            with st.spinner("Gem is drawing card..."):
                try:
                    st.session_state.card_t2 = generate_cached_content("Generate Goethe A1 Sprechen topic card (e.g. Thema: 'Einkaufen', Wort: 'Brot').")
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
                                model=MODEL_NAME,
                                contents=[f"Card: {st.session_state.card_t2}. Transcribe audio and verify if candidate formed a correct W-question with verb in Position 2.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    with sp_tab3:
        st.markdown("**Teil 3:** Draw a card showing an object/situation and make a polite request/instruction (Verb in Position 1).")
        if st.button("🎲 Draw Picture Request Card", type="primary"):
            with st.spinner("Gem is drawing card..."):
                try:
                    st.session_state.card_t3 = generate_cached_content("Generate Goethe A1 Sprechen picture request card (e.g. Gegenstand: Bleistift).")
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
                                model=MODEL_NAME,
                                contents=[f"Card: {st.session_state.card_t3}. Transcribe audio and verify if candidate formed a correct imperative request with verb in Position 1.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. ASK GEM
# ----------------------------------------------------
elif nav_choice == "💬 Ask Gem (AI Tutor)":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("💬 Ask Gem — Interactive AI Tutor")
    if prompt := st.chat_input("Ask Gem a question:"):
        res = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        )
        st.write(res.text)
    st.markdown('</div>', unsafe_allow_html=True)
