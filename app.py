import os
import random
import google.generativeai as genai
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Configure Streamlit Page
st.set_page_config(page_title="Goethe A1 Prep Studio", page_icon="🇩🇪", layout="wide")

# Custom CSS matching Zertifly App Aesthetics
st.markdown("""
<style>
    /* App Background */
    .stApp {
        background-color: #f4f6f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide Streamlit Default Headers */
    header {visibility: hidden;}
    
    /* Zertifly Rounded Main Cards */
    .z-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        border: 1px solid #eaeef4;
    }
    
    .z-card-purple {
        background: #ffffff;
        border-radius: 24px;
        padding: 24px;
        border-left: 6px solid #8b5cf6;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.06);
        margin-bottom: 20px;
    }
    
    .z-card-green {
        background: #ffffff;
        border-radius: 24px;
        padding: 24px;
        border-left: 6px solid #10b981;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.06);
        margin-bottom: 20px;
    }

    /* Email / Notice Display Cards */
    .email-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 15px;
    }

    /* Styled Badges */
    .z-badge {
        background-color: #f1f5f9;
        color: #475569;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 10px;
    }
    .z-badge-purple {
        background-color: #f3e8ff;
        color: #7e22ce;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_dict_only=True)

# Fetch API key securely
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

genai.configure(api_key=api_key)

GOETHE_A1_SYSTEM_PROMPT = """
You are Zerti, an AI assistant for Goethe A1 German exam prep.
Evaluate candidate input strictly against CEFR A1 standards:
- Verb position 2 rule in main sentences.
- Verb position 1 for requests and Ja/Nein questions.
- Address all requested task points in writing.
Provide short, encouraging feedback in clear English with corrected German sentences.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=GOETHE_A1_SYSTEM_PROMPT
)

