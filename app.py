import os
import random
import google.generativeai as genai
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Configure Streamlit Page
st.set_page_config(page_title="Goethe A1 Prep Studio", page_icon="🇩🇪", layout="wide")

# Inject Custom CSS to replicate Zertifly's sleek rounded card design
st.markdown("""
<style>
    /* Main Background & Fonts */
    .main { background-color: #f7f9fc; }
    
    /* Zertifly Rounded Card Style */
    .z-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eef2f7;
    }
    .z-card-purple {
        background: linear-gradient(135deg, #f3e8ff 0%, #ffffff 100%);
        border-radius: 18px;
        padding: 20px;
        border: 1px solid #e9d5ff;
        margin-bottom: 20px;
    }
    .z-card-green {
        background: linear-gradient(135deg, #dcfce7 0%, #ffffff 100%);
        border-radius: 18px;
        padding: 20px;
        border: 1px solid #bbf7d0;
        margin-bottom: 20px;
    }
    .z-card-orange {
        background: linear-gradient(135deg, #ffedd5 0%, #ffffff 100%);
        border-radius: 18px;
        padding: 20px;
        border: 1px solid #fed7aa;
        margin-bottom: 20px;
    }
    .z-badge {
        background-color: #e0e7ff;
        color: #3730a3;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .z-title {
        font-weight: 800;
        font-size: 1.4rem;
        color: #1e293b;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_dict_only=True)

# Fetch API key securely
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

genai.configure(api_key=api_key)

# Strict Goethe A1 Examiner System Instruction
GOETHE_A1_SYSTEM_PROMPT = """
You are a strict, official Goethe-Institut A1 examiner evaluating a candidate preparing for the Goethe-Zertifikat A1: Start Deutsch 1 exam.

EXAM EVALUATION PARAMETERS:
1. WORD ORDER (Wortstellung):
   - Aussagesätze: Conjugated verb in Position 2.
   - W-Fragen: Question word in Pos 1, conjugated verb in Pos 2.
   - Ja/Nein-Fragen & Imperative: Conjugated verb in Position 1.
   - Modalverben: Modal verb in Pos 2 -> Infinitive strictly at the END.
2. SCHREIBEN (TEIL 2) RUBRIC:
   - Verify if all 3 required points are fully covered.
   - Match informal vs. formal greetings/closings:
     * Informal: "Liebe/Lieber [Name]," -> "Viele Grüße" / "Liebe Grüße"
     * Formal: "Sehr geehrte Damen und Herren," -> "Mit freundlichen Grüßen"
3. SPRECHEN (SPEAKING) EVALUATION:
   - Check pronunciation, word order, and accuracy of A1 responses.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=GOETHE_A1_SYSTEM_PROMPT
)

# App Navigation
st.sidebar.title("🇩🇪 Zertifly A1 Prep")
nav_choice = st.sidebar.radio("Navigation", ["🏠 Dashboard", "📚 Exams (Lesen, Hören, Schreiben, Sprechen)", "🎴 Study (Vocabulary)"])

