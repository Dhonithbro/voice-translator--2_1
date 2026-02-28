"""
=============================================================
  TRANSLATOR MODULE v3 — Perfect Multilingual Translation
  Primary  : Google Translate via deep-translator (FREE, any word)
  Fallback : Built-in phrase dictionary (works offline)
  
  Source : English | Hindi | Telugu | Tamil | Malayalam
  Target : English | Hindi | Telugu | Tamil | Malayalam
           German  | French | Spanish
=============================================================
"""
import time, re, json, os

# ── deep-translator (Google Translate wrapper — free, no API key needed) ───────
try:
    from deep_translator import GoogleTranslator
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Language detection (optional)
try:
    from langdetect import detect, detect_langs
    LANG_DETECT_AVAILABLE = True
except Exception:
    LANG_DETECT_AVAILABLE = False

# Map two-letter language codes → internal language keys
LANG_CODE_MAP = {
    "en": "english",
    "hi": "hindi",
    "te": "telugu",
    "ta": "tamil",
    "ml": "malayalam",
    "de": "german",
    "fr": "french",
    "es": "spanish",
}

# ── Language config ────────────────────────────────────────────────────────────
LANGUAGES = {
    "english":   {"label": "English",   "flag": "🇬🇧", "google_code": "en"},
    "hindi":     {"label": "Hindi",     "flag": "🇮🇳", "google_code": "hi"},
    "telugu":    {"label": "Telugu",    "flag": "🇮🇳", "google_code": "te"},
    "tamil":     {"label": "Tamil",     "flag": "🇮🇳", "google_code": "ta"},
    "malayalam": {"label": "Malayalam", "flag": "🇮🇳", "google_code": "ml"},
    "german":    {"label": "German",    "flag": "🇩🇪", "google_code": "de"},
    "french":    {"label": "French",    "flag": "🇫🇷", "google_code": "fr"},
    "spanish":   {"label": "Spanish",   "flag": "🇪🇸", "google_code": "es"},
}

SOURCE_LANGUAGES = ["english", "hindi", "telugu", "tamil", "malayalam"]
TARGET_LANGUAGES = ["english", "hindi", "telugu", "tamil", "malayalam",
                    "german", "french", "spanish"]

