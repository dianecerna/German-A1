import os
import json
import io
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# Streamlit Page Setup
st.set_page_config(
    page_title="Goethe A1 Prep Studio", 
    page_icon="🇩🇪", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Flashcard & Dashboard Styling
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
    .main-card { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .accent-card { background: #ffffff; border-radius: 16px; padding: 24px; border-left: 6px solid #2563eb; box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    
    /* Interactive Flashcard UI */
    .flashcard-front {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .flashcard-word {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #38bdf8;
        margin-bottom: 10px;
    }
    .flashcard-back {
        background: #ffffff;
        border: 2px solid #3b82f6;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Fetch API Key securely
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())
MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = """
You are Gem, an expert German language tutor and official Goethe-Institut A1 examiner evaluating a candidate for Goethe-Zertifikat A1 (Start Deutsch 1).

OFFICIAL GOETHE-ZERTIFIKAT A1 EXAM RULES:
- LESEN (25 mins, 15 tasks):
  * Teil 1: Short personal emails/letters (5 Richtig/Falsch tasks).
  * Teil 2: Situation matching to classified ads Website A vs B (5 tasks).
  * Teil 3: Public signs, notices, info boards (5 Richtig/Falsch tasks).

- HÖREN (20 mins, 15 tasks):
  * Teil 1: 6 everyday dialogues played TWICE (6 multiple-choice A/B/C tasks).
  * Teil 2: 4 public announcements played ONCE (4 Richtig/Falsch tasks).
  * Teil 3: 5 phone messages / voicemails played TWICE (5 multiple-choice A/B/C tasks).

- SCHREIBEN (20 mins, 2 tasks):
  * Teil 1: Formular ausfüllen (5 missing fields based on short scenario).
  * Teil 2: Short informal email/message (~30 words) hitting 3 explicit bullet points.

- SPRECHEN (15 mins, small group format):
  * Teil 1: Sich vorstellen (7 standard points) + Spelling a word / stating phone number.
  * Teil 2: W-Fragen with topic cards (Verb in Position 2 rule).
  * Teil 3: Imperative requests with picture cards (Verb in Position 1 or 'Können Sie bitte...' rule).

When generating JSON for exercises, output strict JSON with no conversational text or markdown wrappers.
"""

# Cached API Helper
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

# Load 600+ Word Bank
@st.cache_data
def load_goethe_vocab():
    try:
        with open("goethe_vocab.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "🍎 Essen & Trinken": ["einkaufen", "das Brot", "der Apfel", "die Milch", "das Wasser"],
            "🚗 Reisen & Verkehr": ["die Fahrkarte", "der Bahnhof", "der Flughafen", "abholen"]
        }

GOETHE_WORD_BANK = load_goethe_vocab()

# Audio Helper
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
    "📖 A1 Core Grammar Modules",
    "📚 Master Goethe Word Engine",
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
    st.write("Replicating exact Goethe-Zertifikat A1 exam structure, audio synthesis, and voice evaluation.")
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
# 2. A1 CORE GRAMMAR MODULES (EXPANDED TO 7 PILLARS)
# ----------------------------------------------------
elif nav_choice == "📖 A1 Core Grammar Modules":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Goethe A1 Core Concept Mastery (7 Foundational Pillars)")
    st.write("Master these essential survival grammar modules required for the Goethe A1 exam.")

    m_tab1, m_tab2, m_tab3, m_tab4, m_tab5, m_tab6, m_tab7 = st.tabs([
        "1. Verbs & Conjugation",
        "2. Perfekt Past Tense",
        "3. Satzbau (Word Order)",
        "4. Nouns & Articles",
        "5. Cases (Kasus)",
        "6. Pronouns",
        "7. Prepositions"
    ])

    with m_tab1:
        st.markdown("### 1. Verben und Konjugation")
        st.markdown("""
        * **Regular Verb Endings:**
          - `ich` **-e** (*ich lerne*) | `du` **-st** (*du wohnst*) | `er/sie/es` **-t** (*er macht*)
          - `wir` **-en** (*wir lernen*) | `ihr` **-t** (*ihr wohnt*) | `sie/Sie` **-en** (*sie machen*)
        * **Stem-Vowel Changing Verbs:** Vowel changes occur only in `du` and `er/sie/es` forms:
          - **e -> i / ie:** *sprechen* -> `du sprichst`, `er spricht` | *sehen* -> `du siehst`, `er sieht`
          - **a -> ä:** *fahren* -> `du fährst`, `er fährt` | *schlafen* -> `du schläfst`, `er schläft`
        * **Modal Verbs:** Modal in Position 2, Infinitive verb at the very end:
          - *können* (can/ability), *möchten* (would like), *wollen* (want), *müssen* (must), *dürfen* (may/permission)
          - *Example:* Ich **kann** heute Deutsch **lernen**.
        * **Separable Verbs (Trennbare Verben):** Prefix splits off and moves to the very end:
          - *einkaufen:* Ich **kaufe** im Supermarkt **ein**.
          - *anrufen:* Sie **ruft** den Arzt **an**.
        """)

    with m_tab2:
        st.markdown("### 2. Vergangenheit (Das Perfekt Tense)")
        st.markdown("""
        Used for conversational past tense (*talking about what you did yesterday*).
        
        **Formula:** `haben` or `sein` (conjugated in Position 2) + `Partizip II` (at the very end).
        * **Auxiliary Verb Selection:**
          - **sein:** Used for movement, location change, or state change (*gehen, fahren, kommen, fliegen, aufstehen*).
            - *Example:* Ich **bin** um 7 Uhr **aufgestanden**.
          - **haben:** Used for most standard transitive verbs.
            - *Example:* Ich **habe** eine E-Mail **geschrieben**.
        * **Partizip II Patterns:**
          - Regular: **ge-** + Verb stem + **-t** (*gekauft, gemacht, gelernt*)
          - Irregular: **ge-** + Changed stem + **-en** (*gesprochen, gesehen, gefahren*)
        """)

    with m_tab3:
        st.markdown("### 3. Satzbau & Fragen (Sentence Structure)")
        st.markdown("""
        * **Main Clause (V2 Rule):** The conjugated verb MUST always sit in **Position 2**.
          - *Subject First:* **Ich** **gehe** heute ins Büro.
          - *Adverb First:* **Heute** **gehe** ich ins Büro.
        * **Questions (Fragesätze):**
          - **W-Fragen (Open):** Question word first -> Verb in Position 2 (*Wo **wohnen** Sie?*)
          - **Ja/Nein-Fragen (Closed):** Conjugated verb in **Position 1** (* **Kommen** Sie aus Spanien?*)
        * **Subordinating Conjunctions (Basic):** *weil* (because), *dass* (that), *wenn* (if/when) send the conjugated verb to the **very end** of the clause:
          - *Ich lerne Deutsch, **weil** ich in Deutschland **arbeite**.*
        """)

    with m_tab4:
        st.markdown("### 4. Nomen und Artikel (Nouns, Articles & Gender)")
        st.markdown("""
        All German nouns are capitalized and categorized by 3 genders:
        
        | Gender | Definite (The) | Indefinite (A/An) | Negative (No/Not A) |
        |---|---|---|---|
        | **Masculine** | **der** Mann | **ein** Mann | **kein** Mann |
        | **Feminine** | **die** Frau | **eine** Frau | **keine** Frau |
        | **Neuter** | **das** Kind | **ein** Kind | **kein** Kind |
        | **Plural** | **die** Kinder | — | **keine** Kinder |

        *Example Negation:* Ich habe **keinen** Hunger. / Das ist **kein** Problem.
        """)

    with m_tab5:
        st.markdown("### 5. Cases (Kasus: Nominativ & Akkusativ)")
        st.markdown("""
        A1 candidates must master the difference between Subject and Direct Object:
        * **Nominativ (Subject):** Performs the action (*der Mann, ein Mann*).
        * **Akkusativ (Direct Object):** Receives the action. **Only masculine articles change!**
        
        | Case | Masculine | Feminine | Neuter | Plural |
        |---|---|---|---|---|
        | **Nominativ** | der / ein | die / eine | das / ein | die / keine |
        | **Akkusativ** | **den / einen / keinen** | die / eine | das / ein | die / keine |

        *Example:* **Der** Mann kauft **einen** Apfel. (*Der Mann* = Subject/Nom, *einen Apfel* = Object/Akk).
        """)

    with m_tab6:
        st.markdown("### 6. Pronomen (Personal & Possessive Pronouns)")
        st.markdown("""
        * **Personal Pronouns:**
          - Singular: `ich` (I), `du` (you informal), `er` (he), `sie` (she), `es` (it)
          - Plural: `wir` (we), `ihr` (you all), `sie` (they), `Sie` (You formal)
        * **Possessive Pronouns (Basic Ownership):**
          - `ich` -> **mein / meine** (*mein Vater, meine Mutter*)
          - `du` -> **dein / deine** (*dein Schlüssel, deine Tasche*)
          - `Sie` (formal) -> **Ihr / Ihre** (*Ihr Name, Ihre Adresse*)
        """)

    with m_tab7:
        st.markdown("### 7. Präpositionen (Prepositions for Time & Location)")
        st.markdown("""
        * **Location & Direction:**
          - **ins** (*in das*) + Destination: *Ich gehe **ins** Büro.*
          - **im** (*in dem*) + Location: *Ich bin **im** Supermarkt.*
          - **nach** + Cities/Countries: *Ich fahre **nach** Berlin.*
          - **zu** + Places/People: *Ich gehe **zum** Arzt.*
        * **Time Expressions:**
          - **um** + Clock times: * **um** 8 Uhr*
          - **am** + Days & parts of day: * **am** Montag, **am** Morgen*
          - **im** + Months & seasons: * **im** Juli, **im** Sommer*
        """)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. MASTER GOETHE WORD ENGINE (FLIP FLASHCARD)
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Interactive Flashcard Engine")
    
    cat_col, word_col = st.columns(2)
    with cat_col:
        selected_cat = st.selectbox("Select Topic Category:", list(GOETHE_WORD_BANK.keys()))
    with word_col:
        selected_word = st.selectbox("Select Keyword:", GOETHE_WORD_BANK[selected_cat])
    
    custom_word = st.text_input("Or type any German word directly:")
    active_word = custom_word.strip() if custom_word.strip() else selected_word

    if "show_card_back" not in st.session_state:
        st.session_state.show_card_back = False

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button(f"🔍 Load Flashcard for '{active_word}'", type="primary"):
            st.session_state.show_card_back = False
    with col_btn2:
        if st.button("🔄 Flip Flashcard (Front / Back)"):
            st.session_state.show_card_back = not st.session_state.show_card_back

    prompt = f"""
    Generate a comprehensive A1 study card for '{active_word}'.
    Return strictly JSON with this schema:
    {{
        "word": "{active_word}",
        "article_gender": "Verb / der / die / das",
        "plural": "N/A or Plural form",
        "english_meaning": "English translation",
        "perfekt_form": "hat/ist + Partizip II",
        "perfekt_sentence": "Sample Perfekt sentence",
        "komparativ": "Komparativ form or N/A",
        "superlativ": "Superlativ form or N/A",
        "conjugation": {{
            "ich": "...", "du": "...", "er_sie_es": "...",
            "wir": "...", "ihr": "...", "sie_Sie": "..."
        }},
        "sample_sentences": ["Ich...", "Du...", "Er/Sie/Es...", "Wir...", "Ihr...", "Sie/sie..."],
        "common_a1_phrases": ["Phrase 1", "Phrase 2"],
        "grammar_notes": "Key A1 grammar rule or preposition requirement"
    }}
    """
    try:
        raw_json = generate_cached_content(prompt, is_json=True)
        data = json.loads(raw_json)

        # FRONT OF FLASHCARD
        if not st.session_state.show_card_back:
            st.markdown(f"""
            <div class="flashcard-front">
                <p style="color: #94a3b8; font-weight: 600;">GOETHE A1 FLASHCARD (FRONT)</p>
                <div class="flashcard-word">{data.get("word", active_word)}</div>
                <p style="color: #cbd5e1;">Click 'Flip Flashcard 🔄' to view full grammar details</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🔊 Native Audio Pronunciation")
            audio_bytes = generate_german_audio_bytes(active_word)
            st.audio(audio_bytes, format="audio/mp3")

        # BACK OF FLASHCARD
        else:
            st.markdown(f"""
            <div class="flashcard-back">
                <h2 style="color: #1e293b; margin-bottom: 5px;">{data.get("word", active_word)}</h2>
                <p style="color: #2563eb; font-weight: 700; font-size: 1.1rem;">Meaning: {data.get("english_meaning", "")}</p>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Article / Gender", data.get("article_gender", "-"))
            m2.metric("Plural Form", data.get("plural", "-"))
            m3.metric("Comparative", data.get("komparativ", "N/A"))
            m4.metric("Superlative", data.get("superlativ", "N/A"))

            st.success(f"⏳ **Perfekt Tense:** `{data.get('perfekt_form', '')}` — *{data.get('perfekt_sentence', '')}*")
            st.info(f"💡 **Grammar Note:** {data.get('grammar_notes', '')}")

            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown("#### 🔄 Full Conjugation")
                conj = data.get("conjugation", {})
                st.table([
                    {"Pronoun": "ich", "Form": conj.get("ich", "-")},
                    {"Pronoun": "du", "Form": conj.get("du", "-")},
                    {"Pronoun": "er / sie / es", "Form": conj.get("er_sie_es", "-")},
                    {"Pronoun": "wir", "Form": conj.get("wir", "-")},
                    {"Pronoun": "ihr", "Form": conj.get("ihr", "-")},
                    {"Pronoun": "sie / Sie", "Form": conj.get("sie_Sie", "-")}
                ])
            with c2:
                st.markdown("#### 📝 Pronoun Sample Sentences")
                for s in data.get("sample_sentences", []):
                    st.markdown(f"• {s}")
                
                st.markdown("#### 💬 Common A1 Phrases")
                for p in data.get("common_a1_phrases", []):
                    st.markdown(f"👉 `{p}`")

    except Exception as e:
        st.error(f"Error compiling flashcard details: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 LESEN (EXACT 15 TASKS)
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
# 5. GOETHE A1 HÖREN (EXACT 15 TASKS WITH NATIVE AUDIO)
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
        st.info("ℹ️ Teil 1: 6 dialogues played **TWICE**. Choose A, B, or C.")
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
        st.warning("⚠️ Teil 2: 4 public announcements played **ONCE**. Judge Richtig or Falsch.")
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
        st.info("ℹ️ Teil 3: 5 phone voicemails played **TWICE**. Choose A, B, or C.")
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
# 6. GOETHE A1 SCHREIBEN (EXACT 2 TASKS)
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
                    prompt = "Generate an official Goethe A1 Schreiben Teil 2 prompt specifying a scenario and 3 explicit bullet points (e.g. apologizing, suggesting alternative, asking question)."
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
# 7. GOETHE A1 SPRECHEN (GROUP SIMULATION FORMAT)
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