# Navigation Bar
st.sidebar.title("🐱 Zertifly Goethe A1")
nav_choice = st.sidebar.radio("Main Navigation", [
    "🏠 Dashboard", 
    "📝 Schreiben (Teil 1 & 2)", 
    "📖 Lesen (Teil 1)", 
    "🎧 Hören (Teil 1)", 
    "🗣️ Sprechen (Teil 1 & 2)",
    "🎴 Vocabulary & Dictionary",
    "🤖 Ask Zerti (AI Tutor)"
])

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Dashboard":
    st.markdown('<div class="z-card-purple">', unsafe_allow_html=True)
    st.markdown('<span class="z-badge-purple">Goethe A1 Preparation</span>', unsafe_allow_html=True)
    st.title("My Exam Journey")
    st.write("📅 **Exam Date:** December 12, 2026")
    st.progress(0.35, text="Stage 1: 3 of 4 stops completed")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.subheader("🔥 Daily Streak")
        st.title("1 Day")
        st.caption("Target: 15 minutes daily study")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.subheader("🎯 Estimated Pass Rate")
        st.title("82%")
        st.caption("Based on completed drills")
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. SCHREIBEN (TEIL 1 FORMULAR & TEIL 2 MITTEILUNG)
# ----------------------------------------------------
elif nav_choice == "📝 Schreiben (Teil 1 & 2)":
    st.markdown('<span class="z-badge-purple">Goethe A1 Schreiben</span>', unsafe_allow_html=True)
    st.title("Registrations, notices and short messages")

    teil_choice = st.radio("Select Exercise Track:", ["Teil 1: Formular", "Teil 2: Mitteilung"], horizontal=True)

    if teil_choice == "Teil 1: Formular":
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.subheader("Bodensee-Rundfahrt — Anmeldung")
        st.write("""
        **Aufgabe:**  
        Ihre Freundin, **Eva Kadavy**, macht mit ihrem Mann und ihren beiden Söhnen (8 und 11 Jahre alt) Urlaub in Seeheim.  
        Im Reisebüro bucht sie für den nächsten Sonntag eine Busfahrt um den Bodensee.  
        Frau Kadavy hat keine Kreditkarte.  

        *In dem Formular fehlen fünf Informationen. Schreiben Sie die fünf fehlenden Informationen.*
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.markdown("### BODENSEE-RUNDFAHRT — Anmeldung")
        st.text_input("Familienname, Vorname:", value="Kadavy, Eva", disabled=True)
        
        a1 = st.text_input("1. Anzahl der Personen:")
        a2 = st.text_input("2. Davon Kinder:")
        st.text_input("Urlaubsadresse:", value="Hotel Schönblick", disabled=True)
        st.text_input("Straße, Hausnummer:", value="Burgstraße 34", disabled=True)
        a3 = st.text_input("3. Zahlungsweise (Bar / Kreditkarte):")

        if st.button("Check Form Answers", type="primary"):
            score = 0
            if a1.strip() == "4": score += 1
            if a2.strip() == "2": score += 1
            if a3.strip().lower() == "bar": score += 1
            st.success(f"Score: {score} / 3 points evaluated automatically.")
            st.caption("Correct answers: 1. 4 | 2. 2 | 3. Bar (since she has no credit card)")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="z-card">', unsafe_allow_html=True)
        st.subheader("Teil 2: E-Mail schreiben")
        st.info("Write a short email (~30 words) covering all 3 required points.")
        prompt_text = st.text_area("Prompt Points:", value="1. Why you cannot come to class tomorrow\n2. Ask for homework\n3. Say when you will return")
        user_msg = st.text_area("Your German Email Response:")

        if st.button("Evaluate Email with Zerti AI", type="primary"):
            if user_msg.strip():
                with st.spinner("Analyzing email structure..."):
                    res = model.generate_content(f"Prompt: {prompt_text}\nStudent email: {user_msg}")
                    st.write(res.text)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. LESEN (FLUGHAFEN & GRILLFEST MATCHING SCREENSHOT)
# ----------------------------------------------------
elif nav_choice == "📖 Lesen (Teil 1)":
    st.markdown('<span class="z-badge">Goethe A1 Lesen</span>', unsafe_allow_html=True)
    st.title("Flughafen & Grillfest")

    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.subheader("Kurze Mitteilungen")
    st.caption("Lesen Sie die beiden Texte und die Aufgaben 1 bis 2. Sind die Aussagen Richtig oder Falsch?")

    # Email Container
    st.markdown("""
    <div class="email-container">
    <b>BETREFF: Hallo Tom,</b><br><br>
    vielen Dank für deine Nachricht! Ich hole dich am Sonntag vom Flughafen ab. 
    Dein Flugzeug landet um 14.20 Uhr. Ich bin schon um 14 Uhr da und warte am Ausgang.<br>
    Ruf mich bitte an, wenn dein Flug später kommt. Meine Nummer hast du ja.<br>
    Bis Sonntag!<br>
    Lena
    </div>
    """, unsafe_allow_html=True)

    q1 = st.radio("1. Lena wartet am Flughafen auf Tom.", ["Richtig", "Falsch"])
    
    st.divider()

    # Letter Container
    st.markdown("""
    <div class="email-container">
    <b>Liebe Sofia,</b><br><br>
    nächsten Samstag mache ich ein Grillfest bei mir im Garten. Wir beginnen um 17 Uhr. 
    Kommst du auch? Es kommen noch andere Freunde, die du kennst. Bitte bring etwas zu trinken mit. 
    Fleisch und Salate habe ich schon genug.<br><br>
    Liebe Grüße
    </div>
    """, unsafe_allow_html=True)

    q2 = st.radio("2. Sofia soll Fleisch und Salate mitbringen.", ["Richtig", "Falsch"])

    if st.button("Submit Lesen Answers", type="primary"):
        c1 = (q1 == "Richtig")
        c2 = (q2 == "Falsch")
        st.write(f"1. Lena wartet am Flughafen: {'✅ Correct' if c1 else '❌ Incorrect (It is Richtig)'}")
        st.write(f"2. Sofia soll Fleisch mitbringen: {'✅ Correct' if c2 else '❌ Incorrect (It is Falsch - she should bring drinks)'}")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. HÖREN (JACKE, KINO & APOTHEKE MATCHING SCREENSHOT)
# ----------------------------------------------------
elif nav_choice == "🎧 Hören (Teil 1)":
    st.markdown('<span class="z-badge-purple">Goethe A1 Hören</span>', unsafe_allow_html=True)
    st.title("Jacke, Kino & Apotheke")

    st.markdown('<div class="z-card-green">', unsafe_allow_html=True)
    st.subheader("Audio Player")
    st.caption("Was ist richtig? Kreuzen Sie an: a, b oder c. Sie hören jeden Text zweimal.")
    
    # Audio player placeholder
    st.audio("https://www.w3schools.com/html/horse.ogg", format="audio/ogg")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.subheader("Aufgaben")

    st.markdown("**1. Was kostet die Jacke?**")
    ans1 = st.radio("Question 1", ["A) 25 Euro.", "B) 45 Euro.", "C) 52 Euro."], label_visibility="collapsed")

    st.markdown("**2. Wann beginnt der Film?**")
    ans2 = st.radio("Question 2", ["A) Um 20.15 Uhr.", "B) Um 19.30 Uhr.", "C) Um 19.45 Uhr."], label_visibility="collapsed")

    if st.button("Check Hören Answers", type="primary"):
        st.success("Answers submitted for evaluation!")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. SPRECHEN (WITH AUDIO VOICE RECORDING)
# ----------------------------------------------------
elif nav_choice == "🗣️ Sprechen (Teil 1 & 2)":
    st.markdown('<span class="z-badge-purple">Goethe A1 Sprechen</span>', unsafe_allow_html=True)
    st.title("Oral Exam Practice")

    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.subheader("Teil 1 — Sich vorstellen")
    st.write("Introduce yourself using A1 details: *Name, Alter, Land, Wohnort, Sprachen, Beruf, Hobby*.")
    
    st.write("🎙️ **Record your spoken self-introduction:**")
    audio = mic_recorder(
        start_prompt="Start Recording 🎙️",
        stop_prompt="Stop Recording 🛑",
        key='sp_rec'
    )

    if audio:
        st.audio(audio['bytes'], format='audio/wav')
        if st.button("Evaluate Spoken Self-Introduction"):
            with st.spinner("Analyzing audio..."):
                audio_part = {"mime_type": "audio/wav", "data": audio['bytes']}
                p = "The user is completing Goethe A1 Sprechen Teil 1 (Self introduction). Transcribe their German speech and verify grammar and pronunciation."
                res = model.generate_content([p, audio_part])
                st.write(res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. VOCABULARY & DICTIONARY
# ----------------------------------------------------
elif nav_choice == "🎴 Vocabulary & Dictionary":
    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.title("Vocabulary Practice (Level A1)")
    st.caption("Core Goethe A1 words sorted by category.")

    words = [
        {"w": "Flughafen", "a": "der", "p": "die Flughäfen", "m": "airport"},
        {"w": "Fahrkarte", "a": "die", "p": "die Fahrkarten", "m": "ticket"},
        {"w": "Formular", "a": "das", "p": "die Formulare", "m": "form"},
        {"w": "Termin", "a": "der", "p": "die Termine", "m": "appointment"},
    ]

    for item in words:
        st.write(f"🔹 **{item['a']} {item['w']}** | Plural: *{item['p']}* — Meaning: *{item['m']}*")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. ZERTI CHATBOT (MATCHING PROFILE CHAT OVERLAY)
# ----------------------------------------------------
elif nav_choice == "🤖 Ask Zerti (AI Tutor)":
    st.markdown('<div class="z-card-purple">', unsafe_allow_html=True)
    st.subheader("🐱 Zerti — Zertifly Assistant")
    st.write("Hi! I'm Zerti, your Goethe A1 study assistant. Ask me any German grammar question or practice exercise logic!")
    st.markdown('</div>', unsafe_allow_html=True)

    user_q = st.text_input("Ask Zerti a question (e.g., 'Where does the verb go with modal verbs?'):")
    if st.button("Ask Zerti"):
        if user_q.strip():
            res = model.generate_content(f"Answer as Zerti, a helpful German tutor: {user_q}")
            st.write(res.text)