# ─── Built-in phrase table (offline fallback — any language pair) ──────────────
PHRASE_TABLE = {
    "how are you":               {"english":"How are you?","hindi":"आप कैसे हैं?","telugu":"మీరు ఎలా ఉన్నారు?","tamil":"நீங்கள் எப்படி இருக்கிறீர்கள்?","malayalam":"താങ്കൾ എങ്ങനെ ഉണ്ട്?","german":"Wie geht es Ihnen?","french":"Comment allez-vous?","spanish":"¿Cómo estás?"},
    "good morning":              {"english":"Good morning!","hindi":"सुप्रभात!","telugu":"శుభోదయం!","tamil":"காலை வணக்கம்!","malayalam":"സുപ്രഭാതം!","german":"Guten Morgen!","french":"Bonjour!","spanish":"¡Buenos días!"},
    "good night":                {"english":"Good night.","hindi":"शुभ रात्रि।","telugu":"శుభ రాత్రి.","tamil":"இனிய இரவு.","malayalam":"ശുഭ രാത്രി.","german":"Gute Nacht.","french":"Bonne nuit.","spanish":"Buenas noches."},
    "hello":                     {"english":"Hello.","hindi":"नमस्ते।","telugu":"హలో.","tamil":"வணக்கம்.","malayalam":"ഹലോ.","german":"Hallo.","french":"Bonjour.","spanish":"Hola."},
    "bye":                       {"english":"Goodbye.","hindi":"अलविदा।","telugu":"వీడ్కోలు.","tamil":"விடைபெறுகிறேன்.","malayalam":"വിടവാങ്ങൽ.","german":"Auf Wiedersehen.","french":"Au revoir.","spanish":"Adiós."},
    "thank you":                 {"english":"Thank you.","hindi":"धन्यवाद।","telugu":"ధన్యవాదాలు.","tamil":"நன்றி.","malayalam":"നന്ദി.","german":"Danke.","french":"Merci.","spanish":"Gracias."},
    "thank you very much":       {"english":"Thank you very much.","hindi":"बहुत धन्यवाद।","telugu":"చాలా ధన్యవాదాలు.","tamil":"மிக்க நன்றி.","malayalam":"വളരെ നന്ദി.","german":"Vielen Dank.","french":"Merci beaucoup.","spanish":"Muchas gracias."},
    "you are welcome":           {"english":"You are welcome.","hindi":"आपका स्वागत है।","telugu":"స్వాగతం.","tamil":"வரவேற்கிறேன்.","malayalam":"സ്വാഗതം.","german":"Bitte sehr.","french":"De rien.","spanish":"De nada."},
    "yes":                       {"english":"Yes.","hindi":"हाँ।","telugu":"అవును.","tamil":"ஆம்.","malayalam":"അതെ.","german":"Ja.","french":"Oui.","spanish":"Sí."},
    "no":                        {"english":"No.","hindi":"नहीं।","telugu":"లేదు.","tamil":"இல்லை.","malayalam":"ഇല്ല.","german":"Nein.","french":"Non.","spanish":"No."},
    "what is your name":         {"english":"What is your name?","hindi":"आपका नाम क्या है?","telugu":"మీ పేరు ఏమిటి?","tamil":"உங்கள் பெயர் என்ன?","malayalam":"താങ്കളുടെ പേര് എന്താണ്?","german":"Wie heißen Sie?","french":"Comment vous appelez-vous?","spanish":"¿Cómo te llamas?"},
    "where do you live":         {"english":"Where do you live?","hindi":"आप कहाँ रहते हैं?","telugu":"మీరు ఎక్కడ నివసిస్తున్నారు?","tamil":"நீங்கள் எங்கு வாழ்கிறீர்கள்?","malayalam":"താങ്കൾ എവിടെ താമസിക്കുന്നു?","german":"Wo wohnen Sie?","french":"Où habitez-vous?","spanish":"¿Dónde vives?"},
    "how old are you":           {"english":"How old are you?","hindi":"आपकी उम्र क्या है?","telugu":"మీ వయసు ఎంత?","tamil":"உங்கள் வயது என்ன?","malayalam":"താങ്കൾക്ക് എത്ര വയസ്സായി?","german":"Wie alt sind Sie?","french":"Quel âge avez-vous?","spanish":"¿Cuántos años tienes?"},
    "excuse me":                 {"english":"Excuse me.","hindi":"माफ़ कीजिए।","telugu":"క్షమించండి.","tamil":"மன்னிக்கவும்.","malayalam":"ക്ഷമിക്കൂ.","german":"Entschuldigung.","french":"Excusez-moi.","spanish":"Disculpe."},
    "i am sorry":                {"english":"I am sorry.","hindi":"मुझे खेद है।","telugu":"నన్ను క్షమించండి.","tamil":"மன்னிக்கவும்.","malayalam":"ക്ഷമിക്കൂ.","german":"Es tut mir leid.","french":"Je suis désolé.","spanish":"Lo siento."},
    "see you tomorrow":          {"english":"See you tomorrow.","hindi":"कल मिलते हैं।","telugu":"రేపు కలుద్దాం.","tamil":"நாளை சந்திப்போம்.","malayalam":"നാളെ കാണാം.","german":"Bis morgen.","french":"À demain.","spanish":"Hasta mañana."},
    "i dont understand":         {"english":"I don't understand.","hindi":"मुझे समझ नहीं आया।","telugu":"నాకు అర్థం కాలేదు.","tamil":"எனக்கு புரியவில்லை.","malayalam":"എനിക്ക് മനസ്സിലാകുന്നില്ല.","german":"Ich verstehe nicht.","french":"Je ne comprends pas.","spanish":"No entiendo."},
    "please speak slowly":       {"english":"Please speak slowly.","hindi":"कृपया धीरे बोलें।","telugu":"దయచేసి నెమ్మదిగా మాట్లాడండి.","tamil":"தயவுசெய்து மெதுவாக பேசுங்கள்.","malayalam":"ദയവായി പതുക്കെ സംസാരിക്കൂ.","german":"Bitte sprechen Sie langsam.","french":"Parlez lentement s'il vous plaît.","spanish":"Por favor habla despacio."},
    "can you help me":           {"english":"Can you help me?","hindi":"क्या आप मेरी मदद कर सकते हैं?","telugu":"మీరు నాకు సహాయం చేయగలరా?","tamil":"நீங்கள் என்னை உதவ முடியுமா?","malayalam":"നിങ്ങൾക്ക് എന്നെ സഹായിക്കാമോ?","german":"Können Sie mir helfen?","french":"Pouvez-vous m'aider?","spanish":"¿Puedes ayudarme?"},
    "please help me":            {"english":"Please help me.","hindi":"कृपया मेरी मदद करें।","telugu":"దయచేసి నన్ను సహాయం చేయండి.","tamil":"தயவுசெய்து என்னை உதவுங்கள்.","malayalam":"ദയവായി എന്നെ സഹായിക്കൂ.","german":"Bitte helfen Sie mir.","french":"Aidez-moi s'il vous plaît.","spanish":"Por favor ayúdame."},
    "what time is it":           {"english":"What time is it?","hindi":"अभी कितने बजे हैं?","telugu":"ఇప్పుడు సమయం ఎంత?","tamil":"இப்போது நேரம் என்ன?","malayalam":"ഇപ്പോൾ സമയം എത്ര ആണ്?","german":"Wie spät ist es?","french":"Quelle heure est-il?","spanish":"¿Qué hora es?"},
    "i am hungry":               {"english":"I am hungry.","hindi":"मुझे भूख लगी है।","telugu":"నాకు ఆకలిగా ఉంది.","tamil":"எனக்கு பசிக்கிறது.","malayalam":"എനിക்ക് വിശക്കുന്നു.","german":"Ich habe Hunger.","french":"J'ai faim.","spanish":"Tengo hambre."},
    "i need water":              {"english":"I need water.","hindi":"मुझे पानी चाहिए।","telugu":"నాకు నీళ్ళు కావాలి.","tamil":"எனக்கு தண்ணீர் வேண்டும்.","malayalam":"എനിക്ക് വെള്ളം വേണം.","german":"Ich brauche Wasser.","french":"J'ai besoin d'eau.","spanish":"Necesito agua."},
    "where is the hotel":        {"english":"Where is the hotel?","hindi":"होटल कहाँ है?","telugu":"హోటల్ ఎక్కడ ఉంది?","tamil":"ஹோட்டல் எங்கே இருக்கிறது?","malayalam":"ഹോട്ടൽ എവിടെ ആണ്?","german":"Wo ist das Hotel?","french":"Où est l'hôtel?","spanish":"¿Dónde está el hotel?"},
    "where is the airport":      {"english":"Where is the airport?","hindi":"हवाई अड्डा कहाँ है?","telugu":"విమానాశ్రయం ఎక్కడ ఉంది?","tamil":"விமான நிலையம் எங்கே?","malayalam":"വിമാനത്താവളം എവിടെ ആണ്?","german":"Wo ist der Flughafen?","french":"Où est l'aéroport?","spanish":"¿Dónde está el aeropuerto?"},
    "how much does it cost":     {"english":"How much does it cost?","hindi":"इसकी कीमत क्या है?","telugu":"ఇది ఎంత?","tamil":"இது எவ்வளவு?","malayalam":"ഇതിന് എത്ര വിലയുണ്ട്?","german":"Wie viel kostet das?","french":"Combien ça coûte?","spanish":"¿Cuánto cuesta?"},
    "i need a taxi":             {"english":"I need a taxi.","hindi":"मुझे टैक्सी चाहिए।","telugu":"నాకు టాక్సీ కావాలి.","tamil":"எனக்கு டாக்சி வேண்டும்.","malayalam":"എനിക്ക് ഒരു ടാക്സി വേണം.","german":"Ich brauche ein Taxi.","french":"J'ai besoin d'un taxi.","spanish":"Necesito un taxi."},
    "i need a doctor":           {"english":"I need a doctor.","hindi":"मुझे डॉक्टर की जरूरत है।","telugu":"నాకు వైద్యుడు కావాలి.","tamil":"எனக்கு மருத்துவர் தேவை.","malayalam":"എനിക்ക് ഒരു ഡോക്ടർ വേണം.","german":"Ich brauche einen Arzt.","french":"J'ai besoin d'un médecin.","spanish":"Necesito un médico."},
    "i have a headache":         {"english":"I have a headache.","hindi":"मुझे सिरदर्द है।","telugu":"నాకు తలనొప్పి ఉంది.","tamil":"எனக்கு தலைவலி இருக்கிறது.","malayalam":"എനിക്ക് തലവേദന ഉണ്ട്.","german":"Ich habe Kopfschmerzen.","french":"J'ai mal à la tête.","spanish":"Tengo dolor de cabeza."},
    "i have a fever":            {"english":"I have a fever.","hindi":"मुझे बुखार है।","telugu":"నాకు జ్వరం ఉంది.","tamil":"எனக்கு காய்ச்சல் இருக்கிறது.","malayalam":"എനിക്ക് പനി ഉണ്ട്.","german":"Ich habe Fieber.","french":"J'ai de la fièvre.","spanish":"Tengo fiebre."},
    "call an ambulance":         {"english":"Call an ambulance!","hindi":"एम्बुलेंस बुलाओ!","telugu":"యాంబులెన్స్ పిలవండి!","tamil":"ஆம்புலன்ஸ் அழையுங்கள்!","malayalam":"ആംബുലൻസ് വിളിക്കൂ!","german":"Rufen Sie einen Krankenwagen!","french":"Appelez une ambulance!","spanish":"¡Llame a una ambulancia!"},
    "where is the hospital":     {"english":"Where is the hospital?","hindi":"अस्पताल कहाँ है?","telugu":"ఆసుపత్రి ఎక్కడ ఉంది?","tamil":"மருத்துவமனை எங்கே இருக்கிறது?","malayalam":"ആശുപത്രി എവിടെ ആണ്?","german":"Wo ist das Krankenhaus?","french":"Où est l'hôpital?","spanish":"¿Dónde está el hospital?"},
    "let us schedule a meeting": {"english":"Let us schedule a meeting.","hindi":"चलिए एक बैठक तय करते हैं।","telugu":"మనం ఒక సమావేశం ఏర్పాటు చేద్దాం.","tamil":"ஒரு கூட்டம் திட்டமிடுவோம்.","malayalam":"നമുക്ക് ഒരു യോഗം ഷെഡ്യൂൾ ചെയ്യാം.","german":"Lassen Sie uns ein Meeting planen.","french":"Planifions une réunion.","spanish":"Programemos una reunión."},
    "please restart the server": {"english":"Please restart the server.","hindi":"कृपया सर्वर पुनः आरंभ करें।","telugu":"దయచేసి సర్వర్ పున:ప్రారంభించండి.","tamil":"சர்வரை மறுதொடக்கம் செய்யவும்.","malayalam":"ദയവായി സർവ്വർ പുനരാരംഭിക്കൂ.","german":"Bitte starten Sie den Server neu.","french":"Veuillez redémarrer le serveur.","spanish":"Por favor reinicie el servidor."},
    "there is a bug in the code":{"english":"There is a bug in the code.","hindi":"कोड में एक बग है।","telugu":"కోడ్‌లో బగ్ ఉంది.","tamil":"குறியீட்டில் ஒரு பிழை உள்ளது.","malayalam":"കോഡിൽ ഒരു ബഗ് ഉണ്ട്.","german":"Es gibt einen Fehler im Code.","french":"Il y a un bug dans le code.","spanish":"Hay un error en el código."},
    "the weather is nice today": {"english":"The weather is nice today.","hindi":"आज मौसम अच्छा है।","telugu":"ఈరోజు వాతావరణం చాలా అందంగా ఉంది.","tamil":"இன்று வானிலை நன்றாக உள்ளது.","malayalam":"ഇന്ന് കാലാവസ്ഥ നല്ലതാണ്.","german":"Das Wetter ist heute schön.","french":"Le temps est beau aujourd'hui.","spanish":"El clima está agradable hoy."},
    "i love reading books":      {"english":"I love reading books.","hindi":"मुझे किताबें पढ़ना बहुत पसंद है।","telugu":"నాకు పుస్తకాలు చదవడం చాలా ఇష్టం.","tamil":"எனக்கு புத்தகங்கள் படிப்பது மிகவும் பிடிக்கும்.","malayalam":"എനിക്ക് പുസ്തകങ്ങൾ വായിക്കാൻ ഇഷ്ടമാണ്.","german":"Ich liebe es, Bücher zu lesen.","french":"J'adore lire des livres.","spanish":"Me encanta leer libros."},
    "when is the final exam":    {"english":"When is the final exam?","hindi":"अंतिम परीक्षा कब है?","telugu":"ఫైనల్ పరీక్ష ఎప్పుడు?","tamil":"இறுதி தேர்வு எப்போது?","malayalam":"അന്തിമ പരീക്ഷ എന്നാണ്?","german":"Wann ist die Abschlussprüfung?","french":"Quand est l'examen final?","spanish":"¿Cuándo es el examen final?"},
    "we need to increase sales":  {"english":"We need to increase sales.","hindi":"हमें बिक्री बढ़ानी होगी।","telugu":"మనం అమ్మకాలు పెంచాలి.","tamil":"நாம் விற்பனையை அதிகரிக்க வேண்டும்.","malayalam":"നമ്മൾ വിൽപ്പന വർദ്ധിപ്പിക്കണം.","german":"Wir müssen den Umsatz steigern.","french":"Nous devons augmenter les ventes.","spanish":"Necesitamos aumentar las ventas."},
    "what happened":             {"english":"What happened?","hindi":"क्या हुआ?","telugu":"ఏమి జరిగింది?","tamil":"என்ன நடந்தது?","malayalam":"എന്ത് സംഭവിച്ചു?","german":"Was ist passiert?","french":"Qu'est-ce qui s'est passé?","spanish":"¿Qué pasó?"},
    "where are you going":       {"english":"Where are you going?","hindi":"आप कहाँ जा रहे हैं?","telugu":"మీరు ఎక్కడికి వెళ్తున్నారు?","tamil":"நீங்கள் எங்கே போகிறீர்கள்?","malayalam":"നിങ്ങൾ എവിടെ പോകുന്നു?","german":"Wo gehen Sie hin?","french":"Où allez-vous?","spanish":"¿Adónde vas?"},
    "i am fine":                 {"english":"I am fine.","hindi":"मैं ठीक हूँ।","telugu":"నేను బాగున్నాను.","tamil":"நான் நலமாக இருக்கிறேன்.","malayalam":"ഞാൻ സുഖമായിരിക്കുന്നു.","german":"Mir geht es gut.","french":"Je vais bien.","spanish":"Estoy bien."},
    "i am tired":                {"english":"I am tired.","hindi":"मैं थका हुआ हूँ।","telugu":"నేను అలసిపోయాను.","tamil":"நான் சோர்வாக இருக்கிறேன்.","malayalam":"ഞാൻ ക്ഷീണിതനാണ്.","german":"Ich bin müde.","french":"Je suis fatigué.","spanish":"Estoy cansado."},
    "i am happy":                {"english":"I am happy.","hindi":"मैं खुश हूँ।","telugu":"నేను సంతోషంగా ఉన్నాను.","tamil":"நான் மகிழ்ச்சியாக இருக்கிறேன்.","malayalam":"ഞാൻ സന്തോഷവാനാണ്.","german":"Ich bin glücklich.","french":"Je suis heureux.","spanish":"Estoy feliz."},
    "i am sad":                  {"english":"I am sad.","hindi":"मैं दुखी हूँ।","telugu":"నేను దుఃఖంగా ఉన్నాను.","tamil":"நான் சோகமாக இருக்கிறேன்.","malayalam":"ഞാൻ സങ്കടത്തിലാണ്.","german":"Ich bin traurig.","french":"Je suis triste.","spanish":"Estoy triste."},
    "open the door":             {"english":"Open the door.","hindi":"दरवाजा खोलो।","telugu":"తలుపు తెరవండి.","tamil":"கதவை திறக்கவும்.","malayalam":"വാതിൽ തുറക്കൂ.","german":"Öffne die Tür.","french":"Ouvrez la porte.","spanish":"Abre la puerta."},
    "close the window":          {"english":"Close the window.","hindi":"खिड़की बंद करो।","telugu":"కిటికీ మూయండి.","tamil":"ஜன்னலை மூடவும்.","malayalam":"ജനൽ അടക്കൂ.","german":"Schließe das Fenster.","french":"Fermez la fenêtre.","spanish":"Cierra la ventana."},
    "i need help":               {"english":"I need help.","hindi":"मुझे मदद चाहिए।","telugu":"నాకు సహాయం కావాలి.","tamil":"எனக்கு உதவி தேவை.","malayalam":"എനിക്ക് സഹായം വേണം.","german":"Ich brauche Hilfe.","french":"J'ai besoin d'aide.","spanish":"Necesito ayuda."},
    "where is the bathroom":     {"english":"Where is the bathroom?","hindi":"बाथरूम कहाँ है?","telugu":"బాత్రూమ్ ఎక్కడ ఉంది?","tamil":"குளியலறை எங்கே?","malayalam":"ബാത്ത്റൂം എവിടെ?","german":"Wo ist das Badezimmer?","french":"Où est la salle de bain?","spanish":"¿Dónde está el baño?"},
    "i want to eat":             {"english":"I want to eat.","hindi":"मुझे खाना खाना है।","telugu":"నాకు తినాలని ఉంది.","tamil":"நான் சாப்பிட வேண்டும்.","malayalam":"എനിക്ക് കഴിക്കണം.","german":"Ich möchte essen.","french":"Je veux manger.","spanish":"Quiero comer."},
    "i want to sleep":           {"english":"I want to sleep.","hindi":"मुझे नींद आ रही है।","telugu":"నాకు నిద్ర వస్తోంది.","tamil":"நான் தூங்க வேண்டும்.","malayalam":"എനിക്ക് ഉറങ്ങണം.","german":"Ich möchte schlafen.","french":"Je veux dormir.","spanish":"Quiero dormir."},
    "how much is the rent":      {"english":"How much is the rent?","hindi":"किराया कितना है?","telugu":"అద్దె ఎంత?","tamil":"வாடகை எவ்வளவு?","malayalam":"വാടക എത്രയാണ്?","german":"Wie hoch ist die Miete?","french":"Quel est le loyer?","spanish":"¿Cuánto es el alquiler?"},
    "call the police":           {"english":"Call the police!","hindi":"पुलिस को बुलाओ!","telugu":"పోలీసులను పిలవండి!","tamil":"போலீஸை அழையுங்கள்!","malayalam":"പോലീസിനെ വിളിക്കൂ!","german":"Rufen Sie die Polizei!","french":"Appelez la police!","spanish":"¡Llame a la policía!"},
    "i am lost":                 {"english":"I am lost.","hindi":"मैं रास्ता भूल गया।","telugu":"నేను దారి తప్పాను.","tamil":"நான் வழி தெரியாமல் போனேன்.","malayalam":"ഞാൻ വഴി തെറ്റി.","german":"Ich habe mich verirrt.","french":"Je me suis perdu.","spanish":"Estoy perdido."},
    "nice to meet you":          {"english":"Nice to meet you.","hindi":"आपसे मिलकर खुशी हुई।","telugu":"మిమ్మల్ని కలవడం సంతోషం.","tamil":"உங்களை சந்திப்பதில் மகிழ்ச்சி.","malayalam":"നിങ്ങളെ കണ്ടതിൽ സന്തോഷം.","german":"Schön, Sie kennenzulernen.","french":"Enchanté de vous rencontrer.","spanish":"Encantado de conocerte."},
    "i love you":                {"english":"I love you.","hindi":"मैं तुमसे प्यार करता हूँ।","telugu":"నేను నిన్ను ప్రేమిస్తున్నాను.","tamil":"நான் உன்னை நேசிக்கிறேன்.","malayalam":"ഞാൻ നിന്നെ സ്നേഹിക്കുന്നു.","german":"Ich liebe dich.","french":"Je t'aime.","spanish":"Te amo."},
    "happy birthday":            {"english":"Happy birthday!","hindi":"जन्मदिन मुबारक!","telugu":"పుట్టిన రోజు శుభాకాంక్షలు!","tamil":"பிறந்த நாள் வாழ்த்துகள்!","malayalam":"ജന്മദിന ആശംസകൾ!","german":"Alles Gute zum Geburtstag!","french":"Joyeux anniversaire!","spanish":"¡Feliz cumpleaños!"},
    "congratulations":           {"english":"Congratulations!","hindi":"बधाई हो!","telugu":"అభినందనలు!","tamil":"வாழ்த்துகள்!","malayalam":"അഭിനന്ദനങ്ങൾ!","german":"Herzlichen Glückwunsch!","french":"Félicitations!","spanish":"¡Felicitaciones!"},
    "i am from india":           {"english":"I am from India.","hindi":"मैं भारत से हूँ।","telugu":"నేను భారతదేశం నుండి వచ్చాను.","tamil":"நான் இந்தியாவிலிருந்து வருகிறேன்.","malayalam":"ഞാൻ ഇന്ത്യയിൽ നിന്നാണ്.","german":"Ich komme aus Indien.","french":"Je viens d'Inde.","spanish":"Soy de India."},
    "what is this":              {"english":"What is this?","hindi":"यह क्या है?","telugu":"ఇది ఏమిటి?","tamil":"இது என்ன?","malayalam":"ഇത് എന்তോ?","german":"Was ist das?","french":"Qu'est-ce que c'est?","spanish":"¿Qué es esto?"},
    "i dont know":               {"english":"I don't know.","hindi":"मुझे नहीं पता।","telugu":"నాకు తెలియదు.","tamil":"எனக்கு தெரியாது.","malayalam":"എനിക്ക് അറിയില്ല.","german":"Ich weiß nicht.","french":"Je ne sais pas.","spanish":"No lo sé."},
    "how was your day":          {"english":"How was your day?","hindi":"आपका दिन कैसा था?","telugu":"మీ రోజు ఎలా గడిచింది?","tamil":"உங்கள் நாள் எப்படி இருந்தது?","malayalam":"നിങ്ങളുടെ ദിവസം എങ്ങനെ ഉണ്ടായിരുന്നു?","german":"Wie war Ihr Tag?","french":"Comment s'est passée votre journée?","spanish":"¿Cómo estuvo tu día?"},
    "please wait":               {"english":"Please wait.","hindi":"कृपया प्रतीक्षा करें।","telugu":"దయచేసి వేచి ఉండండి.","tamil":"தயவுசெய்து காத்திருங்கள்.","malayalam":"ദയവായി കാത്തിരിക്കൂ.","german":"Bitte warten Sie.","french":"Veuillez attendre.","spanish":"Por favor espere."},
    "i agree":                   {"english":"I agree.","hindi":"मैं सहमत हूँ।","telugu":"నేను అంగీకరిస్తున్నాను.","tamil":"நான் ஒப்புக்கொள்கிறேன்.","malayalam":"ഞാൻ സമ്മതിക്കുന്നു.","german":"Ich stimme zu.","french":"Je suis d'accord.","spanish":"Estoy de acuerdo."},
    "i disagree":                {"english":"I disagree.","hindi":"मैं असहमत हूँ।","telugu":"నేను అంగీకరించను.","tamil":"நான் ஒப்புக்கொள்ளவில்லை.","malayalam":"ഞാൻ സമ്മതിക്കുന്നില്ല.","german":"Ich stimme nicht zu.","french":"Je ne suis pas d'accord.","spanish":"No estoy de acuerdo."},
}

