import os
import json
import streamlit as st
from google import genai
from google.genai import types
from streamlit_mic_recorder import mic_recorder

st.set_page_config(
    page_title="Goethe A1 Prep Studio", 
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
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 Missing Gemini API Key in Streamlit Secrets!")
    st.stop()

client = genai.Client(api_key=api_key.strip())
MODEL_NAME = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
You are Zerti, an expert German language tutor and official Goethe-Institut A1 examiner evaluating a candidate for Goethe-Zertifikat A1 (Start Deutsch 1).
Always strictly follow Goethe A1 rules, V2 verb placement, and formal/informal writing rubrics.
"""

# Categorized Word Bank (600+ Words Structure across categories)
GOETHE_WORD_BANK = {
    "🍎 Essen & Trinken": ["einkaufen", "das Brot", "der Apfel", "die Milch", "das Wasser", "der Kaffee", "der Fleisch", "die Butter", "bestellen", "schmecken", "das Restaurant", "der Flasche", "das Frühstück", "kochen", "trinken"],
    "🚗 Reisen & Verkehr": ["die Fahrkarte", "der Bahnhof", "der Flughafen", "abholen", "ankommen", "umsteigen", "der Bus", "der Zug", "das Flugzeug", "die Haltestelle", "buchen", "die Reise", "der Koffer", "spät", "pünktlich"],
    "🏠 Wohnen & Alltag": ["die Wohnung", "das Zimmer", "mieten", "der Schlüssel", "das Bad", "die Küche", "der Tisch", "der Stuhl", "das Bett", "schlafen", "wohnen", "die Adresse", "die Straße", "die Stadt", "das Haus"],
    "💼 Arbeit & Beruf": ["der Termin", "die Sprechstunde", "arbeiten", "der Arzt", "die Firma", "der Chef", "der Kollege", "die Pause", "das Büro", "der Beruf", "telefonieren", "schreiben", "die E-Mail", "der Kunde", "das Geld"],
    "🛒 Einkaufen & Geld": ["bezahlen", "kostet", "billig", "teuer", "das Geschäft", "die Kasse", "kaufen", "das Kleid", "die Hose", "die Größe", "die Scheckkarte", "Euro", "der Rabatt", "die Tasche", "suchen"],
    "👨‍👩‍👧 Familie & Freizeit": ["die Familie", "die Kinder", "der Vater", "die Mutter", "der Freund", "die Hobbys", "sport", "lesen", "tanzen", "schwimmen", "musik", "treffen", "der Urlaub", "die Sonne", "das Wochenende"]
}

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
    st.title("Goethe-Zertifikat A1 Prep Studio")
    st.write("📅 **Exam Date:** December 12, 2026")
    st.write("Practice interactive Lesen, Hören, Schreiben, Sprechen modules with live scoring.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Vocabulary Engine")
    
    cat_col, word_col = st.columns(2)
    with cat_col:
        selected_cat = st.selectbox("Select Topic Category:", list(GOETHE_WORD_BANK.keys()))
    with word_col:
        selected_word = st.selectbox("Select Keyword:", GOETHE_WORD_BANK[selected_cat])
    
    custom_word = st.text_input("Or type any German word directly:")
    active_word = custom_word.strip() if custom_word.strip() else selected_word

    if st.button(f"🔍 Generate Interactive Flashcard for '{active_word}'", type="primary"):
        with st.spinner("Zerti is compiling your study flashcard..."):
            prompt = f"Generate a comprehensive A1 study card for '{active_word}' including Word, Article/Gender, Plural, English Meaning, Perfekt form, full 6-pronoun conjugations, 6 sample sentences, and common A1 phrases."
            try:
                res = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. INTERACTIVE GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Goethe A1 Lesen — Interactive Practice")

    if st.button("🎲 Generate Interactive Lesen Exercise", type="primary"):
        with st.spinner("Generating exercise with interactive radio options..."):
            prompt = """
            Generate 1 Goethe A1 Lesen Teil 1 exercise.
            Return strictly a JSON object with this key structure (no markdown codeblock wrapping):
            {
                "text": "The German email text...",
                "questions": [
                    {
                        "id": "q1",
                        "statement": "Statement 1 in German",
                        "options": ["richtig", "falsch"],
                        "answer": "richtig",
                        "explanation": "Why this is correct"
                    },
                    {
                        "id": "q2",
                        "statement": "Statement 2 in German",
                        "options": ["richtig", "falsch"],
                        "answer": "falsch",
                        "explanation": "Why this is correct"
                    }
                ]
            }
            """
            try:
                res = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                st.session_state.current_lesen = json.loads(res.text)
            except Exception as e:
                st.error(f"Error parsing exercise: {str(e)}")

    if "current_lesen" in st.session_state:
        ex = st.session_state.current_lesen
        st.markdown("### 📧 Text")
        st.info(ex["text"])

        st.markdown("### 📝 Aufgaben")
        user_answers = {}
        for idx, q in enumerate(ex["questions"], start=1):
            st.markdown(f"**{idx}. {q['statement']}**")
            user_answers[q["id"]] = st.radio(
                f"Select answer for Question {idx}:", 
                q["options"], 
                key=f"rad_{q['id']}"
            )

        if st.button("Submit Answers & Grade"):
            score = 0
            for q in ex["questions"]:
                user_choice = user_answers.get(q["id"])
                if user_choice == q["answer"]:
                    score += 1
                    st.success(f"✅ Question '{q['statement']}': Correct! ({q['explanation']})")
                else:
                    st.error(f"❌ Question '{q['statement']}': Incorrect. Correct answer: {q['answer']}. ({q['explanation']})")
            st.metric("Your Score", f"{score} / {len(ex['questions'])}")
            
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. OTHER MODULES
# ----------------------------------------------------
elif nav_choice == "💬 Ask Zerti (AI Tutor)":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("💬 Ask Zerti")
    if prompt := st.chat_input("Ask a question:"):
        res = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        st.write(res.text)
    st.markdown('</div>', unsafe_allow_html=True)
