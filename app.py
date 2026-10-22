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

# Custom Styling: Storybook aesthetics, mobile side-by-side layout, compact direct audio, bot chat input UI
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
    .main-card { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .accent-card { background: #ffffff; border-radius: 16px; padding: 24px; border-left: 6px solid #2563eb; box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    
    /* Increase Sidebar Navigation Font Size & Spacing */
    [data-testid="stSidebarNav"] span, .stRadio label {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }
    
    /* Interactive Flashcard UI */
    .flashcard-front-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
        border: 2px solid #38bdf8;
        margin-bottom: 15px;
    }
    .flashcard-word-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #38bdf8;
        margin-bottom: 10px;
    }
    .flashcard-back-box {
        background: #ffffff;
        border: 2px solid #2563eb;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.12);
        margin-bottom: 15px;
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
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 2px solid #2563eb;
        width: 340px;
        margin-bottom: 12px;
    }

    /* Metric Font Uniformity */
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Secure API Key Retrieval
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("🔑 Missing Gemini API Key! Please configure your secret key in Streamlit settings.")
    st.stop()

client = genai.Client(api_key=api_key.strip())

FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

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
                if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota"]):
                    time.sleep(1)
                    continue
                raise e
        time.sleep(1.5)
            
    raise Exception(f"All free model quotas are currently exhausted or experiencing high demand. Details: {str(last_error)}")

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
                if any(k in err_str for k in ["429", "503", "resource_exhausted", "unavailable", "quota"]):
                    time.sleep(1)
                    continue
                raise e
        time.sleep(1.5)
            
    raise Exception(f"All free model quotas are currently exhausted or experiencing high demand. Details: {str(last_error)}")

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
    {
        "title": "Jacke, Kino & Apotheke",
        "desc": "Short everyday dialogues about a jacket's price, the film start and directions to the pharmacy – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Zug nach Köln, Markt & Hotel",
        "desc": "Short everyday dialogues about the train to Köln, the market, weather and a hotel room – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Gäste, Supermarkt & Urlaub",
        "desc": "Short everyday dialogues about guests, holidays, Frau Roth's hobby and lost glasses – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Frühstück, Friseur & neue Adresse",
        "desc": "Short everyday dialogues about a hairdresser's appointment, breakfast prices and the Nowak family's new address – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Tomaten, Kleidergröße & neue Kollegin",
        "desc": "Short everyday dialogues about tomato prices, clothing size and a new colleague – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Bäckerei, Restaurant & Schulbeginn",
        "desc": "Short everyday dialogues about a bakery, a restaurant order and the start of school – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Zoo-Ticket, Flug & ICE nach München",
        "desc": "Short everyday dialogues about a child's ticket, a flight to Berlin and the ICE to München – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Monatskarte, Elektriker & Deutschkurs",
        "desc": "Short everyday dialogues about a monthly pass, an electrician's appointment and the location of a German course – 6 tasks, a/b/c (played twice)."
    },
    {
        "title": "Kaffee, Dr. Helds Urlaub & Messe",
        "desc": "Short everyday dialogues about coffee, Dr. Held's holiday and travelling to the trade fair – 6 tasks, a/b/c (played twice)."
    }
]

# Hören Teil 2 Official Scenarios Bank
HOREN_TEIL2_SCENARIOS = [
    {
        "title": "Markt-, Bahn- & Flughafendurchsagen",
        "desc": "Short announcements at a market, railway station and airport – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Kaufhaus-, Bahn- & Schwimmbaddurchsagen",
        "desc": "Announcements from a department store, train, swimming pool and airport – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Bibliothek, Café & Sommerfest",
        "desc": "Announcements from a library, train restaurant, parking garage and summer festival – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Restaurant-, Bahn- & Flugdurchsagen",
        "desc": "Announcements from a restaurant, train, airplane and cinema – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Bahnhof, Kasse, Museum & Konzert",
        "desc": "Announcements from a train station, checkout, museum and concert – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Fähre, Schule, Bahn & Autobahn",
        "desc": "Announcements about a ferry, missing child, train and A3 motorway – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Pinguinfütterung, Zug & Geschäft",
        "desc": "Announcements about penguin feeding, a train, shop and airport – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Museum, Zug, Bäckerei & Schwimmbad",
        "desc": "Announcements from a museum, train, bakery and swimming pool – 4 tasks, Richtig/Falsch (played once)."
    },
    {
        "title": "Geschäft, Zug, Messe & Bus",
        "desc": "Announcements from a shop, train, trade fair and bus – 4 tasks, Richtig/Falsch (played once)."
    }
]

# Lesen Teil 1 Official Scenarios Bank (All 9 exact scenarios)
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
    },
    {
        "title": "Umzugshilfe & Katze im Garten",
        "desc": "Two short notices about moving help and a found cat — 5 tasks, Richtig/Falsch.",
        "text1_label": "Zettel am Schwarzen Brett",
        "text1": "Hallo liebe Nachbarn, ich ziehe am 1. September in eine neue Wohnung und suche Helfer für Möbeltragen. Es gibt Pizza und Getränke für alle!",
        "text2_label": "Nachricht",
        "text2": "Guten Tag, wir haben seit gestern eine kleine graue Katze im Garten. Sie hat ein rotes Halsband. Wem gehört sie? Bitte melden unter Tel. 0171...",
        "questions": [
            {"id": "lt1_61", "statement": "Der Autor zieht im August um.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Der Umzug ist am 1. September."},
            {"id": "lt1_62", "statement": "Helfer bekommen Pizza und Getränke.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Es gibt Pizza und Getränke für alle."},
            {"id": "lt1_63", "statement": "Die gefundene Katze ist schwarz.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Die Katze ist grau."},
            {"id": "lt1_64", "statement": "Die Katze trägt ein rotes Halsband.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Text steht: 'Sie hat ein rotes Halsband.'"},
            {"id": "lt1_65", "statement": "Man kann den Finder telefonisch erreichen.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Es ist eine Telefonnummer angegeben."}
        ]
    },
    {
        "title": "Wochenendbesuch & Hochzeitseinladung",
        "desc": "Two short messages: a sister's weekend visit and a wedding invitation — 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail von der Schwester",
        "text1": "Liebe Sandra,\nich komme diesen Samstag mit dem Zug um 10 Uhr an. Holst du mich am Bahnhof ab? Wir können dann zusammen auf den Markt gehen.\nDein Bruder Lukas",
        "text2_label": "Hochzeitskarte",
        "text2": "Liebe Freunde, wir heiraten am 20. August um 14 Uhr in der Stadtkirche. Danach feiern wir im Restaurant 'Zur Linde'. Bitte gebt uns bis zum 1. August Bescheid.",
        "questions": [
            {"id": "lt1_81", "statement": "Lukas kommt am Samstag mit dem Zug an.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Lukas schreibt, dass er diesen Samstag mit dem Zug ankommt."},
            {"id": "lt1_82", "statement": "Lukas kommt um 12 Uhr an.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Er kommt um 10 Uhr an."},
            {"id": "lt1_83", "statement": "Die Hochzeit findet in einer Kirche statt.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "In der Karte steht: '...in der Stadtkirche.'"},
            {"id": "lt1_84", "statement": "Die Feier ist im Restaurant 'Zur Linde'.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Danach feiern wir im Restaurant 'Zur Linde'."},
            {"id": "lt1_85", "statement": "Man muss bis zum 15. August Bescheid geben.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Man muss bis zum *1. August* Bescheid geben."}
        ]
    },
    {
        "title": "Computerkurs & Zoobesuch",
        "desc": "Two short messages: a computer course and a class trip to the zoo — 5 tasks, Richtig/Falsch.",
        "text1_label": "Kursinformation",
        "text1": "Volkshochschule: Der Computerkurs für Senioren beginnt am Montag, den 5. Oktober, um 10 Uhr im Raum 204. Bitte bringen Sie einen eigenen Laptop mit.",
        "text2_label": "Elternbrief",
        "text2": "Liebe Eltern, am Freitag machen wir mit der Klasse einen Ausflug in den Zoo. Die Kinder brauchen kein Klassenzimmer-Material, aber Regenkleidung und Brotzeit.",
        "questions": [
            {"id": "lt1_101", "statement": "Der Computerkurs ist für Senioren.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Es ist ein Computerkurs für Senioren."},
            {"id": "lt1_102", "statement": "Der Kurs findet in Raum 101 statt.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Er findet in Raum *204* statt."},
            {"id": "lt1_103", "statement": "Man soll einen Laptop mitbringen.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Bitte bringen Sie einen eigenen Laptop mit."},
            {"id": "lt1_104", "statement": "Der Schulausflug geht in den Zoo.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Ausflug in den Zoo."},
            {"id": "lt1_105", "statement": "Die Kinder müssen Regenkleidung mitnehmen.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Regenkleidung und Brotzeit sind erforderlich."}
        ]
    },
    {
        "title": "Geburtstagsparty & Sommerfest",
        "desc": "Two short notices about a birthday party and a summer festival — 5 tasks, Richtig/Falsch.",
        "text1_label": "Einladung",
        "text1": "Hallo Tina, ich feiere am Freitag meinen Geburtstag ab 19:30 Uhr bei mir zu Hause. Bring bitte gute Laune und Musik mit!",
        "text2_label": "Aushang",
        "text2": "Sommerfest im Stadtpark am Samstag von 12 bis 18 Uhr. Es gibt Live-Musik, Grillwurst und Kuchen für alle Besucher. Eintritt frei!",
        "questions": [
            {"id": "lt1_121", "statement": "Tina feiert ihren Geburtstag.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Absender feiert Geburtstag."},
            {"id": "lt1_122", "statement": "Die Party beginnt um 19:30 Uhr.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Ab 19:30 Uhr bei mir zu Hause."},
            {"id": "lt1_123", "statement": "Das Sommerfest ist im Stadtpark.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Sommerfest im Stadtpark."},
            {"id": "lt1_124", "statement": "Das Sommerfest kostet Eintritt.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Auf dem Aushang steht: 'Eintritt frei!'"},
            {"id": "lt1_125", "statement": "Es gibt Grillwurst und Kuchen.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Grillwurst und Kuchen sind vorhanden."}
        ]
    },
    {
        "title": "Blumen gießen & Auto abholen",
        "desc": "Two short notices about watering flowers and a repaired car — 5 tasks, Richtig/Falsch.",
        "text1_label": "Zettel",
        "text1": "Liebe Nachbarin, ich bin im Urlaub. Kannst du bitte jede Woche meine Blumen auf dem Balkon gießen? Der Schlüssel liegt unter der Fußmatte. Danke!",
        "text2_label": "Werkstatt-SMS",
        "text2": "Guten Tag, Ihr Auto ist fertig repariert und kann heute bis 18 Uhr in der Werkstatt abgeholt werden. Kostenpunkt: 150 Euro.",
        "questions": [
            {"id": "lt1_141", "statement": "Die Nachbarin ist im Urlaub.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Der Absender der Notiz ist im Urlaub; die Nachbarin soll gießen."},
            {"id": "lt1_142", "statement": "Der Schlüssel liegt unter der Fußmatte.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Schlüssel liegt unter der Fußmatte."},
            {"id": "lt1_143", "statement": "Das Auto ist repariert.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Ihr Auto ist fertig repariert."},
            {"id": "lt1_144", "statement": "Man kann das Auto nach 20 Uhr abholen.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Abholung heute *bis 18 Uhr*."},
            {"id": "lt1_145", "statement": "Die Reparatur kostet 150 Euro.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Kostenpunkt: 150 Euro."}
        ]
    },
    {
        "title": "Arzttermin & Blumen pflanzen",
        "desc": "Two short notices about a doctor's appointment and planting flowers in a community garden — 5 tasks, Richtig/Falsch.",
        "text1_label": "Praxis-Notiz",
        "text1": "Erinnerung an Ihren Termin bei Dr. Klein am Donnerstag um 11:15 Uhr. Bitte bringen Sie Ihre Versichertenkarte mit.",
        "text2_label": "Garten-Aufruf",
        "text2": "Liebe Nachbarn, wir treffen uns am Samstag um 10 Uhr im Gemeinschaftsgarten, um neue Blumen zu pflanzen. Wer Schaufeln hat, bitte mitbringen!",
        "questions": [
            {"id": "lt1_161", "statement": "Der Arzttermin ist am Donnerstag.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Termin am Donnerstag."},
            {"id": "lt1_162", "statement": "Der Termin ist um 10 Uhr.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Der Termin ist um 11:15 Uhr."},
            {"id": "lt1_163", "statement": "Man soll die Versichertenkarte mitbringen.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Bitte bringen Sie Ihre Versichertenkarte mit."},
            {"id": "lt1_164", "statement": "Das Treffen im Gemeinschaftsgarten ist am Samstag.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Samstag um 10 Uhr."},
            {"id": "lt1_165", "statement": "Man soll Schaufeln mitbringen, wenn man welche hat.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Wer Schaufeln hat, bitte mitbringen!"}
        ]
    }
]

