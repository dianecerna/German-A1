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

FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]

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

# Toddler Space Visual Data Bank
TODDLER_VISUAL_TOPICS = {
    "Körperteile (Body Parts)": [
        {"term": "der Kopf", "en": "Head", "icon": "🧠", "desc": "Used for thinking and wearing hats."},
        {"term": "das Auge", "en": "Eye", "icon": "👁️", "desc": "Used for seeing colors and reading."},
        {"term": "die Nase", "en": "Nose", "icon": "👃", "desc": "Used for smelling flowers and food."},
        {"term": "der Mund", "en": "Mouth", "icon": "👄", "desc": "Used for speaking German and eating."},
        {"term": "das Ohr", "en": "Ear", "icon": "👂", "desc": "Used for listening to German audio."},
        {"term": "die Hand", "en": "Hand", "icon": "✋", "desc": "Used for writing and waving."},
        {"term": "das Bein", "en": "Leg", "icon": "🦵", "desc": "Used for walking and running."}
    ],
    "Verkehrsmittel (Transportation)": [
        {"term": "das Auto", "en": "Car", "icon": "🚗", "desc": "Four-wheeled motor vehicle for roads."},
        {"term": "der Bus", "en": "Bus", "icon": "🚌", "desc": "Large public transport vehicle."},
        {"term": "der Zug", "en": "Train", "icon": "🚆", "desc": "Rail transport connecting cities."},
        {"term": "das Flugzeug", "en": "Airplane", "icon": "✈️", "desc": "Aircraft for flying across countries."},
        {"term": "das Fahrrad", "en": "Bicycle", "icon": "🚲", "desc": "Two-wheeled pedal vehicle."},
        {"term": "das Schiff", "en": "Ship", "icon": "🚢", "desc": "Large watercraft for seas."}
    ],
    "Farben (Colors)": [
        {"term": "rot", "en": "Red", "icon": "🔴", "desc": "Color of apples and stop signs."},
        {"term": "blau", "en": "Blue", "icon": "🔵", "desc": "Color of the sky and ocean."},
        {"term": "gelb", "en": "Yellow", "icon": "🟡", "desc": "Color of the sun and lemons."},
        {"term": "grün", "en": "Green", "icon": "🟢", "desc": "Color of grass and trees."},
        {"term": "schwarz", "en": "Black", "icon": "⬛", "desc": "Darkest color."},
        {"term": "weiß", "en": "White", "icon": "⬜", "desc": "Color of snow and clouds."}
    ],
    "Haus & Möbel (House & Furniture)": [
        {"term": "das Zimmer", "en": "Room", "icon": "🚪", "desc": "An enclosed space inside a house."},
        {"term": "die Küche", "en": "Kitchen", "icon": "🍳", "desc": "Where food is prepared and cooked."},
        {"term": "das Bad", "en": "Bathroom", "icon": "🚿", "desc": "Where you wash and shower."},
        {"term": "der Tisch", "en": "Table", "icon": "🪵", "desc": "Furniture with a flat top for dining or work."},
        {"term": "der Stuhl", "en": "Chair", "icon": "🪑", "desc": "Seat for one person."},
        {"term": "das Bett", "en": "Bed", "icon": "🛏️", "desc": "Piece of furniture for sleeping."}
    ],
    "Schulsachen (School Supplies)": [
        {"term": "das Buch", "en": "Book", "icon": "📖", "desc": "Bound pages for reading and learning."},
        {"term": "der Stift", "en": "Pen / Pencil", "icon": "✏️", "desc": "Writing instrument."},
        {"term": "das Heft", "en": "Notebook", "icon": "📓", "desc": "Book for taking notes in class."},
        {"term": "die Schultasche", "en": "School Bag", "icon": "🎒", "desc": "Bag used by students to carry supplies."},
        {"term": "der Tisch", "en": "School Desk", "icon": "🪞", "desc": "Desk used in classrooms."}
    ],
    "Uhrzeit & Zeit (Telling Time)": [
        {"term": "die Uhr", "en": "Clock / Watch", "icon": "⏰", "desc": "Device for measuring time."},
        {"term": "die Stunde", "en": "Hour", "icon": "⌛", "desc": "Sixty minutes of time."},
        {"term": "die Minute", "en": "Minute", "icon": "⏱️", "desc": "Sixty seconds of time."},
        {"term": "der Morgen", "en": "Morning", "icon": "🌅", "desc": "Early part of the day."},
        {"term": "der Abend", "en": "Evening", "icon": "🌆", "desc": "End of the day before night."}
    ]
}

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