# ----------------------------------------------------
# 1. DASHBOARD VIEW (Matching Zertifly Screenshot)
# ----------------------------------------------------
if nav_choice == "🏠 Dashboard":
    st.markdown('<div class="z-card-purple">', unsafe_allow_html=True)
    st.markdown('<span class="z-badge">Goethe A1 Target</span>', unsafe_allow_html=True)
    st.markdown('<div class="z-title">My Exam Journey</div>', unsafe_allow_html=True)
    st.write("📅 **Exam Date:** December 12, 2026")
    st.progress(0.25, text="1 of 4 core modules completed")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.subheader("🔥 Daily Streak")
        st.title("1 Day")
        st.caption("Keep practicing daily to build retention!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.subheader("📊 Chance of Passing")
        st.title("78%")
        st.caption("Based on your recent Schreiben & Sprechen drills.")
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. EXAMS VIEW (Matching Zertifly Exam Sections)
# ----------------------------------------------------
elif nav_choice == "📚 Exams (Lesen, Hören, Schreiben, Sprechen)":
    exam_tab1, exam_tab2, exam_tab3, exam_tab4 = st.tabs([
        "🗣️ Goethe A1 Sprechen", 
        "📝 Goethe A1 Schreiben", 
        "📖 Goethe A1 Lesen", 
        "🎧 Goethe A1 Hören"
    ])

    # SPRECHEN (WITH VOICE INPUT RECORDING)
    with exam_tab1:
        st.markdown('<div class="z-card-orange">', unsafe_allow_html=True)
        st.markdown('<span class="z-badge">Oral Exam Simulation</span>', unsafe_allow_html=True)
        st.markdown('<div class="z-title">Goethe A1 Sprechen Practice</div>', unsafe_allow_html=True)
        st.write("Practice speaking directly using your microphone. The AI will evaluate your spoken German grammar and verb placement.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Teil 2: Informationen erfragen (Ask a Question)")
        st.info("Theme: **Einkaufen** | Card Keyword: **Brot**")

        st.write("🎙️ **Record your spoken German response:**")
        # Audio recording component
        audio = mic_recorder(
            start_prompt="Click to Start Recording 🎙️",
            stop_prompt="Click to Stop Recording 🛑",
            key='sprechen_recorder'
        )

        if audio:
            st.audio(audio['bytes'], format='audio/wav')
            st.success("Recording captured successfully!")
            
            if st.button("Evaluate Spoken Audio with AI"):
                with st.spinner("Analyzing audio and evaluating German syntax..."):
                    audio_part = {
                        "mime_type": "audio/wav",
                        "data": audio['bytes']
                    }
                    prompt = "The user is attempting Goethe A1 Sprechen Teil 2. Theme: Einkaufen, Keyword: Brot. Transcribe their spoken German and evaluate if their question format and verb placement are correct."
                    response = model.generate_content([prompt, audio_part])
                    st.markdown("### Examiner Feedback")
                    st.write(response.text)

        st.divider()
        st.write("Or type your spoken response manually:")
        user_speech_text = st.text_input("Type response:")
        if st.button("Check Typed Response"):
            if user_speech_text.strip():
                response = model.generate_content(f"Task: Goethe A1 Sprechen. Keyword: Brot. Student response: {user_speech_text}")
                st.write(response.text)

    # SCHREIBEN
    with exam_tab2:
        st.markdown('<div class="z-card-purple">', unsafe_allow_html=True)
        st.markdown('<span class="z-badge">Writing Module</span>', unsafe_allow_html=True)
        st.markdown('<div class="z-title">Goethe A1 Schreiben Teil 2</div>', unsafe_allow_html=True)
        st.write("Write short messages about everyday situations (~30 words).")
        st.markdown('</div>', unsafe_allow_html=True)

        prompt_context = st.text_area(
            "Exam Scenario & Points:",
            value="1. Grund für das Schreiben (Why you cannot come to class tomorrow)\n2. Hausaufgaben (Ask for the homework)\n3. Wiederkommen (Say when you will return)",
            height=100
        )
        user_email = st.text_area("Your Response in German:", height=120)

        if st.button("Evaluate Email", type="primary"):
            if user_email.strip():
                with st.spinner("Grading against official Goethe A1 criteria..."):
                    query = f"EXAM PROMPT:\n{prompt_context}\n\nSTUDENT RESPONSE:\n{user_email}"
                    response = model.generate_content(query)
                    st.markdown("### Examiner Breakdown")
                    st.write(response.text)

    # LESEN
    with exam_tab3:
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.markdown('<span class="z-badge">Reading Module</span>', unsafe_allow_html=True)
        st.markdown('<div class="z-title">Goethe A1 Lesen Teil 1</div>', unsafe_allow_html=True)
        st.write("Read short notices, emails, and posted signs.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.info("""
        **Email:**  
        Hallo Eva,  
        ich bin am Samstag in München. Hast du Zeit? Wir können zusammen einen Kaffee trinken.  
        Liebe Grüße,  
        Maria
        """)
        
        q1 = st.radio("1. Maria möchte sich am Samstag mit Eva treffen.", ["Richtig", "Falsch"])
        if st.button("Check Reading Answer"):
            if q1 == "Richtig":
                st.success("Richtig! Maria asked 'Hast du Zeit?' for Saturday.")
            else:
                st.error("Falsch. The statement is correct (Richtig).")

    # HÖREN
    with exam_tab4:
        st.markdown('<div class="z-card-green">', unsafe_allow_html=True)
        st.markdown('<span class="z-badge">Listening Module</span>', unsafe_allow_html=True)
        st.markdown('<div class="z-title">Goethe A1 Hören Practice</div>', unsafe_allow_html=True)
        st.write("Listen to everyday dialogues and announcements.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Audio tracks and listening tasks will load here.")

# ----------------------------------------------------
# 3. STUDY VIEW (Vocabulary Flashcards)
# ----------------------------------------------------
elif nav_choice == "🎴 Study (Vocabulary)":
    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.markdown('<span class="z-badge">Vocabulary Mastery</span>', unsafe_allow_html=True)
    st.markdown('<div class="z-title">Goethe A1 Word Trainer (650 Words)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    A1_VOCAB = [
        {"word": "Termin", "article": "der", "plural": "die Termine", "meaning": "appointment"},
        {"word": "Fahrkarte", "article": "die", "plural": "die Fahrkarten", "meaning": "ticket"},
        {"word": "Anmeldung", "article": "die", "plural": "die Anmeldungen", "meaning": "registration"},
        {"word": "Flughafen", "article": "der", "plural": "die Flughäfen", "meaning": "airport"},
        {"word": "Formular", "article": "das", "plural": "die Formulare", "meaning": "form"},
    ]

    if "current_word" not in st.session_state:
        st.session_state.current_word = random.choice(A1_VOCAB)

    item = st.session_state.current_word
    st.subheader(f"Word: **{item['word']}**  *(Meaning: {item['meaning']})*")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("der"):
            if item["article"] == "der":
                st.success(f"Correct! der {item['word']} | Plural: {item['plural']}")
            else:
                st.error(f"Answer: {item['article']} {item['word']}")
    with col2:
        if st.button("die"):
            if item["article"] == "die":
                st.success(f"Correct! die {item['word']} | Plural: {item['plural']}")
            else:
                st.error(f"Answer: {item['article']} {item['word']}")
    with col3:
        if st.button("das"):
            if item["article"] == "das":
                st.success(f"Correct! das {item['word']} | Plural: {item['plural']}")
            else:
                st.error(f"Answer: {item['article']} {item['word']}")

    if st.button("Next Word ➔"):
        st.session_state.current_word = random.choice(A1_VOCAB)
        st.rerun()