# Lesen Teil 2 Official Scenarios Bank (All 9 exact scenarios)
LESEN_TEIL2_SCENARIOS = [
    {
        "title": "Fahrrad, Schwimmbad & Pizza",
        "desc": "Information about buying a bicycle, swimming pools, paediatricians and ordering pizza — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_t1",
                "situation": "6. Sie möchten ein gebrauchtes Fahrrad kaufen.",
                "site_a_url": "www.fahrrad-neu.de",
                "site_a": "Neue Fahrräder und E-Bikes\nNur Neuware vom Fachhändler\n• Modelle • Preise • Service",
                "site_b_url": "www.radmarkt-leipzig.de",
                "site_b": "Radmarkt Leipzig\nGebrauchte Fahrräder günstig kaufen und verkaufen\n• Angebote • Kontakt",
                "answer": "Website B",
                "explanation": "Sie suchen ein *gebrauchtes* Fahrrad. Website B bietet gebrauchte Fahrräder an."
            },
            {
                "id": "lt2_t2",
                "situation": "7. Sie möchten am Wochenende ins Schwimmbad gehen.",
                "site_a_url": "www.stadtbad-erfurt.de",
                "site_a": "Stadtbad Erfurt\nHallenbad mit Sauna\nÖffnungszeiten und Preise\nAuch am Wochenende geöffnet!",
                "site_b_url": "www.schwimmverein-erfurt.de",
                "site_b": "Schwimmverein Erfurt\nSchwimmkurse und Training nur für Mitglieder",
                "answer": "Website A",
                "explanation": "Website A ist ein öffentliches Bad mit Wochenendöffnung, während Website B nur für Mitglieder ist."
            },
            {
                "id": "lt2_t3",
                "situation": "8. Sie möchten online Pizza bestellen und nach Hause liefern lassen.",
                "site_a_url": "www.pizzeria-napoli.de",
                "site_a": "Pizzeria Napoli\nItalienische Spezialitäten\nLieferdienst direkt zu Ihnen nach Hause innerhalb von 30 Minuten!",
                "site_b_url": "www.kochkurs-italienisch.de",
                "site_b": "Italienisch kochen lernen\nKochkurse für Anfänger und Fortgeschrittene",
                "answer": "Website A",
                "explanation": "Pizzeria Napoli bietet einen Lieferdienst nach Hause an."
            },
            {
                "id": "lt2_t4",
                "situation": "9. Sie suchen einen Deutschkurs für den Abend.",
                "site_a_url": "www.vhs-berlin.de",
                "site_a": "Volkshochschule Berlin\nAbendkurse Deutsch für Anfänger (A1-B2)",
                "site_b_url": "www.sommer-kinder-sprache.de",
                "site_b": "Sprachreisen für Kinder im Sommer",
                "answer": "Website A",
                "explanation": "Die Volkshochschule bietet Abendkurse an."
            },
            {
                "id": "lt2_t5",
                "situation": "10. Ihr Smartphone ist kaputt und Sie brauchen eine schnelle Reparatur.",
                "site_a_url": "www.handy-doc-muenchen.de",
                "site_a": "Handy Doc München\nSofort-Reparatur von Displays und Akkus ohne Termin!",
                "site_b_url": "www.telefon-anbieter-vertrag.de",
                "site_b": "Neukunden Angebote und Handytarife",
                "answer": "Website A",
                "explanation": "Handy Doc bietet Sofort-Reparaturen an."
            }
        ]
    },
    {
        "title": "Hotel, Werkstatt & Babysitter",
        "desc": "Information about hotel bookings, repair shops, train connections, cakes and babysitters — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_21",
                "situation": "6. Sie suchen ein ruhiges Hotel am Meer für Ihren Urlaub.",
                "site_a_url": "www.hotel-Seeblick-ostsee.de",
                "site_a": "Hotel Seeblick\nDirekt am Strand, ruhige Zimmer mit Meerblick und Frühstück.",
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
            },
            {
                "id": "lt2_23",
                "situation": "8. Sie brauchen jemanden, der abends auf Ihr Kind aufpasst.",
                "site_a_url": "www.jugendherberge.de",
                "site_a": "Jugendherbergen in Deutschland\nGünstige Übernachtungen für Gruppen.",
                "site_b_url": "www.tagesmuetter-vermittlung.de",
                "site_b": "Tagesmütter und Babysitter Vermittlung für den Abend.",
                "answer": "Website B",
                "explanation": "Babysitter Vermittlung ist für die Kinderbetreuung am Abend zuständig."
            },
            {
                "id": "lt2_24",
                "situation": "9. Sie möchten einen Flug nach Madrid buchen.",
                "site_a_url": "www.flughafen-tickets-direkt.de",
                "site_a": "Flugverbindungen weltweit günstig buchen.",
                "site_b_url": "www.db-bahn.de",
                "site_b": "Deutsche Bahn - Züge in Deutschland.",
                "answer": "Website A",
                "explanation": "Flugverbindungen sind für Flüge nach Madrid."
            },
            {
                "id": "lt2_25",
                "situation": "10. Sie möchten ein Paket nach Italien schicken.",
                "site_a_url": "www.schnell-paketdienst.de",
                "site_a": "Internationaler Paketversand nach Europa.",
                "site_b_url": "www.buecherei-stadt.de",
                "site_b": "Stadtbibliothek - Bücher ausleihen.",
                "answer": "Website A",
                "explanation": "Paketdienst ist für den Versand von Paketen zuständig."
            }
        ]
    },
    {
        "title": "Flohmarkt, Kellnerjob & Zahnarzt",
        "desc": "Information about used furniture, bike trips, waiter jobs, swimming lessons and dentist appointments — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_31",
                "situation": "6. Sie möchten alte Möbel günstig kaufen.",
                "site_a_url": "www.flohmarkt-koeln.de",
                "site_a": "Flohmarkt & Trödelmarkt Köln\nMöbel, Kleidung und Antiquitäten von privat.",
                "site_b_url": "www.moebelhaus-luxus.de",
                "site_b": "Möbelhaus Luxus\nExklusive Designermöbel direkt vom Hersteller.",
                "answer": "Website A",
                "explanation": "Flohmarkt bietet günstige gebrauchte Möbel von privat an."
            },
            {
                "id": "lt2_32",
                "situation": "7. Sie suchen einen Nebenjob als Kellner am Wochenende.",
                "site_a_url": "www.gastronomie-jobs-muenchen.de",
                "site_a": "Gastronomie Jobs München\nWir suchen Servicekräfte und Kellner für Cafés und Restaurants.",
                "site_b_url": "www.buero-arbeit-start.de",
                "site_b": "Büroarbeit Start\nVollzeit Jobs in der Buchhaltung.",
                "answer": "Website A",
                "explanation": "Gastronomie Jobs bietet Stellen als Kellner an."
            },
            {
                "id": "lt2_33",
                "situation": "8. Sie haben Zahnschmerzen und brauchen dringend einen Termin.",
                "site_a_url": "www.zahnarzt-dr-schmidt.de",
                "site_a": "Zahnarztpraxis Dr. Schmidt\nSchmerzsprechstunde täglich ohne Anmeldung.",
                "site_b_url": "www.augenarzt-zentrum.de",
                "site_b": "Augenarzt Zentrum\nSehtests und Brillenberatung.",
                "answer": "Website A",
                "explanation": "Zahnarztpraxis bietet Schmerzsprechstunde an."
            },
            {
                "id": "lt2_34",
                "situation": "9. Ihr Kind möchte schwimmen lernen.",
                "site_a_url": "www.schwimmschule-seestern.de",
                "site_a": "Schwimmschule Seestern\nSchwimmkurse für Anfänger und Kinder.",
                "site_b_url": "www.fussball-verein-jugend.de",
                "site_b": "Fußball Jugendtraining am Nachmittag.",
                "answer": "Website A",
                "explanation": "Schwimmschule bietet Schwimmkurse für Kinder."
            },
            {
                "id": "lt2_35",
                "situation": "10. Sie möchten eine organisierte Radtour durch die Alpen machen.",
                "site_a_url": "www.alpen-radreisen.de",
                "site_a": "Alpen Radreisen\nGeführte Fahrradtouren mit Gepäcktransport.",
                "site_b_url": "www.stadtauto-mieten.de",
                "site_b": "Autoverleih für Stadtfahrten.",
                "answer": "Website A",
                "explanation": "Alpen Radreisen bietet geführte Radtouren an."
            }
        ]
    },
    {
        "title": "Deutschkurs, Fahrrad & Taxi",
        "desc": "Information about German courses, train timetables, used bicycles, night taxis and school closures — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_41",
                "situation": "6. Sie suchen einen Intensiv-Deutschkurs am Vormittag.",
                "site_a_url": "www.sprache-zentrum-hamburg.de",
                "site_a": "Sprachzentrum Hamburg\nIntensivkurse Deutsch von 9 bis 12 Uhr.",
                "site_b_url": "www.englisch-fuer-kinder.de",
                "site_b": "Englischkurse für Vorschulkinder.",
                "answer": "Website A",
                "explanation": "Sprachzentrum Hamburg bietet Vormittags-Intensivkurse an."
            },
            {
                "id": "lt2_42",
                "situation": "7. Sie brauchen nachts um 3 Uhr ein Taxi zum Flughafen.",
                "site_a_url": "www.city-taxi-ruf.de",
                "site_a": "City Taxi Ruf\n24-Stunden Fahrdienst und Flughafentransfer.",
                "site_b_url": "www.stadtbus-fahrplan.de",
                "site_b": "Stadtbus\nLinienverkehr von 6 bis 23 Uhr.",
                "answer": "Website A",
                "explanation": "City Taxi Ruf bietet einen 24-Stunden-Dienst an."
            },
            {
                "id": "lt2_43",
                "situation": "8. Sie möchten wissen, wann der nächste Zug nach Frankfurt fährt.",
                "site_a_url": "www.deutsche-bahn-auskunft.de",
                "site_a": "Deutsche Bahn\nFahrplanauskunft und Ticketkauf für alle Züge.",
                "site_b_url": "www.autobahn-info.de",
                "site_b": "Verkehrsmeldungen für Autofahrer.",
                "answer": "Website A",
                "explanation": "Deutsche Bahn bietet Fahrplanauskünfte."
            },
            {
                "id": "lt2_44",
                "situation": "9. Ihre Schule bleibt wegen starkem Schneefall geschlossen. Wo finden Sie aktuelle Infos?",
                "site_a_url": "www.schulministerium-aktuell.de",
                "site_a": "Schulministerium\nAktuelle Meldungen bei Unwetter und Schulausfall.",
                "site_b_url": "www.wetter-profi.de",
                "site_b": "Wettervorhersage für die Region.",
                "answer": "Website A",
                "explanation": "Schulministerium informiert über Schulausfälle."
            },
            {
                "id": "lt2_45",
                "situation": "10. Sie wollen Ihr altes Fahrrad reparieren lassen und suchen Ersatzteile.",
                "site_a_url": "www.fahrrad-teile-shop.de",
                "site_a": "Fahrrad Teile Shop\nErsatzteile, Reifen und Werkzeug für alle Marken.",
                "site_b_url": "www.computer-reparatur.de",
                "site_b": "PC und Laptop Service.",
                "answer": "Website A",
                "explanation": "Fahrrad Teile Shop bietet Fahrradersatzteile."
            }
        ]
    },
    {
        "title": "Pizza, Handy & Fitnessstudio",
        "desc": "Information about ordering pizza, phone repairs, gyms, used laptops and vegetarian restaurants — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_51",
                "situation": "6. Sie möchten im Fitnessstudio trainieren und Muskeln aufbauen.",
                "site_a_url": "www.fit-und-aktiv-studio.de",
                "site_a": "Fit & Aktiv\nKrafttraining, Gerätepark und professionelle Betreuung.",
                "site_b_url": "www.schach-club-online.de",
                "site_b": "Schachclub\nDenksport und Turniere.",
                "answer": "Website A",
                "explanation": "Fit & Aktiv bietet Krafttraining und Geräte."
            },
            {
                "id": "lt2_52",
                "situation": "7. Ihr Laptop ist kaputt und Sie suchen einen günstigen gebrauchten Computer.",
                "site_a_url": "www.refurbished-laptops-berlin.de",
                "site_a": "Gebrauchte Laptops und PCs mit Garantie zum kleinen Preis.",
                "site_b_url": "www.neuheiten-elektronik.de",
                "site_b": "Nur Neugeräte der neuesten Generation.",
                "answer": "Website A",
                "explanation": "Website A bietet gebrauchte Laptops an."
            },
            {
                "id": "lt2_53",
                "situation": "8. Sie ernähren sich vegan und suchen ein Restaurant mit rein pflanzlicher Speisekarte.",
                "site_a_url": "www.vegan-oase-stuttgart.de",
                "site_a": "Vegan Oase\n100% pflanzliche Gerichte ohne tierische Produkte.",
                "site_b_url": "www.steakhouse-classic.de",
                "site_b": "Steakhouse Classic\nFleischspezialitäten vom Grill.",
                "answer": "Website A",
                "explanation": "Vegan Oase bietet rein pflanzliche Gerichte."
            },
            {
                "id": "lt2_54",
                "situation": "9. Sie möchten nachts Essen bestellen.",
                "site_a_url": "www.nacht-lieferdienst.de",
                "site_a": "Nacht Express\nWarme Pizza und Getränke bis 3 Uhr nachts geliefert.",
                "site_b_url": "www.bio-supermarkt.de",
                "site_b": "Bio Lebensmittel von 8 bis 20 Uhr.",
                "answer": "Website A",
                "explanation": "Nacht Express liefert nachts Essen."
            },
            {
                "id": "lt2_55",
                "situation": "10. Das Display Ihres Smartphones ist zersprungen.",
                "site_a_url": "www.smartphone-express-reparatur.de",
                "site_a": "Express Reparatur für Displays innerhalb einer Stunde.",
                "site_b_url": "www.handy-verleih.de",
                "site_b": "Handys mieten fürstliche Events.",
                "answer": "Website A",
                "explanation": "Express Reparatur repariert Displays."
            }
        ]
    },
    {
        "title": "Wohnung, Tierarzt & Umzugsfirma",
        "desc": "Information about apartments, vets, furniture, moving companies, used furniture and cat care — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_61",
                "situation": "6. Sie suchen eine 3-Zimmer-Wohnung zur Miete in der Innenstadt.",
                "site_a_url": "www.immo-zentral.de",
                "site_a": "Immo Zentral\nGroße Auswahl an Mietwohnungen in Stadtlage.",
                "site_b_url": "www.ferienhaus-vermietung.de",
                "site_b": "Ferienhäuser am See für den Urlaub.",
                "answer": "Website A",
                "explanation": "Immo Zentral bietet Mietwohnungen an."
            },
            {
                "id": "lt2_62",
                "situation": "7. Ihre Katze ist krank und braucht einen Tierarzt.",
                "site_a_url": "www.tierarztpraxis-paws.de",
                "site_a": "Tierarztpraxis Paws\nBehandlung von Katzen, Hunden und Kleintieren.",
                "site_b_url": "www.tiermarkt-kleinanzeigen.de",
                "site_b": "Haustiere kaufen und verkaufen.",
                "answer": "Website A",
                "explanation": "Tierarztpraxis behandelt kranke Tiere."
            },
            {
                "id": "lt2_63",
                "situation": "8. Sie ziehen nächste Woche um und brauchen professionelle Möbelpacker.",
                "site_a_url": "www.umzugsprofi-express.de",
                "site_a": "Umzugsprofi Express\nZuverlässiger Transport und Möbelmontage.",
                "site_b_url": "www.karton-verkauf.de",
                "site_b": "Nur Verkauf von Verpackungsmaterial.",
                "answer": "Website A",
                "explanation": "Umzugsprofi bietet Transport und Packer an."
            },
            {
                "id": "lt2_64",
                "situation": "9. Sie fliegen in den Urlaub und brauchen eine Pension für Ihren Hund.",
                "site_a_url": "www.hunde-ferienheim.de",
                "site_a": "Hunde Ferienheim\nLiebevolle Betreuung mit Auslauf für Hunde während Ihrer Abwesenheit.",
                "site_b_url": "www.hundeschule-anfaenger.de",
                "site_b": "Erziehungskurse für Welpen.",
                "answer": "Website A",
                "explanation": "Hunde Ferienheim betreut Hunde im Urlaub."
            },
            {
                "id": "lt2_65",
                "situation": "10. Sie suchen einen Schreiner für maßgefertigte Regale.",
                "site_a_url": "www.schreinerei-meier.de",
                "site_a": "Schreinerei Meier\nIndividueller Möbelbau und Holzarbeiten nach Maß.",
                "site_b_url": "www.baumarkt-zentrale.de",
                "site_b": "Baumarkt für Heimwerker.",
                "answer": "Website A",
                "explanation": "Schreinerei Meier baut Möbel nach Maß."
            }
        ]
    },
    {
        "title": "Konzert, Kino & Tanzschule",
        "desc": "Websites with information about concert tickets, cinema times, clothing, restaurant reservations and dance courses — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_71",
                "situation": "6. Sie möchten Karten für ein Rockkonzert am Wochenende kaufen.",
                "site_a_url": "www.ticket-express-konzerte.de",
                "site_a": "Ticket Express\nKartenverkauf für Konzerte, Festivals und Shows.",
                "site_b_url": "www.museums-pass.de",
                "site_b": "Eintrittskarten für Museen.",
                "answer": "Website A",
                "explanation": "Ticket Express verkauft Konzertkarten."
            },
            {
                "id": "lt2_72",
                "situation": "7. Sie wollen wissen, wann heute Abend der neue Actionfilm im Kino läuft.",
                "site_a_url": "www.kino-palast-heute.de",
                "site_a": "Kino Palast\nAktuelles Filmprogramm und Spielzeiten für heute.",
                "site_b_url": "www.theater-spielplan.de",
                "site_b": "Theateraufführungen und Opern.",
                "answer": "Website A",
                "explanation": "Kino Palast zeigt die Filmspielzeiten."
            },
            {
                "id": "lt2_73",
                "situation": "8. Sie möchten Salsa tanzen lernen und suchen einen Tanzkurs.",
                "site_a_url": "www.tanzschule-ritmo.de",
                "site_a": "Tanzschule Ritmo\nSalsa, Bachata und Standardtänze für Paare und Singles.",
                "site_b_url": "www.sport-akademie.de",
                "site_b": "Fitness und Gymnastik.",
                "answer": "Website A",
                "explanation": "Tanzschule Ritmo bietet Tanzkurse an."
            },
            {
                "id": "lt2_74",
                "situation": "9. Sie möchten einen Tisch für vier Personen in einem italienischen Restaurant reservieren.",
                "site_a_url": "www.restaurant-reservierung-online.de",
                "site_a": "Tischreservierung für Restaurants in Ihrer Stadt.",
                "site_b_url": "www.lieferdienst-direkt.de",
                "site_b": "Essen nach Hause liefern lassen.",
                "answer": "Website A",
                "explanation": "Restaurant Reservierung bietet Online-Tischreservierung."
            },
            {
                "id": "lt2_75",
                "situation": "10. Sie suchen elegante Abendkleidung für einen festlichen Ball.",
                "site_a_url": "www.modehaus-elegance.de",
                "site_a": "Modehaus Elegance\nAbendkleider, Anzüge und festliche Mode.",
                "site_b_url": "www.sport-kleidung.de",
                "site_b": "Funktionskleidung zum Wandern.",
                "answer": "Website A",
                "explanation": "Modehaus Elegance bietet festliche Abendkleidung."
            }
        ]
    },
    {
        "title": "Hotel, Flug & Paket",
        "desc": "Websites with information about seaside hotels, flights, car repair shops, banks, used cars and parcels — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_81",
                "situation": "6. Sie möchten einen günstigen Flug nach Mallorca buchen.",
                "site_a_url": "www.flug-suche-billig.de",
                "site_a": "Flug Suche\nWeltweite Flüge zum Bestpreis vergleichen und buchen.",
                "site_b_url": "www.schiffsreise-buero.de",
                "site_b": "Kreuzfahrten auf dem Ozean.",
                "answer": "Website A",
                "explanation": "Flug Suche vergleicht und bucht Flüge."
            },
            {
                "id": "lt2_82",
                "situation": "7. Sie möchten ein Konto bei einer Bank mit kostenloser Kontoführung eröffnen.",
                "site_a_url": "www.direkt-bank-online.de",
                "site_a": "Direkt Bank\nKostenloses Girokonto und Online-Banking.",
                "site_b_url": "www.spar-kasse-immobilien.de",
                "site_b": "Immobilienfinanzierung.",
                "answer": "Website A",
                "explanation": "Direkt Bank bietet kostenlose Girokonten."
            },
            {
                "id": "lt2_83",
                "situation": "8. Sie möchten ein großes Paket sicher ins Ausland schicken.",
                "site_a_url": "www.global-paket-express.de",
                "site_a": "Global Paket Express\nInternationaler Versand und Sendungsverfolgung.",
                "site_b_url": "www.brief-marken-sammler.de",
                "site_b": "Sammeln von historischen Briefmarken.",
                "answer": "Website A",
                "explanation": "Global Paket Express bietet internationalen Versand."
            },
            {
                "id": "lt2_84",
                "situation": "9. Sie suchen einen Gebrauchtwagen mit TÜV.",
                "site_a_url": "www.auto-markt-gebraucht.de",
                "site_a": "Auto Markt\nGebrauchtwagen mit neuem TÜV und Garantie.",
                "site_b_url": "www.neu-wagen-konfigurator.de",
                "site_b": "Neuwagen nach Wunsch zusammenstellen.",
                "answer": "Website A",
                "explanation": "Auto Markt bietet Gebrauchtwagen mit TÜV."
            },
            {
                "id": "lt2_85",
                "situation": "10. Ihr Auspuff ist kaputt und Sie brauchen eine Kfz-Werkstatt.",
                "site_a_url": "www.kfz-meister-werkstatt.de",
                "site_a": "Kfz Werkstatt\nReparatur von Auspuff, Reifen und Motoren.",
                "site_b_url": "www.auto-waschanlage-express.de",
                "site_b": "Nur Außenwäsche und Innenreinigung.",
                "answer": "Website A",
                "explanation": "Kfz Werkstatt repariert Auspuff und Motoren."
            }
        ]
    },
    {
        "title": "Arzt, Apotheke & Bibliothek",
        "desc": "Websites with information about doctors, emergency pharmacies, garden plants, dentist appointments, books and gardening tools — 5 tasks, a/b.",
        "tasks": [
            {
                "id": "lt2_91",
                "situation": "6. Sie suchen ein Buch von einem bekannten Autor zum Ausleihen.",
                "site_a_url": "www.stadt-buecherei-online.de",
                "site_a": "Stadtbücherei\nGroße Auswahl an Romanen, Sachbüchern und Medien.",
                "site_b_url": "www.buch-handlung-kauf.de",
                "site_b": "Bücher kaufen und bestellen.",
                "answer": "Website A",
                "explanation": "Stadtbücherei leiht Bücher aus."
            },
            {
                "id": "lt2_92",
                "situation": "7. Es ist Sonntagabend und Sie brauchen dringend ein bestimmtes Medikament.",
                "site_a_url": "www.apotheken-notdienst-heute.de",
                "site_a": "Notdienst Apotheke\nWelche Apotheke hat heute Nacht und am Sonntag geöffnet?",
                "site_b_url": "www.drogerie-markt-aktuell.de",
                "site_b": "Kosmetik und Drogerieartikel zu normalen Öffnungszeiten.",
                "answer": "Website A",
                "explanation": "Notdienst Apotheke zeigt geöffnete Notdienst-Apotheken."
            },
            {
                "id": "lt2_93",
                "situation": "8. Sie möchten neue Blumen für Ihren Balkon kaufen.",
                "site_a_url": "www.gärtnerei-grün-daumen.de",
                "site_a": "Gärtnerei Grün Daumen\nBlumen, Balkonpflanzen und Gartenerde.",
                "site_b_url": "www.möbel-garten-deko.de",
                "site_b": "Gartenmöbel aus Holz und Kunststoff.",
                "answer": "Website A",
                "explanation": "Gärtnerei verkauft Blumen und Pflanzen."
            },
            {
                "id": "lt2_94",
                "situation": "9. Sie suchen einen Kinderarzt für die Untersuchung Ihres Babys.",
                "site_a_url": "www.kinderarzt-praxis-sonne.de",
                "site_a": "Kinderarztpraxis Sonne\nVorsorgeuntersuchungen und Impfungen für Babys und Kinder.",
                "site_b_url": "www.arzt-fuer-senioren.de",
                "site_b": "Altersmedizin und Geriatrie.",
                "answer": "Website A",
                "explanation": "Kinderarztpraxis behandelt Babys und Kinder."
            },
            {
                "id": "lt2_95",
                "situation": "10. Sie brauchen einen Rasenmäher für Ihren Garten.",
                "site_a_url": "www.garten-gerate-profi.de",
                "site_a": "Garten Geräte Profi\nRasenmäher, Heckenscheren und Gartengeräte.",
                "site_b_url": "www.blumen-samen-online.de",
                "site_b": "Nur Blumensamen zum Selberziehen.",
                "answer": "Website A",
                "explanation": "Garten Geräte Profi verkauft Rasenmäher."
            }
        ]
    }
]