# Lesen Teil 1 Official Scenarios Bank (Matching exact app layout & screenshot 51)
LESEN_TEIL1_SCENARIOS = [
    {
        "title": "Flughafen & Grillfest",
        "desc": "Two short messages: airport pickup (email from Lena to Tom) and a garden barbecue (letter to Sofia) – 5 tasks, Richtig/Falsch.",
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
        "title": "Vegetarisches Essen & Fußballtraining",
        "desc": "Two short messages: vegetarian dinner and football training – 5 tasks, Richtig/Falsch.",
        "text1_label": "E-Mail (Abendessen)",
        "text1": "Hallo Anna,\n\nich koche heute Abend vegetarisch. Es gibt Gemüselasuppe und Salat. Komm doch um 19 Uhr zu mir!\nLiebe Grüße,\nMaria",
        "text2_label": "SMS (Fußball)",
        "text2": "Hallo zusammen, das Fußballtraining am Mittwoch fällt leider aus, weil der Platz nass ist. Nächste Woche spielen wir wieder normal.\nGruß, Trainer Stefan",
        "questions": [
            {"id": "lt1_21", "statement": "Maria kocht heute Abend Fleisch.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Maria kocht vegetarisch (Gemüsesuppe und Salat)."},
            {"id": "lt1_22", "statement": "Das Essen beginnt um 19 Uhr.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Maria lädt Anna um 19 Uhr ein."},
            {"id": "lt1_23", "statement": "Das Fußballtraining findet am Mittwoch statt.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Das Training fällt aus."},
            {"id": "lt1_24", "statement": "Der Sportplatz ist nass.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Grund für den Ausfall ist ein nasser Platz."},
            {"id": "lt1_25", "statement": "Nächste Woche findet das Training wieder statt.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Der Trainer schreibt: 'Nächste Woche spielen wir wieder normal.'"}
        ]
    },
    {
        "title": "Umzugshilfe & Katze im Garten",
        "desc": "Two short notices about moving help and a found cat – 5 tasks, Richtig/Falsch.",
        "text1_label": "Zettel am Schwarzen Brett",
        "text1": "Hallo liebe Nachbarn, ich ziehe am 1. September in eine neue Wohnung und suche Helfer für Möbeltragen. Es gibt Pizza und Getränke für alle!",
        "text2_label": "Nachricht",
        "text2": "Guten Tag, wir haben seit gestern eine kleine graue Katze im Garten. Sie hat ein rotes Halsband. Wem gehört sie? Bitte melden unter Tel. 0171...",
        "questions": [
            {"id": "lt1_31", "statement": "Der Autor zieht im August um.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Der Umzug ist am 1. September."},
            {"id": "lt1_32", "statement": "Helfer bekommen Pizza und Getränke.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Es gibt Pizza und Getränke für alle."},
            {"id": "lt1_33", "statement": "Die gefundene Katze ist schwarz.", "options": ["richtig", "falsch"], "answer": "falsch", "explanation": "Die Katze ist grau."},
            {"id": "lt1_34", "statement": "Die Katze trägt ein rotes Halsband.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Im Text steht: 'Sie hat ein rotes Halsband.'"},
            {"id": "lt1_35", "statement": "Man kann den Finder telefonisch erreichen.", "options": ["richtig", "falsch"], "answer": "richtig", "explanation": "Es ist eine Telefonnummer angegeben."}
        ]
    }
]

# Lesen Teil 2 Official Scenarios Bank (Matching exact app layout & screenshot 52)
LESEN_TEIL2_SCENARIOS = [
    {
        "title": "Fahrrad, Schwimmbad & Pizza",
        "desc": "Information about buying a bicycle, swimming pools, and ordering pizza – 5 tasks, a/b.",
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
        "desc": "Information about hotel bookings, repair shops, and babysitters – 5 tasks, a/b.",
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
    }
]

