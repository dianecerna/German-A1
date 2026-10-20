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

# Custom Styling
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
    .main-card { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .accent-card { background: #ffffff; border-radius: 16px; padding: 24px; border-left: 6px solid #2563eb; box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06); margin-bottom: 20px; border: 1px solid #e2e8f0; }
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
You are Gem, an expert German language tutor teaching a non-native German learn A1 German language, and you are also the official Goethe-Institut A1 examiner evaluating a candidate for Goethe-Zertifikat A1 (Start Deutsch 1).

# --- AFTER (Insert Step 2 here) ---
client = genai.Client(api_key=api_key.strip())
MODEL_NAME = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
You are Gem, an expert German language tutor...
"""

# ==========================================
# STEP 2: CACHED GEMINI FUNCTION
# ==========================================
@st.cache_data(show_spinner=False)
def generate_cached_content(prompt_text, is_json=False):
    config_args = {"system_instruction": SYSTEM_INSTRUCTION}
    if is_json:
        config_args["response_mime_type"] = "application/json"
    
    res = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_text,
        config=types.GenerateContentConfig(**config_args)
    )
    return res.text
    
OFFICIAL GOETHE A1 EXAM FORMAT RULES:
- LESEN TEIL 1: Short personal emails/letters with Richtig/Falsch questions.
- LESEN TEIL 2: Scenarios matching user intent to Website A or Website B.
- LESEN TEIL 3: Public signs/notices with Richtig/Falsch statements.

- HÖREN TEIL 1: Conversations played TWICE with Multiple Choice (a, b, c) items.
- HÖREN TEIL 2: Public announcements played ONCE with Richtig/Falsch items.
- HÖREN TEIL 3: Telephone messages/voicemails played TWICE with Multiple Choice (a, b, c) items.

- SCHREIBEN TEIL 1: Formular ausfüllen (5 gaps of missing personal/travel info).
- SCHREIBEN TEIL 2: Short Email (~30 words) with 3 explicit bullet points.

- SPRECHEN TEIL 1: Sich vorstellen (7 standard points) & Buchstabieren/Zahlen.
- SPRECHEN TEIL 2: W-Fragen mit Themenkarte (Verb in Position 2 rule).
- SPRECHEN TEIL 3: Bitten/Aufforderungen mit Bildkarte (Verb in Position 1 or 'Können Sie bitte...' rule).

When returning JSON for structured exercises, output strict JSON with no additional markdown wrapping or conversational text.
"""

# Categorized Word Bank
GOETHE_WORD_BANK = {
    "🍎 Essen & Trinken": ["einkaufen", "das Brot", "der Apfel", "die Milch", "das Wasser", "der Kaffee", "das Fleisch", "die Butter", "bestellen", "schmecken", "das Restaurant", "die Flasche", "das Frühstück", "kochen", "trinken"],
    "🚗 Reisen & Verkehr": ["die Fahrkarte", "der Bahnhof", "der Flughafen", "abholen", "ankommen", "umsteigen", "der Bus", "der Zug", "das Flugzeug", "die Haltestelle", "buchen", "die Reise", "der Koffer", "spät", "pünktlich"],
    "🏠 Wohnen & Alltag": ["die Wohnung", "das Zimmer", "mieten", "der Schlüssel", "das Bad", "die Küche", "der Tisch", "der Stuhl", "das Bett", "schlafen", "wohnen", "die Adresse", "die Straße", "die Stadt", "das Haus"],
    "💼 Arbeit & Beruf": ["der Termin", "die Sprechstunde", "arbeiten", "der Arzt", "die Firma", "der Chef", "der Kollege", "die Pause", "das Büro", "der Beruf", "telefonieren", "schreiben", "die E-Mail", "der Kunde", "das Geld"],
    "🛒 Einkaufen & Geld": ["bezahlen", "kostet", "billig", "teuer", "das Geschäft", "die Kasse", "kaufen", "das Kleid", "die Hose", "die Größe", "die Scheckkarte", "Euro", "der Rabatt", "die Tasche", "suchen"],
    "👨‍👩‍👧 Familie & Freizeit": ["die Familie", "die Kinder", "der Vater", "die Mutter", "der Freund", "die Hobbys", "sport", "lesen", "tanzen", "schwimmen", "musik", "treffen", "der Urlaub", "die Sonne", "das Wochenende"]
}

# Sidebar Navigation
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
    "💬 Ask Gem (AI Tutor)"
])