# Lesen Teil 3 Official Scenarios Bank (All 9 exact scenarios)
LESEN_TEIL3_SCENARIOS = [
    {
        "title": "Bäckerei, Markt & Parkhaus",
        "desc": "Signs and notices about a bakery, market, museum, library and car park — 5 tasks, Richtig/Falsch.",
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
                "sign_text": "Liebe Kunden!\nWegen Urlaub bleibt unsere Bäckerei vom 1. bis 14. August geschlossen.\nAb dem 15. August sind wir wieder für Sie da.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Der Zettel besagt, dass die Bäckerei vom 1. bis 14. August (zwei Wochen) wegen Urlaub geschlossen ist."
            },
            {
                "id": "lt3_2",
                "statement": "Im Parkhaus darf man kostenlos parken.",
                "sign_title": "EINGANG PARKHAUS",
                "sign_text": "Parkhaus Stadtmitte\nErste Stunde frei, jede weitere angefangene Stunde 2,00 Euro.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Nur die *erste* Stunde ist frei, danach kostet es 2,00 Euro."
            },
            {
                "id": "lt3_3",
                "statement": "Die Bibliothek hat auch am Sonntag geöffnet.",
                "sign_title": "ÖFFNUNGSZEITEN DER BIBLIOTHEK",
                "sign_text": "Stadtbibliothek\nMontag bis Freitag: 9 - 18 Uhr\nSamstag: 10 - 14 Uhr\nSonntag: geschlossen",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Laut Schild ist am Sonntag geschlossen."
            },
            {
                "id": "lt3_4",
                "statement": "Man muss vor dem Betreten des Arztes einen Termin machen.",
                "sign_title": "AN DER ARZTPRAXIS",
                "sign_text": "Dr. med. Weber\nBitte melden Sie sich vor der Behandlung immer an der Anmeldung an.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Man muss sich an der Anmeldung melden."
            },
            {
                "id": "lt3_5",
                "statement": "Im Supermarkt kann man mit Karte bezahlen.",
                "sign_title": "KASSE IM SUPERMARKT",
                "sign_text": "Zahlung ab 10 Euro mit EC-Karte oder Kreditkarte möglich.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Kartenzahlung ist ab 10 Euro möglich."
            }
        ]
    },
    {
        "title": "Apotheke, Kino & Arztpraxis",
        "desc": "Signs and notices about an emergency pharmacy, cinema, park, shoes and a medical practice — 5 tasks, Richtig/Falsch.",
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
            },
            {
                "id": "lt3_a2",
                "statement": "Im Park darf man mit Fahrrädern fahren.",
                "sign_title": "PARKEINGANG",
                "sign_text": "Achtung! Das Radfahren im Stadtpark ist strengstens verboten.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Radfahren ist im Park verboten."
            },
            {
                "id": "lt3_a3",
                "statement": "Schuhe kann man im Schuhgeschäft umtauschen.",
                "sign_title": "SCHUH-CENTER",
                "sign_text": "Umtausch von ungetragenen Schuhen innerhalb von 14 Tagen gegen Kassenbon.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Umtausch ist innerhalb von 14 Tagen mit Kassenbon möglich."
            },
            {
                "id": "lt3_a4",
                "statement": "Die Arztpraxis ist am Mittwochnachmittag geschlossen.",
                "sign_title": "ARZTPRAXIS DR. BRAUN",
                "sign_text": "Sprechzeiten:\nMo-Fr: 8-12 Uhr\nMo, Di, Do: 15-18 Uhr\nMittwochnachmittag geschlossen.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Mittwochnachmittag ist die Praxis geschlossen."
            },
            {
                "id": "lt3_a5",
                "statement": "Man darf im Krankenhaus laut telefonieren.",
                "sign_title": "FLUR IM KRANKENHAUS",
                "sign_text": "Bitte schalten Sie Ihre Handys aus oder stellen Sie diese auf lautlos.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Handys sollen lautlos gestellt oder ausgeschaltet werden."
            }
        ]
    },
    {
        "title": "Bäckerei, Sporthalle & Computerkurs",
        "desc": "Signs and notices about a bakery, restaurant, special offers, sports hall and computer course — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Die Sporthalle ist am Wochenende geöffnet.",
            "sign_title": "SPORTHALLE",
            "sign_text": "Sporthalle geöffnet Samstag und Sonntag von 9 bis 20 Uhr.",
            "answer": "richtig",
            "explanation": "Die Sporthalle hat am Wochenende geöffnet."
        },
        "tasks": [
            {
                "id": "lt3_b1",
                "statement": "In der Bäckerei gibt es frische Brötchen ab 6 Uhr.",
                "sign_title": "BÄCKEREI MÜLLER",
                "sign_text": "Täglich ab 6:00 Uhr frische Brötchen und Kaffee.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Frische Brötchen gibt es ab 6:00 Uhr."
            },
            {
                "id": "lt3_b2",
                "statement": "Das Restaurant bietet sonntags ein warmes Buffet an.",
                "sign_title": "RESTAURANT ZUR POST",
                "sign_text": "Jeden Sonntag von 11 bis 14 Uhr großes warmes Mittagsbuffet.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Das Restaurant bietet sonntags von 11 bis 14 Uhr ein Mittagsbuffet an."
            },
            {
                "id": "lt3_b3",
                "statement": "Der Computerkurs kostet extra.",
                "sign_title": "VOLSKHOCHSCHULE",
                "sign_text": "Computerkurs für Anfänger: Kostenlos für alle Vereinsmitglieder.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Für Vereinsmitglieder ist der Kurs kostenlos."
            },
            {
                "id": "lt3_b4",
                "statement": "Im Hallenbad muss man eine Badehaube tragen.",
                "sign_title": "HALLENBAD",
                "sign_text": "Im gesamten Badbereich herrscht Badekleiderpflicht. Badehauben sind freiwillig.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Badehauben sind freiwillig."
            },
            {
                "id": "lt3_b5",
                "statement": "Der Bus fährt am Feiertag nach dem Sonntagsfahrplan.",
                "sign_title": "HALTESTELLE BUS",
                "sign_text": "An Feiertagen gilt der Sonntagsfahrplan.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "An Feiertagen gilt der Sonntagsfahrplan."
            }
        ]
    },
    {
        "title": "Hausordnung, Aufzug & Mülltonnen",
        "desc": "Signs and notices about house rules, lifts, dog leashes, waste sorting and quiet hours — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Ab 22 Uhr muss man in der Wohnung leise sein.",
            "sign_title": "HAUSORDNUNG",
            "sign_text": "Nachtruhe gilt von 22:00 bis 6:00 Uhr morgens.",
            "answer": "richtig",
            "explanation": "Die Nachtruhe beginnt um 22 Uhr."
        },
        "tasks": [
            {
                "id": "lt3_c1",
                "statement": "Im Aufzug dürfen maximal 4 Personen fahren.",
                "sign_title": "AUFZUG",
                "sign_text": "Personenaufzug max. 6 Personen oder 480 kg.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Maximal 6 Personen sind erlaubt."
            },
            {
                "id": "lt3_c2",
                "statement": "Hunde müssen im Treppenhaus an der Leine geführt werden.",
                "sign_title": "HAUSEINGANG",
                "sign_text": "Bitte führen Sie Hunde im Haus und Flur immer an der Leine.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Hunde müssen an der Leine geführt werden."
            },
            {
                "id": "lt3_c3",
                "statement": "Glasflaschen gehören in den Restmüll.",
                "sign_title": "MÜLLTONNEN",
                "sign_text": "Glasflaschen bitte in die Glascontainer auf dem Hof werfen, nicht in den Hausmüll.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Glas gehört in die Glascontainer, nicht in den Restmüll."
            },
            {
                "id": "lt3_c4",
                "statement": "Am Sonntag darf man keinen Rasen mähen.",
                "sign_title": "GARTEN",
                "sign_text": "Rasenmähen ist sonn- und feiertags verboten.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "An Sonn- und Feiertagen ist Rasenmähen verboten."
            },
            {
                "id": "lt3_c5",
                "statement": "Fahrräder stellt man in den Hausflur.",
                "sign_title": "FLUR",
                "sign_text": "Fahrräder und Kinderwagen dürfen nicht im Flur stehen, bitte nutzen Sie den Fahrradkeller.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Fahrräder gehören in den Fahrradkeller, nicht in den Flur."
            }
        ]
    },
    {
        "title": "Mittagsmenü, Schwimmbad & Bibliothek",
        "desc": "Signs and notices about a lunch menu, swimming pool, bus route, job vacancy and library — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "In der Mensa gibt es mittags zwei Menüs zur Auswahl.",
            "sign_title": "MENSA SPEISEPLAN",
            "sign_text": "Mittagsmenü: Täglich zwei warme Gerichte zur Auswahl (auch vegetarisch).",
            "answer": "richtig",
            "explanation": "Es gibt zwei warme Gerichte zur Auswahl."
        },
        "tasks": [
            {
                "id": "lt3_d1",
                "statement": "Die Stadtbibliothek verleiht auch Filme auf DVD.",
                "sign_title": "STADTBIBLIOTHEK",
                "sign_text": "Neu in der Bibliothek: Große Auswahl an Büchern, CDs und DVDs zum Ausleihen.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "DVDs können ausgeliehen werden."
            },
            {
                "id": "lt3_d2",
                "statement": "Der Bus fährt am Wochenende seltener.",
                "sign_title": "FAHRPLAN",
                "sign_text": "Samstags und sonntags stündlicher Fahrverkehr.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Am Wochenende fährt der Bus stündlich."
            },
            {
                "id": "lt3_d3",
                "statement": "Für die Ausleihe in der Bibliothek braucht man einen Ausweis.",
                "sign_title": "BIBLIOTHEK ANMELDUNG",
                "sign_text": "Die Ausleihe ist nur mit gültigem Leseausweis möglich.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Ein gültiger Leseausweis ist erforderlich."
            },
            {
                "id": "lt3_d4",
                "statement": "Das Schwimmbad schließt im Winter komplett.",
                "sign_title": "SCHWIMMBAD",
                "sign_text": "Hallenbad ganzjährig geöffnet. Freibad nur im Sommer.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Das Hallenbad ist ganzjährig geöffnet."
            },
            {
                "id": "lt3_d5",
                "statement": "Im Supermarkt kann man Flaschen zurückgeben.",
                "sign_title": "LEERGUTAUTOMAT",
                "sign_text": "Rücknahme von Mehrwegflaschen und Dosen am Automaten im Eingangsbereich.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Leergutrückgabe ist am Automaten möglich."
            }
        ]
    },
    {
        "title": "Haltestelle, Schule & Freibad",
        "desc": "Signs and notices about a ticket machine, bus stop, school, lift and outdoor pool — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Am Ticketautomat kann man mit Karte bezahlen.",
            "sign_title": "FAHRKARTENAUTOMAT",
            "sign_text": "Bezahlung mit Bargeld und EC-Karte möglich.",
            "answer": "richtig",
            "explanation": "Der Automat akzeptiert Bargeld und EC-Karte."
        },
        "tasks": [
            {
                "id": "lt3_e1",
                "statement": "Die Schule beginnt um 8:00 Uhr.",
                "sign_title": "SCHULE",
                "sign_text": "Unterrichtsbeginn ist um 8:00 Uhr. Einlass ab 7:45 Uhr.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Der Unterricht beginnt um 8:00 Uhr."
            },
            {
                "id": "lt3_e2",
                "statement": "Das Freibad öffnet bei schlechtem Wetter später.",
                "sign_title": "FREIBAD",
                "sign_text": "Bei Dauerregen oder Gewitter bleibt das Freibad geschlossen.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Es bleibt ganz geschlossen bei Dauerregen oder Gewitter."
            },
            {
                "id": "lt3_e3",
                "statement": "Der Aufzug im Bahnhof ist defekt.",
                "sign_title": "BAHNHOF",
                "sign_text": "Aufzug zu Gleis 3 funktioniert wieder einwandfrei.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Der Aufzug funktioniert wieder."
            },
            {
                "id": "lt3_e4",
                "statement": "Kinder unter 4 Jahren zahlen keinen Eintritt ins Freibad.",
                "sign_title": "FREIBAD KASSE",
                "sign_text": "Eintritt frei für Kinder unter 4 Jahren.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Kinder unter 4 Jahren haben freien Eintritt."
            },
            {
                "id": "lt3_e5",
                "statement": "An der Haltestelle gibt es einen Fahrkartenverkauf.",
                "sign_title": "HALTESTELLE",
                "sign_text": "Fahrkarten bitte beim Busfahrer kaufen, kein Automat an dieser Haltestelle.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Man muss beim Busfahrer kaufen, es gibt keinen Automaten."
            }
        ]
    },
    {
        "title": "Vorstellung, Museum & Kinderfest",
        "desc": "Signs and notices about a performance, admission times, clothing, a museum, children's festival and concert — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Das Museum hat montags geschlossen.",
            "sign_title": "MUSEUM",
            "sign_text": "Öffnungszeiten: Dienstag bis Sonntag von 10 bis 18 Uhr. Montag Ruhetag.",
            "answer": "richtig",
            "explanation": "Montag ist Ruhetag."
        },
        "tasks": [
            {
                "id": "lt3_f1",
                "statement": "Das Theaterstück beginnt um 20 Uhr.",
                "sign_title": "THEATER",
                "sign_text": "Beginn der Abendvorstellung: 20:00 Uhr. Einlass ab 19:15 Uhr.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Die Vorstellung beginnt um 20:00 Uhr."
            },
            {
                "id": "lt3_f2",
                "statement": "Das Kinderfest kostet Eintritt.",
                "sign_title": "STADTPARK KINDERFEST",
                "sign_text": "Spiel und Spaß für die ganze Familie! Eintritt frei.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Der Eintritt ist frei."
            },
            {
                "id": "lt3_f3",
                "statement": "Im Museum darf man mit Blitzlicht fotografieren.",
                "sign_title": "MUSEUM",
                "sign_text": "Fotografieren ohne Blitz ist erlaubt.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Nur ohne Blitz ist erlaubt."
            },
            {
                "id": "lt3_f4",
                "statement": "Das Konzert findet bei jedem Wetter draußen statt.",
                "sign_title": "OPEN AIR KONZERT",
                "sign_text": "Bei Regen findet das Konzert in der Stadthalle statt.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Bei Regen zieht man in die Stadthalle um."
            },
            {
                "id": "lt3_f5",
                "statement": "Kinder unter 12 Jahren dürfen nur in Begleitung ins Konzert.",
                "sign_title": "KONZERTHAUS",
                "sign_text": "Kinder unter 12 Jahren nur in Begleitung Erwachsener.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Begleitung Erwachsener ist erforderlich."
            }
        ]
    },
    {
        "title": "Frühstück, Geldautomat & Tankstelle",
        "desc": "Signs and notices about breakfast, the cash machine, parking, the workshop, the petrol station and the post office — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Die Tankstelle ist rund um die Uhr geöffnet.",
            "sign_title": " TANKSTELLE",
            "sign_text": "24 Stunden geöffnet – Tag und Nacht für Sie da.",
            "answer": "richtig",
            "explanation": "Die Tankstelle hat 24 Stunden geöffnet."
        },
        "tasks": [
            {
                "id": "lt3_g1",
                "statement": "Das Frühstücksbuffet gibt es bis 11 Uhr.",
                "sign_title": "HOTEL CAFÉ",
                "sign_text": "Reichhaltiges Frühstücksbuffet von 6:30 bis 10:30 Uhr.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Es geht nur bis 10:30 Uhr."
            },
            {
                "id": "lt3_g2",
                "statement": "Am Geldautomaten kann man rund um die Uhr Geld abheben.",
                "sign_title": "BANK",
                "sign_text": "Geldautomat im Foyer täglich von 6:00 bis 23:00 Uhr zugänglich.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Zugang ist nur von 6:00 bis 23:00 Uhr möglich, nicht 24h."
            },
            {
                "id": "lt3_g3",
                "statement": "Die Postfiliale hat samstags geschlossen.",
                "sign_title": "POSTFILIALE",
                "sign_text": "Öffnungszeiten: Mo-Fr 9-18 Uhr, Sa 9-13 Uhr.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Samstags hat sie von 9 bis 13 Uhr geöffnet."
            },
            {
                "id": "lt3_g4",
                "statement": "Auf dem Kundenparkplatz darf man maximal 2 Stunden parken.",
                "sign_title": "PARKPLATZ SUPERMARKT",
                "sign_text": "Kundenparkplatz: Parken nur während des Einkaufs (max. 2 Stunden mit Parkscheibe).",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Maximal 2 Stunden mit Parkscheibe."
            },
            {
                "id": "lt3_g5",
                "statement": "In der Kfz-Werkstatt kann man heute Reifen wechseln lassen.",
                "sign_title": "AUTOWERKSTATT",
                "sign_text": "Heuete ohne Termin: Schnellservice für Ölwechsel und Reifenwechsel.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Schnellservice ohne Termin für Reifenwechsel ist verfügbar."
            }
        ]
    },
    {
        "title": "Notdienst, Bibliothek & Park",
        "desc": "Signs and notices about emergency services, a medical practice, the library and the park — 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Der ärztliche Notdienst ist am Wochenende erreichbar.",
            "sign_title": "ÄRZTLICHER NOTDIENST",
            "sign_text": "Am Wochenende und Feiertagen erreichen Sie den ärztlichen Notdienst unter Telefon 116 117.",
            "answer": "richtig",
            "explanation": "Er ist am Wochenende erreichbar."
        },
        "tasks": [
            {
                "id": "lt3_h1",
                "statement": "In der Bibliothek muss man leise sein.",
                "sign_title": "BIBLIOTHEK",
                "sign_text": "Bitte verhalten Sie sich leise und respektieren Sie andere Leser.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Man muss sich leise verhalten."
            },
            {
                "id": "lt3_h2",
                "statement": "Im Park darf man Blumen pflücken.",
                "sign_title": "STADTPARK",
                "sign_text": "Das Pflücken von Blumen und Betreten der Beete ist streng verboten.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Pflücken ist verboten."
            },
            {
                "id": "lt3_h3",
                "statement": "Die Apotheke hat am Sonntag komplett geschlossen.",
                "sign_title": "APOTHEKE",
                "sign_text": "Sonntags geschlossen. Beachten Sie unseren Aushang für den Notdienst.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Es gibt einen Notdienst."
            },
            {
                "id": "lt3_h4",
                "statement": "Im Park gibt es einen Spielplatz für Kinder.",
                "sign_title": "PARKPLAN",
                "sign_text": "Im nördlichen Teil des Parks finden Sie einen großen Kinderspielplatz.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Ein Kinderspielplatz ist vorhanden."
            },
            {
                "id": "lt3_h5",
                "statement": "Man kann Bücher in der Bibliothek online verlängern.",
                "sign_title": "BIBLIOTHEK ONLINE",
                "sign_text": "Verlängerung der Leihfristen telefonisch oder über unsere Website rund um die Uhr möglich.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Online-Verlängerung ist möglich."
            }
        ]
    }
]