# Lesen Teil 3 Official Scenarios Bank (Matching exact app layout & screenshot 53)
LESEN_TEIL3_SCENARIOS = [
    {
        "title": "Bäckerei, Markt & Parkhaus",
        "desc": "Signs and notices about a bakery, language school, library and car park – 5 tasks, Richtig/Falsch.",
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
        "title": "Haltestelle, Schule & Freibad",
        "desc": "Signs and notices about public transport, schools, and pools – 5 tasks, Richtig/Falsch.",
        "example": {
            "statement": "Die Buslinie 14 fährt zum Bahnhof.",
            "sign_title": "AN DER BUSHALTESTELLE",
            "sign_text": "Buslinie 14 Richtung Hauptbahnhof fährt alle 10 Minuten.",
            "answer": "richtig",
            "explanation": "Die Haltestelle zeigt die Linie 14 zum Hauptbahnhof."
        },
        "tasks": [
            {
                "id": "lt3_21",
                "statement": "Kinder unter 6 Jahren zahlen keinen Eintritt ins Schwimmbad.",
                "sign_title": "FREIBAD KASSE",
                "sign_text": "Eintrittspreise:\nErwachsene 4,00 €\nKinder unter 6 Jahren frei!",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Auf dem Schild steht klar 'Kinder unter 6 Jahren frei!'."
            },
            {
                "id": "lt3_22",
                "statement": "Der Aufzug im Bahnhof funktioniert.",
                "sign_title": "AM AUFZUG",
                "sign_text": "Achtung! Aufzug außer Betrieb wegen Reparatur.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Der Aufzug ist wegen Reparatur außer Betrieb."
            },
            {
                "id": "lt3_23",
                "statement": "Im Supermarkt gibt es frischen Fisch.",
                "sign_title": "FISCHTHEKE",
                "sign_text": "Heute frischer Lachs und Forelle direkt vom Markt.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Es gibt frischen Lachs und Forelle."
            },
            {
                "id": "lt3_24",
                "statement": "Hunde sind im Lebensmittelgeschäft erlaubt.",
                "sign_title": "EINGANG SUPERMARKT",
                "sign_text": "Aus hygienischen Gründen sind Hunde im Geschäft leider nicht erlaubt.",
                "options": ["richtig", "falsch"],
                "answer": "falsch",
                "explanation": "Hunde sind laut Schild nicht erlaubt."
            },
            {
                "id": "lt3_25",
                "statement": "Die Postfiliale schließt samstags um 13 Uhr.",
                "sign_title": "POSTFILIALE",
                "sign_text": "Öffnungszeiten Samstag: 9:00 bis 13:00 Uhr.",
                "options": ["richtig", "falsch"],
                "answer": "richtig",
                "explanation": "Samstags schließt sie um 13:00 Uhr."
            }
        ]
    }
]

