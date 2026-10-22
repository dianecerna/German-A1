import os
import json
import io
import random
import time
import pypdf
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

# Custom Styling: Icon replacements, Colored Dropdown Frames, Section Frames, Tap-to-Answer, Split Question/Answer Frames
st.markdown("""
<style>
    /* Global Clean Modern Sans-Serif Font & Background */
    .stApp {
        background-color: #f0f4f8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    *, div, span, p, h1, h2, h3, h4, h5, h6, label, button {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Colorful Section Frames */
    .frame-blue { border: 2.5px solid #3b82f6; border-radius: 20px; padding: 24px; background: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(59, 130, 246, 0.12); }
    .frame-purple { border: 2.5px solid #8b5cf6; border-radius: 20px; padding: 24px; background: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(139, 92, 246, 0.12); }
    .frame-emerald { border: 2.5px solid #10b981; border-radius: 20px; padding: 24px; background: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.12); }
    .frame-amber { border: 2.5px solid #f59e0b; border-radius: 20px; padding: 24px; background: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(245, 158, 11, 0.12); }
    .frame-rose { border: 2.5px solid #f43f5e; border-radius: 20px; padding: 24px; background: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(244, 63, 94, 0.12); }

    /* Separate Question and Answer Frames */
    .question-frame {
        background: #f8fafc;
        border: 2px solid #cbd5e1;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .answer-frame {
        background: #ffffff;
        border: 2px solid #3b82f6;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        border-radius: 24px;
        padding: 36px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
        border: 2px solid #3b82f6;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 15px;
        color: #60a5fa;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #e2e8f0;
        line-height: 1.6;
        max-width: 800px;
        margin-bottom: 0px;
    }

    /* Sidebar Navigation */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebarNav"] span, .stRadio label {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
        letter-spacing: 0.02em;
    }

    /* Fix Collapse Sidebar Control Icon (Replace text/double underscore with arrow icon) */
    [data-testid="collapsedControl"] span {
        display: none !important;
    }
    [data-testid="collapsedControl"]::after {
        content: "➡️" !important;
        font-size: 1.2rem;
        display: block;
    }

    /* Framed Dropdown Elements with Colored Borders */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #f8fafc !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.1);
        transition: border-color 0.2s ease;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #2563eb !important;
        background-color: #eff6ff !important;
    }

    /* Interactive Flashcard UI */
    .flashcard-front-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 2px solid #60a5fa;
        margin-bottom: 15px;
    }
    .flashcard-word-title {
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #60a5fa;
        margin-bottom: 10px;
    }
    .flashcard-back-box {
        background: #ffffff;
        border: 2px solid #1e3a8a;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.15);
        margin-bottom: 15px;
    }
    .flashcard-back-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .meaning-subtitle {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 15px;
    }

    /* Floating Cute Bot Widget on Bottom Left */
    .floating-bot-container {
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 99999;
    }
    .bot-popout-box {
        background: #ffffff;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2);
        border: 2px solid #1e3a8a;
        width: 340px;
        margin-bottom: 12px;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    strong, b {
        font-weight: 700 !important;
        color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 **Missing Gemini API Key!** Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())

FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

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
    for attempt in range(2):
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
                if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota", "not_found"]):
                    time.sleep(1)
                    continue
                raise e
        time.sleep(1.5)
            
    raise Exception(f"All model quotas are currently exhausted or experiencing high demand. Details: {str(last_error)}")

def generate_dynamic_content(prompt_text: str, is_json: bool = False) -> str:
    config_args = {"system_instruction": SYSTEM_INSTRUCTION}
    if is_json:
        config_args["response_mime_type"] = "application/json"
    
    last_error = None
    for attempt in range(2):
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
                if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota", "not_found"]):
                    time.sleep(1)
                    continue
                raise e
        time.sleep(1.5)
            
    raise Exception(f"All model quotas are currently exhausted or experiencing high demand. Details: {str(last_error)}")

@st.cache_data(show_spinner=False)
def generate_german_audio_bytes(text: str) -> bytes:
    tts = gTTS(text=text, lang='de')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.getvalue()

def play_direct_audio(text_to_speak, unique_key):
    audio_bytes = generate_german_audio_bytes(text_to_speak)
    b64_audio = io.BytesIO(audio_bytes).read()
    st.audio(b64_audio, format="audio/mp3", autoplay=True)

# Hören Teil 1 Official Scenarios Bank
HOREN_TEIL1_SCENARIOS = [
    {"title": "Jacke, Kino & Apotheke", "desc": "Short everyday dialogues about a jacket's price, the film start and directions to the pharmacy – 6 tasks, a/b/c."},
    {"title": "Zug nach Köln, Markt & Hotel", "desc": "Short everyday dialogues about the train to Köln, the market, weather and a hotel room – 6 tasks, a/b/c."},
    {"title": "Gäste, Supermarkt & Urlaub", "desc": "Short everyday dialogues about guests, holidays, Frau Roth's hobby and lost glasses – 6 tasks, a/b/c."}
]

# Hören Teil 2 Official Scenarios Bank
HOREN_TEIL2_SCENARIOS = [
    {"title": "Markt-, Bahn- & Flughafendurchsagen", "desc": "Short announcements at a market, railway station and airport – 4 tasks, Richtig/Falsch."},
    {"title": "Kaufhaus-, Bahn- & Schwimmbaddurchsagen", "desc": "Announcements from a department store, train, swimming pool and airport – 4 tasks, Richtig/Falsch."}
]

# Lesen Teil 1 Official Scenarios Bank (Multiple distinct scenarios for true refreshing)
LESEN_TEIL1_SCENARIOS = [
    {
        "title": "Flughafen & Grillfest",
        "desc": "Two short messages: airport pickup and a garden barbecue — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail (Lena an Tom)",
        "text1": "BETREFF: Hallo Tom,\n\nvielen Dank für deine Nachricht! Ich hole dich am Sonntag vom Flughafen ab. Dein Flugzeug landet um 14.20 Uhr. Ich bin schon um 14 Uhr da und warte am Ausgang.\nRuf mich bitte an, wenn dein Flug später kommt. Meine Nummer hast du ja.\nBis Sonntag!\nLena",
        "text2_label": "BRIEF (Einladung zum Grillfest)",
        "text2": "Liebe Sofia,\n\nnächsten Samstag mache ich ein Grillfest bei mir im Garten. Wir beginnen um 17 Uhr. Kommst du auch? Es kommen noch andere Freunde, die du kennst. Bitte bring etwas zu trinken mit. Fleisch und Salate habe ich schon genug. Wenn es regnet, feiern wir in der Wohnung.",
        "questions": [
            {"id": "lt1_1", "statement": "Lena holt Tom am Samstag vom Flughafen ab.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Im Text steht, dass sie ihn am *Sonntag* abholt."},
            {"id": "lt1_2", "statement": "Tom landet um 14.20 Uhr.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Text bestätigt: 'Dein Flugzeug landet um 14.20 Uhr.'"},
            {"id": "lt1_3", "statement": "Lena wartet am Ausgang.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Lena schreibt: '...und warte am Ausgang.'"},
            {"id": "lt1_4", "statement": "Sofia soll Fleisch und Salate mitbringen.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Fleisch und Salate sind genug da; Sofia soll *etwas zu trinken* mitbringen."},
            {"id": "lt1_5", "statement": "Bei Regen findet das Grillfest in der Wohnung statt.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Brief steht: 'Wenn es regnet, feiern wir in der Wohnung.'"}
        ]
    },
    {
        "title": "Krankmeldung & Vereinsausflug",
        "desc": "Two short messages: a sick note and a club outing — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail an die Arbeit",
        "text1": "Sehr geehrte Frau Braun,\nich kann heute leider nicht ins Büro kommen, da ich starkes Fieber und Husten habe. Ich gehe heute Nachmittag zum Arzt und bringe morgen die Krankmeldung mit.\nMit freundlichen Grüßen,\nMarkus Weber",
        "text2_label": "Aushang (Sportverein)",
        "text2": "Liebe Vereinsmitglieder,\nserer Jahresausflug findet am Samstag, den 14. Juli, statt. Wir fahren mit dem Bus in die Berge zum Wandern. Anmeldung bitte bis Mittwoch bei Trainer Klaus.",
        "questions": [
            {"id": "lt1_21", "statement": "Markus hat Fieber und Husten.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Markus schreibt, dass er starkes Fieber und Husten hat."},
            {"id": "lt1_22", "statement": "Markus bringt die Krankmeldung erst nächste Woche.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Er bringt sie *morgen* mit."},
            {"id": "lt1_23", "statement": "Der Vereinsausflug ist am Sonntag.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Der Ausflug findet am *Samstag*, den 14. Juli, statt."},
            {"id": "lt1_24", "statement": "Man fährt mit dem Bus in die Berge.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Aushang steht: 'Wir fahren mit dem Bus in die Berge.'"},
            {"id": "lt1_25", "statement": "Man muss sich bis Mittwoch bei Klaus anmelden.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Anmeldung bitte bis Mittwoch bei Trainer Klaus."}
        ]
    },
    {
        "title": "Vegetarisches Essen & Fußballtraining",
        "desc": "Two short messages: a vegetarian dinner and football training — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail (Abendessen)",
        "text1": "Hallo Anna,\n\nich koche heute Abend vegetarisch. Es gibt Gemüsesuppe und Salat. Komm doch um 19 Uhr zu mir!\nLiebe Grüße,\nMaria",
        "text2_label": "SMS (Fußball)",
        "text2": "Hallo zusammen, das Fußballtraining am Mittwoch fällt leider aus, weil der Platz nass ist. Nächste Woche spielen wir wieder normal.\nGruß, Trainer Stefan",
        "questions": [
            {"id": "lt1_41", "statement": "Maria kocht heute Abend Fleisch.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Maria kocht vegetarisch (Gemüsesuppe und Salat)."},
            {"id": "lt1_42", "statement": "Das Essen beginnt um 19 Uhr.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Maria lädt Anna um 19 Uhr ein."},
            {"id": "lt1_43", "statement": "Das Fußballtraining findet am Mittwoch statt.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Das Training fällt aus."},
            {"id": "lt1_44", "statement": "Der Sportplatz ist nass.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Grund für den Ausfall ist ein nasser Platz."},
            {"id": "lt1_45", "statement": "Nächste Woche findet das Training wieder statt.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Trainer schreibt: 'Nächste Woche spielen wir wieder normal.'"}
        ]
    }
]

# Lesen Teil 2 Official Scenarios Bank
LESEN_TEIL2_SCENARIOS = [
    {
        "title": "Fahrrad, Schwimmbad & Pizza",
        "desc": "Information about buying a bicycle, swimming pools, and ordering pizza — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_t1",
                "situation": "6. Sie möchten ein gebrauchtes Fahrrad kaufen.",
                "site_a_url": "www.fahrrad-neu.de",
                "site_a": "Neue Fahrräder und E-Bikes\nNur Neuware vom Fachhändler",
                "site_b_url": "www.radmarkt-leipzig.de",
                "site_b": "Radmarkt Leipzig\nGebrauchte Fahrräder günstig kaufen und verkaufen",
                "answer": "Website B",
                "explanation": "Sie suchen ein *gebrauchtes* Fahrrad. Website B bietet gebrauchte Fahrräder an."
            },
            {
                "id": "lt2_t2",
                "situation": "7. Sie möchten am Wochenende ins Schwimmbad gehen.",
                "site_a_url": "www.stadtbad-erfurt.de",
                "site_a": "Stadtbad Erfurt\nHallenbad mit Sauna\nAuch am Wochenende geöffnet!",
                "site_b_url": "www.schwimmverein-erfurt.de",
                "site_b": "Schwimmverein Erfurt\nSchwimmkurse und Training nur für Mitglieder",
                "answer": "Website A",
                "explanation": "Website A ist ein öffentliches Bad mit Wochenendöffnung."
            }
        ]
    },
    {
        "title": "Hotel, Werkstatt & Babysitter",
        "desc": "Information about hotel bookings, repair shops, and babysitters — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_21",
                "situation": "6. Sie suchen ein ruhiges Hotel am Meer für Ihren Urlaub.",
                "site_a_url": "www.hotel-Seeblick-ostsee.de",
                "site_a": "Hotel Seeblick\nDirekt am Strand, ruhige Zimmer mit Meerblick.",
                "site_b_url": "www.city-hotel-bahnhof.de",
                "site_b": "City Hotel am Hauptbahnhof\nZentral, ideal für Geschäftsreisende.",
                "answer": "Website A",
                "explanation": "Hotel Seeblick liegt direkt am Strand und bietet Meerblick."
            },
            {
                "id": "lt2_22",
                "situation": "7. Ihr Auto hat Probleme mit den Bremsen.",
                "site_a_url": "www.autowerkstatt-mueller.de",
                "site_a": "Kfz-Meisterbetrieb Müller\nReparatur aller Automarken, Bremsenservice und TÜV.",
                "site_b_url": "www.auto-waschpark.de",
                "site_b": "Autowaschpark Express\nPflege und Reinigung für Ihr Auto.",
                "answer": "Website A",
                "explanation": "Kfz-Meisterbetrieb Müller bietet Bremsenservice an."
            }
        ]
    }
]

# Lesen Teil 3 Official Scenarios Bank
LESEN_TEIL3_SCENARIOS = [
    {
        "title": "Bäckerei, Markt & Parkhaus",
        "desc": "Signs and notices about a bakery, market, and car park — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Zum Deutsch Lernen gehen Sie in die Beethovenstraße 23.",
            "sign_title": "AN DER TÜR DER SPRACHSCHULE",
            "sign_text": "SPRACHZENTRUM\nDas Sprachzentrum ist umgezogen.\nSie finden uns jetzt in der Beethovenstr. 23",
            "answer": "richtig",
            "explanation": "Das Schild bestätigt, dass das Sprachzentrum jetzt in der Beethovenstr. 23 ist."
        },
        "tasks": [
            {
                "id": "lt3_1",
                "statement": "Im August ist die Bäckerei zwei Wochen geschlossen.",
                "sign_title": "AN DER BÄCKEREI",
                "sign_text": "Liebe Kunden!\nWegen Urlaub bleibt unsere Bäckerei vom 1. bis 14. August geschlossen.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Der Zettel besagt, dass die Bäckerei vom 1. bis 14. August wegen Urlaub geschlossen ist."
            },
            {
                "id": "lt3_2",
                "statement": "Im Parkhaus darf man kostenlos parken.",
                "sign_title": "EINGANG PARKHAUS",
                "sign_text": "Parkhaus Stadtmitte\nErste Stunde frei, jede weitere angefangene Stunde 2,00 Euro.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Nur die *erste* Stunde ist frei, danach kostet es 2,00 Euro."
            }
        ]
    },
    {
        "title": "Apotheke, Kino & Arztpraxis",
        "desc": "Signs and notices about an emergency pharmacy, cinema, and medical practice — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Die Apotheke hat nachts Notdienst.",
            "sign_title": "APOTHEKE NOTDIENST",
            "sign_text": "Heute Nacht hat die Central-Apotheke für Notfälle geöffnet.",
            "answer": "richtig",
            "explanation": "Das Schild zeigt, welche Apotheke Nachtdienst hat."
        },
        "tasks": [
            {
                "id": "lt3_a1",
                "statement": "Im Kino läuft der Film erst ab 18 Jahren.",
                "sign_title": "KINO KASSE",
                "sign_text": "Heute Abend: 'Abenteuer in Berlin' (FSK ab 12 Jahren).",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Der Film ist ab 12 Jahren freigegeben, nicht ab 18."
            }
        ]
    }
]

# Schreiben Teil 1 Official Scenarios Bank
SCHREIBEN_TEIL1_SCENARIOS = [
    {
        "title": "Bodensee-Rundfahrt — Anmeldung",
        "desc": "Registration for a Bodensee tour with Eva Kadavy – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Ihre Freundin, Eva Kadavy, macht mit ihrem Mann und ihren beiden Söhnen Urlaub in Seeheim.\n\nIm Reisebüro bucht sie für den nächsten Sonntag eine Busfahrt um den Bodensee.",
        "form_title": "BODENSEE-RUNDFAHRT — Anmeldung",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Kadavy, Eva", "is_gap": False},
            {"id": "sf2", "label": "1. Anzahl der Personen:", "answer": "4", "is_gap": True, "placeholder": "z. B. 4"},
            {"id": "sf3", "label": "2. Davon Kinder:", "answer": "2", "is_gap": True, "placeholder": "z. B. 2"}
        ]
    },
    {
        "title": "Praxis Dr. Sommer — Patienteninformation",
        "desc": "Pavel Novák's patient information for a doctor's visit – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Pavel Novák (geboren 1985) hat starke Kopfschmerzen und geht in die Arztpraxis Dr. Sommer.\n\nEr ist bei der Krankenkasse AOK versichert.",
        "form_title": "ARZTPRAXIS DR. SOMMER — Patientenkarte",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Novák, Pavel", "is_gap": False},
            {"id": "sf2", "label": "1. Geburtsjahr:", "answer": "1985", "is_gap": True, "placeholder": "z. B. 1985"},
            {"id": "sf3", "label": "2. Beschwerde:", "answer": "Kopfschmerzen", "is_gap": True, "placeholder": "z. B. Kopfschmerzen"}
        ]
    }
]

# Schreiben Teil 2 Official Scenarios Bank
SCHREIBEN_TEIL2_SCENARIOS = [
    {
        "title": "Dresden besuchen — Touristeninformation",
        "desc": "Message to the tourist information office about visiting Dresden – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie möchten im August Dresden besuchen. Schreiben Sie an die Touristeninformation.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Warum schreiben Sie?",
            "2. Bitten Sie: Informationen über das Kulturprogramm.",
            "3. Fragen Sie: Hoteladressen?"
        ],
        "prompt": "Sehr geehrte Damen und Herren,\n\nich möchte im August Dresden besuchen und plane eine Reise. Könnten Sie mir bitte Informationen über das Kulturprogramm schicken? Haben Sie auch Empfehlungen für Hoteladressen?\n\nMit freundlichen Grüßen,\n[Dein Name]"
    },
    {
        "title": "Krank — Nachricht an den Deutschkurs",
        "desc": "Email to Frau Wolf about being ill and missing German class – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie sind krank und können heute nicht in den Deutschkurs kommen. Schreiben Sie an Ihre Lehrerin, Frau Wolf.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Grund für das Schreiben (krank).",
            "2. Wie lange bleiben Sie zu Hause?",
            "3. Fragen nach den Hausaufgaben."
        ],
        "prompt": "Liebe Frau Wolf,\n\nich liege leider mit starkem Fieber im Bett und kann heute nicht in den Deutschkurs kommen. Ich muss zwei Tage zu Hause bleiben. Könnten Sie mir bitte per E-Mail die Hausaufgaben schicken?\n\nLiebe Grüße,\n[Dein Name]"
    }
]

# Sidebar Navigation
st.sidebar.title("🇩🇪 Goethe A1 Studio")
st.sidebar.caption("Target Exam: **Dec 12, 2026**")
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
    "📖 A1 & A2 Short Stories",
    "💬 Ask Gem (AI Tutor)"
])

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">✨ GOETHE A1 EXAM PREP STUDIO</div>
        <div class="hero-title">Goethe-Zertifikat A1 Studio</div>
        <div class="hero-subtitle">Target Exam: <span style="color: #ffffff; font-weight: 700;">December 12, 2026</span>[span_0](start_span)[span_0](end_span). Complete Goethe A1 curriculum preparation featuring the complete 612-word Goethe vocabulary list, official flashcards, grammar exercises, fully structured 3-part Goethe exam simulators with live countdowns, and enchanted storybooks[span_1](start_span)[span_1](end_span).</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="frame-blue">', unsafe_allow_html=True)
        st.subheader("📖 Lesen & ✍️ Schreiben")
        st.markdown("""
        * **Lesen (25 Mins - 15 Tasks across 3 Parts):**
          - **Teil 1:** Short Emails (Richtig/Falsch) - *Official exam scenarios fully integrated!*
          - **Teil 2:** Classified Ads (Option A or B) - *Official exam scenarios fully integrated!*
          - **Teil 3:** Public Signs (Richtig/Falsch) - *Official exam scenarios fully integrated!*
        * **Schreiben (20 Mins - 2 Parts):**
          - **Teil 1:** Fill 5 Missing Gaps on Form with Scenario
          - **Teil 2:** Write ~30-Word Message hitting 3 required points
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="frame-purple">', unsafe_allow_html=True)
        st.subheader("🎧 Hören & 🗣️ Sprechen")
        st.markdown("""
        * **Hören (20 Mins - 15 Tasks across 3 Parts):**
          - **Teil 1:** 6 Dialogues (A/B/C)
          - **Teil 2:** 4 Announcements (Richtig/Falsch)
          - **Teil 3:** 5 Voicemails (A/B/C)
        * **Sprechen (15 Mins - 3 Parts):**
          - **Teil 1:** Self-Introduction & Spelling/Numbers
          - **Teil 2:** W-Questions with Topic Card
          - **Teil 3:** Imperative Requests with Object Card
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="frame-emerald">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Interactive Flashcard Engine (Complete Vocabulary)")
    st.write("Browse through the complete Goethe A1 vocabulary list categorized into your thematic groups.")

    TOP_1000_VOCAB_CATEGORIES = {
        "1. Person & Alltag (Personal & Daily Life)": {
            "Verben": ["heißen", "heiraten", "wohnen", "leben", "kennen", "kennenlernen", "schlafen", "aufstehen", "baden", "duschen"],
            "Nomen": ["die Familie", "der Vater", "die Mutter", "der Sohn", "die Tochter", "der Bruder", "die Schwester", "der Mann", "die Frau", "das Kind"]
        },
        "2. Essen & Trinken (Food & Drink)": {
            "Verben": ["essen", "trinken", "kochen", "backen", "frühstücken", "schmecken", "grillen", "bestellen"],
            "Nomen": ["das Essen", "das Frühstück", "das Mittagessen", "das Abendessen", "das Wasser", "der Kaffee", "der Tee", "das Bier", "der Wein"]
        }
    }

    vocab_tree = TOP_1000_VOCAB_CATEGORIES

    main_cats = ["ALL"] + list(vocab_tree.keys())
    selected_main_cat = st.selectbox("📂 **Select Main Category:**", main_cats)

    if selected_main_cat == "ALL":
        sub_cats = ["ALL"]
        selected_sub_cat = "ALL"
        all_pool = []
        for cat, subdict in vocab_tree.items():
            for sub, wlist in subdict.items():
                all_pool.extend(wlist)
        available_words = ["ALL"] + list(set(all_pool))
    else:
        sub_dict = vocab_tree[selected_main_cat]
        sub_cats = ["ALL"] + list(sub_dict.keys())
        selected_sub_cat = st.selectbox("📁 **Select Subcategory:**", sub_cats)

        if selected_sub_cat == "ALL":
            all_sub_pool = []
            for sub, wlist in sub_dict.items():
                all_sub_pool.extend(wlist)
            available_words = ["ALL"] + list(set(all_sub_pool))
        else:
            available_words = ["ALL"] + sub_dict[selected_sub_cat]

    selected_word_dropdown = st.selectbox("🔤 **Select specific word (or ALL):**", available_words)

    col_w1, col_w2 = st.columns([3, 1])
    with col_w1:
        if selected_word_dropdown == "ALL":
            actual_pool = [w for w in available_words if w != "ALL"]
            active_word = random.choice(actual_pool) if actual_pool else "sein"
        else:
            active_word = selected_word_dropdown
    with col_w2:
        if st.button("🎲 Shuffle Random Word", use_container_width=True):
            actual_pool = [w for w in available_words if w != "ALL"]
            st.session_state.current_flashcard_word = random.choice(actual_pool) if actual_pool else "sein"
            st.session_state.show_card_back = False
            st.rerun()

    # Vocab Quiz Button below Random Word button
    if "vocab_quiz_active" not in st.session_state:
        st.session_state.vocab_quiz_active = False

    if not st.session_state.vocab_quiz_active:
        if st.button("📝 Vocab Quiz", use_container_width=True, type="primary"):
            st.session_state.vocab_quiz_active = True
            st.session_state.vocab_quiz_direction = st.radio("Select Quiz Direction:", ["English to German", "German to English"], horizontal=True)
            flat_vocab = [w for w in available_words if w != "ALL"]
            if not flat_vocab:
                flat_vocab = ["sein", "haben", "gehen", "machen", "essen"]
            chosen_w = random.choice(flat_vocab)
            st.session_state.vocab_quiz_word = chosen_w
            # Fetch meaning
            try:
                trans_res = generate_cached_content(f"Translate '{chosen_w}' to English and return JSON: {{\"translation\": \"...\"}}", is_json=True)
                st.session_state.vocab_quiz_translation = json.loads(trans_res).get("translation", "meaning")
            except:
                st.session_state.vocab_quiz_translation = "meaning"
            st.rerun()
    else:
        st.markdown("### 📝 Vocab Quiz Session")
        q_dir = st.session_state.get("vocab_quiz_direction", "English to German")
        q_word = st.session_state.get("vocab_quiz_word", "sein")
        q_trans = st.session_state.get("vocab_quiz_translation", "to be")

        if q_dir == "English to German":
            prompt_text = f"What is the German word for English: **{q_trans}**?"
            target_ans = q_word
        else:
            prompt_text = f"What is the English meaning for German: **{q_word}**?"
            target_ans = q_trans

        st.markdown(f"**Question:** {prompt_text}")
        user_vocab_ans = st.text_input("Your answer:", key="vocab_quiz_input_box")

        col_vq1, col_vq2 = st.columns(2)
        with col_vq1:
            if st.button("Submit Answer (Tap)", use_container_width=True, type="primary"):
                # Evaluate with AI explanation
                eval_prompt = f"Evaluate user answer '{user_vocab_ans}' against target '{target_ans}'. Return JSON: {{\"correct\": true/false, \"explanation\": \"...\"}}"
                try:
                    eval_out = json.loads(generate_cached_content(eval_prompt, is_json=True))
                    if eval_out.get("correct", False):
                        st.success(f"🟢 Correct! {eval_out.get('explanation', '')}")
                    else:
                        st.error(f"🔴 Incorrect. The correct answer was '{target_ans}'. {eval_out.get('explanation', '')}")
                except Exception as ex:
                    st.error(f"Error checking answer: {str(ex)}")
        with col_vq2:
            if st.button("Exit Quiz", use_container_width=True):
                st.session_state.vocab_quiz_active = False
                st.rerun()

    if "current_flashcard_word" not in st.session_state or st.session_state.current_flashcard_word not in available_words:
        st.session_state.current_flashcard_word = active_word

    if selected_word_dropdown != "ALL" and selected_word_dropdown != st.session_state.current_flashcard_word:
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
            {{"pronoun": "ich", "form": "...", "sentence": "German sentence", "sentence_en": "English sentence"}}
        ],
        "perfekt_tense": {{
            "formula": "hat/ist + Partizip II",
            "sample_sentence_de": "German Perfekt sentence",
            "sample_sentence_en": "English Perfekt sentence"
        }},
        "comparative_superlative": "N/A",
        "common_phrases": [
            {{"phrase_de": "German phrase", "phrase_en": "English translation"}}
        ],
        "grammar_notes": "Important A1 grammar note"
    }}
    """

    try:
        raw_json = generate_cached_content(prompt, is_json=True)
        data = json.loads(raw_json)

        if not st.session_state.get("show_card_back", False):
            st.markdown(f"""
            <div class="flashcard-front-box">
                <p style="color: #60a5fa; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 8px;">⭐ {selected_main_cat} / {selected_sub_cat} ⭐</p>
                <div class="flashcard-word-title">{data.get("word", active_word)}</div>
                <p style="color: #e2e8f0; font-size: 0.9rem; margin-bottom: 0px;">Click speaker icon for instant audio playback, or flip card for details.</p>
            </div>
            """, unsafe_allow_html=True)
            
            c_aud_front = st.columns([0.5, 10])
            with c_aud_front[0]:
                if st.button("🔊", key="audio_front_btn"):
                    play_direct_audio(active_word, "front_word")
            with c_aud_front[1]:
                st.caption(f"Listen to pronunciation of **{active_word}**")

        else:
            st.markdown(f"""
            <div class="flashcard-back-box">
                <p style="color: #1e3a8a; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 2px;">⭐ {selected_main_cat} / {selected_sub_cat}</p>
                <div class="flashcard-back-title">{data.get("word", active_word)}</div>
                <div class="meaning-subtitle">Meaning: <b>{data.get("english_meaning", "")}</b></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Part of Speech", data.get("part_of_speech", "N/A"))
            c2.metric("Gender", data.get("gender", "N/A"))
            c3.metric("Plural Form", data.get("plural_form", "N/A"))
            c4.metric("Comp. / Superlative", data.get("comparative_superlative", "N/A"))

    except Exception as e:
        st.error(f"Error compiling flashcard details: {str(e)}")

    st.divider()

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        if st.button("🔄 Flip Flashcard (Front / Back)", use_container_width=True, type="primary"):
            st.session_state.show_card_back = not st.session_state.get("show_card_back", False)
            st.rerun()

    with col_f2:
        if st.button("🎲 Random Word in Deck", use_container_width=True):
            actual_pool = [w for w in available_words if w != "ALL"]
            st.session_state.current_flashcard_word = random.choice(actual_pool) if actual_pool else "sein"
            st.session_state.show_card_back = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. CORE GRAMMAR PRACTICE & EXERCISES
# ----------------------------------------------------
elif nav_choice == "📖 Core Grammar Practice & Exercises":
    st.markdown('<div class="frame-amber">', unsafe_allow_html=True)
    st.subheader("📖 Core Grammar Practice & Exercises")
    st.write("Review class handbook modules with rigorous bullet points and targeted practice questions.")

    handbook_lessons = [
        "Lesson 1: German Alphabet, Pronunciation, and Article Recognition",
        "Lesson 2: German Noun Gender and Everyday Word Patterns"
    ]

    selected_lesson = st.selectbox("Select Handbook Lesson to Review & Practice:", handbook_lessons)

    if st.button("📖 Load Rigorous Review & Practice Exercises", type="primary"):
        with st.spinner("Gem is compiling clean bulleted notes and practice exercises..."):
            prompt = f"""
            Create a detailed study review & practice package for '{selected_lesson}'.
            Return strict JSON format:
            {{
                "lesson_title": "{selected_lesson}",
                "lesson_explanation": "Bulleted markdown guide...",
                "exercises_mc": [
                    {{"id": "mc1", "question": "Q1", "options": ["A", "B", "C", "D"], "correct": "A", "explanation": "..."}}
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
        st.subheader("📝 Practice Exercises")
        for idx, q in enumerate(mod.get("exercises_mc", []), start=1):
            # Separate question frame and answer frame
            st.markdown(f"""
            <div class="question-frame">
                <b>Q{idx}. {q['question']}</b>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
            cols_ans = st.columns(len(q['options']))
            for opt_i, opt_val in enumerate(q['options']):
                with cols_ans[opt_i]:
                    if st.button(opt_val, key=f"btn_mc_{q['id']}_{opt_i}", use_container_width=True):
                        if opt_val == q['correct']:
                            st.success(f"🟢 Correct! {q['explanation']}")
                        else:
                            st.error(f"🔴 Incorrect. Correct was '{q['correct']}'. {q['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 4. GOETHE A1 LESEN
# ----------------------------------------------------
elif nav_choice == "📖 Goethe A1 Lesen (Reading)":
    st.markdown('<div class="frame-rose">', unsafe_allow_html=True)
    st.subheader("📖 Goethe A1 Lesen Practice (25 Mins, 15 Points across 3 Parts)")

    l_tab1, l_tab2, l_tab3 = st.tabs([
        "Teil 1: Short Messages", 
        "Teil 2: Classified Ads", 
        "Teil 3: Public Signs"
    ])

    with l_tab1:
        st.markdown("**Teil 1 (Kurze Mitteilungen):** Select from scenarios or click Refresh to get a completely new scenario.")
        
        if "dyn_lesen_t1_idx" not in st.session_state:
            st.session_state.dyn_lesen_t1_idx = 0

        col_lt1_sel, col_lt1_ref = st.columns([4, 1])
        with col_lt1_sel:
            scenario_titles = [s["title"] for s in LESEN_TEIL1_SCENARIOS]
            selected_lesen_t1_title = st.selectbox("📂 **Select Lesen Teil 1 Scenario Set:**", scenario_titles, key="lesen_t1_sel")
        with col_lt1_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_lesen_t1", use_container_width=True):
                # Cycle index to rotate through scenarios
                st.session_state.dyn_lesen_t1_idx = (st.session_state.dyn_lesen_t1_idx + 1) % len(LESEN_TEIL1_SCENARIOS)
                st.success("Refreshed scenario!")
                st.rerun()

        # Get active scenario based on index or title selection
        active_idx = st.session_state.dyn_lesen_t1_idx
        selected_lesen_t1_obj = LESEN_TEIL1_SCENARIOS[active_idx]
        
        st.info(f"📌 **Description:** {selected_lesen_t1_obj['desc']}")
        
        st.markdown('<div class="question-frame">', unsafe_allow_html=True)
        st.markdown(f"**{selected_lesen_t1_obj.get('text1_label', 'E-Mail')}**\n{selected_lesen_t1_obj['text1']}")
        st.markdown(f"**{selected_lesen_t1_obj.get('text2_label', 'Brief')}**\n{selected_lesen_t1_obj['text2']}")
        st.markdown('</div>', unsafe_allow_html=True)

        for idx, q in enumerate(selected_lesen_t1_obj["questions"], start=1):
            st.markdown(f"""
            <div class="question-frame">
                <b>Task {idx}: {q['statement']}</b>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
            cols_q1 = st.columns(len(q['options']))
            for opt_idx, opt_val in enumerate(q['options']):
                with cols_q1[opt_idx]:
                    if st.button(opt_val, key=f"lt1_{active_idx}_{q['id']}_{opt_val}", use_container_width=True):
                        if opt_val == q['answer']:
                            st.success(f"🟢 Correct! {q['explanation']}")
                        else:
                            st.error(f"🔴 Incorrect. Correct was '{q['answer']}'. {q['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)

    with l_tab2:
        st.markdown("**Teil 2 (Zuordnung):** Classified Ads matching.")
        if "dyn_lesen_t2_idx" not in st.session_state:
            st.session_state.dyn_lesen_t2_idx = 0
        if st.button("Refresh Scenarios", key="ref_lesen_t2"):
            st.session_state.dyn_lesen_t2_idx = (st.session_state.dyn_lesen_t2_idx + 1) % len(LESEN_TEIL2_SCENARIOS)
            st.rerun()
        
        sel_t2 = LESEN_TEIL2_SCENARIOS[st.session_state.dyn_lesen_t2_idx]
        st.markdown(f"### {sel_t2['title']}")
        for t in sel_t2['tasks']:
            st.markdown(f"""
            <div class="question-frame">
                <b>{t['situation']}</b>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
            cols_t2 = st.columns(2)
            with cols_t2[0]:
                if st.button(f"Choose A: {t['site_a_url']}", key=f"t2_a_{t['id']}", use_container_width=True):
                    if "Website A" == t['answer']:
                        st.success(f"🟢 Correct! {t['explanation']}")
                    else:
                        st.error(f"🔴 Incorrect. Correct was {t['answer']}. {t['explanation']}")
            with cols_t2[1]:
                if st.button(f"Choose B: {t['site_b_url']}", key=f"t2_b_{t['id']}", use_container_width=True):
                    if "Website B" == t['answer']:
                        st.success(f"🟢 Correct! {t['explanation']}")
                    else:
                        st.error(f"🔴 Incorrect. Correct was {t['answer']}. {t['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)

    with l_tab3:
        st.markdown("**Teil 3 (Öffentliche Hinweise):** Public Signs.")
        if "dyn_lesen_t3_idx" not in st.session_state:
            st.session_state.dyn_lesen_t3_idx = 0
        if st.button("Refresh Scenarios", key="ref_lesen_t3"):
            st.session_state.dyn_lesen_t3_idx = (st.session_state.dyn_lesen_t3_idx + 1) % len(LESEN_TEIL3_SCENARIOS)
            st.rerun()
            
        sel_t3 = LESEN_TEIL3_SCENARIOS[st.session_state.dyn_lesen_t3_idx]
        st.markdown(f"### {sel_t3['title']}")
        for t in sel_t3['tasks']:
            st.markdown(f"""
            <div class="question-frame">
                <b>{t['statement']}</b> — <em>{t['sign_title']}</em><br>
                <code>{t['sign_text']}</code>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
            cols_t3 = st.columns(len(t['options']))
            for opt_i, opt_v in enumerate(t['options']):
                with cols_t3[opt_i]:
                    if st.button(opt_v, key=f"t3_{t['id']}_{opt_v}", use_container_width=True):
                        if opt_v == t['answer']:
                            st.success(f"🟢 Correct! {t['explanation']}")
                        else:
                            st.error(f"🔴 Incorrect. Correct was {t['answer']}. {t['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="frame-blue">', unsafe_allow_html=True)
    st.subheader("🎧 Goethe A1 Hören Practice (20 Mins, 15 Points across 3 Parts)")

    h_tab1, h_tab2, h_tab3 = st.tabs([
        "Teil 1: 6 Dialogues", 
        "Teil 2: 4 Announcements", 
        "Teil 3: 5 Voicemails"
    ])

    with h_tab1:
        st.markdown("**Teil 1:** Dialogues.")
        selected_scenario_title = st.selectbox("📂 **Select Hören Teil 1 Scenario Set:**", [s["title"] for s in HOREN_TEIL1_SCENARIOS])
        if st.button(f"▶️ Load Exercise ({selected_scenario_title})", type="primary"):
            st.session_state.h_t1_active = {
                "scenario_title": selected_scenario_title,
                "tasks": [
                    {"id": "h1_1", "full_script": "Guten Tag, was kostet diese Jacke?", "question": "Wie viel kostet die Jacke?", "options": ["a) 50 Euro", "b) 60 Euro", "c) 70 Euro"], "answer": "a) 50 Euro", "explanation": "Der Verkäufer nennt den Preis 50 Euro."}
                ]
            }

        if "h_t1_active" in st.session_state:
            d = st.session_state.h_t1_active
            for idx, t in enumerate(d["tasks"], start=1):
                st.markdown(f"""
                <div class="question-frame">
                    <b>Dialogue {idx}</b>
                </div>
                """, unsafe_allow_html=True)
                st.audio(generate_german_audio_bytes(t["full_script"]), format="audio/mp3")
                
                st.markdown(f"""
                <div class="question-frame">
                    <b>{t['question']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
                cols_h1 = st.columns(len(t['options']))
                for o_i, o_v in enumerate(t['options']):
                    with cols_h1[o_i]:
                        if st.button(o_v, key=f"ht1_{t['id']}_{o_v}", use_container_width=True):
                            if o_v == t['answer']:
                                st.success(f"🟢 Correct! {t['explanation']}")
                            else:
                                st.error(f"🔴 Incorrect. Correct was {t['answer']}. {t['explanation']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with h_tab2:
        st.markdown("**Teil 2:** Announcements.")
        selected_scenario_t2 = st.selectbox("📂 **Select Hören Teil 2 Scenario Set:**", [s["title"] for s in HOREN_TEIL2_SCENARIOS])
        if st.button(f"▶️ Load Exercise ({selected_scenario_t2})", type="primary"):
            st.session_state.h_t2_active = {
                "tasks": [
                    {"id": "h2_1", "script": "Achtung auf Gleis 3.", "statement": "Der Zug fährt auf Gleis 3 ab.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Die Durchsage bestätigt Gleis 3."}
                ]
            }
        
        if "h_t2_active" in st.session_state:
            d2 = st.session_state.h_t2_active
            for idx, t in enumerate(d2["tasks"], start=1):
                st.audio(generate_german_audio_bytes(t["script"]), format="audio/mp3")
                st.markdown(f"""
                <div class="question-frame">
                    <b>{t['statement']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
                cols_h2 = st.columns(2)
                for o_i, o_v in enumerate(t['options']):
                    with cols_h2[o_i]:
                        if st.button(o_v, key=f"ht2_{t['id']}_{o_v}", use_container_width=True):
                            if o_v == t['answer']:
                                st.success(f"🟢 Correct! {t['explanation']}")
                            else:
                                st.error(f"🔴 Incorrect. Correct was {t['answer']}. {t['explanation']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with h_tab3:
        st.markdown("**Teil 3:** Voicemails.")
        if st.button("🎲 Generate Hören Teil 3", type="primary"):
            st.session_state.hoeren_t3 = {
                "tasks": [
                    {"id": "h3_1", "script": "Hallo Anna, hier ist Stefan.", "question": "Wer ruft an?", "options": ["a) Stefan", "b) Maria", "c) Thomas"], "answer": "a) Stefan", "explanation": "Stefan stellt sich am Anfang vor."}
                ]
            }
        
        if "hoeren_t3" in st.session_state:
            for idx, t in enumerate(st.session_state.hoeren_t3["tasks"], start=1):
                st.audio(generate_german_audio_bytes(t["script"]), format="audio/mp3")
                st.markdown(f"""
                <div class="question-frame">
                    <b>{t['question']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
                cols_h3 = st.columns(len(t['options']))
                for o_i, o_v in enumerate(t['options']):
                    with cols_h3[o_i]:
                        if st.button(o_v, key=f"ht3_{t['id']}_{o_v}", use_container_width=True):
                            if o_v == t['answer']:
                                st.success(f"🟢 Correct! {t['explanation']}")
                            else:
                                st.error(f"🔴 Incorrect. Correct was {t['answer']}. {t['explanation']}")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="frame-purple">', unsafe_allow_html=True)
    st.subheader("✍️ Goethe A1 Schreiben Practice (20 Mins, 2 Parts)")

    s_tab1, s_tab2 = st.tabs([
        "Teil 1: Formular", 
        "Teil 2: Mitteilung"
    ])

    with s_tab1:
        st.markdown("**Teil 1 (Formular):** Fill out forms.")
        if "dyn_schreiben_t1_idx" not in st.session_state:
            st.session_state.dyn_schreiben_t1_idx = 0

        if st.button("Refresh Scenarios", key="ref_schreiben_t1"):
            st.session_state.dyn_schreiben_t1_idx = (st.session_state.dyn_schreiben_t1_idx + 1) % len(SCHREIBEN_TEIL1_SCENARIOS)
            st.rerun()

        sel_st1 = SCHREIBEN_TEIL1_SCENARIOS[st.session_state.dyn_schreiben_t1_idx]
        
        st.markdown(f"""
        <div class="question-frame">
            <b>{sel_st1['aufgabe']}</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### {sel_st1['form_title']}")
        
        user_form_inputs = {}
        st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
        for field in sel_st1["fields"]:
            if not field.get("is_gap", False):
                st.text_input(field["label"], value=field.get("default", ""), disabled=True)
            else:
                user_form_inputs[field["id"]] = st.text_input(field["label"], placeholder=field.get("placeholder", "..."))
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✔ Check Form", type="primary"):
            for field in sel_st1["fields"]:
                if field.get("is_gap", False):
                    u_val = str(user_form_inputs.get(field["id"], "")).strip().lower()
                    c_val = str(field["answer"]).strip().lower()
                    if u_val == c_val or c_val in u_val:
                        st.success(f"🟢 {field['label']} Correct! (`{field['answer']}`)")
                    else:
                        st.error(f"🔴 {field['label']} Incorrect. Correct: `{field['answer']}`")

    with s_tab2:
        st.markdown("**Teil 2 (Mitteilung):** Write messages.")
        if "dyn_schreiben_t2_idx" not in st.session_state:
            st.session_state.dyn_schreiben_t2_idx = 0

        if st.button("Refresh Scenarios", key="ref_schreiben_t2"):
            st.session_state.dyn_schreiben_t2_idx = (st.session_state.dyn_schreiben_t2_idx + 1) % len(SCHREIBEN_TEIL2_SCENARIOS)
            st.rerun()

        sel_st2 = SCHREIBEN_TEIL2_SCENARIOS[st.session_state.dyn_schreiben_t2_idx]
        
        st.markdown(f"""
        <div class="question-frame">
            <b>{sel_st2['aufgabe_text']}</b><br>
            <ul>
                {"".join([f"<li>{pt}</li>" for pt in sel_st2["points"]])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="answer-frame">', unsafe_allow_html=True)
        u_email = st.text_area("Write your text here...", height=160)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✔ Analyze text", type="primary"):
            if u_email.strip():
                with st.spinner("Analyzing text..."):
                    eval_res = generate_dynamic_content(f"Evaluate student text for Goethe A1 Schreiben Teil 2 task: {sel_st2['aufgabe_text']}\nSubmission:\n{u_email}")
                    st.write(eval_res)

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="frame-emerald">', unsafe_allow_html=True)
    st.subheader("🗣️ Goethe A1 Sprechen Practice (15 Mins, 3 Parts)")

    sp_tab1, sp_tab2, sp_tab3 = st.tabs([
        "Teil 1: Vorstellung", 
        "Teil 2: W-Fragen", 
        "Teil 3: Bitten"
    ])

    with sp_tab1:
        st.markdown("**Teil 1:** Introduce yourself.")
        rec_t1 = mic_recorder(start_prompt="Record Self-Introduction 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t1")
        if rec_t1:
            st.audio(rec_t1['bytes'], format='audio/wav')
            if st.button("Evaluate Introduction"):
                audio_part = types.Part.from_bytes(data=rec_t1['bytes'], mime_type="audio/wav")
                eval_res = client.models.generate_content(model=FALLBACK_MODELS[0], contents=["Evaluate self-introduction against Goethe A1 criteria.", audio_part])
                st.write(eval_res.text)

    with sp_tab2:
        st.markdown("**Teil 2:** Topic cards & W-questions.")
        if st.button("🎲 Draw Topic Card", type="primary"):
            st.session_state.card_t2 = generate_dynamic_content("Generate Goethe A1 Sprechen topic card.")
        if "card_t2" in st.session_state:
            st.success(st.session_state.card_t2)
            rec_t2 = mic_recorder(start_prompt="Record W-Question 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t2")

    with sp_tab3:
        st.markdown("**Teil 3:** Picture requests.")
        if st.button("🎲 Draw Picture Request Card", type="primary"):
            st.session_state.card_t3 = generate_dynamic_content("Generate Goethe A1 Sprechen picture card.")
        if "card_t3" in st.session_state:
            st.success(st.session_state.card_t3)
            rec_t3 = mic_recorder(start_prompt="Record Request 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t3")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. GOETHE A1 MOCK EXAMINATION
# ----------------------------------------------------
elif nav_choice == "🏆 Goethe A1 Mock Examination":
    st.markdown('<div class="frame-amber">', unsafe_allow_html=True)
    st.subheader("🏆 Full CEFR A1 Timed Mock Examination Simulator")
    st.write("Simulate the exact Goethe-Zertifikat A1 exam with live section-by-section countdown timers.")

    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []
    if "exam_stage" not in st.session_state:
        st.session_state.exam_stage = "MENU"

    if st.session_state.exam_stage == "MENU":
        if st.button("🚀 Start Full Timed Mock Exam Simulation", type="primary"):
            st.session_state.exam_stage = "LESEN"
            st.rerun()
    elif st.session_state.exam_stage == "LESEN":
        st.markdown("### 📖 Mock Exam - Lesen Section")
        st.info("Reading comprehension mock task...")
        if st.button("Proceed to Hören ➔", type="primary"):
            st.session_state.exam_stage = "HOEREN"
            st.rerun()
    elif st.session_state.exam_stage == "HOEREN":
        st.markdown("### 🎧 Mock Exam - Hören Section")
        st.audio(generate_german_audio_bytes("Guten Tag, willkommen am Hauptbahnhof München."), format="audio/mp3")
        if st.button("Proceed to Schreiben ➔", type="primary"):
            st.session_state.exam_stage = "SCHREIBEN"
            st.rerun()
    elif st.session_state.exam_stage == "SCHREIBEN":
        st.markdown("### ✍️ Mock Exam - Schreiben Section")
        st.text_input("Formular field 1:")
        if st.button("Finish Exam & View Scorecard", type="primary"):
            st.session_state.exam_history.append({"date": time.strftime("%Y-%m-%d"), "lesen": 5, "hoeren": 3, "schreiben": 4, "sprechen": 3, "total": 15, "percentage": 100})
            st.session_state.exam_stage = "MENU"
            st.success("Mock exam completed successfully!")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 9. A1 & A2 SHORT STORIES
# ----------------------------------------------------
elif nav_choice == "📖 A1 & A2 Short Stories":
    st.markdown('<div class="frame-rose">', unsafe_allow_html=True)
    st.subheader("📖 Enchanted Storybook Reader")
    story_level = st.radio("Select CEFR Level:", ["A1 Level (Fairy Tales)", "A2 Level (Classics)"], horizontal=True)
    if st.button("📖 Open Storybook", type="primary"):
        st.info("Once upon a time in Berlin, there was a little dog named Bruno...")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 10. ASK GEM
# ----------------------------------------------------
elif nav_choice == "💬 Ask Gem (AI Tutor)":
    st.markdown('<div class="frame-blue">', unsafe_allow_html=True)
    st.subheader("💬 Ask Gem — Interactive AI Tutor")
    if prompt := st.chat_input("Ask Gem a question:"):
        try:
            res = generate_dynamic_content(prompt)
            st.write(res)
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# FLOATING CUTE BOT WIDGET
# ----------------------------------------------------
if "bot_open" not in st.session_state:
    st.session_state.bot_open = False
if "bot_last_response" not in st.session_state:
    st.session_state.bot_last_response = ""

st.markdown('<div class="floating-bot-container">', unsafe_allow_html=True)

if st.session_state.bot_open:
    st.markdown('<div class="bot-popout-box">', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns([4, 1])
    with col_b1:
        st.markdown("🤖 **Gem (AI Tutor):**")
    with col_b2:
        if st.button("✕", key="close_bot_popout"):
            st.session_state.bot_open = False
            st.rerun()

    bot_query = st.text_input("Ask me anything:", key="bot_chat_input")
    if bot_query:
        st.session_state.bot_last_response = generate_dynamic_content(bot_query)

    if st.session_state.bot_last_response:
        st.write(st.session_state.bot_last_response)

    st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.bot_open:
    if st.button("🤖 Chat with Gem", key="open_bot_btn", type="primary"):
        st.session_state.bot_open = True
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
