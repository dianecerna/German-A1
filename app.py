import os
import random
import streamlit as st
from google import genai
from google.genai import types
from streamlit_mic_recorder import mic_recorder

# Configure Streamlit Page - Force Sidebar Expanded
st.set_page_config(
    page_title="Goethe A1 Prep Studio", 
    page_icon="🇩🇪", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS without hiding the header bar
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .accent-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06);
        margin-bottom: 20px;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    .pill-badge {
        background-color: #eff6ff;
        color: #1d4ed8;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Fetch API Key securely
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

# Initialize GenAI Client
client = genai.Client(api_key=api_key.strip())

SYSTEM_INSTRUCTION = """
You are Zerti, an expert German language tutor and official Goethe-Institut A1 examiner evaluating a candidate for Goethe-Zertifikat A1 (Start Deutsch 1).

OFFICIAL GOETHE A1 EXAM FORMAT RULES:
- LESEN TEIL 1: Short emails/letters with Richtig/Falsch questions.
- LESEN TEIL 2: Scenarios matching an intent to Website A or Website B.
- LESEN TEIL 3: Public signs/notices with Richtig/Falsch statements.

- HÖREN TEIL 1: Audio transcripts played TWICE with A/B/C items.
- HÖREN TEIL 2: Public announcements played ONCE with Richtig/Falsch items.
- HÖREN TEIL 3: Phone messages played TWICE with A/B/C items.

- SCHREIBEN TEIL 1: Formular ausfüllen (5 missing pieces of personal/travel information).
- SCHREIBEN TEIL 2: E-Mail / Brief (~30 words) covering 3 explicit bullet points. Evaluate on task completion (3/3 points), V2 verb order, and matching salutations/closings.

- SPRECHEN TEIL 1: Sich vorstellen (7 criteria: Name, Alter, Land, Wohnort, Sprachen, Beruf, Hobby + Buchstabieren/Zahlen).
- SPRECHEN TEIL 2: Informationen erfragen und antworten (W-Fragen using Thema/Wort cards, conjugated verb in Position 2).
- SPRECHEN TEIL 3: Bitten formulieren und darauf reagieren (Imperatives/Requests with Position 1 verb rule or 'Können Sie bitte...').

VOCABULARY RULE: Provide exhaustive, highly structured A1 word analyses including full pronoun conjugations (ich, du, er/sie/es, wir, ihr, sie/Sie), Perfekt forms, case rules (Akk/Dat), comparative forms, sample sentences, and common phrases.
"""

GOETHE_A1_SAMPLE_WORDS = [
    "einkaufen", "Termin", "Fahrkarte", "anrufen", "gut", "Formular", 
    "Anmeldung", "Flughafen", "abholen", "Apotheke", "verstehen", "groß",
    "reservieren", "Bahnhof", "bezahlen", "Wohnung", "mitbringen", "Sprechstunde"
]

# Navigation Sidebar
st.sidebar.title("🇩🇪 Goethe A1 Studio")
st.sidebar.caption("Target Exam: Dec 12, 2026")
st.sidebar.divider()

nav_choice = st.sidebar.radio("Navigation", [
    "🏠 Study Dashboard", 
    "📚 Master Goethe Word Engine",
    "📖 Goethe A1 Lesen (Reading)",
    "🎧 Goethe A1 Hören (Listening)",
    "✍️ Goethe A1 Schreiben (Writing)", 
    "🗣️ Goethe A1 Sprechen (Speaking)",
    "💬 Ask Zerti (AI Tutor)"
])

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.markdown('<span class="pill-badge">Goethe-Zertifikat A1 Structure</span>', unsafe_allow_html=True)
    st.title("Official Exam Format & Deep Vocab Engine")
    st.write("📅 **Exam Date:** December 12, 2026")
    st.write("Master A1 vocabulary with full pronoun conjugations, Perfekt forms, case rules, and exam drills.")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📖 Lesen & ✍️ Schreiben")
        st.markdown("""
        * **Lesen Teil 1:** Emails/Letters (Richtig/Falsch)
        * **Lesen Teil 2:** Web Advertisements (Site A or B)
        * **Lesen Teil 3:** Public Signs (Richtig/Falsch)
        * **Schreiben Teil 1:** Form filling (5 gaps)
        * **Schreiben Teil 2:** ~30-word Email (3 points)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🎧 Hören & 🗣️ Sprechen")
        st.markdown("""
        * **Hören Teil 1:** Conversations (2x Audio, A/B/C)
        * **Hören Teil 2:** Announcements (1x Audio, Richtig/Falsch)
        * **Hören Teil 3:** Voicemails (2x Audio, A/B/C)
        * **Sprechen Teil 1:** Self-Introduction & Spelling
        * **Sprechen Teil 2:** W-Questions (V2 rule)
        * **Sprechen Teil 3:** Requests & Imperatives (V1 rule)
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Vocabulary Engine")
    st.write("Select or search any German word to generate a complete A1 study card.")

    col_select, col_search = st.columns([1, 1])
    with col_select:
        selected_word = st.selectbox("Select an A1 Keyword:", GOETHE_A1_SAMPLE_WORDS)
    with col_search:
        custom_word = st.text_input("Or type any German word:")

    active_word = custom_word.strip() if custom_word.strip() else selected_word

    if st.button(f"🔍 Generate Full Breakdown for '{active_word}'", type="primary"):
        with st.spinner(f"Zerti is compiling comprehensive A1 grammar details for '{active_word}'..."):
            vocab_prompt = f"""
            Analyze the German word '{active_word}' strictly for a Goethe A1 level candidate.
            Provide a beautifully formatted, clear Markdown study card covering:

            1. **Basic Info**: Word, Article (der/die/das if noun), Plural Form, English Meaning.
            2. **Grammar & Cases**:
               - If Verb: Present tense rules, **Perfekt tense** (hat/ist + Partizip II), and required case/preposition (e.g. Akkusativ/Dativ).
               - If Noun: Gender, Akkusativ form, Dativ form, and example prepositions.
               - If Adjective: Positive, **Komparativ**, and **Superlativ** forms.
            3. **Full Pronoun Conjugations (if verb or applicable)**:
               - ich
               - du
               - er / sie / es
               - wir
               - ihr
               - sie / Sie
            4. **Sample Sentences for Every Pronoun**:
               - Provide 6 clear A1 sentences (one for each pronoun: ich, du, er/sie/es, wir, ihr, sie/Sie) using '{active_word}' in correct V2 word order with English translations.
            5. **Commonly Used A1 Phrases & Collocations**:
               - 3 to 4 everyday A1 phrases or exam expressions using '{active_word}'.
            """
            
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=vocab_prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
            )
            st.markdown(res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Goethe A1 Lesen Practice (25 Mins, 15 Points)")
    
    lesen_tab1, lesen_tab2, lesen_tab3 = st.tabs([
        "Teil 1: E-Mails & Briefe", 
        "Teil 2: Webseiten & Anzeigen", 
        "Teil 3: Schilder & Aushänge"
    ])

    with lesen_tab1:
        st.markdown("**Teil 1:** Read short personal messages and decide if statements are Richtig or Falsch.")
        if st.button("🎲 Generate Lesen Teil 1 Exercise"):
            with st.spinner("Generating Teil 1 passage..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Lesen Teil 1 exercise using Goethe A1 vocabulary: 1 short personal email (~35 words) followed by 2 Richtig/Falsch comprehension questions with answer explanations.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)

    with lesen_tab2:
        st.markdown("**Teil 2:** Read a scenario and select which website matches the user's intent (Website A vs Website B).")
        if st.button("🎲 Generate Lesen Teil 2 Exercise"):
            with st.spinner("Generating Teil 2 ads..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Lesen Teil 2 exercise using Goethe A1 vocabulary: A user scenario and 2 short website descriptions (Website A vs Website B). State which site is correct and why.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)

    with lesen_tab3:
        st.markdown("**Teil 3:** Read public signs/notices and evaluate Richtig/Falsch statements.")
        if st.button("🎲 Generate Lesen Teil 3 Exercise"):
            with st.spinner("Generating Teil 3 sign..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Lesen Teil 3 exercise using Goethe A1 vocabulary: 1 realistic German public sign text and 2 Richtig/Falsch questions.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🎧 Goethe A1 Hören Practice (20 Mins, 15 Points)")
    
    hoeren_tab1, hoeren_tab2, hoeren_tab3 = st.tabs([
        "Teil 1: Alltagsgespräche (2x)", 
        "Teil 2: Durchsagen (1x)", 
        "Teil 3: Telefonansagen (2x)"
    ])

    with hoeren_tab1:
        st.info("ℹ️ In the exam, Teil 1 audio is played **twice**.")
        st.markdown("**Teil 1:** Short everyday conversations with multiple-choice items (a, b, c).")
        if st.button("🎲 Generate Hören Teil 1 Script & Questions"):
            with st.spinner("Generating audio transcript scenario..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Hören Teil 1 dialogue transcript using Goethe A1 vocabulary with 2 multiple-choice questions (a, b, c) and explanations.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)

    with hoeren_tab2:
        st.warning("⚠️ In the exam, Teil 2 announcements are played **only ONCE**.")
        st.markdown("**Teil 2:** Public announcements at train stations, airports, or shops with Richtig/Falsch questions.")
        if st.button("🎲 Generate Hören Teil 2 Announcement"):
            with st.spinner("Generating announcement script..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Hören Teil 2 public announcement script using Goethe A1 vocabulary with 2 Richtig/Falsch questions.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)

    with hoeren_tab3:
        st.info("ℹ️ In the exam, Teil 3 telephone messages are played **twice**.")
        st.markdown("**Teil 3:** Answering machine messages or voicemails with multiple-choice items (a, b, c).")
        if st.button("🎲 Generate Hören Teil 3 Voicemail"):
            with st.spinner("Generating voicemail script..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Hören Teil 3 voicemail transcript using Goethe A1 vocabulary with 2 multiple-choice questions (a, b, c).",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✍️ Goethe A1 Schreiben Practice (20 Mins, 15 Points)")

    schr_tab1, schr_tab2 = st.tabs([
        "Teil 1: Formular ausfüllen (5 Lücken)", 
        "Teil 2: E-Mail / Brief (~30 Wörter)"
    ])

    with schr_tab1:
        st.markdown("**Teil 1:** Read a short background text and fill in the 5 missing pieces of information on a registration form.")
        if st.button("🎲 Generate Schreiben Teil 1 Scenario & Form"):
            with st.spinner("Generating form exercise..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Schreiben Teil 1 exercise using Goethe A1 vocabulary: A background scenario about booking a trip/hotel, and a form with 5 missing fields (1 to 5) to fill in, along with answer key.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)

    with schr_tab2:
        st.markdown("**Teil 2:** Write a short message/email (~30 words) addressing all 3 required points.")
        if "writing_prompt" not in st.session_state:
            st.session_state.writing_prompt = ""

        if st.button("🎲 Generate Schreiben Teil 2 Prompt"):
            with st.spinner("Generating email prompt..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate an official Goethe A1 Schreiben Teil 2 prompt using Goethe A1 vocabulary: A realistic scenario with 3 bullet points.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.session_state.writing_prompt = res.text

        if st.session_state.writing_prompt:
            st.info(st.session_state.writing_prompt)
            user_text = st.text_area("Your Response in German:", height=140)

            if st.button("Evaluate E-Mail with AI", type="primary"):
                if user_text.strip():
                    with st.spinner("Evaluating submission against Goethe A1 rubric..."):
                        eval_res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"PROMPT:\n{st.session_state.writing_prompt}\n\nSUBMISSION:\n{user_text}\n\nGrade task fulfillment (3 points), V2 verb order, and matching salutations/closings.",
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                        )
                        st.markdown("### Official Examiner Breakdown")
                        st.write(eval_res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🗣️ Goethe A1 Sprechen Practice (15 Mins, 15 Points)")

    sp_tab1, sp_tab2, sp_tab3 = st.tabs([
        "Teil 1: Sich vorstellen & Buchstabieren", 
        "Teil 2: Informationen erfragen (Themenkarten)", 
        "Teil 3: Bitten & Reaktionen (Bilderkarte)"
    ])

    with sp_tab1:
        st.markdown("""
        **Teil 1:** Introduce yourself using the 7 standard Goethe prompt categories, then practice spelling a word or stating a telephone number/postcode:
        * *Name* | *Alter* | *Land* | *Wohnort* | *Sprachen* | *Beruf* | *Hobby*
        """)
        user_intro = st.text_area("Type your self-introduction in German:")
        if st.button("Evaluate Self-Introduction"):
            if user_intro.strip():
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Evaluate this candidate's Goethe A1 Sprechen Teil 1 self-introduction and verify if all 7 points are covered accurately: {user_intro}",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.write(res.text)

    with sp_tab2:
        st.markdown("**Teil 2:** Draw a topic card (Theme + Keyword) to formulate a W-question. Verb MUST be in Position 2!")
        if "card_prompt_t2" not in st.session_state:
            st.session_state.card_prompt_t2 = "Thema: Einkaufen | Wort: Brot"

        if st.button("🎲 Draw Teil 2 Card"):
            with st.spinner("Drawing card..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Sprechen Teil 2 topic card drawing from official Goethe A1 Wortliste (e.g. Thema: 'Einkaufen', Wort: 'Brot').",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.session_state.card_prompt_t2 = res.text

        st.success(f"🎴 **Your Card:** {st.session_state.card_prompt_t2}")

        audio_t2 = mic_recorder(
            start_prompt="Record Question 🎙️",
            stop_prompt="Stop Recording 🛑",
            key='sp_rec_t2'
        )

        if audio_t2:
            st.audio(audio_t2['bytes'], format='audio/wav')
            if st.button("Evaluate Spoken Question"):
                with st.spinner("Zerti is evaluating your question syntax..."):
                    audio_part = types.Part.from_bytes(data=audio_t2['bytes'], mime_type="audio/wav")
                    prompt = f"Card: {st.session_state.card_prompt_t2}. Transcribe spoken audio and verify if candidate formed a correct Goethe A1 W-question with verb in Position 2."
                    eval_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[prompt, audio_part],
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.write(eval_res.text)

    with sp_tab3:
        st.markdown("**Teil 3:** Draw a request card (Object/Picture) to make an imperative or request. Verb MUST be in Position 1!")
        if "card_prompt_t3" not in st.session_state:
            st.session_state.card_prompt_t3 = "Gegenstand: Bleistift (Pencil)"

        if st.button("🎲 Draw Teil 3 Card"):
            with st.spinner("Drawing card..."):
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate a Goethe A1 Sprechen Teil 3 picture/object request card drawing from Goethe A1 vocabulary.",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.session_state.card_prompt_t3 = res.text

        st.success(f"🎴 **Your Card:** {st.session_state.card_prompt_t3}")

        audio_t3 = mic_recorder(
            start_prompt="Record Request 🎙️",
            stop_prompt="Stop Recording 🛑",
            key='sp_rec_t3'
        )

        if audio_t3:
            st.audio(audio_t3['bytes'], format='audio/wav')
            if st.button("Evaluate Spoken Request"):
                with st.spinner("Zerti is evaluating your request syntax..."):
                    audio_part = types.Part.from_bytes(data=audio_t3['bytes'], mime_type="audio/wav")
                    prompt = f"Card: {st.session_state.card_prompt_t3}. Transcribe spoken audio and verify if candidate formed a correct Goethe A1 request/imperative with verb in Position 1."
                    eval_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[prompt, audio_part],
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.write(eval_res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. ASK ZERTI
# ----------------------------------------------------
elif nav_choice == "💬 Ask Zerti (AI Tutor)":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("🐱 Zerti — Interactive AI Tutor")
    st.write("Ask Zerti about grammar rules, sentence structures, or vocabulary explanations.")
    st.markdown('</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask Zerti a question:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Zerti is thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