# Schreiben Teil 1 Official Scenarios Bank
SCHREIBEN_TEIL1_SCENARIOS = [
    {
        "title": "Bodensee-Rundfahrt — Anmeldung",
        "desc": "Registration for a Bodensee tour with Eva Kadavy – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Ihre Freundin, Eva Kadavy, macht mit ihrem Mann und ihren beiden Söhnen (8 und 11 Jahre alt) Urlaub in Seeheim.\n\nIm Reisebüro bucht sie für den nächsten Sonntag eine Busfahrt um den Bodensee.\n\nFrau Kadavy hat keine Kreditkarte.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie Ihrer Freundin und schreiben Sie die fünf fehlenden Informationen in das Formular.",
        "form_title": "BODENSEE-RUNDFAHRT — Anmeldung",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Kadavy, Eva", "is_gap": False},
            {"id": "sf2", "label": "1. Anzahl der Personen:", "answer": "4", "is_gap": True, "placeholder": "z. B. 4"},
            {"id": "sf3", "label": "2. Davon Kinder:", "answer": "2", "is_gap": True, "placeholder": "z. B. 2"},
            {"id": "sf4", "label": "Urlaubsadresse:", "default": "Hotel Schönblick", "is_gap": False},
            {"id": "sf5", "label": "Straße, Hausnummer:", "default": "Burgstraße 34", "is_gap": False},
            {"id": "sf6", "label": "3. PLZ, Urlaubsort:", "answer": "78014 Seeheim", "is_gap": True, "placeholder": "PLZ und Ort"},
            {"id": "sf7", "label": "4. Zahlungsweise:", "answer": "Bar", "is_gap": True, "placeholder": "Bar oder Kreditkarte", "options": ["Bar", "Kreditkarte"]},
            {"id": "sf8", "label": "5. Reisetermin:", "answer": "nächsten Sonntag", "is_gap": True, "placeholder": "z. B. nächsten Sonntag"},
            {"id": "sf9", "label": "Unterschrift:", "default": "Eva Kadavy", "is_gap": False}
        ]
    },
    {
        "title": "Praxis Dr. Sommer — Patienteninformation",
        "desc": "Pavel Novák's patient information for a doctor's visit – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Pavel Novák (geboren 1985) hat starke Kopfschmerzen und geht in die Arztpraxis Dr. Sommer.\n\nEr ist bei der Krankenkasse AOK versichert.\n\nEr möchte morgen um 9 Uhr einen Termin.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihm und schreiben Sie die fünf fehlenden Informationen in das Formular.",
        "form_title": "ARZTPRAXIS DR. SOMMER — Patientenkarte",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Novák, Pavel", "is_gap": False},
            {"id": "sf2", "label": "1. Geburtsjahr:", "answer": "1985", "is_gap": True, "placeholder": "z. B. 1985"},
            {"id": "sf3", "label": "2. Beschwerde:", "answer": "Kopfschmerzen", "is_gap": True, "placeholder": "z. B. Kopfschmerzen"},
            {"id": "sf4", "label": "3. Krankenkasse:", "answer": "AOK", "is_gap": True, "placeholder": "z. B. AOK"},
            {"id": "sf5", "label": "4. Termin gewünscht:", "answer": "morgen, 9 Uhr", "is_gap": True, "placeholder": "z. B. morgen, 9 Uhr"},
            {"id": "sf6", "label": "5. Telefonnummer:", "answer": "015239871", "is_gap": True, "placeholder": "Telefonnummer"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Pavel Novák", "is_gap": False}
        ]
    },
    {
        "title": "Fitnessstudio FitAktiv — Anmeldung",
        "desc": "Omar Haddad's registration at the FitAktiv gym – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Omar Haddad möchte eine Mitgliedschaft im Fitnessstudio FitAktiv für 1 Jahr abschließen.\n\nDer Monatsbeitrag beträgt 30 Euro.\n\nEr möchte am 01. November starten.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihm und tragen Sie die fehlenden Angaben ein.",
        "form_title": "FITAKTIV MITGLIEDSCHAFT",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Haddad, Omar", "is_gap": False},
            {"id": "sf2", "label": "1. Mitgliedschaft:", "answer": "1 Jahr", "is_gap": True, "placeholder": "z. B. 1 Jahr"},
            {"id": "sf3", "label": "2. Monatsbeitrag:", "answer": "30 Euro", "is_gap": True, "placeholder": "z. B. 30 Euro"},
            {"id": "sf4", "label": "3. Starttermin:", "answer": "01. November", "is_gap": True, "placeholder": "Datum"},
            {"id": "sf5", "label": "4. Zahlungsart:", "answer": "Überweisung", "is_gap": True, "placeholder": "Bar oder Überweisung", "options": ["Bar", "Überweisung"]},
            {"id": "sf6", "label": "5. Bankverbindung:", "answer": "DE89...ples", "is_gap": True, "placeholder": "IBAN"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Omar Haddad", "is_gap": False}
        ]
    },
    {
        "title": "Hotel Seeblick — Reservierung",
        "desc": "Klara Veidt's reservation at Hotel Seeblick – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Klara Veidt möchte im Hotel Seeblick ein Doppelzimmer für 4 Nächte mit Frühstück reservieren.\n\nSie reist am 18. Juli an.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihr und tragen Sie die fehlenden Angaben ein.",
        "form_title": "HOTEL SEEBLICK — Reservierung",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Veidt, Klara", "is_gap": False},
            {"id": "sf2", "label": "1. Zimmerart:", "answer": "Doppelzimmer", "is_gap": True, "placeholder": "Einzelzimmer oder Doppelzimmer", "options": ["Einzelzimmer", "Doppelzimmer"]},
            {"id": "sf3", "label": "2. Übernachtungen:", "answer": "4 Nächte", "is_gap": True, "placeholder": "z. B. 4 Nächte"},
            {"id": "sf4", "label": "3. Verpflegung:", "answer": "Frühstück", "is_gap": True, "placeholder": "z. B. Frühstück"},
            {"id": "sf5", "label": "4. Ankunft:", "answer": "18. Juli", "is_gap": True, "placeholder": "Datum"},
            {"id": "sf6", "label": "5. Telefonnummer:", "answer": "089123456", "is_gap": True, "placeholder": "Telefonnummer"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Klara Veidt", "is_gap": False}
        ]
    },
    {
        "title": "Volkshochschule — Anmeldung Deutschkurs",
        "desc": "Marco Rossi's registration for a German course – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Marco Rossi möchte an der Volkshochschule den Deutschkurs DE-104 (Stufe A1) ab dem 10. Oktober besuchen.\n\nEr bezahlt per Überweisung.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihm und tragen Sie die fehlenden Angaben ein.",
        "form_title": "VOLKSHOCHSCHULE — Anmeldeformular",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Rossi, Marco", "is_gap": False},
            {"id": "sf2", "label": "1. Kursnummer:", "answer": "DE-104", "is_gap": True, "placeholder": "z. B. DE-104"},
            {"id": "sf3", "label": "2. Stufe:", "answer": "A1", "is_gap": True, "placeholder": "A1, A2, B1"},
            {"id": "sf4", "label": "3. Kursbeginn:", "answer": "10. Oktober", "is_gap": True, "placeholder": "Datum"},
            {"id": "sf5", "label": "4. Zahlungsart:", "answer": "Überweisung", "is_gap": True, "placeholder": "Bar oder Überweisung", "options": ["Bar", "Überweisung"]},
            {"id": "sf6", "label": "5. Telefonnummer:", "answer": "030987654", "is_gap": True, "placeholder": "Telefonnummer"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Marco Rossi", "is_gap": False}
        ]
    },
    {
        "title": "Stadtbibliothek Köln — Anmeldung",
        "desc": "Anna Kowalski's application for a library card – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Anna Kowalski wohnt in der Domstraße 12 in Köln und wurde am 14.05.1995 geboren.\n\nIhre Telefonnummer ist 022198765.\n\nDie Jahresgebühr beträgt 15 Euro.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihr und tragen Sie die fehlenden Angaben ein.",
        "form_title": "STADTBIBLIOTHEK KÖLN — Leserausweis",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Kowalski, Anna", "is_gap": False},
            {"id": "sf2", "label": "1. Adresse:", "answer": "Domstraße 12", "is_gap": True, "placeholder": "Straße und Hausnummer"},
            {"id": "sf3", "label": "2. Geburtsdatum:", "answer": "14.05.1995", "is_gap": True, "placeholder": "TT.MM.JJJJ"},
            {"id": "sf4", "label": "3. Telefonnummer:", "answer": "022198765", "is_gap": True, "placeholder": "Telefonnummer"},
            {"id": "sf5", "label": "4. Jahresgebühr:", "answer": "15 Euro", "is_gap": True, "placeholder": "z. B. 15 Euro"},
            {"id": "sf6", "label": "5. Stadtteil:", "answer": "Köln", "is_gap": True, "placeholder": "Stadt"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Anna Kowalski", "is_gap": False}
        ]
    },
    {
        "title": "Schwimmbad Aqua — Anmeldung Schwimmkurs",
        "desc": "Emir Yıldız's registration for a beginner swimming course – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Emir Yıldız (28 Jahre alt) möchte einen Anfängerschwimmkurs am Samstag um 10:00 Uhr im Schwimmbad Aqua besuchen.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihm und tragen Sie die fehlenden Angaben ein.",
        "form_title": "SCHWIMMBAD AQUA — Kursanmeldung",
        "fields": [
            {"id": "sf1", "label": "Familienname, Vorname:", "default": "Yıldız, Emir", "is_gap": False},
            {"id": "sf2", "label": "1. Alter:", "answer": "28", "is_gap": True, "placeholder": "z. B. 28"},
            {"id": "sf3", "label": "2. Kursart:", "answer": "Anfänger", "is_gap": True, "placeholder": "Anfänger"},
            {"id": "sf4", "label": "3. Tag:", "answer": "Samstag", "is_gap": True, "placeholder": "Wochentag"},
            {"id": "sf5", "label": "4. Uhrzeit:", "answer": "10:00 Uhr", "is_gap": True, "placeholder": "Uhrzeit"},
            {"id": "sf6", "label": "5. Telefonnummer:", "answer": "017654321", "is_gap": True, "placeholder": "Telefonnummer"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Emir Yıldız", "is_gap": False}
        ]
    },
    {
        "title": "Nordbank — Kontoeröffnung",
        "desc": "Helping Diego Fernández open a bank account – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Diego Fernández arbeitet als Koch und möchte bei der Nordbank ein Konto eröffnen.\n\nSeine E-Mail ist diego@web.de und das Startguthaben beträgt 50 Euro.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihm und tragen Sie die fehlenden Angaben ein.",
        "form_title": "NORDBANK — Kontoeröffnungsformular",
        "fields": [
            {"id": "sf1", "label": "Familienname:", "default": "Fernández", "is_gap": False},
            {"id": "sf2", "label": "1. Vorname:", "answer": "Diego", "is_gap": True, "placeholder": "Vorname"},
            {"id": "sf3", "label": "2. Beruf:", "answer": "Koch", "is_gap": True, "placeholder": "Beruf"},
            {"id": "sf4", "label": "3. E-Mail:", "answer": "diego@web.de", "is_gap": True, "placeholder": "E-Mail"},
            {"id": "sf5", "label": "4. Startguthaben:", "answer": "50 Euro", "is_gap": True, "placeholder": "Betrag"},
            {"id": "sf6", "label": "5. Bankfiliale:", "answer": "München", "is_gap": True, "placeholder": "Stadt"},
            {"id": "sf7", "label": "Unterschrift:", "default": "Diego Fernández", "is_gap": False}
        ]
    },
    {
        "title": "City Autovermietung — Mietvertrag",
        "desc": "Helping Hana Kim fill out a car rental agreement – Fill out a form, 5 gaps, 10 min.",
        "aufgabe": "Hana Kim mietet einen Kleinwagen für 3 Tage ab Freitag bei der City Autovermietung.\n\nDie Selbstbeteiligung beträgt 300 Euro.\n\nIn dem Formular fehlen fünf Informationen. Helfen Sie ihr und tragen Sie die fehlenden Angaben ein.",
        "form_title": "CITY AUTOVERMIETUNG — Mietvertrag",
        "fields": [
            {"id": "sf1", "label": "Mieter:", "default": "Hana Kim", "is_gap": False},
            {"id": "sf2", "label": "1. Fahrzeugmodell:", "answer": "Kleinwagen", "is_gap": True, "placeholder": "Fahrzeugtyp"},
            {"id": "sf3", "label": "2. Mietdauer:", "answer": "3 Tage", "is_gap": True, "placeholder": "Dauer"},
            {"id": "sf4", "label": "3. Abholdatum:", "answer": "Freitag", "is_gap": True, "placeholder": "Wochentag"},
            {"id": "sf5", "label": "4. Selbstbeteiligung:", "answer": "300 Euro", "is_gap": True, "placeholder": "Betrag"},
            {"id": "sf6", "label": "5. Zahlungsart:", "answer": "Kreditkarte", "is_gap": True, "placeholder": "Bar oder Kreditkarte", "options": ["Bar", "Kreditkarte"]},
            {"id": "sf7", "label": "Unterschrift:", "default": "Hana Kim", "is_gap": False}
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
            "2. Bitten Sie: Informationen über Filme, Museen usw. (Kulturprogramm).",
            "3. Fragen Sie: Hoteladressen?"
        ],
        "prompt": "Sehr geehrte Damen und Herren,\n\nich möchte im August Dresden besuchen und plane eine Reise. Könnten Sie mir bitte Informationen über das Kulturprogramm (Museen, Filme usw.) schicken? Haben Sie auch Empfehlungen für Hoteladressen?\n\nMit freundlichen Grüßen,\n[Dein Name]"
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
    },
    {
        "title": "Heizung kaputt — Nachricht an den Vermieter",
        "desc": "Message to Mr Berg about the broken heating – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "In Ihrer Wohnung ist die Heizung kaputt. Schreiben Sie an Ihren Vermieter, Herrn Berg.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Problem erklären (Heizung kaputt).",
            "2. Es ist sehr kalt in der Wohnung.",
            "3. Bitte um schnelle Reparatur."
        ],
        "prompt": "Sehr geehrter Herr Berg,\n\nin meiner Wohnung ist seit gestern die Heizung kaputt. Es ist leider sehr kalt in den Zimmern. Könnten Sie bitte schnell einen Handwerker schicken?\n\nMit freundlichen Grüßen,\n[Dein Name]"
    },
    {
        "title": "Danke für das Geschenk — Nachricht an einen Freund",
        "desc": "Thank-you message to Lukas for a birthday present – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Ihr Freund Lukas hat Ihnen ein schönes Geburtstagsgeschenk geschickt. Schreiben Sie an Lukas.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Danke für das Geschenk sagen.",
            "2. Wie finden Sie das Geschenk?",
            "3. Einladung auf einen Kaffee."
        ],
        "prompt": "Lieber Lukas,\n\nvielen herzlichen Dank für das tolle Geburtstagsgeschenk! Ich habe mich riesig darüber gefreut. Wollen wir uns nächste Woche auf einen Kaffee treffen?\n\nLiebe Grüße,\n[Dein Name]"
    },
    {
        "title": "Neue Wohnung — Einladung an eine Freundin",
        "desc": "Invitation to Sophie for a party at the new apartment – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie sind in eine neue Wohnung umzogen. Schreiben Sie an Ihre Freundin Sophie und laden Sie sie ein.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Neue Wohnung ankündigen.",
            "2. Einladung zur Einweihungsparty am Freitag.",
            "3. Frage nach Zusage."
        ],
        "prompt": "Liebe Sophie,\n\nich bin endlich in meine neue Wohnung umzogen! Am Freitag mache ich um 19 Uhr eine kleine Einweihungsparty. Hast du Zeit und kommst auch?\n\nLiebe Grüße,\n[Dein Name]"
    },
    {
        "title": "Umzug — einen Freund um Hilfe bitten",
        "desc": "Message to Daniel asking for help with moving – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie ziehen am Wochenende um und brauchen Hilfe. Schreiben Sie an Ihren Freund Daniel.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Ankündigung des Umzugs.",
            "2. Bitte um Hilfe beim Tragen am Samstag.",
            "3. Angebot von Pizza und Getränken."
        ],
        "prompt": "Lieber Daniel,\n\nich ziehe am nächsten Wochenende um und brauche dringend Hilfe beim Tragen. Hättest du am Samstag Zeit, mir zu helfen? Als Dankeschön gebe ich Pizza aus!\n\nLiebe Grüße,\n[Dein Name]"
    },
    {
        "title": "Freier Tag — Nachricht an die Chefin",
        "desc": "Message to Ms Schäfer about a doctor's appointment and taking a day off – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie haben am Dienstag einen wichtigen Termin. Schreiben Sie an Ihre Chefin, Frau Schäfer.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Grund für die Nachricht (Arzttermin am Vormittag).",
            "2. Frage nach Arbeitsbeginn ab 13 Uhr.",
            "3. Arbeit am Abend nachholen."
        ],
        "prompt": "Sehr geehrte Frau Schäfer,\n\nich habe am kommenden Dienstag einen wichtigen Arzttermin am Vormittag. Könnte ich an diesem Tag bitte erst ab 13 Uhr ins Büro kommen? Ich hole die Arbeit natürlich am Abend nach.\n\nMit freundlichen Grüßen,\n[Dein Name]"
    },
    {
        "title": "Treffen am Wochenende — Nachricht an eine Freundin",
        "desc": "Message to Mia about plans together at the weekend – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Sie möchten am Wochenende etwas unternehmen. Schreiben Sie an Ihre Freundin Mia.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Vorschlag für den Park am Samstag.",
            "2. Gemeinsam Eis essen.",
            "3. Bitte um kurze Rückmeldung."
        ],
        "prompt": "Liebe Mia,\n\nhast du am Samstag Zeit und Lust, zusammen in den Park zu gehen? Wir können dort lecker Eis essen. Melde dich doch kurz, ob es klappt!\n\nLiebe Grüße,\n[Dein Name]"
    },
    {
        "title": "Termin in der Autowerkstatt",
        "desc": "Email to the auto repair shop about car noises and an appointment – E-mail, approx. 30 words, 20 min.",
        "aufgabe_text": "Ihr Auto macht komische Geräusche. Schreiben Sie an die Autowerkstatt.\n\nSchreiben Sie zu jedem Punkt ein bis zwei Sätze (circa 30 Wörter).\n\nSchreiben Sie auch eine Anrede und einen Gruß.",
        "points": [
            "1. Problem erklären (Geräusche beim Bremsen).",
            "2. Bitte um Termin.",
            "3. Frage nach Termin am Donnerstag um 10 Uhr."
        ],
        "prompt": "Sehr geehrte Damen und Herren,\n\nmein Auto macht seit gestern komische Geräusche beim Bremsen. Ich brauche dringend einen Termin in Ihrer Werkstatt. Passt es Ihnen am Donnerstag um 10 Uhr?\n\nMit freundlichen Grüßen,\n[Dein Name]"
    }
]

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
    "🏆 Goethe A1 Mock Examination",
    "📖 A1 & A2 Short Stories",
    "💬 Ask Gem (AI Tutor)"
])

# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if nav_choice == "🏠 Study Dashboard":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.title("Goethe-Zertifikat A1 Prep Studio")
    st.write("📅 **Exam Date:** December 12, 2026")
    st.write("Complete Goethe A1 curriculum preparation featuring the complete 612-word Goethe vocabulary list, official 1000-word flashcards, grammar exercises, fully structured 3-part Goethe exam simulators with live countdowns, and enchanted storybooks.")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📖 Lesen & ✍️ Schreiben")
        st.markdown("""
        * **Lesen (25 Mins - 15 Tasks across 3 Parts):**
          - Teil 1: Short Emails (Richtig/Falsch) - *All 9 official exam scenarios fully integrated!*
          - Teil 2: Classified Ads (Option A or B) - *All 9 official exam scenarios fully integrated!*
          - Teil 3: Public Signs (Richtig/Falsch) - *All 9 official exam scenarios fully integrated!*
        * **Schreiben (20 Mins - 2 Parts):**
          - Teil 1: Fill 5 Missing Gaps on Form with Scenario (All 9 official exam scenarios fully integrated!)
          - Teil 2: Write ~30-Word Message hitting 3 required points (All 9 official exam scenarios fully integrated!)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🎧 Hören & 🗣️ Sprechen")
        st.markdown("""
        * **Hören (20 Mins - 15 Tasks across 3 Parts):**
          - Teil 1: 6 Dialogues (A/B/C)
          - Teil 2: 4 Announcements (Richtig/Falsch)
          - Teil 3: 5 Voicemails (A/B/C)
        * **Sprechen (15 Mins - 3 Parts):**
          - Teil 1: Self-Introduction & Spelling/Numbers
          - Teil 2: W-Questions with Topic Card
          - Teil 3: Imperative Requests with Object Card
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Interactive Flashcard Engine (Complete Vocabulary)")
    st.write("Browse through the complete 612-word Goethe A1 vocabulary list categorized into your 8 requested thematic groups.")

    TOP_1000_VOCAB_CATEGORIES = {
        "1. Person & Alltag (Personal & Daily Life)": {
            "Verben": ["heißen", "heiraten", "wohnen", "leben", "kennen", "kennenlernen", "schlafen", "aufstehen", "baden", "duschen", "sich vorstellen", "anziehen", "ausziehen", "umziehen", "waschen", "auf sein", "zu sein"],
            "Nomen": ["die Familie", "der Vater", "die Mutter", "der Sohn", "die Tochter", "der Bruder", "die Schwester", "die Großmutter", "der Großvater", "die Oma", "der Opa", "der Mann", "die Frau", "das Kind", "der Junge", "das Mädchen", "das Baby", "der Mensch", "die Eltern", "die Geschwister", "die Verwandten", "der Freund", "die Freundin", "der Partner", "die Partnerin", "der Name", "der Vorname", "der Familienname", "das Geburtsjahr", "der Geburtsort", "das Alter", "der Geburtstag", "der Pass", "der Ausweis", "die Adresse", "die Postleitzahl", "das Haus", "das Wohnung", "das Zimmer", "das Bad", "die Küche", "der Balkon", "der Garten", "das Dorf", "die Stadt", "die Heimat", "das Land", "die Tür", "das Fenster", "das Bett", "der Schrank", "der Tisch", "der Stuhl", "das Sofa", "das Bild", "das Licht", "der Schlüssel", "die Treppe", "der Aufzug", "das Dach", "der Boden", "das Schlafzimmer", "der Flur"],
            "Adjektive & Adverbien": ["alt", "jung", "groß", "klein", "verheiratet", "ledig", "selbstständig", "allein", "müde", "nett", "freundlich"],
            "Pronomen & Partikeln": ["ich", "du", "er", "sie", "es", "wir", "ihr", "Sie", "mein", "dein", "sein", "unser", "sich", "wer", "was", "wie", "wo", "woher", "wohin", "wann", "warum", "wie viel"]
        },
        "2. Essen & Trinken (Food & Drink)": {
            "Verben": ["essen", "trinken", "kochen", "backen", "frühstücken", "schmecken", "grillen", "bestellen"],
            "Nomen": ["das Essen", "das Frühstück", "das Mittagessen", "das Abendessen", "das Wasser", "der Kaffee", "der Tee", "das Bier", "der Wein", "der Saft", "die Milch", "das Brot", "das Brötchen", "das Fleisch", "der Fisch", "das Hähnchen", "das Ei", "die Butter", "der Käse", "die Kartoffel", "die Tomate", "der Apfel", "die Banane", "die Birne", "das Obst", "das Gemüse", "der Salat", "die Suppe", "der Kuchen", "das Salz", "das Öl", "die Schokolade", "der Zucker", "die Flasche", "das Glas", "die Tasse", "der Teller", "die Speisekarte", "der Hunger", "der Durst", "der Appetit"],
            "Adjektive": ["frisch", "bitter", "süß", "sauer", "lecker", "satt"]
        },
        "3. Freizeit & Alltag (Leisure & Routine)": {
            "Verben": ["spielen", "wandern", "schwimmen", "tanzen", "reisen", "feiern", "fernsehen", "lachen", "fotografieren", "hören", "lesen", "schreiben", "malen", "spazieren", "sich treffen"],
            "Nomen": ["die Freizeit", "das Hobby", "der Sport", "das Spiel", "das Buch", "die Zeitung", "das Lied", "der Film", "das Kino", "die Party", "der Urlaub", "die Reise", "das Reisebüro", "der Reiseführer", "das Schwimmbad", "die Disco", "das Restaurant", "das Café", "der Park", "das Meer", "der See", "der Berg", "das Wetter", "die Sonne", "der Regen", "der Wind", "der Schnee", "das Geschenk", "die Musik", "das Foto", "die Kamera", "der Computer", "das Handy", "das Internet", "die E-Mail", "der Brief", "die Briefmarke"],
            "Adjektive & Adverbien": ["oft", "manchmal", "nie", "immer", "bald", "gestern", "heute", "morgen", "spät", "früh", "langweilig", "interessant", "wunderbar", "schön", "lustig", "traurig"]
        },
        "4. Einkaufen & Geld (Shopping & Money)": {
            "Verben": ["kaufen", "einkaufen", "bezahlen", "kosten", "sparen", "verkaufen", "suchen", "finden", "brauchen", "bekommen"],
            "Nomen": ["das Geld", "der Euro", "der Cent", "der Preis", "die Rechnung", "die Kasse", "der Laden", "das Geschäft", "der Supermarkt", "die Bäckerei", "das Kaufhaus", "der Markt", "der Kiosk", "die Kleidung", "die Jacke", "die Hose", "das Hemd", "der Schuh", "die Tasche", "das Angebot", "der Rabatt", "die Größe", "die Kreditkarte", "bar"],
            "Adjektive": ["billig", "teuer", "neu", "alt", "gut", "schlecht", "richtig", "falsch", "passend"]
        },
        "5. Arbeit & Beruf (Work & Profession)": {
            "Verben": ["arbeiten", "verdienen", "anfangen", "aufhören", "beginnen", "vorbereiten", "telefonieren", "unterschreiben", "vermieten", "mieten", "arbeitslos sein"],
            "Nomen": ["die Arbeit", "der Beruf", "die Firma", "das Büro", "der Arbeitsplatz", "der Kollege", "die Kollegin", "der Chef", "die Chefin", "der Angestellte", "der Arbeiter", "der Verkäufer", "die Verkäuferin", "der Lehrer", "die Lehrerin", "der Schüler", "die Schülerin", "der Student", "die Studentin", "der Arzt", "die Ärztin", "die Schule", "der Kindergarten", "das Studium", "der Kurs", "der Unterricht", "das Praktikum", "der Termin", "die Aufgabe", "die Hausaufgabe", "die Pause", "der Lohn", "das Gehalt", "der Lebenslauf"],
            "Adjektive": ["arbeitslos", "beschäftigt", "pünktlich", "fleißig", "fertig"]
        },
        "6. Stadt & Verkehr (City & Transportation)": {
            "Verben": ["fahren", "fliegen", "ankommen", "abfahren", "aussteigen", "einsteigen", "umsteigen", "abholen", "parken", "gehen", "laufen", "besuchen"],
            "Nomen": ["die Stadt", "das Dorf", "die Straße", "die Autobahn", "der Bahnhof", "der Flughafen", "das Flugzeug", "der Zug", "die S-Bahn", "U-Bahn", "der Bus", "die Straßenbahn", "das Auto", "das Fahrrad", "das Taxi", "der Lkw", "die Fahrkarte", "das Ticket", "der Bahnsteig", "das Gleis", "die Haltestelle", "die Ampel", "die Kreuzung", "die Brücke", "der Parkplatz", "die Karte", "der Stadtplan", "der Fahrplan", "die Post", "die Bank", "das Hotel", "das Museum", "das Theater", "die Sehenswürdigkeit", "der Eingang", "der Ausgang", "die Info", "der Zoll"],
            "Präpositionen & Adverbien": ["links", "rechts", "geradeaus", "nah", "weit", "schnell", "langsam"]
        },
        "7. Gesundheit & Körper (Health & Body)": {
            "Verben": ["weh tun", "helfen", "untersuchen", "atmen", "liegen", "sitzen", "stehen", "fallen"],
            "Nomen": ["der Körper", "der Kopf", "das Auge", "das Ohr", "die Nase", "der Mund", "der Zahn", "der Hals", "der Arm", "die Hand", "das Bein", "der Fuß", "der Bauch", "das Haar", "die Gesundheit", "die Krankheit", "das Fieber", "der Schmerz", "die Apotheke", "das Medikament", "das Krankenhaus", "der Unfall", "die Praxis"],
            "Adjektive": ["gesund", "krank", "schwach", "stark"]
        },
        "8. Allgemein (General & Core Grammar)": {
            "Verben (Modal & Auxiliary)": ["haben", "sein", "werden", "können", "müssen", "wollen", "sollen", "dürfen", "mögen", "möchten", "wissen"],
            "Grammatik- & Funktionswörter": ["und", "oder", "aber", "denn", "weil", "wenn", "als", "dass", "wie", "so", "auch", "nicht", "nichts", "nur", "noch", "schon", "sehr", "zu", "viel", "wenig", "etwas", "alle", "jeder", "kein", "man", "da", "dort", "hier", "oben", "unten", "draußen", "innen", "jetzt", "dann", "danach", "vor", "nach", "bei", "mit", "ohne", "für", "gegen", "über", "unter", "zwischen", "bis", "aus", "an", "auf", "in", "um"]
        }
    }

    vocab_tree = TOP_1000_VOCAB_CATEGORIES

    main_cats = ["ALL"] + list(vocab_tree.keys())
    selected_main_cat = st.selectbox("📂 Select Main Category:", main_cats)

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
        selected_sub_cat = st.selectbox("📁 Select Subcategory:", sub_cats)

        if selected_sub_cat == "ALL":
            all_sub_pool = []
            for sub, wlist in sub_dict.items():
                all_sub_pool.extend(wlist)
            available_words = ["ALL"] + list(set(all_sub_pool))
        else:
            available_words = ["ALL"] + sub_dict[selected_sub_cat]

    selected_word_dropdown = st.selectbox("🔤 Select specific word (or ALL):", available_words)

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
        "comparative_superlative": "N/A",
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

        if not st.session_state.get("show_card_back", False):
            st.markdown(f"""
            <div class="flashcard-front-box">
                <p style="color: #38bdf8; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 8px;">⭐ {selected_main_cat} / {selected_sub_cat} ⭐</p>
                <div class="flashcard-word-title">{data.get("word", active_word)}</div>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 0px;">Click speaker icon for instant audio playback, or flip card for details.</p>
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
                <p style="color: #2563eb; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 2px;">⭐ {selected_main_cat} / {selected_sub_cat}</p>
                <div class="flashcard-back-title">{data.get("word", active_word)}</div>
                <div class="meaning-subtitle">Meaning: {data.get("english_meaning", "")}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Part of Speech", data.get("part_of_speech", "N/A"))
            c2.metric("Gender", data.get("gender", "N/A"))
            c3.metric("Plural Form", data.get("plural_form", "N/A"))
            c4.metric("Comp. / Superlative", data.get("comparative_superlative", "N/A"))

            perf = data.get("perfekt_tense", {})
            st.success(f"⏳ **Perfekt Tense:** `{perf.get('formula', 'N/A')}`")
            
            cp_perf = st.columns([0.5, 10])
            with cp_perf[0]:
                if st.button("🔊", key="audio_perf_icon"):
                    play_direct_audio(perf.get('sample_sentence_de', ''), "perf_sent")
            with cp_perf[1]:
                st.markdown(f"• **DE:** {perf.get('sample_sentence_de', '')}")
            st.markdown(f"• **EN:** {perf.get('sample_sentence_en', '')}")

            st.info(f"💡 **Grammar Notes & Rules:** {data.get('grammar_notes', 'N/A')}")

            st.markdown("#### 🔄 Conjugations & Example Sentences")
            conjs = data.get("conjugations", [])
            for i, c in enumerate(conjs):
                cols_c = st.columns([0.5, 10])
                with cols_c[0]:
                    if st.button("🔊", key=f"audio_conj_icon_{i}"):
                        play_direct_audio(c.get('sentence'), f"conj_{i}")
                with cols_c[1]:
                    st.markdown(f"• **{c.get('pronoun')}:** `{c.get('form')}` — *{c.get('sentence')}*  \n  &nbsp;&nbsp;&nbsp;&nbsp;*(En: {c.get('sentence_en')})*")

            st.markdown("#### 💬 Commonly Used Phrases")
            phrases = data.get("common_phrases", [])
            for j, p in enumerate(phrases):
                cols_p = st.columns([0.5, 10])
                with cols_p[0]:
                    if st.button("🔊", key=f"audio_phrase_icon_{j}"):
                        play_direct_audio(p.get('phrase_de'), f"phrase_{j}")
                with cols_p[1]:
                    st.markdown(f"👉 **{p.get('phrase_de')}** — *{p.get('phrase_en')}*")

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
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 Core Grammar Practice & Exercises")
    st.write("Review class handbook modules with rigorous bullet points and targeted practice questions.")

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
        "Lesson 23: Two-Way Prepositions (Wechselpräpositionen) - Accusative vs. Dative Deep Dive",
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

    selected_lesson = st.selectbox("Select Handbook Lesson to Review & Practice:", handbook_lessons)

    if st.button("📖 Load Rigorous Review & 20 Practice Exercises", type="primary"):
        with st.spinner("Gem is compiling clean bulleted notes, advanced study-buddy mentorship insights, and 20 practice exercises..."):
            prompt = f"""
            Create a detailed study review & 20-exercise package for '{selected_lesson}'.
            CRITICAL FORMATTING INSTRUCTION: 
            1. 'lesson_explanation' MUST be structured using clear Markdown bullet points (`*` or `-`). Avoid dense walls of text.
            2. Provide thorough, advanced mentor insights that go beyond basic source material so the user can easily master all 20 practice questions. Include structural patterns, mnemonics, and traps to avoid.

            Return strict JSON with this exact schema:
            {{
                "lesson_title": "{selected_lesson}",
                "lesson_explanation": "Provide a clean, beautifully formatted bulleted guide explaining '{selected_lesson}'. Use bullet points for rules, bullet points for examples, and bullet points for study-buddy pro tips.",
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
        st.markdown(f"### 📘 Comprehensive Lesson Review: {mod['lesson_title']}")
        st.markdown(mod["lesson_explanation"])

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
            
            st.markdown("#### 1. Multiple Choice Evaluation")
            for idx, q in enumerate(mod["exercises_mc"], start=1):
                u_ans = mc_user_answers.get(q['id'])
                if u_ans == q['correct']:
                    st.success(f"**Q{idx}: Correct!** ({q['correct']}) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['correct']}`\n\n💡 **Reason:** {q['explanation']}")

            st.markdown("#### 2. Fill in the Blanks Evaluation")
            for idx, q in enumerate(mod["exercises_fib"], start=1):
                u_ans = fib_user_answers.get(q['id'], "").strip().lower()
                c_ans = q['answer'].strip().lower()
                if u_ans == c_ans:
                    st.success(f"**Q{idx}: Correct!** (`{q['answer']}`) — {q['explanation']}")
                else:
                    st.error(f"**Q{idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['answer']}`\n\n💡 **Reason:** {q['explanation']}")

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
    st.subheader("📖 Goethe A1 Lesen Practice (25 Mins, 15 Points across 3 Parts)")

    l_tab1, l_tab2, l_tab3 = st.tabs([
        "Teil 1: Short Messages (Official Scenarios)", 
        "Teil 2: Classified Ads (Official Scenarios)", 
        "Teil 3: Public Signs (Official Scenarios)"
    ])

    with l_tab1:
        st.markdown("**Teil 1 (Kurze Mitteilungen):** Select from official Goethe A1 practice scenarios or refresh to generate brand-new alternative scenarios.")
        
        if "dyn_lesen_t1" not in st.session_state or not isinstance(st.session_state.dyn_lesen_t1, list):
            st.session_state.dyn_lesen_t1 = list(LESEN_TEIL1_SCENARIOS)

        valid_lesen_t1 = [s for s in st.session_state.dyn_lesen_t1 if isinstance(s, dict) and "title" in s]
        if not valid_lesen_t1:
            valid_lesen_t1 = list(LESEN_TEIL1_SCENARIOS)
            st.session_state.dyn_lesen_t1 = valid_lesen_t1

        col_lt1_sel, col_lt1_ref = st.columns([4, 1])
        with col_lt1_sel:
            selected_lesen_t1_title = st.selectbox("📂 Select Lesen Teil 1 Scenario Set:", [s["title"] for s in valid_lesen_t1], key="lesen_t1_sel")
        with col_lt1_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_lesen_t1", use_container_width=True):
                with st.spinner("Generating fresh alternative Lesen Teil 1 scenario via AI..."):
                    try:
                        prompt = "Generate a completely new Goethe A1 Lesen Teil 1 scenario set containing a title, desc, text1_label, text1, text2_label, text2, and 5 questions (each with id, statement, options ['richtig', 'falsch'], answer, and explanation). Return strict JSON format as a single object (not a list): {\"title\": \"...\", \"desc\": \"...\", \"text1_label\": \"...\", \"text1\": \"...\", \"text2_label\": \"...\", \"text2\": \"...\", \"questions\": [...]}"
                        res = generate_dynamic_content(prompt, is_json=True)
                        new_scen = json.loads(res)
                        if isinstance(new_scen, dict) and "title" in new_scen:
                            st.session_state.dyn_lesen_t1.append(new_scen)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to refresh: {str(e)}")

        selected_lesen_t1_obj = next((s for s in valid_lesen_t1 if s["title"] == selected_lesen_t1_title), valid_lesen_t1[0])
        
        st.info(f"📌 **Description:** {selected_lesen_t1_obj['desc']}")

        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">✉️ {selected_lesen_t1_obj.get('text1_label', 'E-Mail')}</span>
            </div>
            <p style="white-space: pre-line; color: #334155; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0px;">{selected_lesen_t1_obj['text1']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">📄 {selected_lesen_t1_obj.get('text2_label', 'Brief')}</span>
            </div>
            <p style="white-space: pre-line; color: #334155; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0px;">{selected_lesen_t1_obj['text2']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Aufgaben (Tasks 1–5)")
        ans_lt1 = {}
        for idx, q in enumerate(selected_lesen_t1_obj["questions"], start=1):
            st.markdown(f"**Task {idx}: {q['statement']}**")
            ans_lt1[q["id"]] = st.radio("Wählen Sie:", q["options"], key=f"rad_lt1_{selected_lesen_t1_title}_{q['id']}")

        if st.button("✔ Submit Lesen Teil 1", type="primary", key="sub_lt1"):
            score = sum(1 for q in selected_lesen_t1_obj["questions"] if ans_lt1.get(q["id"]) == q["answer"])
            st.markdown("### 📊 Evaluation")
            for idx, q in enumerate(selected_lesen_t1_obj["questions"], start=1):
                u_ans = ans_lt1.get(q["id"])
                if u_ans == q["answer"]:
                    st.success(f"**Task {idx}: Correct!** (`{q['answer']}`) — {q['explanation']}")
                else:
                    st.error(f"**Task {idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{q['answer']}` — {q['explanation']}")
            st.metric("Lesen Teil 1 Score", f"{score} / 5")

    with l_tab2:
        st.markdown("**Teil 2 (Zuordnung / Classified Ads):** Select from official Goethe A1 practice scenarios or refresh to generate brand-new alternative scenarios.")
        
        if "dyn_lesen_t2" not in st.session_state or not isinstance(st.session_state.dyn_lesen_t2, list):
            st.session_state.dyn_lesen_t2 = list(LESEN_TEIL2_SCENARIOS)

        valid_lesen_t2 = [s for s in st.session_state.dyn_lesen_t2 if isinstance(s, dict) and "title" in s]
        if not valid_lesen_t2:
            valid_lesen_t2 = list(LESEN_TEIL2_SCENARIOS)
            st.session_state.dyn_lesen_t2 = valid_lesen_t2

        col_lt2_sel, col_lt2_ref = st.columns([4, 1])
        with col_lt2_sel:
            selected_lesen_t2_title = st.selectbox("📂 Select Lesen Teil 2 Scenario Set:", [s["title"] for s in valid_lesen_t2], key="lesen_t2_sel")
        with col_lt2_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_lesen_t2", use_container_width=True):
                with st.spinner("Generating fresh alternative Lesen Teil 2 scenario via AI..."):
                    try:
                        prompt = "Generate a completely new Goethe A1 Lesen Teil 2 scenario set containing a title, desc, and 5 tasks (each with id, situation, site_a_url, site_a, site_b_url, site_b, answer ['Website A', 'Website B'], and explanation). Return strict JSON format as a single object: {\"title\": \"...\", \"desc\": \"...\", \"tasks\": [...]}"
                        res = generate_dynamic_content(prompt, is_json=True)
                        new_scen = json.loads(res)
                        if isinstance(new_scen, dict) and "title" in new_scen:
                            st.session_state.dyn_lesen_t2.append(new_scen)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to refresh: {str(e)}")

        selected_lesen_t2_obj = next((s for s in valid_lesen_t2 if s["title"] == selected_lesen_t2_title), valid_lesen_t2[0])
        
        st.info(f"📌 **Description:** {selected_lesen_t2_obj['desc']}")

        ans_lt2 = {}
        for idx, task in enumerate(selected_lesen_t2_obj["tasks"], start=1):
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <p style="font-weight: 700; color: #1e293b; font-size: 1.05rem; margin-bottom: 12px;">{task['situation']}</p>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #2563eb;">🌐 {task['site_a_url']}</span><br>
                    <p style="white-space: pre-line; color: #334155; font-size: 0.9rem; margin-top: 6px; margin-bottom: 0px;">{task['site_a']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #2563eb;">🌐 {task['site_b_url']}</span><br>
                    <p style="white-space: pre-line; color: #334155; font-size: 0.9rem; margin-top: 6px; margin-bottom: 0px;">{task['site_b']}</p>
                </div>
                """, unsafe_allow_html=True)

            ans_lt2[task["id"]] = st.radio(f"Select website for task {idx}:", ["Website A", "Website B"], key=f"rad_lt2_{selected_lesen_t2_title}_{task['id']}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✔ Submit Lesen Teil 2", type="primary", key="sub_lt2"):
            score = sum(1 for t in selected_lesen_t2_obj["tasks"] if ans_lt2.get(t["id"]) == t["answer"])
            st.markdown("### 📊 Evaluation")
            for idx, t in enumerate(selected_lesen_t2_obj["tasks"], start=1):
                u_ans = ans_lt2.get(t["id"])
                if u_ans == t["answer"]:
                    st.success(f"**Task {idx}: Correct!** (`{t['answer']}`) — {t['explanation']}")
                else:
                    st.error(f"**Task {idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{t['answer']}` — {t['explanation']}")
            st.metric("Lesen Teil 2 Score", f"{score} / 5")

    with l_tab3:
        st.markdown("**Teil 3 (Öffentliche Hinweise / Public Signs):** Select from official Goethe A1 practice scenarios or refresh to generate brand-new alternative scenarios.")
        
        if "dyn_lesen_t3" not in st.session_state or not isinstance(st.session_state.dyn_lesen_t3, list):
            st.session_state.dyn_lesen_t3 = list(LESEN_TEIL3_SCENARIOS)

        valid_lesen_t3 = [s for s in st.session_state.dyn_lesen_t3 if isinstance(s, dict) and "title" in s]
        if not valid_lesen_t3:
            valid_lesen_t3 = list(LESEN_TEIL3_SCENARIOS)
            st.session_state.dyn_lesen_t3 = valid_lesen_t3

        col_lt3_sel, col_lt3_ref = st.columns([4, 1])
        with col_lt3_sel:
            selected_lesen_t3_title = st.selectbox("📂 Select Lesen Teil 3 Scenario Set:", [s["title"] for s in valid_lesen_t3], key="lesen_t3_sel")
        with col_lt3_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_lesen_t3", use_container_width=True):
                with st.spinner("Generating fresh alternative Lesen Teil 3 scenario via AI..."):
                    try:
                        prompt = "Generate a completely new Goethe A1 Lesen Teil 3 scenario set containing a title, desc, example (with statement, sign_title, sign_text, answer, explanation), and 5 tasks (each with id, statement, sign_title, sign_text, options ['richtig', 'falsch'], answer, explanation). Return strict JSON format as a single object: {\"title\": \"...\", \"desc\": \"...\", \"example\": {...}, \"tasks\": [...]}"
                        res = generate_dynamic_content(prompt, is_json=True)
                        new_scen = json.loads(res)
                        if isinstance(new_scen, dict) and "title" in new_scen:
                            st.session_state.dyn_lesen_t3.append(new_scen)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to refresh: {str(e)}")

        selected_lesen_t3_obj = next((s for s in valid_lesen_t3 if s["title"] == selected_lesen_t3_title), valid_lesen_t3[0])
        
        st.info(f"📌 **Description:** {selected_lesen_t3_obj['desc']}")

        ex = selected_lesen_t3_obj["example"]
        st.markdown(f"""
        <div style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <p style="font-weight: 700; color: #475569; margin-bottom: 4px;">BEISPIEL (0)</p>
            <p style="font-weight: 600; color: #1e293b; font-size: 1rem; margin-bottom: 12px;">{ex['statement']}</p>
            <span style="font-size: 0.85rem; font-weight: 700; color: #2563eb;">{ex['sign_title']}</span>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-top: 6px; margin-bottom: 10px;">
                <p style="white-space: pre-line; color: #334155; font-size: 0.95rem; margin-bottom: 0px;">{ex['sign_text']}</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <button disabled style="background: #22c55e; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600;">{ex['answer'].capitalize()}</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ans_lt3 = {}
        for idx, task in enumerate(selected_lesen_t3_obj["tasks"], start=1):
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <p style="font-weight: 700; color: #1e293b; font-size: 1rem; margin-bottom: 12px;">{idx}. {task['statement']}</p>
                <span style="font-size: 0.85rem; font-weight: 700; color: #2563eb;">{task['sign_title']}</span>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-top: 6px; margin-bottom: 12px;">
                    <p style="white-space: pre-line; color: #334155; font-size: 0.95rem; margin-bottom: 0px;">{task['sign_text']}</p>
                </div>
            """, unsafe_allow_html=True)
            ans_lt3[task["id"]] = st.radio(f"Antwort für Aufgabe {idx}:", task["options"], key=f"rad_lt3_{selected_lesen_t3_title}_{task['id']}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✔ Submit Lesen Teil 3", type="primary", key="sub_lt3"):
            score = sum(1 for t in selected_lesen_t3_obj["tasks"] if ans_lt3.get(t["id"]) == t["answer"])
            st.markdown("### 📊 Evaluation")
            for idx, t in enumerate(selected_lesen_t3_obj["tasks"], start=1):
                u_ans = ans_lt3.get(t["id"])
                if u_ans == t["answer"]:
                    st.success(f"**Task {idx}: Correct!** (`{t['answer']}`) — {t['explanation']}")
                else:
                    st.error(f"**Task {idx}: Incorrect.** Your answer: `{u_ans}` | Correct: `{t['answer']}` — {t['explanation']}")
            st.metric("Lesen Teil 3 Score", f"{score} / 5")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 5. GOETHE A1 HÖREN
# ----------------------------------------------------
elif nav_choice == "🎧 Goethe A1 Hören (Listening)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🎧 Goethe A1 Hören Practice (20 Mins, 15 Points across 3 Parts)")

    h_tab1, h_tab2, h_tab3 = st.tabs([
        "Teil 1: 6 Dialogues (Scenarios)", 
        "Teil 2: 4 Announcements (Scenarios)", 
        "Teil 3: 5 Voicemails (Played 2x)"
    ])

    with h_tab1:
        st.markdown("**Teil 1:** Select from official practice scenario sets for dialogues.")
        
        selected_scenario_title = st.selectbox("📂 Select Hören Teil 1 Scenario Set:", [s["title"] for s in HOREN_TEIL1_SCENARIOS])
        selected_scenario_obj = next(s for s in HOREN_TEIL1_SCENARIOS if s["title"] == selected_scenario_title)
        
        st.info(f"📌 **Description:** {selected_scenario_obj['desc']}")

        if st.button(f"▶️ Start Exercise ({selected_scenario_title})", type="primary") or f"hoeren_t1_loaded_{selected_scenario_title}" not in st.session_state:
            with st.spinner(f"Gem is synthesizing 6 dialogues for '{selected_scenario_title}'..."):
                prompt = f"""
                Generate Goethe A1 Hören Teil 1 exercises for the specific theme: '{selected_scenario_title}' ({selected_scenario_obj['desc']}).
                Generate exactly 6 dialogues where two speakers converse naturally. Each dialogue should have 1 multiple-choice task (a/b/c).
                Return strict JSON format:
                {{
                    "scenario_title": "{selected_scenario_title}",
                    "tasks": [
                        {{"id": "h1_1", "full_script": "Dialogue 1 German script...", "question": "Question 1", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."}},
                        {{"id": "h1_2", "full_script": "Dialogue 2 German script...", "question": "Question 2", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."}},
                        {{"id": "h1_3", "full_script": "Dialogue 3 German script...", "question": "Question 3", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."}},
                        {{"id": "h1_4", "full_script": "Dialogue 4 German script...", "question": "Question 4", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A", "explanation": "..."}},
                        {{"id": "h1_5", "full_script": "Dialogue 5 German script...", "question": "Question 5", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B", "explanation": "..."}},
                        {{"id": "h1_6", "full_script": "Dialogue 6 German script...", "question": "Question 6", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C", "explanation": "..."}}
                    ]
                }}
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state[f"hoeren_t1_loaded_{selected_scenario_title}"] = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        cache_key = f"hoeren_t1_loaded_{selected_scenario_title}"
        if cache_key in st.session_state:
            d = st.session_state[cache_key]
            ans1 = {}
            for idx, t in enumerate(d["tasks"], start=1):
                st.markdown(f"#### 🔊 Dialogue {idx} ({selected_scenario_title}) — Played 2x")
                st.audio(generate_german_audio_bytes(t["full_script"]), format="audio/mp3")

                with st.expander(f"👁️ Full Transcript {idx}"): 
                    st.write(t["full_script"])

                st.markdown(f"**Task {idx}: {t['question']}**")
                ans1[t["id"]] = st.radio(f"Select Q{idx}:", t["options"], key=f"rad_ht1_{selected_scenario_title}_{t['id']}")
            if st.button(f"Submit Hören Teil 1 ({selected_scenario_title})"):
                score = sum(1 for t in d["tasks"] if ans1.get(t["id"]) == t["answer"])
                st.success(f"Teil 1 Score for '{selected_scenario_title}': {score} / 6")

    with h_tab2:
        st.markdown("**Teil 2:** Select from official practice scenario sets for announcements.")
        
        selected_scenario_t2 = st.selectbox("📂 Select Hören Teil 2 Scenario Set:", [s["title"] for s in HOREN_TEIL2_SCENARIOS])
        selected_scenario_t2_obj = next(s for s in HOREN_TEIL2_SCENARIOS if s["title"] == selected_scenario_t2)
        
        st.info(f"📌 **Description:** {selected_scenario_t2_obj['desc']}")

        if st.button(f"▶️ Start Exercise ({selected_scenario_t2})", type="primary") or f"hoeren_t2_loaded_{selected_scenario_t2}" not in st.session_state:
            with st.spinner(f"Gem is synthesizing 4 announcements for '{selected_scenario_t2}'..."):
                prompt = f"""
                Generate Goethe A1 Hören Teil 2 exercises for the specific theme: '{selected_scenario_t2}' ({selected_scenario_t2_obj['desc']}).
                Generate exactly 4 announcements with 1 Richtig/Falsch task each.
                Return strict JSON format:
                {{
                    "scenario_title": "{selected_scenario_t2}",
                    "tasks": [
                        {{"id": "h2_1", "script": "Announcement 1 transcript...", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."}},
                        {{"id": "h2_2", "script": "Announcement 2 transcript...", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."}},
                        {{"id": "h2_3", "script": "Announcement 3 transcript...", "statement": "Statement 3", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "..."}},
                        {{"id": "h2_4", "script": "Announcement 4 transcript...", "statement": "Statement 4", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "..."}}
                    ]
                }}
                """
                try:
                    json_str = generate_dynamic_content(prompt, is_json=True)
                    st.session_state[f"hoeren_t2_loaded_{selected_scenario_t2}"] = json.loads(json_str)
                except Exception as e: st.error(f"Error: {str(e)}")

        cache_key_t2 = f"hoeren_t2_loaded_{selected_scenario_t2}"
        if cache_key_t2 in st.session_state:
            d2 = st.session_state[cache_key_t2]
            ans2 = {}
            for idx, t in enumerate(d2["tasks"], start=1):
                st.markdown(f"#### 🔊 Announcement {idx} ({selected_scenario_t2}) — Played 1x")
                st.audio(generate_german_audio_bytes(t["script"]), format="audio/mp3")

                with st.expander(f"👁️ Transcript {idx}"): 
                    st.write(t["script"])

                st.markdown(f"**Task {idx}: {t['statement']}**")
                ans2[t["id"]] = st.radio(f"Select Q{idx}:", t["options"], key=f"rad_ht2_{selected_scenario_t2}_{t['id']}")
            if st.button(f"Submit Hören Teil 2 ({selected_scenario_t2})"):
                score = sum(1 for t in d2["tasks"] if ans2.get(t["id"]) == t["answer"])
                st.success(f"Teil 2 Score for '{selected_scenario_t2}': {score} / 4")

    with h_tab3:
        st.info("ℹ️ Teil 3: 5 phone voicemails played TWICE. Choose A, B, or C.")
        if st.button("🎲 Generate Hören Teil 3 Scenario", type="primary") or st.button("🔄 Generate New Hören Teil 3 Audio & Tasks"):
            with st.spinner("Gem is synthesizing 5 new voicemail messages..."):
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
                    json_str = generate_dynamic_content(prompt, is_json=True)
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
    st.subheader("✍️ Goethe A1 Schreiben Practice (20 Mins, 2 Parts)")

    s_tab1, s_tab2 = st.tabs([
        "Teil 1: Formular (Official 9 Scenarios)", 
        "Teil 2: Mitteilung (Official 9 Scenarios)"
    ])

    with s_tab1:
        st.markdown("**Teil 1 (Formular):** Select from official Goethe A1 practice scenarios or refresh to generate brand-new alternative form-filling scenarios.")
        
        if "dyn_schreiben_t1" not in st.session_state or not isinstance(st.session_state.dyn_schreiben_t1, list):
            st.session_state.dyn_schreiben_t1 = list(SCHREIBEN_TEIL1_SCENARIOS)

        valid_schreiben_t1 = [s for s in st.session_state.dyn_schreiben_t1 if isinstance(s, dict) and "title" in s]
        if not valid_schreiben_t1:
            valid_schreiben_t1 = list(SCHREIBEN_TEIL1_SCENARIOS)
            st.session_state.dyn_schreiben_t1 = valid_schreiben_t1

        col_st1_sel, col_st1_ref = st.columns([4, 1])
        with col_st1_sel:
            selected_schreiben_t1_title = st.selectbox("📂 Select Schreiben Teil 1 Scenario Set:", [s["title"] for s in valid_schreiben_t1], key="schreiben_t1_sel")
        with col_st1_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_schreiben_t1", use_container_width=True):
                with st.spinner("Generating fresh alternative Schreiben Teil 1 scenario via AI..."):
                    try:
                        prompt = "Generate a completely new Goethe A1 Schreiben Teil 1 scenario containing title, desc, aufgabe, form_title, and fields (a list of objects with id, label, default (optional), answer (if is_gap), is_gap (true/false), placeholder, options (optional)). Return strict JSON format as a single object: {\"title\": \"...\", \"desc\": \"...\", \"aufgabe\": \"...\", \"form_title\": \"...\", \"fields\": [...]}"
                        res = generate_dynamic_content(prompt, is_json=True)
                        new_scen = json.loads(res)
                        if isinstance(new_scen, dict) and "title" in new_scen:
                            st.session_state.dyn_schreiben_t1.append(new_scen)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to refresh: {str(e)}")

        selected_schreiben_t1_obj = next((s for s in valid_schreiben_t1 if s["title"] == selected_schreiben_t1_title), valid_schreiben_t1[0])
        
        st.markdown(f"""
        <div style="background: #f1f5f9; border-left: 5px solid #8b5cf6; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
            <p style="font-weight: 700; color: #6d28d9; margin-bottom: 8px;">📋 Aufgabe</p>
            <p style="white-space: pre-line; color: #1e293b; margin-bottom: 0px;">{selected_schreiben_t1_obj['aufgabe']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### 📄 {selected_schreiben_t1_obj['form_title']}")
        
        user_form_inputs = {}
        for field in selected_schreiben_t1_obj["fields"]:
            if not field.get("is_gap", False):
                st.text_input(field["label"], value=field.get("default", ""), disabled=True, key=f"disabled_{selected_schreiben_t1_title}_{field['id']}")
            else:
                if "options" in field:
                    user_form_inputs[field["id"]] = st.radio(field["label"], field["options"], key=f"gap_rad_{selected_schreiben_t1_title}_{field['id']}")
                else:
                    user_form_inputs[field["id"]] = st.text_input(field["label"], placeholder=field.get("placeholder", "..."), key=f"gap_inp_{selected_schreiben_t1_title}_{field['id']}")

        st.markdown("##### ⌨️ Special German Characters")
        sc_cols = st.columns(7)
        chars = ["ä", "ö", "ü", "ß", "Ä", "Ö", "Ü"]
        for idx, ch in enumerate(chars):
            sc_cols[idx].code(ch)

        col_b_clear, col_b_check = st.columns(2)
        with col_b_clear:
            if st.button("✖️ Clear Form", use_container_width=True):
                st.rerun()
        with col_b_check:
            submit_form_btn = st.button("✔ Check Form", type="primary", use_container_width=True)

        if submit_form_btn:
            score = 0
            total_gaps = sum(1 for f in selected_schreiben_t1_obj["fields"] if f.get("is_gap", False))
            st.markdown("### 📊 Evaluation Results")
            for field in selected_schreiben_t1_obj["fields"]:
                if field.get("is_gap", False):
                    u_val = str(user_form_inputs.get(field["id"], "")).strip().lower()
                    c_val = str(field["answer"]).strip().lower()
                    if u_val == c_val or c_val in u_val:
                        score += 1
                        st.success(f"**{field['label']}** Correct! (`{field['answer']}`)")
                    else:
                        st.error(f"**{field['label']}** Incorrect. Your answer: `{user_form_inputs.get(field['id'], '')}` | Correct: `{field['answer']}`")
            st.metric("Formular Score", f"{score} / {total_gaps}")

    with s_tab2:
        st.markdown("**Teil 2 (Mitteilung):** Select from official Goethe A1 practice scenarios or refresh to generate brand-new alternative message-writing scenarios.")
        
        if "dyn_schreiben_t2" not in st.session_state or not isinstance(st.session_state.dyn_schreiben_t2, list):
            st.session_state.dyn_schreiben_t2 = list(SCHREIBEN_TEIL2_SCENARIOS)

        valid_schreiben_t2 = [s for s in st.session_state.dyn_schreiben_t2 if isinstance(s, dict) and "title" in s]
        if not valid_schreiben_t2:
            valid_schreiben_t2 = list(SCHREIBEN_TEIL2_SCENARIOS)
            st.session_state.dyn_schreiben_t2 = valid_schreiben_t2

        col_st2_sel, col_st2_ref = st.columns([4, 1])
        with col_st2_sel:
            selected_schreiben_t2_title = st.selectbox("📂 Select Schreiben Teil 2 Scenario Set:", [s["title"] for s in valid_schreiben_t2], key="schreiben_t2_select")
        with col_st2_ref:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scenarios", key="ref_schreiben_t2", use_container_width=True):
                with st.spinner("Generating fresh alternative Schreiben Teil 2 scenario via AI..."):
                    try:
                        prompt = "Generate a completely new Goethe A1 Schreiben Teil 2 scenario containing title, desc, aufgabe_text, points (list of 3 strings), and prompt (sample answer). Return strict JSON format as a single object: {\"title\": \"...\", \"desc\": \"...\", \"aufgabe_text\": \"...\", \"points\": [\"...\", \"...\", \"...\"], \"prompt\": \"...\"}"
                        res = generate_dynamic_content(prompt, is_json=True)
                        new_scen = json.loads(res)
                        if isinstance(new_scen, dict) and "title" in new_scen:
                            st.session_state.dyn_schreiben_t2.append(new_scen)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to refresh: {str(e)}")

        selected_schreiben_t2_obj = next((s for s in valid_schreiben_t2 if s["title"] == selected_schreiben_t2_title), valid_schreiben_t2[0])
        
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 1.2rem; margin-right: 8px;">📄</span>
                <span style="font-weight: 700; font-size: 1.1rem; color: #1e293b;">Aufgabe (Task)</span>
            </div>
            <p style="white-space: pre-line; color: #334155; font-size: 0.95rem; line-height: 1.5; margin-bottom: 16px;">{selected_schreiben_t2_obj['aufgabe_text']}</p>
        """, unsafe_allow_html=True)

        for pt in selected_schreiben_t2_obj["points"]:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; font-weight: 500; color: #1e293b;">
                {pt}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("✨ Redemittel (Ready Phrases)"):
            st.markdown("""
            * **Anrede (Salutation):** *Sehr geehrte Damen und Herren,* / *Sehr geehrte(r) Frau/Herr [Name],* / *Liebe(r) [Name],*
            * **Grund (Reason):** *ich schreibe Ihnen, weil...* / *ich möchte...* / *ich habe eine Frage...*
            * **Bitten / Fragen (Requests / Questions):** *Könnten Sie mir bitte...* / *Hätten Sie am... Zeit?* / *Wann kann ich...*
            * **Gruß (Sign-off):** *Mit freundlichen Grüßen,* / *Liebe Grüße,*
            """)

        with st.expander("📖 Sample Answer (Musterlösung)"):
            st.info(selected_schreiben_t2_obj['prompt'])

        st.markdown("### Your Text")
        u_email = st.text_area("Write your text here...", height=160, key=f"email_resp_{selected_schreiben_t2_title}", placeholder="Write your text here...")
        
        word_count = len(u_email.strip().split()) if u_email.strip() else 0
        st.caption(f"Word Count: {word_count} (Target: ~30 words)")

        st.markdown("##### Special Characters")
        sc_cols2 = st.columns(7)
        chars2 = ["ä", "ö", "ü", "ß", "Ä", "Ö", "Ü"]
        for idx, ch in enumerate(chars2):
            sc_cols2[idx].code(ch)

        col_t2_clear, col_t2_analyze = st.columns(2)
        with col_t2_clear:
            if st.button("✖️ Clear text", use_container_width=True, key="clear_t2_btn"):
                st.rerun()
        with col_t2_analyze:
            analyze_btn = st.button("✔ Analyze text", type="primary", use_container_width=True, key="analyze_t2_btn")

        if analyze_btn:
            if u_email.strip():
                with st.spinner("Gem is analyzing task fulfillment across all 3 points, word count, and grammar..."):
                    try:
                        eval_prompt = f"""
                        TASK SCENARIO:
                        {selected_schreiben_t2_obj['aufgabe_text']}
                        REQUIRED POINTS:
                        {json.dumps(selected_schreiben_t2_obj['points'])}

                        STUDENT SUBMISSION:
                        {u_email}

                        Evaluate the student's text against official Goethe A1 Schreiben Teil 2 standards:
                        1. Did the student cover all 3 required points?
                        2. Is the word count appropriate (~30 words)?
                        3. Are salutation and sign-off included?
                        4. Grammatical accuracy (V2 word order, verb conjugation, spelling).
                        Provide constructive feedback and a score.
                        """
                        eval_res = generate_dynamic_content(eval_prompt)
                        st.markdown("### 📊 Official Examiner Evaluation")
                        st.write(eval_res)
                    except Exception as e: st.error(f"Error: {str(e)}")
            else:
                st.warning("Please write your text before analyzing.")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. GOETHE A1 SPRECHEN
# ----------------------------------------------------
elif nav_choice == "🗣️ Goethe A1 Sprechen (Speaking)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🗣️ Goethe A1 Sprechen Practice (15 Mins, 3 Parts)")

    sp_tab1, sp_tab2, sp_tab3 = st.tabs([
        "Teil 1: Sich vorstellen & Buchstabieren", 
        "Teil 2: W-Fragen mit Themenkarten", 
        "Teil 3: Bitten mit Bildkarten"
    ])

    with sp_tab1:
        st.markdown("""
        **Teil 1:** Introduce yourself briefly to the examiners (using guides: Name, Jahre, alt, Herkunft, Wohnort, Sprachen, Beruf, Hobby) and spell a word or state your phone number/ZIP code.
        """)
        rec_t1 = mic_recorder(start_prompt="Record Self-Introduction 🎙️", stop_prompt="Stop Recording 🛑", key="rec_sp_t1")
        if rec_t1:
            st.audio(rec_t1['bytes'], format='audio/wav')
            if st.button("Evaluate Introduction"):
                with st.spinner("Gem is analyzing introduction..."):
                    try:
                        audio_part = types.Part.from_bytes(data=rec_t1['bytes'], mime_type="audio/wav")
                        eval_res = client.models.generate_content(
                            model=FALLBACK_MODELS[0],
                            contents=["Transcribe audio and evaluate candidate self-introduction and spelling against Goethe A1 criteria.", audio_part],
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                        )
                        st.write(eval_res.text)
                    except Exception as e: st.error(f"Error: {str(e)}")

    with sp_tab2:
        st.markdown("**Teil 2:** Draw a card with a theme and a prompt word, formulate a basic question to ask a partner, and answer their question in return.")
        
        col_sp2_a, col_sp2_b = st.columns(2)
        with col_sp2_a:
            if st.button("🎲 Draw Topic Card", type="primary"):
                with st.spinner("Gem is drawing card..."):
                    try:
                        st.session_state.card_t2 = generate_dynamic_content("Generate Goethe A1 Sprechen topic card (e.g. Thema: 'Einkaufen', Wort: 'Brot').")
                    except Exception as e: st.error(f"Error: {str(e)}")
        with col_sp2_b:
            if st.button("🔄 Draw Another Topic Card"):
                with st.spinner("Gem is drawing a new card..."):
                    try:
                        st.session_state.card_t2 = generate_dynamic_content("Generate Goethe A1 Sprechen topic card with a completely different theme.")
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
                                model=FALLBACK_MODELS[0],
                                contents=[f"Card: {st.session_state.card_t2}. Transcribe audio and verify if candidate formed a correct W-question with verb in Position 2.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    with sp_tab3:
        st.markdown("**Teil 3:** Draw a card showing an object or situation and make a simple request or give a polite instruction to your partner.")
        
        col_sp3_a, col_sp3_b = st.columns(2)
        with col_sp3_a:
            if st.button("🎲 Draw Picture Request Card", type="primary"):
                with st.spinner("Gem is drawing card..."):
                    try:
                        st.session_state.card_t3 = generate_dynamic_content("Generate Goethe A1 Sprechen picture request card (e.g. Gegenstand: Bleistift).")
                    except Exception as e: st.error(f"Error: {str(e)}")
        with col_sp3_b:
            if st.button("🔄 Draw Another Picture Card"):
                with st.spinner("Gem is drawing a new picture card..."):
                    try:
                        st.session_state.card_t3 = generate_dynamic_content("Generate a brand new Goethe A1 Sprechen picture card.")
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
                                model=FALLBACK_MODELS[0],
                                contents=[f"Card: {st.session_state.card_t3}. Transcribe audio and verify if candidate formed a correct imperative request with verb in Position 1.", audio_part],
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
                            )
                            st.write(eval_res.text)
                        except Exception as e: st.error(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. GOETHE A1 MOCK EXAMINATION
# ----------------------------------------------------
elif nav_choice == "🏆 Goethe A1 Mock Examination":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("🏆 Full CEFR A1 Timed Mock Examination Simulator")
    st.write("Simulate the exact Goethe-Zertifikat A1 exam with live section-by-section countdown timers (Lesen: 25 mins, Hören: 20 mins, Schreiben: 20 mins, Sprechen: 15 mins). Each attempt randomizes fresh questions.")

    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []
    if "mock_data" not in st.session_state:
        st.session_state.mock_data = None
    if "exam_stage" not in st.session_state:
        st.session_state.exam_stage = "MENU"
    if "section_timer_start" not in st.session_state:
        st.session_state.section_timer_start = 0
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}

    if st.session_state.exam_history:
        st.markdown("### 📊 Progress Report & Score History")
        table_data = {
            "Metric / Section": ["Lesen (max 5)", "Hören (max 3)", "Schreiben (max 4)", "Sprechen (max 3)", "Total Score (max 15)", "Passing Percentage"]
        }
        for i, rec in enumerate(st.session_state.exam_history):
            table_data[f"Attempt {i+1} ({rec['date']})"] = [
                f"{rec['lesen']}/5", 
                f"{rec['hoeren']}/3", 
                f"{rec['schreiben']}/4", 
                f"{rec['sprechen']}/3",
                f"{rec['total']}/15", 
                f"{rec['percentage']}%"
            ]
        st.table(table_data)

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            latest_pct = st.session_state.exam_history[-1]["percentage"]
            st.info(f"🤖 **Gem's Official Exam Readiness Assessment:** Your latest mock score is **{latest_pct}%**. Passing requirement for Goethe A1 is **60%**.")
        with col_h2:
            if st.button("🗑️ Reset All Score History", type="secondary"):
                st.session_state.exam_history = []
                st.success("All score history cleared!")
                st.rerun()

    st.divider()

    if st.session_state.exam_stage != "MENU":
        if st.button("🔄 Reset Current Exam & Return to Menu", type="secondary"):
            st.session_state.mock_data = None
            st.session_state.exam_stage = "MENU"
            st.session_state.exam_answers = {}
            st.rerun()
        st.divider()

    if st.session_state.exam_stage == "MENU":
        if st.button("🚀 Start Full Timed Mock Exam Simulation", type="primary"):
            with st.spinner("Gem is generating a randomized official Goethe A1 simulated examination paper..."):
                seed_val = random.randint(1, 100000)
                mock_prompt = f"""
                Generate a randomized full Goethe-Zertifikat A1 simulated exam paper (Seed: {seed_val}) in strict JSON format.
                Return strict JSON format:
                {{
                    "lesen": {{
                        "text": "Reading passage here...",
                        "questions": [
                            {{"id": "m_l1", "statement": "Statement 1", "options": ["richtig", "falsch"], "answer": "richtig"}},
                            {{"id": "m_l2", "statement": "Statement 2", "options": ["richtig", "falsch"], "answer": "falsch"}},
                            {{"id": "m_l3", "statement": "Statement 3", "options": ["richtig", "falsch"], "answer": "richtig"}},
                            {{"id": "m_l4", "statement": "Statement 4", "options": ["richtig", "falsch"], "answer": "falsch"}},
                            {{"id": "m_l5", "statement": "Statement 5", "options": ["richtig", "falsch"], "answer": "richtig"}}
                        ]
                    }},
                    "hoeren": {{
                        "script": "Hören dialogue transcript here...",
                        "questions": [
                            {{"id": "m_h1", "question": "Question 1", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "a) Option A"}},
                            {{"id": "m_h2", "question": "Question 2", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "b) Option B"}},
                            {{"id": "m_h3", "question": "Question 3", "options": ["a) Option A", "b) Option B", "c) Option C"], "answer": "c) Option C"}}
                        ]
                    }},
                    "schreiben": {{
                        "form_scenario": "Form scenario details...",
                        "form_fields": [
                            {{"id": "mf1", "label": "1. Name", "answer": "Schmidt"}},
                            {{"id": "mf2", "label": "2. Personen", "answer": "2"}},
                            {{"id": "mf3", "label": "3. Tag", "answer": "Freitag"}},
                            {{"id": "mf4", "label": "4. Zahlung", "answer": "Kreditkarte"}}
                        ],
                        "email_prompt": "Write an email to your friend."
                    }},
                    "sprechen": {{
                        "part1_prompt": "Introduce yourself.",
                        "part2_card": "Thema: Urlaub",
                        "part3_card": "Gegenstand: Kugelschreiber"
                    }}
                }}
                """
                try:
                    res_json = generate_dynamic_content(mock_prompt, is_json=True)
                    st.session_state.mock_data = json.loads(res_json)
                    st.session_state.exam_stage = "LESEN"
                    st.session_state.section_timer_start = time.time()
                    st.session_state.exam_answers = {}
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating exam: {str(e)}")

    elif st.session_state.exam_stage == "LESEN":
        duration = 25 * 60
        elapsed = int(time.time() - st.session_state.section_timer_start)
        remaining = duration - elapsed

        if remaining <= 0:
            st.warning("⏱️ Lesen time is up! Proceeding to Hören.")
            st.session_state.exam_stage = "HOEREN"
            st.session_state.section_timer_start = time.time()
            st.rerun()

        st.markdown(f"### 📖 Part 1: Lesen (Reading) — Timer: **{remaining // 60:02d}:{remaining % 60:02d}**")
        exam = st.session_state.mock_data
        st.info(exam["lesen"]["text"])

        m_lesen_ans = {}
        for idx, q in enumerate(exam["lesen"]["questions"], start=1):
            st.markdown(f"**Q{idx}. {q['statement']}**")
            m_lesen_ans[q['id']] = st.radio("Select:", q['options'], key=f"m_l_{q['id']}")

        if st.button("Submit Lesen & Proceed to Hören ➔", type="primary"):
            st.session_state.exam_answers["lesen"] = m_lesen_ans
            st.session_state.exam_stage = "HOEREN"
            st.session_state.section_timer_start = time.time()
            st.rerun()

    elif st.session_state.exam_stage == "HOEREN":
        duration = 20 * 60
        elapsed = int(time.time() - st.session_state.section_timer_start)
        remaining = duration - elapsed

        if remaining <= 0:
            st.warning("⏱️ Hören time is up! Proceeding to Schreiben.")
            st.session_state.exam_stage = "SCHREIBEN"
            st.session_state.section_timer_start = time.time()
            st.rerun()

        st.markdown(f"### 🎧 Part 2: Hören (Listening) — Timer: **{remaining // 60:02d}:{remaining % 60:02d}**")
        exam = st.session_state.mock_data
        st.audio(generate_german_audio_bytes(exam["hoeren"]["script"]), format="audio/mp3")

        with st.expander("👁️ View Transcript"):
            st.write(exam["hoeren"]["script"])

        m_hoeren_ans = {}
        for idx, q in enumerate(exam["hoeren"]["questions"], start=1):
            st.markdown(f"**Q{idx}. {q['question']}**")
            m_hoeren_ans[q['id']] = st.radio("Select choice:", q['options'], key=f"m_h_{q['id']}")

        if st.button("Submit Hören & Proceed to Schreiben ➔", type="primary"):
            st.session_state.exam_answers["hoeren"] = m_hoeren_ans
            st.session_state.exam_stage = "SCHREIBEN"
            st.session_state.section_timer_start = time.time()
            st.rerun()

    elif st.session_state.exam_stage == "SCHREIBEN":
        duration = 20 * 60
        elapsed = int(time.time() - st.session_state.section_timer_start)
        remaining = duration - elapsed

        if remaining <= 0:
            st.warning("⏱️ Schreiben time is up! Proceeding to Sprechen.")
            st.session_state.exam_stage = "SPRECHEN"
            st.session_state.section_timer_start = time.time()
            st.rerun()

        st.markdown(f"### ✍️ Part 3: Schreiben (Writing) — Timer: **{remaining // 60:02d}:{remaining % 60:02d}**")
        exam = st.session_state.mock_data
        st.info(exam["schreiben"]["form_scenario"])

        m_form_inputs = {}
        for f in exam["schreiben"]["form_fields"]:
            m_form_inputs[f["id"]] = st.text_input(f["label"], key=f"m_form_{f['id']}")

        st.markdown("---")
        st.info(exam["schreiben"]["email_prompt"])
        m_email_input = st.text_area("Your German Email Response (~30 words):", key="m_email_resp")

        if st.button("Submit Schreiben & Proceed to Sprechen ➔", type="primary"):
            st.session_state.exam_answers["form"] = m_form_inputs
            st.session_state.exam_answers["email"] = m_email_input
            st.session_state.exam_stage = "SPRECHEN"
            st.session_state.section_timer_start = time.time()
            st.rerun()

    elif st.session_state.exam_stage == "SPRECHEN":
        duration = 15 * 60
        elapsed = int(time.time() - st.session_state.section_timer_start)
        remaining = duration - elapsed

        if remaining <= 0:
            st.warning("⏱️ Sprechen time is up! Submitting exam.")
            st.session_state.exam_stage = "RESULTS"
            st.rerun()

        st.markdown(f"### 🗣️ Part 4: Sprechen (Speaking) — Timer: **{remaining // 60:02d}:{remaining % 60:02d}**")
        exam = st.session_state.mock_data

        st.markdown("#### Teil 1")
        mic_recorder(start_prompt="Record Teil 1 🎙️", stop_prompt="Stop 🛑", key="mock_sp1")
        st.markdown("#### Teil 2")
        mic_recorder(start_prompt="Record Teil 2 🎙️", stop_prompt="Stop 🛑", key="mock_sp2")
        st.markdown("#### Teil 3")
        mic_recorder(start_prompt="Record Teil 3 🎙️", stop_prompt="Stop 🛑", key="mock_sp3")

        if st.button("🏁 Finish Exam & View Scorecard", type="primary"):
            st.session_state.exam_stage = "RESULTS"
            st.rerun()

    elif st.session_state.exam_stage == "RESULTS":
        exam = st.session_state.mock_data
        ans = st.session_state.exam_answers

        lesen_score = sum(1 for q in exam["lesen"]["questions"] if ans.get("lesen", {}).get(q["id"]) == q["answer"])
        hoeren_score = sum(1 for q in exam["hoeren"]["questions"] if ans.get("hoeren", {}).get(q["id"]) == q["answer"])
        form_score = sum(1 for f in exam["schreiben"]["form_fields"] if ans.get("form", {}).get(f["id"], "").strip().lower() == f["answer"].strip().lower())
        sprechen_score = 3
        
        total_score = lesen_score + hoeren_score + form_score + sprechen_score
        total_max = 15
        percentage = int((total_score / total_max) * 100)

        if not st.session_state.exam_history or st.session_state.exam_history[-1]["date"] != time.strftime("%Y-%m-%d %H:%M"):
            st.session_state.exam_history.append({
                "date": time.strftime("%Y-%m-%d %H:%M"),
                "lesen": lesen_score,
                "hoeren": hoeren_score,
                "schreiben": form_score,
                "sprechen": sprechen_score,
                "total": total_score,
                "percentage": percentage
            })

        st.success(f"🎉 **Mock Examination Completed!** Final Score: **{total_score} / 15** ({percentage}%)")
        st.metric("📖 Lesen Score", f"{lesen_score} / 5")
        st.metric("🎧 Hören Score", f"{hoeren_score} / 3")
        st.metric("✍️ Schreiben Score", f"{form_score} / 4")
        st.metric("🗣️ Sprechen Score", f"{sprechen_score} / 3")

        if st.button("🔄 Return to Mock Exam Menu & Retake", type="primary"):
            st.session_state.mock_data = None
            st.session_state.exam_stage = "MENU"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 9. A1 & A2 SHORT STORIES
# ----------------------------------------------------
elif nav_choice == "📖 A1 & A2 Short Stories":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
    st.subheader("📖 Enchanted Storybook Reader: 20 Fairy Tales & 20 Classics")
    st.write("Immerse yourself in 20 A1 fairy tales and 20 A2 classic fictions with complete audio narration and sentence-by-sentence translation.")

    story_level = st.radio("Select CEFR Level:", ["A1 Level (20 Fairy Tales & Disney Stories)", "A2 Level (20 Fiction Classics & Novels)"], horizontal=True)

    if story_level == "A1 Level (20 Fairy Tales & Disney Stories)":
        a1_20_stories = {
            "Aschenputtel (Cinderella)": "Cinderella",
            "Rotkäppchen (Little Red Riding Hood)": "Little Red Riding Hood",
            "Die kleine Meerjungfrau (The Little Mermaid)": "The Little Mermaid",
            "Schneewittchen (Snow White)": "Snow White",
            "Die Schöne und das Biest (Beauty and the Beast)": "Beauty and the Beast",
            "Aladdin und die Wunderlampe (Aladdin)": "Aladdin",
            "Dornröschen (Sleeping Beauty)": "Sleeping Beauty",
            "Rapunzel (Tangled)": "Rapunzel",
            "Der König der Löwen (The Lion King)": "The Lion King",
            "Die Eiskönigin (Frozen)": "Frozen",
            "Hänsel und Gretel": "Hansel and Gretel",
            "Der Froschkönig (The Frog Prince)": "The Frog Prince",
            "Peter Pan": "Peter Pan",
            "Pinocchio": "Pinocchio",
            "Dumbo": "Dumbo",
            "Bambi": "Bambi",
            "Das Dschungelbuch (The Jungle Book)": "The Jungle Book",
            "Alice im Wunderland (Alice in Wonderland)": "Alice in Wonderland",
            "Herkules (Hercules)": "Hercules",
            "Mulan": "Mulan"
        }
        story_choice_de = st.selectbox("Select A1 Story:", list(a1_20_stories.keys()))
        story_choice_en = a1_20_stories[story_choice_de]
    else:
        a2_20_stories = {
            "Moby Dick": "Moby Dick",
            "Die Schatzinsel (Treasure Island)": "Treasure Island",
            "Robinson Crusoe": "Robinson Crusoe",
            "Gullivers Reisen (Gulliver's Travels)": "Gullivers Travels",
            "Der Graf von Monte Christo (Count of Monte Cristo)": "Count of Monte Cristo",
            "Sherlock Holmes": "Sherlock Holmes",
            "Dracula": "Dracula",
            "Frankenstein": "Frankenstein",
            "In 80 Tagen um die Welt (Around the World in 80 Days)": "Around the World in 80 Days",
            "Der alte Mann und das Meer (The Old Man and the Sea)": "The Old Man and the Sea",
            "Die Zeitmaschine (The Time Machine)": "The Time Machine",
            "Krieg der Welten (The War of the Worlds)": "Krieg der Welten",
            "Der letzte Mohikaner (The Last of the Mohicans)": "Der letzte Mohikaner",
            "Jane Eyre": "Jane Eyre",
            "Stolz und Vorurteil (Pride and Prejudice)": "Stolz und Vorurteil",
            "Oliver Twist": "Oliver Twist",
            "Eine Weihnachtsgeschichte (A Christmas Carol)": "Eine Weihnachtsgeschichte",
            "Die drei Musketiere (The Three Musketeers)": "Die drei Musketiere",
            "Tom Sawyers Abenteuer (The Adventures of Tom Sawyer)": "Tom Sawyers Abenteuer",
            "Don Quijote (Don Quixote)": "Don Quijote"
        }
        story_choice_de = st.selectbox("Select A2 Story:", list(a2_20_stories.keys()))
        story_choice_en = a2_20_stories[story_choice_de]

    num_parts = st.slider("Select Number of Story Parts (Up to 40):", min_value=10, max_value=40, value=20, step=5)

    if st.button("📖 Open Enchanted Storybook", type="primary"):
        with st.spinner(f"Gem is compiling the {num_parts}-part story..."):
            story_prompt = f"""
            Generate a rich story for '{story_choice_de} ({story_choice_en})' at level '{story_level}'.
            Create exactly {num_parts} distinct narrative parts/sentences.
            For each part, provide:
            1. 'german': German sentence/paragraph.
            2. 'english': English translation.
            Also provide:
            - 'main_image_url': A cover image URL.
            - 'full_audio_text': The entire German story as one continuous uncut string.
            - 'full_english_text': The entire English story translation as one continuous paragraph.

            Return strict JSON format:
            {{
                "title_de": "{story_choice_de}",
                "title_en": "{story_choice_en}",
                "main_image_url": "https://picsum.photos/seed/{story_choice_en.replace(' ', '')}cover/800/400",
                "full_audio_text": "Full continuous German text...",
                "full_english_text": "Full continuous English translation...",
                "paragraphs": [
                    {{"german": "German part 1...", "english": "English part 1..."}},
                    {{"german": "German part 2...", "english": "English part 2..."}}
                ]
            }}
            """
            try:
                story_json = generate_cached_content(story_prompt, is_json=True)
                st.session_state.active_story = json.loads(story_json)
            except Exception as e:
                st.error(f"Error loading story: {str(e)}")

    if "active_story" in st.session_state:
        st.markdown(f"## 👑 {st.session_state.active_story['title_de']} / *{st.session_state.active_story['title_en']}*")
        st.image(st.session_state.active_story["main_image_url"], use_column_width=True)
        
        story_tab1, story_tab2 = st.tabs(["📖 Sentence-by-Sentence Reader", "📜 Full Story Reader"])
        
        with story_tab1:
            st.markdown("#### 🎧 Section Audio Narration (Full Story)")
            col_fa, _ = st.columns([0.5, 10])
            with col_fa:
                if st.button("🔊", key="audio_full_story_btn"):
                    play_direct_audio(st.session_state.active_story['full_audio_text'], "full_story_audio")
            st.divider()

            for idx, p in enumerate(st.session_state.active_story["paragraphs"], 1):
                st.markdown(f"**Part {idx}**")
                col_aud, col_text = st.columns([0.5, 10])
                with col_aud:
                    if st.button("🔊", key=f"audio_story_p_{idx}   "):
                        play_direct_audio(p["german"], f"story_p_{idx}")
                with col_text:
                    st.info(f"**🇩🇪 German:** {p['german']}")
                    st.success(f"**🇬🇧 English:** {p['english']}")
                st.divider()

        with story_tab2:
            st.markdown("### 📜 Full Story Combined Reading")
            col_fa2, _ = st.columns([0.5, 10])
            with col_fa2:
                if st.button("🔊", key="audio_full_story_combined"):
                    play_direct_audio(st.session_state.active_story['full_audio_text'], "full_story_combined_audio")
            st.caption("Click speaker icon to listen to the entire German story.")
            
            st.markdown("#### 🇩🇪 German Full Text")
            st.info(st.session_state.active_story['full_audio_text'])
            
            st.markdown("#### 🇬🇧 English Full Translation")
            st.success(st.session_state.active_story['full_english_text'])

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 10. ASK GEM
# ----------------------------------------------------
elif nav_choice == "💬 Ask Gem (AI Tutor)":
    st.markdown('<div class="accent-card">', unsafe_allow_html=True)
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
if "bot_knowledge_feedback" not in st.session_state:
    st.session_state.bot_knowledge_feedback = ""

st.markdown('<div class="floating-bot-container">', unsafe_allow_html=True)

if st.session_state.bot_open:
    st.markdown("""
    <div class="bot-popout-box">
    """, unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns([4, 1])
    with col_b1:
        st.markdown("🤖 **Gem (AI Tutor):**")
    with col_b2:
        if st.button("✕", key="close_bot_popout"):
            st.session_state.bot_open = False
            st.rerun()

    bot_query = st.text_input("Ask me anything (e.g. Dative case):", key="bot_chat_input", placeholder="Type your question here...")
    if bot_query:
        try:
            augmented_prompt = f"{bot_query}\n\n[Instruction: Explain the grammar concept clearly and conclude with an interactive knowledge check question for the user.]"
            ans = generate_dynamic_content(augmented_prompt)
            st.session_state.bot_last_response = ans
            st.session_state.bot_knowledge_feedback = ""
        except Exception as e:
            st.session_state.bot_last_response = f"Error: {str(e)}"

    if st.session_state.bot_last_response:
        st.write(st.session_state.bot_last_response)
        st.markdown("---")
        st.markdown("✍️ **Answer Knowledge Check Here:**")
        user_kc_answer = st.text_input("Answer to Gem's question:", key="bot_kc_input")
        if st.button("Submit Answer to Gem"):
            with st.spinner("Gem is grading your answer..."):
                eval_prompt = f"The user was asked a knowledge check question based on: '{st.session_state.bot_last_response}'. The user answered: '{user_kc_answer}'. Grade this answer, explain why it is correct or incorrect, and provide encouragement."
                feedback = generate_dynamic_content(eval_prompt)
                st.session_state.bot_knowledge_feedback = feedback
        
        if st.session_state.bot_knowledge_feedback:
            st.info(st.session_state.bot_knowledge_feedback)

    st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.bot_open:
    if st.button("🤖 Chat with Gem", key="open_bot_btn", type="primary"):
        st.session_state.bot_open = True
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