def generate_german_audio(text):
    tts = gTTS(text=text, lang='de')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.title("Goethe-Zertifikat A1 Prep Studio")
    st.write("📅 **Exam Date:** December 12, 2026")
    st.write("Full exam replication with interactive radio controls, real playable audio clips, and voice evaluations by Gem.")
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

    if st.button(f"🔍 Generate Flashcard for '{active_word}'", type="primary"):
        with st.spinner("Gem is compiling your study flashcard..."):
            prompt = f"Generate a comprehensive A1 study card for '{active_word}' including Word, Article/Gender, Plural, English Meaning, Perfekt form, full 6-pronoun conjugations, 6 sample sentences, and common A1 phrases."
            try:
                res = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                )
                st.markdown(res.text)
                st.audio(generate_german_audio(active_word), format="audio/mp3")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. GOETHE A1 LESEN (TEIL 1, 2, 3)
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Goethe A1 Lesen Practice (25 Mins, 15 Points)")

    l_tab1, l_tab2, l_tab3 = st.tabs([
        "Teil 1: E-Mails & Briefe", 
        "Teil 2: Webseiten & Anzeigen", 
        "Teil 3: Schilder & Aushänge"
    ])

    # --- LESEN TEIL 1 ---
    with l_tab1:
        st.markdown("**Teil 1:** Read a short personal message and answer Richtig/Falsch questions.")
        if st.button("🎲 Generate Lesen Teil 1 Exercise", type="primary"):
            with st.spinner("Gem is generating Teil 1 exercise..."):
                prompt = """
                Generate 1 Goethe A1 Lesen Teil 1 exercise (short personal email ~35 words).
                Return strict JSON format:
                {
                    "text": "Email text in German...",
                    "questions": [
                        {"id": "lt1_1", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Why correct"},
                        {"id": "lt1_2", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Why correct"}
                    ]
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.lesen_t1 = json.loads(res.text)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "lesen_t1" in st.session_state:
            data = st.session_state.lesen_t1
            st.info(data["text"])
            ans = {}
            for idx, q in enumerate(data["questions"], start=1):
                st.markdown(f"**{idx}. {q['statement']}**")
                ans[q["id"]] = st.radio(f"Select Q{idx}:", q["options"], key=f"rad_{q['id']}")
            if st.button("Submit Teil 1 Answers"):
                score = sum(1 for q in data["questions"] if ans.get(q["id"]) == q["answer"])
                st.success(f"Teil 1 Score: {score} / {len(data['questions'])}")

    # --- LESEN TEIL 2 ---
    with l_tab2:
        st.markdown("**Teil 2:** Read a user scenario and decide whether Website A or Website B fits best.")
        if st.button("🎲 Generate Lesen Teil 2 Exercise", type="primary"):
            with st.spinner("Gem is generating Teil 2 exercise..."):
                prompt = """
                Generate 1 Goethe A1 Lesen Teil 2 exercise (1 situation + Website A and Website B).
                Return strict JSON format:
                {
                    "situation": "Situation in German...",
                    "site_a": "Website A description...",
                    "site_b": "Website B description...",
                    "question": "Welche Website ist richtig?",
                    "options": ["Website A", "Website B"],
                    "answer": "Website A",
                    "explanation": "Why website A fits"
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.lesen_t2 = json.loads(res.text)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "lesen_t2" in st.session_state:
            d = st.session_state.lesen_t2
            st.warning(f"**Situation:** {d['situation']}")
            col1, col2 = st.columns(2)
            with col1: st.info(f"**Website A:**\n{d['site_a']}")
            with col2: st.info(f"**Website B:**\n{d['site_b']}")
            u_ans = st.radio(d["question"], d["options"], key="rad_lt2")
            if st.button("Submit Teil 2 Answer"):
                if u_ans == d["answer"]:
                    st.success(f"✅ Correct! ({d['explanation']})")
                else:
                    st.error(f"❌ Incorrect. Correct answer: {d['answer']}. ({d['explanation']})")

    # --- LESEN TEIL 3 ---
    with l_tab3:
        st.markdown("**Teil 3:** Read a public sign or notice and determine if statements are Richtig or Falsch.")
        if st.button("🎲 Generate Lesen Teil 3 Exercise", type="primary"):
            with st.spinner("Gem is generating Teil 3 sign..."):
                prompt = """
                Generate 1 Goethe A1 Lesen Teil 3 exercise (public sign/notice).
                Return strict JSON format:
                {
                    "sign_text": "Public sign text in German...",
                    "questions": [
                        {"id": "lt3_1", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Why correct"}
                    ]
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.lesen_t3 = json.loads(res.text)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "lesen_t3" in st.session_state:
            d3 = st.session_state.lesen_t3
            st.error(f"🛑 **Aushang/Schild:**\n\n{d3['sign_text']}")
            ans3 = {}
            for q in d3["questions"]:
                st.markdown(f"**{q['statement']}**")
                ans3[q["id"]] = st.radio("Select choice:", q["options"], key=f"rad_{q['id']}")
            if st.button("Submit Teil 3 Answers"):
                score3 = sum(1 for q in d3["questions"] if ans3.get(q["id"]) == q["answer"])
                st.success(f"Teil 3 Score: {score3} / {len(d3['questions'])}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 HÖREN (TEIL 1, 2, 3 WITH AUDIO)
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🎧 Goethe A1 Hören Practice (20 Mins, 15 Points)")

    h_tab1, h_tab2, h_tab3 = st.tabs([
        "Teil 1: Alltagsgespräche (2x Audio)", 
        "Teil 2: Durchsagen (1x Audio)", 
        "Teil 3: Telefonansagen (2x Audio)"
    ])

    # --- HÖREN TEIL 1 ---
    with h_tab1:
        st.info("ℹ️ In the official exam, Teil 1 audio conversations are played **twice**.")
        if st.button("🎲 Generate Hören Teil 1 Clip & Questions", type="primary"):
            with st.spinner("Gem is synthesizing audio and compiling questions..."):
                prompt = """
                Generate 1 Goethe A1 Hören Teil 1 exercise (short dialogue played twice).
                Return strict JSON format:
                {
                    "audio_script": "Short German conversation transcript...",
                    "questions": [
                        {"id": "ht1_1", "statement": "Question 1 in German", "options": ["a) Option 1", "b) Option 2", "c) Option 3"], "answer": "a) Option 1", "explanation": "Why correct"}
                    ]
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.hoeren_t1 = json.loads(res.text)
                    st.session_state.hoeren_t1_audio = generate_german_audio(st.session_state.hoeren_t1["audio_script"]).getvalue()
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t1" in st.session_state:
            d = st.session_state.hoeren_t1
            st.markdown("### 🔊 Listen to Conversation")
            st.audio(st.session_state.hoeren_t1_audio, format="audio/mp3")
            with st.expander("👁️ View Script Transcript"): st.write(d["audio_script"])
            ans = {}
            for q in d["questions"]:
                st.markdown(f"**{q['statement']}**")
                ans[q["id"]] = st.radio("Select answer:", q["options"], key=f"rad_{q['id']}")
            if st.button("Submit Hören Teil 1"):
                score = sum(1 for q in d["questions"] if ans.get(q["id"]) == q["answer"])
                st.success(f"Teil 1 Score: {score} / {len(d['questions'])}")

    # --- HÖREN TEIL 2 ---
    with h_tab2:
        st.warning("⚠️ In the official exam, Teil 2 announcements are played **only ONCE**.")
        if st.button("🎲 Generate Hören Teil 2 Clip & Questions", type="primary"):
            with st.spinner("Gem is synthesizing public announcement audio..."):
                prompt = """
                Generate 1 Goethe A1 Hören Teil 2 exercise (train station or airport announcement).
                Return strict JSON format:
                {
                    "audio_script": "German public announcement transcript...",
                    "questions": [
                        {"id": "ht2_1", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Why correct"}
                    ]
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.hoeren_t2 = json.loads(res.text)
                    st.session_state.hoeren_t2_audio = generate_german_audio(st.session_state.hoeren_t2["audio_script"]).getvalue()
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t2" in st.session_state:
            d = st.session_state.hoeren_t2
            st.markdown("### 🔊 Listen to Public Announcement")
            st.audio(st.session_state.hoeren_t2_audio, format="audio/mp3")
            with st.expander("👁️ View Announcement Transcript"): st.write(d["audio_script"])
            ans = {}
            for q in d["questions"]:
                st.markdown(f"**{q['statement']}**")
                ans[q["id"]] = st.radio("Select choice:", q["options"], key=f"rad_{q['id']}")
            if st.button("Submit Hören Teil 2"):
                score = sum(1 for q in d["questions"] if ans.get(q["id"]) == q["answer"])
                st.success(f"Teil 2 Score: {score} / {len(d['questions'])}")

    # --- HÖREN TEIL 3 ---
    with h_tab3:
        st.info("ℹ️ In the official exam, Teil 3 telephone voicemail messages are played **twice**.")
        if st.button("🎲 Generate Hören Teil 3 Clip & Questions", type="primary"):
            with st.spinner("Gem is synthesizing voicemail message..."):
                prompt = """
                Generate 1 Goethe A1 Hören Teil 3 exercise (voicemail/answering machine message).
                Return strict JSON format:
                {
                    "audio_script": "German voicemail message transcript...",
                    "questions": [
                        {"id": "ht3_1", "statement": "Question 1 in German", "options": ["a) Option 1", "b) Option 2", "c) Option 3"], "answer": "b) Option 2", "explanation": "Why correct"}
                    ]
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.hoeren_t3 = json.loads(res.text)
                    st.session_state.hoeren_t3_audio = generate_german_audio(st.session_state.hoeren_t3["audio_script"]).getvalue()
                except Exception as e: st.error(f"Error: {str(e)}")

        if "hoeren_t3" in st.session_state:
            d = st.session_state.hoeren_t3
            st.markdown("### 🔊 Listen to Voicemail")
            st.audio(st.session_state.hoeren_t3_audio, format="audio/mp3")
            with st.expander("👁️ View Voicemail Transcript"): st.write(d["audio_script"])
            ans = {}
            for q in d["questions"]:
                st.markdown(f"**{q['statement']}**")
                ans[q["id"]] = st.radio("Select choice:", q["options"], key=f"rad_{q['id']}")
            if st.button("Submit Hören Teil 3"):
                score = sum(1 for q in d["questions"] if ans.get(q["id"]) == q["answer"])
                st.success(f"Teil 3 Score: {score} / {len(d['questions'])}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 SCHREIBEN (TEIL 1 & 2)
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✍️ Goethe A1 Schreiben Practice (20 Mins, 15 Points)")

    s_tab1, s_tab2 = st.tabs([
        "Teil 1: Formular ausfüllen (5 Lücken)", 
        "Teil 2: E-Mail / Brief (~30 Wörter)"
    ])

    with s_tab1:
        st.markdown("**Teil 1:** Read a travel or booking scenario and fill in the 5 missing fields on the form.")
        if st.button("🎲 Generate Schreiben Teil 1 Form Scenario", type="primary"):
            with st.spinner("Gem is creating form exercise..."):
                prompt = """
                Generate 1 Goethe A1 Schreiben Teil 1 form exercise.
                Return strict JSON format:
                {
                    "scenario": "Background text describing a customer/tourist...",
                    "form_title": "Anmeldung / Hotel Registration Form",
                    "fields": [
                        {"id": "f1", "label": "1. Reiseziel (Destination)", "answer": "Berlin"},
                        {"id": "f2", "label": "2. Anzahl der Personen (Number of people)", "answer": "3"},
                        {"id": "f3", "label": "3. Anreisetag (Arrival date)", "answer": "Freitag"},
                        {"id": "f4", "label": "4. Zahlungsart (Payment method)", "answer": "Kreditkarte"},
                        {"id": "f5", "label": "5. Telefonnummer (Phone)", "answer": "0176123456"}
                    ]
                }
                """
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.schreiben_t1 = json.loads(res.text)
                except Exception as e: st.error(f"Error: {str(e)}")

        if "schreiben_t1" in st.session_state:
            d = st.session_state.schreiben_t1
            st.info(f"**Scenario:** {d['scenario']}")
            st.markdown(f"### 📋 {d['form_title']}")
            user_inputs = {}
            for field in d["fields"]:
                user_inputs[field["id"]] = st.text_input(field["label"], key=f"inp_{field['id']}")
            
            if st.button("Check Form Gaps"):
                score = 0
                for field in d["fields"]:
                    val = user_inputs[field["id"]].strip().lower()
                    ans = field["answer"].strip().lower()
                    if val == ans:
                        score += 1
                        st.success(f"✅ {field['label']}: Correct!")
                    else:
                        st.error(f"❌ {field['label']}: Expected '{field['answer']}', you wrote '{user_inputs[field['id']]}'.")
                st.metric("Form Score", f"{score} / 5")

    with s_tab2:
        st.markdown("**Teil 2:** Write a short email (~30 words) covering all 3 required points.")
        if st.button("🎲 Generate Schreiben Teil 2 Prompt", type="primary"):
            with st.spinner("Gem is creating writing prompt..."):
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME,
                        contents="Generate an official Goethe A1 Schreiben Teil 2 prompt with 3 explicit bullet points.",
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.schreiben_t2_prompt = res.text
                except Exception as e: st.error(f"Error: {str(e)}")

        if "schreiben_t2_prompt" in st.session_state:
            st.info(st.session_state.schreiben_t2_prompt)
            u_email = st.text_area("Write your German email response (~30 words):", height=140)
            if st.button("Evaluate Email with Gem"):
                if u_email.strip():
                    with st.spinner("Gem is evaluating your email..."):
                        try:
                            eval_res = client.models.generate_content(
                                model=MODEL_NAME,
                                contents=f"PROMPT:\n{st.session_state.schreiben_t2_prompt}\n\nSUBMISSION:\n{u_email}\n\nGrade task fulfillment (3/3 points), V2 verb order, and matching salutations/closings.",
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.markdown("### Official Examiner Breakdown")
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SPRECHEN (TEIL 1, 2, 3 WITH MIC INPUT)
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🗣️ Goethe A1 Sprechen Practice (15 Mins, 15 Points)")

    sp_tab1, sp_tab2, sp_tab3 = st.tabs([
        "Teil 1: Sich vorstellen & Buchstabieren", 
        "Teil 2: W-Fragen (Themenkarten)", 
        "Teil 3: Bitten & Reaktionen (Bildkarten)"
    ])

    # --- SPRECHEN TEIL 1 ---
    with sp_tab1:
        st.markdown("""
        **Teil 1:** Practice introducing yourself using the 7 standard Goethe criteria:
        *1. Name | 2. Alter | 3. Land | 4. Wohnort | 5. Sprachen | 6. Beruf | 7. Hobby*
        """)
        rec_t1 = mic_recorder(start_prompt="Record Self-Introduction 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t1")
        if rec_t1:
            st.audio(rec_t1['bytes'], format='audio/wav')
            if st.button("Evaluate Introduction"):
                with st.spinner("Gem is analyzing your pronunciation and self-introduction..."):
                    try:
                        audio_part = types.Part.from_bytes(data=rec_t1['bytes'], mime_type="audio/wav")
                        eval_res = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=["Transcribe spoken audio and evaluate whether candidate correctly covers standard Goethe A1 self-introduction points.", audio_part],
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                        )
                        st.write(eval_res.text)
                    except Exception as e: st.error(f"Error: {str(e)}")

    # --- SPRECHEN TEIL 2 ---
    with sp_tab2:
        st.markdown("**Teil 2:** Draw a topic card (Theme + Keyword) and ask a W-question. Verb MUST be in Position 2!")
        if st.button("🎲 Draw Teil 2 Topic Card", type="primary"):
            with st.spinner("Gem is drawing card..."):
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents="Generate a Goethe A1 Sprechen topic card (e.g. Thema: 'Einkaufen', Wort: 'Brot').",
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.card_t2 = res.text
                except Exception as e: st.error(f"Error: {str(e)}")

        if "card_t2" in st.session_state:
            st.success(f"🎴 **Your Card:** {st.session_state.card_t2}")
            rec_t2 = mic_recorder(start_prompt="Record W-Question 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t2")
            if rec_t2:
                st.audio(rec_t2['bytes'], format='audio/wav')
                if st.button("Evaluate Question Syntax"):
                    with st.spinner("Gem is evaluating verb placement..."):
                        try:
                            audio_part = types.Part.from_bytes(data=rec_t2['bytes'], mime_type="audio/wav")
                            eval_res = client.models.generate_content(
                                model=MODEL_NAME,
                                contents=[f"Card: {st.session_state.card_t2}. Transcribe audio and verify if candidate formed a correct W-question with conjugated verb in Position 2.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    # --- SPRECHEN TEIL 3 ---
    with sp_tab3:
        st.markdown("**Teil 3:** Draw an object/request card and make an imperative request. Verb MUST be in Position 1!")
        if st.button("🎲 Draw Teil 3 Request Card", type="primary"):
            with st.spinner("Gem is drawing card..."):
                try:
                    res = client.models.generate_content(
                        model=MODEL_NAME, contents="Generate a Goethe A1 Sprechen request card (e.g. Gegenstand: Bleistift).",
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                    )
                    st.session_state.card_t3 = res.text
                except Exception as e: st.error(f"Error: {str(e)}")

        if "card_t3" in st.session_state:
            st.success(f"🎴 **Your Card:** {st.session_state.card_t3}")
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
# 7. ASK GEM
# ----------------------------------------------------
elif nav_choice == "💬 Ask Gem (AI Tutor)":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("💬 Ask Gem — Interactive AI Tutor")
    if prompt := st.chat_input("Ask Gem a question:"):
        res = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        st.write(res.text)
    st.markdown('</div>', unsafe_allow_html=True)