# Schreiben Teil 1 Official Scenarios Bank (All 9 exact scenarios)
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
        "prompt": "Liebe Sophie,\n\nich bin endlich in meine neue Wohnung umgezogen! Am Freitag mache ich um 19 Uhr eine kleine Einweihungsparty. Hast du Zeit und kommst auch?\n\nLiebe Grüße,\n[Dein Name]"
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
    "🧸 Toddler Visual Space (Interactive Vocab)",
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
    st.write("Complete Goethe A1 curriculum preparation featuring the Toddler Visual Space, official 1000-word flashcards, grammar exercises, fully structured 3-part Goethe exam simulators with live countdowns, and enchanted storybooks.")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("📖 Lesen & ✍️ Schreiben")
        st.markdown("""
        * **Lesen (25 Mins - 15 Tasks across 3 Parts):**
          - Teil 1: Short Emails (Richtig/Falsch) - *Fully integrated with official scenarios & email layout UI!*
          - Teil 2: Classified Ads (Option A or B) - *Fully integrated with web links & side-by-side site choices!*
          - Teil 3: Public Signs (Richtig/Falsch) - *Fully integrated with notice boxes & example items!*
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
# 2. TODDLER VISUAL SPACE (INTERACTIVE VOCAB)
# ----------------------------------------------------
elif nav_choice == "🧸 Toddler Visual Space (Interactive Vocab)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🧸 Toddler Visual Space: Essential A1 Terms & Visual Matching")
    st.write("Explore fundamental everyday German terms with visual icons, descriptions, audio pronunciation, and interactive matching challenges.")

    selected_toddler_cat = st.selectbox("📂 Select Visual Category:", list(TODDLER_VISUAL_TOPICS.keys()))
    items = TODDLER_VISUAL_TOPICS[selected_toddler_cat]

    st.markdown("### 🖼️ Visual Flashcards & Audio Playback")
    cols = st.columns(3)
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 14px; padding: 20px; text-align: center; margin-bottom: 15px;">
                <div style="font-size: 3rem; margin-bottom: 8px;">{item['icon']}</div>
                <h3 style="color: #2563eb; margin: 0px 0px 4px 0px;">{item['term']}</h3>
                <p style="color: #64748b; font-weight: 600; margin: 0px 0px 8px 0px;">{item['en']}</p>
                <p style="color: #334155; font-size: 0.85rem; margin: 0px;">{item['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 Listen ({item['term']})", key=f"toddler_audio_{selected_toddler_cat}_{idx}", use_container_width=True):
                play_direct_audio(item['term'], f"toddler_{idx}")

    st.divider()
    st.markdown("### 🧩 Interactive Matching Challenge")
    st.write("Test your memory! Match the English meaning to the correct German term.")

    if f"match_target_{selected_toddler_cat}" not in st.session_state:
        st.session_state[f"match_target_{selected_toddler_cat}"] = random.choice(items)

    target = st.session_state[f"match_target_{selected_toddler_cat}"]
    st.markdown(f"**Target English Meaning:** <span style='font-size: 1.4rem; color: #2563eb; font-weight: 700;'>{target['en']} {target['icon']}</span>", unsafe_allow_html=True)

    options = [i['term'] for i in items]
    random.shuffle(options)
    user_match = st.radio("Select the correct German term:", options, key=f"match_rad_{selected_toddler_cat}")

    if st.button("Check Match", key=f"check_match_{selected_toddler_cat}", type="primary"):
        if user_match == target['term']:
            st.success(f"🎉 Richtig! `{target['term']}` means {target['en']}.")
            play_direct_audio(target['term'], "correct_match")
            st.session_state[f"match_target_{selected_toddler_cat}"] = random.choice(items)
            st.rerun()
        else:
            st.error(f"❌ Falsch. Try again! Listen to pronunciation of options using the cards above.")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 3. MASTER GOETHE WORD ENGINE
# ----------------------------------------------------
elif nav_choice == "📚 Master Goethe Word Engine":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📚 Master Goethe A1 Interactive Flashcard Engine (Top 1000 Vocabulary)")
    st.write("Browse through official Goethe A1 and CEFR essential vocabulary categorized by official themes. Select 'ALL' to shuffle randomly across the entire deck.")

    TOP_1000_VOCAB_CATEGORIES = {
        "1. Person & Alltag (Personal & Daily Life)": {
            "Angaben zur Person (Personal Info)": ["der Name", "das Alter", "die Herkunft", "die Sprache", "ledig", "verheiratet", "kommen", "wohnen", "heißen", "sprechen"],
            "Wohnen & Haushalt (Housing & Home)": ["die Wohnung", "das Zimmer", "die Miete", "die Adresse", "der Tisch", "der Stuhl", "die Küche", "das Bett", "kosten", "umziehen"],
            "Familie & Freunde (Family & Friends)": ["die Eltern", "die Mutter", "der Vater", "der Bruder", "die Schwester", "das Kind", "der Freund", "die Familie", "groß", "klein"]
        },
        "2. Essen & Trinken (Food & Drink)": {
            "Lebensmittel (Groceries)": ["der Apfel", "das Wasser", "das Brot", "die Milch", "das Fleisch", "das Obst", "das Gemüse", "der Käse", "das Ei", "der Fisch"],
            "Im Restaurant & Café (Dining Out)": ["die Speisekarte", "zahlen", "lecker", "das Restaurant", "das Café", "der Kellner", "bestellen", "das Trinkgeld", "hungrig", "durstig"]
        },
        "3. Freizeit & Alltag (Leisure & Routine)": {
            "Tagesablauf (Daily Routine)": ["aufstehen", "frühstücken", "arbeiten", "schlafen", "spät", "früh", "der Morgen", "der Abend", "die Uhr", "beginnen"],
            "Hobbys & Sport (Hobbies & Sports)": ["lesen", "Fußball spielen", "fernsehen", "das Buch", "das Kino", "die Musik", "schwimmen", "reisen", "das Hobby", "fotografieren"],
            "Wetter & Jahreszeiten (Weather & Seasons)": ["das Wetter", "kalt", "warm", "der Sommer", "der Winter", "die Sonne", "der Regen", "schneien", "der Frühling", "der Herbst"]
        },
        "4. Einkaufen & Geld (Shopping & Money)": {
            "Geschäfte & Kleidung (Stores & Clothing)": ["das Geschäft", "die Hose", "das Hemd", "teuer", "billig", "die Farbe", "kaufen", "die Größe", "der Schuh", "die Jacke"],
            "Bezahlen & Zahlen (Paying & Numbers)": ["das Geld", "der Euro", "die Kreditkarte", "null", "eins", "hundert", "tausend", "bezahlen", "kostbar", "billig"]
        },
        "5. Arbeit & Beruf (Work & Profession)": {
            "Berufe & Arbeitsplatz (Jobs & Workplace)": ["der Arzt", "die Ärztin", "das Büro", "arbeiten", "der Kollege", "die Chefin", "der Beruf", "die Firma", "der Computer", "die Arbeit"],
            "Termine & Bürokommunikation (Appointments & Comm)": ["der Termin", "anrufen", "morgen", "gestern", "die E-Mail", "das Telefon", "die Nachricht", "verschieben", "pünktlich", "absagen"]
        },
        "6. Stadt & Verkehr (City & Transportation)": {
            "Unterwegs sein (Getting Around)": ["der Bus", "der Zug", "der Bahnhof", "links", "rechts", "das Ticket", "fahren", "fliegen", "das Auto", "die Haltestelle"],
            "In der Stadt (In the City)": ["das Krankenhaus", "die Post", "die Bank", "die Apotheke", "die Straße", "die Brücke", "der Markt", "das Museum", "die Stadt", "der Park"]
        },
        "7. Gesundheit & Körper (Health & Body)": {
            "Der Körper (The Body)": ["der Kopf", "der Arm", "das Bein", "das Auge", "das Mund", "das Haar", "der Rücken", "die Hand", "der Fuß", "wehtun"],
            "Beim Arzt (At the Doctor)": ["krank", "der Arzt", "die Apotheke", "das Medikament", "das Rezept", "schmerzen", "helfen", "gesund", "das Fieber", "die Praxis"]
        },
        "8. Allgemein (General & Core Grammar)": {
            "Grundverben & Pronomen (Core Verbs & Pronouns)": ["sein", "haben", "werden", "können", "müssen", "ich", "du", "er", "sie", "es", "wir", "ihr", "sie", "Sie"],
            "Präpositionen & Konnektoren (Prepositions & Connectors)": ["und", "aber", "oder", "denn", "in", "auf", "mit", "für", "von", "zu"]
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
# 4. CORE GRAMMAR PRACTICE & EXERCISES
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
# 5. GOETHE A1 LESEN
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
        st.markdown("**Teil 1 (Kurze Mitteilungen):** Read two short messages/emails and determine if the 5 statements are Richtig or Falsch (matching exact app UI & screenshot 51).")
        
        selected_lesen_t1_title = st.selectbox("📂 Select Lesen Teil 1 Scenario Set:", [s["title"] for s in LESEN_TEIL1_SCENARIOS], key="lesen_t1_sel")
        selected_lesen_t1_obj = next(s for s in LESEN_TEIL1_SCENARIOS if s["title"] == selected_lesen_t1_title)
        
        st.info(f"📌 **Description:** {selected_lesen_t1_obj['desc']}")

        # Display Message 1 box matching screenshot 51 UI
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">✉️ {selected_lesen_t1_obj['text1_label']}</span>
            </div>
            <p style="white-space: pre-line; color: #334155; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0px;">{selected_lesen_t1_obj['text1']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Display Message 2 box matching screenshot 51 UI
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">📄 {selected_lesen_t1_obj['text2_label']}</span>
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
        st.markdown("**Teil 2 (Zuordnung / Classified Ads):** Match 5 user situations to website options A or B (matching exact app UI & screenshot 52).")
        
        selected_lesen_t2_title = st.selectbox("📂 Select Lesen Teil 2 Scenario Set:", [s["title"] for s in LESEN_TEIL2_SCENARIOS], key="lesen_t2_sel")
        selected_lesen_t2_obj = next(s for s in LESEN_TEIL2_SCENARIOS if s["title"] == selected_lesen_t2_title)
        
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
        st.markdown("**Teil 3 (Öffentliche Hinweise / Public Signs):** Read public signs and notices and determine if statements are Richtig or Falsch (matching exact app UI & screenshot 53).")
        
        selected_lesen_t3_title = st.selectbox("📂 Select Lesen Teil 3 Scenario Set:", [s["title"] for s in LESEN_TEIL3_SCENARIOS], key="lesen_t3_sel")
        selected_lesen_t3_obj = next(s for s in LESEN_TEIL3_SCENARIOS if s["title"] == selected_lesen_t3_title)
        
        st.info(f"📌 **Description:** {selected_lesen_t3_obj['desc']}")

        # Display Example Box matching screenshot 53 UI
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
# 6. GOETHE A1 HÖREN
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
# 7. GOETHE A1 SCHREIBEN
# ----------------------------------------------------
elif nav_choice == "✍️ Goethe A1 Schreiben (Writing)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✍️ Goethe A1 Schreiben Practice (20 Mins, 2 Parts)")

    s_tab1, s_tab2 = st.tabs([
        "Teil 1: Formular (Official 9 Scenarios)", 
        "Teil 2: Mitteilung (Official 9 Scenarios)"
    ])

    with s_tab1:
        st.markdown("**Teil 1 (Formular):** Select from all 9 official Goethe A1 practice scenarios. Fill in the 5 missing information gaps exactly like the official Goethe-Zertifikat A1 exam interface.")
        
        selected_schreiben_t1_title = st.selectbox("📂 Select Schreiben Teil 1 Scenario Set:", [s["title"] for s in SCHREIBEN_TEIL1_SCENARIOS])
        selected_schreiben_t1_obj = next(s for s in SCHREIBEN_TEIL1_SCENARIOS if s["title"] == selected_schreiben_t1_title)
        
        st.markdown(f"""
        <div style="background: #f1f5f9; border-left: 5px solid #8b5cf6; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
            <p style="font-weight: 700; color: #6d28d9; margin-bottom: 8px;">📋 Aufgabe</p>
            <p style="white-space: pre-line; color: #1e293b; margin-bottom: 0px;">{selected_schreiben_t1_obj['aufgabe']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### 📄 {selected_schreiben_t1_obj['form_title']}")
        
        user_form_inputs = {}
        for field in selected_schreiben_t1_obj["fields"]:
            if not field["is_gap"]:
                st.text_input(field["label"], value=field["default"], disabled=True, key=f"disabled_{selected_schreiben_t1_title}_{field['id']}")
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
            total_gaps = sum(1 for f in selected_schreiben_t1_obj["fields"] if f["is_gap"])
            st.markdown("### 📊 Evaluation Results")
            for field in selected_schreiben_t1_obj["fields"]:
                if field["is_gap"]:
                    u_val = str(user_form_inputs.get(field["id"], "")).strip().lower()
                    c_val = str(field["answer"]).strip().lower()
                    if u_val == c_val or c_val in u_val:
                        score += 1
                        st.success(f"**{field['label']}** Correct! (`{field['answer']}`)")
                    else:
                        st.error(f"**{field['label']}** Incorrect. Your answer: `{user_form_inputs.get(field['id'], '')}` | Correct: `{field['answer']}`")
            st.metric("Formular Score", f"{score} / {total_gaps}")

    with s_tab2:
        st.markdown("**Teil 2 (Mitteilung):** Select from all 9 official Goethe A1 practice scenarios. Write an email (~30 words) hitting all 3 required points.")
        
        selected_schreiben_t2_title = st.selectbox("📂 Select Schreiben Teil 2 Scenario Set:", [s["title"] for s in SCHREIBEN_TEIL2_SCENARIOS], key="schreiben_t2_select")
        selected_schreiben_t2_obj = next(s for s in SCHREIBEN_TEIL2_SCENARIOS if s["title"] == selected_schreiben_t2_title)
        
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
# 8. GOETHE A1 SPRECHEN
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
# 9. GOETHE A1 MOCK EXAMINATION
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
# 10. A1 & A2 SHORT STORIES
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
# 11. ASK GEM
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