# ── Build reverse lookup: any language phrase → english key ───────────────────
_REVERSE = {}

def _norm(text):
    """Normalize text for matching - remove punctuation, lowercase, strip"""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def _fuzzy_match(norm_in, threshold=0.6):
    """Find close matches in the reverse dictionary using substring matching"""
    if not norm_in:
        return None

    # Try exact match first
    if norm_in in _REVERSE:
        return _REVERSE[norm_in]

    # Try substring matching (both directions)
    matches = []
    for key, value in _REVERSE.items():
        if not key:
            continue
        # Check if normalized input is in key or key is in normalized input
        if norm_in in key:
            similarity = len(norm_in) / len(key)
            matches.append((similarity, value))
        elif key in norm_in:
            similarity = len(key) / len(norm_in)
            matches.append((similarity, value))

    if matches:
        # Return the best match (highest similarity)
        best_match = max(matches, key=lambda x: x[0])
        if best_match[0] >= threshold:
            return best_match[1]

    return None


def detect_language(text: str):
    """Detect language code and map to internal language key.

    Returns (lang_key, confidence) or (None, 0.0) if detection unavailable.
    """
    if not LANG_DETECT_AVAILABLE or not text or not text.strip():
        return (None, 0.0)
    try:
        # detect_langs returns list like [LangProb(lang='en', prob=0.99), ...]
        candidates = detect_langs(text)
        if not candidates:
            return (None, 0.0)
        top = candidates[0]
        code = str(top.lang)
        conf = float(top.prob)
        mapped = LANG_CODE_MAP.get(code)
        return (mapped, conf) if mapped else (None, conf)
    except Exception:
        try:
            code = detect(text)
            mapped = LANG_CODE_MAP.get(code)
            return (mapped, 0.5) if mapped else (None, 0.5)
        except Exception:
            return (None, 0.0)

