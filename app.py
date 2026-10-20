import os
import random
import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="Goethe A1 Prep Studio", page_icon="🇩🇪", layout="wide")

# Fetch API key securely from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

genai.configure(api_key=api_key)

# System prompt tuned strictly for official Goethe A1 criteria
GOETHE_A1_SYSTEM_PROMPT = """
You are a strict, official Goethe-Institut A1 examiner evaluating a candidate preparing for the Goethe-Zertifikat A1: Start Deutsch 1 exam.

EVALUATION PARAMETERS:
1. WORD ORDER (Wortstellung):
   - Aussagesätze: Conjugated verb in Position 2.
   - W-Fragen: Question word in Pos 1, conjugated verb in Pos 2.
   - Ja/Nein-Fragen & Imperative: Conjugated verb in Position 1.
   - Modalverben (können, müssen, wollen): Modal verb in Pos 2 -> Infinitive strictly at the END.
2. SCHREIBEN (TEIL 2) RUBRIC:
   - Check if all 3 content points are completely addressed.
   - Match informal vs. formal greetings/closings:
     * Informal: "Liebe/Lieber [Name]," -> "Viele Grüße" / "Liebe Grüße"
     * Formal: "Sehr geehrte Damen und Herren," / "Sehr geehrte Frau/Herr [Name]," -> "Mit freundlichen Grüßen"
3. SCOPE RESTRICTIONS:
   - Do not suggest B1+ complex sentences (no subordinate clauses with 'weil', 'dass', 'obwohl').
   - Keep suggested vocabulary within the Goethe A1 650-word scope.
   - Feedback format: 
     1. Task fulfilment score (Did they address all 3 points?)
     2. A1 Grammar & Word Order check
     3. Corrected German version line-by-line
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=GOETHE_A1_SYSTEM_PROMPT
)

st.title("🇩🇪 Personal Goethe A1 Exam Prep Studio")
st.caption("Target Exam Date: December 12 | Focus: Goethe-Zertifikat A1 (Start Deutsch 1)")

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "🎴 Daily Vocab & Article Drill", 
    "📝 Schreiben Grader (Teil 2)", 
    "🗣️ Sprechen Trainer (Teil 1, 2 & 3)"
])

# ----------------------------------------------------
# TAB 1: DAILY VOCABULARY & GENDER DRILL
# ----------------------------------------------------
with tab1:
    st.header("Daily Goethe A1 Gender & Plural Drill")
    st.info("Train der/die/das recall for core Goethe A1 vocabulary.")
    
    A1_VOCAB = [
        {"word": "Termin", "article": "der", "plural": "die Termine", "meaning": "appointment", "example": "Ich habe einen Termin beim Arzt."},
        {"word": "Fahrkarte", "article": "die", "plural": "die Fahrkarten", "meaning": "ticket", "example": "Wo kann ich eine Fahrkarte kaufen?"},
        {"word": "Anmeldung", "article": "die", "plural": "die Anmeldungen", "meaning": "registration", "example": "Bitte füllen Sie die Anmeldung aus."},
        {"word": "Flughafen", "article": "der", "plural": "die Flughäfen", "meaning": "airport", "example": "Der Bus fährt zum Flughafen."},
        {"word": "Formular", "article": "das", "plural": "die Formulare", "meaning": "form", "example": "Schreiben Sie den Namen in das Formular."},
        {"word": "Schlüssel", "article": "der", "plural": "die Schlüssel", "meaning": "key", "example": "Hier ist der Schlüssel."},
        {"word": "Rechnung", "article": "die", "plural": "die Rechnungen", "meaning": "bill", "example": "Die Rechnung, bitte."},
    ]

    if "current_word" not in st.session_state:
        st.session_state.current_word = random.choice(A1_VOCAB)

    item = st.session_state.current_word

    st.subheader(f"Word: **{item['word']}**  *(Meaning: {item['meaning']})*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("der"):
            if item["article"] == "der":
                st.success(f"Correct! **der {item['word']}** | Plural: {item['plural']}")
                st.caption(f"Example: {item['example']}")
            else:
                st.error(f"Incorrect. Answer: **{item['article']} {item['word']}**")
    
    with col2:
        if st.button("die"):
            if item["article"] == "die":
                st.success(f"Correct! **die {item['word']}** | Plural: {item['plural']}")
                st.caption(f"Example: {item['example']}")
            else:
                st.error(f"Incorrect. Answer: **{item['article']} {item['word']}**")

    with col3:
        if st.button("das"):
            if item["article"] == "das":
                st.success(f"Correct! **das {item['word']}** | Plural: {item['plural']}")
                st.caption(f"Example: {item['example']}")
            else:
                st.error(f"Incorrect. Answer: **{item['article']} {item['word']}**")

    if st.button("Next Word ➔"):
        st.session_state.current_word = random.choice(A1_VOCAB)
        st.rerun()

# ----------------------------------------------------
# TAB 2: WRITING EVALUATOR
# ----------------------------------------------------
with tab2:
    st.header("Schreiben Teil 2 Evaluator (~30 words)")
    st.info("Write a short email/letter covering all 3 bullet points below.")

    prompt_context = st.text_area(
        "Exam Scenario & Prompt Points:",
        value="1. Grund für das Schreiben (Why you cannot come to class tomorrow)\n2. Hausaufgaben (Ask for the homework)\n3. Wiederkommen (Say when you will return)",
        height=100
    )

    user_email = st.text_area("Your Response in German:", height=150)

    if st.button("Evaluate Email", type="primary"):
        if not user_email.strip():
            st.warning("Please type your German text first.")
        else:
            with st.spinner("Grading against official Goethe A1 criteria..."):
                query = f"EXAM PROMPT:\n{prompt_context}\n\nSTUDENT RESPONSE:\n{user_email}"
                response = model.generate_content(query)
                st.markdown("### Examiner Feedback")
                st.write(response.text)

# ----------------------------------------------------
# TAB 3: SPEAKING TRAINER
# ----------------------------------------------------
with tab3:
    st.header("Sprechen Card Drill (Teil 2 & Teil 3)")
    st.markdown("**Theme:** Einkaufen | **Keyword:** *Brot* | **Goal:** Ask a question or make a request.")

    user_question = st.text_input("Type your question or request in German:")

    if st.button("Check Verb Position & Syntax"):
        if not user_question.strip():
            st.warning("Please enter a German sentence.")
        else:
            with st.spinner("Checking V1/V2 verb placement..."):
                query = f"Task: Goethe A1 Sprechen. Theme: Einkaufen. Keyword: Brot. Candidate Input: {user_question}"
                response = model.generate_content(query)
                st.markdown("### Syntax & Position Analysis")
                st.write(response.text)
