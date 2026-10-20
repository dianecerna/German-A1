import os
import google.generativeai as genai
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Configure Streamlit Page
st.set_page_config(page_title="Goethe A1 AI Studio", page_icon="🇩🇪", layout="wide")

# Custom Zertifly CSS Theme
st.markdown("""
<style>
    .stApp {
        background-color: #f4f6f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    header {visibility: hidden;}
    .z-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        border: 1px solid #eaeef4;
    }
    .z-card-purple {
        background: #ffffff;
        border-radius: 20px;
        padding: 20px;
        border-left: 6px solid #8b5cf6;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.05);
        margin-bottom: 20px;
    }
    .z-badge {
        background-color: #f3e8ff;
        color: #7e22ce;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Fetch API Key securely
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

genai.configure(api_key=api_key)

# Strict Goethe A1 Examiner System Prompt
GOETHE_A1_SYSTEM_PROMPT = """
You are Zerti, an expert German language tutor and official Goethe-Institut A1 examiner.
Your job is to generate dynamic CEFR A1 exercises and provide strict, constructive feedback.

A1 GOETHE RULES TO ENFORCE:
1. WORD ORDER (Wortstellung):
   - Position 2 rule for conjugated main verbs.
   - Position 1 rule for Ja/Nein questions and imperatives.
   - Modal verbs in Pos 2 -> Infinitive verb at the very END.
2. SCHREIBEN (TEIL 2):
   - Candidate must address all 3 requested prompt bullet points.
   - Match formal vs informal salutations/closings.
3. EXPLANATION FORMAT:
   - Provide clear, direct explanations in English.
   - Break down German sentence structures line-by-line when analyzing errors.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=GOETHE_A1_SYSTEM_PROMPT
)

# Navigation
st.sidebar.title("🐱 Zerti Goethe A1 AI")
nav_choice = st.sidebar.radio("Navigation", [
    "🏠 AI Dashboard", 
    "✍️ AI Schreiben Generator", 
    "📖 AI Lesen Generator", 
    "🗣️ AI Sprechen & Voice Trainer",
    "💬 Ask Zerti (Grammar & Sentence AI)"
])

# ----------------------------------------------------
# 1. AI DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 AI Dashboard":
    st.markdown('<div class="z-card-purple">', unsafe_allow_html=True)
    st.markdown('<span class="z-badge">Dynamic Exam Studio</span>', unsafe_allow_html=True)
    st.title("My AI-Powered Goethe A1 Journey")
    st.write("📅 **Target Exam Date:** December 12, 2026")
    st.write("Generative AI generates fresh practice drills every session based on official Goethe-Institut parameters.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. GENERATIVE SCHREIBEN (WRITING)
# ----------------------------------------------------
elif nav_choice == "✍️ AI Schreiben Generator":
    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.subheader("Generative Schreiben Practice (Teil 2)")
    st.write("Click below to have the AI generate a brand new Goethe A1 writing prompt.")

    if "schreiben_prompt" not in st.session_state:
        st.session_state.schreiben_prompt = ""

    if st.button("🎲 Generate New Writing Prompt", type="secondary"):
        with st.spinner("Zerti is creating a new exam scenario..."):
            gen_query = "Generate a realistic Goethe A1 Schreiben Teil 2 exam prompt. Include an everyday scenario and 3 explicit bullet points (in English/German mix) that the student must write about in ~30 words."
            res = model.generate_content(gen_query)
            st.session_state.schreiben_prompt = res.text

    if st.session_state.schreiben_prompt:
        st.info(st.session_state.schreiben_prompt)

        user_email = st.text_area("Your German Response:", height=150)

        if st.button("Evaluate Response with AI", type="primary"):
            if user_email.strip():
                with st.spinner("Zerti is grading your response..."):
                    eval_query = f"EXAM PROMPT:\n{st.session_state.schreiben_prompt}\n\nSTUDENT SUBMISSION:\n{user_email}\n\nGrade this against Goethe A1 criteria (Task completion 3/3 points, V2 verb rule, salutation match)."
                    eval_res = model.generate_content(eval_query)
                    st.markdown("### Examiner Breakdown")
                    st.write(eval_res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. GENERATIVE LESEN (READING)
# ----------------------------------------------------
elif nav_choice == "📖 AI Lesen Generator":
    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.subheader("Generative Lesen Practice (Teil 1)")
    st.write("Generate short A1 emails or notices with 2 Richtig/Falsch comprehension questions.")

    if "lesen_exercise" not in st.session_state:
        st.session_state.lesen_exercise = ""

    if st.button("🎲 Generate New Reading Passage", type="secondary"):
        with st.spinner("Creating reading passage..."):
            read_gen_query = """
            Generate a short Goethe A1 level German email or notice (approx 40 words).
            Then provide 2 statements about the text marked as either (Richtig) or (Falsch), along with explanations.
            """
            res = model.generate_content(read_gen_query)
            st.session_state.lesen_exercise = res.text

    if st.session_state.lesen_exercise:
        st.write(st.session_state.lesen_exercise)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. AI SPRECHEN & VOICE TRAINER
# ----------------------------------------------------
elif nav_choice == "🗣️ AI Sprechen & Voice Trainer":
    st.markdown('<div class="z-card">', unsafe_allow_html=True)
    st.subheader("Generative Sprechen Card Drill")
    st.write("Draw a random A1 theme and keyword card, then speak your response.")

    if "card_theme" not in st.session_state:
        st.session_state.card_theme = "Einkaufen — Keyword: Brot"

    if st.button("🎲 Draw New Theme Card"):
        with st.spinner("Drawing card..."):
            card_res = model.generate_content("Generate a random Goethe A1 Sprechen Teil 2 topic card (e.g., Theme: 'Freizeit', Keyword: 'Sport').")
            st.session_state.card_theme = card_res.text

    st.success(f"🎴 **Your Card:**\n{st.session_state.card_theme}")

    st.write("🎙️ **Record your spoken question or request:**")
    audio = mic_recorder(
        start_prompt="Start Recording 🎙️",
        stop_prompt="Stop Recording 🛑",
        key='sp_ai_rec'
    )

    if audio:
        st.audio(audio['bytes'], format='audio/wav')
        if st.button("Evaluate Voice Recording"):
            with st.spinner("Zerti is analyzing your speech and grammar..."):
                audio_part = {"mime_type": "audio/wav", "data": audio['bytes']}
                prompt = f"The student drew this card: {st.session_state.card_theme}. Transcribe their spoken German audio and check if their sentence structure and verb placement (V1 or V2 rule) are correct."
                eval_res = model.generate_content([prompt, audio_part])
                st.markdown("### Audio Syntax & Grammar Evaluation")
                st.write(eval_res.text)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. ASK ZERTI (INTERACTIVE GRAMMAR TUTOR)
# ----------------------------------------------------
elif nav_choice == "💬 Ask Zerti (Grammar & Sentence AI)":
    st.markdown('<div class="z-card-purple">', unsafe_allow_html=True)
    st.subheader("🐱 Zerti — Interactive AI Tutor")
    st.write("Ask Zerti to explain grammar concepts, analyze sentence structures, or break down Goethe A1 rules.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input chat box
    if prompt := st.chat_input("Ask Zerti anything (e.g. 'Explain the V2 rule in German'):"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Zerti is thinking..."):
                response = model.generate_content(f"Answer as Zerti, a helpful German tutor: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