def _build_reverse():
    global _REVERSE
    if _REVERSE:
        return
    for en_key, langs in PHRASE_TABLE.items():
        for lang, phrase in langs.items():
            _REVERSE[_norm(phrase)] = en_key
            _REVERSE[phrase.lower().strip()] = en_key

# ── Core translate ─────────────────────────────────────────────────────────────
def translate(text: str, src_lang: str = "english", tgt_lang: str = "telugu") -> dict:
    t0 = time.perf_counter()
    _build_reverse()
    # Validate and normalize language codes
    src_lang = src_lang.lower().strip()
    tgt_lang = tgt_lang.lower().strip()

    detected_src = None
    # Allow 'auto' / 'detect' for automatic source-language detection
    if src_lang in ("auto", "detect"):
        det_key, det_conf = detect_language(text)
        if det_key:
            detected_src = det_key
            src_lang = det_key
        else:
            # fallback to english when detection unavailable
            src_lang = "english"

    # Check if languages are supported
    if src_lang not in LANGUAGES:
        return _make(text, f"❌ Source language '{src_lang}' not supported", "error", src_lang, tgt_lang, t0, detected_src)
    if tgt_lang not in LANGUAGES:
        return _make(text, f"❌ Target language '{tgt_lang}' not supported", "error", src_lang, tgt_lang, t0, detected_src)

    # Same language = no translation needed
    if src_lang == tgt_lang:
        return _make(text, text, "same-language", src_lang, tgt_lang, t0, detected_src)

    # Validate input text
    if not text or not text.strip():
        return _make(text, "[No text provided]", "error", src_lang, tgt_lang, t0, detected_src)

    src_code = LANGUAGES[src_lang].get("google_code", "en")
    tgt_code = LANGUAGES[tgt_lang].get("google_code", "en")

    translated = None
    source = "not-found"

    # ── 1. Dictionary first (for common phrases — always accurate) ─────────────
    norm_in = _norm(text)

    # Try exact match combined with fuzzy matching
    en_key = _REVERSE.get(norm_in) or _REVERSE.get(text.lower().strip())
    if not en_key:
        en_key = _fuzzy_match(norm_in)

    if en_key and en_key in PHRASE_TABLE:
        translated = PHRASE_TABLE[en_key].get(tgt_lang)
        source = "dictionary"

    # ── 2. Google Translate for custom phrases (handles ANY word/sentence) ────
    if not translated and GOOGLE_AVAILABLE:
        try:
            translated = GoogleTranslator(source=src_code, target=tgt_code).translate(text)
            source = "google"
        except Exception as e:
            print(f"[!] Google Translate error for '{text}': {e}")

    # ── 3. Last resort: try to translate individual words ─────────────────────
    if not translated and GOOGLE_AVAILABLE:
        try:
            words = text.split()
            translated_words = []
            for word in words:
                try:
                    tw = GoogleTranslator(source=src_code, target=tgt_code).translate(word)
                    translated_words.append(tw)
                except:
                    translated_words.append(word)
            translated = " ".join(translated_words)
            source = "google-wordwise"
        except Exception as e:
            print(f"[!] Word-wise translation error: {e}")

    # ── 4. Graceful message if all methods fail ───────────────────────────────
    if not translated:
        translated = f"⚠️ Translation unavailable (no phrase for '{text}')"
        source = "not-found"

    return _make(text, translated, source, src_lang, tgt_lang, t0, detected_src)

def _make(original, translated, source, src_lang, tgt_lang, t0, detected_src=None):
    source_map = {
        "google": 0.97,
        "google-wordwise": 0.85,
        "dictionary": 0.99,
        "same-language": 1.0,
        "error": 0.0,
        "not-found": 0.0,
    }
    conf = source_map.get(source, 0.5)

    result = {
        "original": original,
        "translated": translated,
        "src_lang": src_lang,
        "tgt_lang": tgt_lang,
        "model_used": "Google Translate (deep-translator)" if "google" in source else "phrase-dictionary",
        "source": source,
        "confidence": conf,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
    }
    if detected_src:
        result["detected_src"] = detected_src
    return result

def supported_languages():
    return {
        "source": [{"key": k, "label": LANGUAGES[k]["label"], "flag": LANGUAGES[k]["flag"]} for k in SOURCE_LANGUAGES],
        "target": [{"key": k, "label": LANGUAGES[k]["label"], "flag": LANGUAGES[k]["flag"]} for k in TARGET_LANGUAGES],
    }

if __name__ == "__main__":
    tests = [
        ("what happened",        "english",   "french"),
        ("what happened",        "english",   "telugu"),
        ("what happened",        "english",   "hindi"),
        ("how are you",          "english",   "spanish"),
        ("i am going to school", "english",   "telugu"),
        ("ఏమి జరిగింది?",         "telugu",    "english"),
        ("आप कैसे हैं?",          "hindi",     "french"),
        ("good morning",         "english",   "malayalam"),
        ("i love you",           "english",   "tamil"),
        ("congratulations",      "english",   "german"),
    ]
    print("Testing translator...\n")
    for text, src, tgt in tests:
        r = translate(text, src, tgt)
        icon = "✅" if r["source"] != "not-found" else "❌"
        print(f"{icon} [{src}→{tgt}] '{text}' → '{r['translated']}'  [{r['source']}]")
