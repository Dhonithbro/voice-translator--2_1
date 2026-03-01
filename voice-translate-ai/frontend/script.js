/**
 * script.js — VoiceTranslate AI Bidirectional
 * Source : English | Hindi | Telugu | Tamil | Malayalam
 * Target : English | Hindi | Telugu | Tamil | Malayalam | German | French | Spanish
 */

const API_BASE = "https://voice-translator-21-production.up.railway.app";
const WS_URL   = "wss://voice-translator-21-production.up.railway.app/ws/translate";

let srcLang = "english";
let tgtLang = "telugu";
let isRecording = false;
let recognition = null;
let ws = null;
let history = [];

const LANG_META = {
  english:   { label: "English",   flag: "🇬🇧" },
  hindi:     { label: "Hindi",     flag: "🇮🇳" },
  telugu:    { label: "Telugu",    flag: "🇮🇳" },
  tamil:     { label: "Tamil",     flag: "🇮🇳" },
  malayalam: { label: "Malayalam", flag: "🇮🇳" },
  german:    { label: "German",    flag: "🇩🇪" },
  french:    { label: "French",    flag: "🇫🇷" },
  spanish:   { label: "Spanish",   flag: "🇪🇸" },
};

// ── Full phrase table (mirrors backend PHRASE_TABLE) for offline demo ─────────
const PHRASE_TABLE = {
  "how are you":              { english:"How are you?", hindi:"आप कैसे हैं?", telugu:"మీరు ఎలా ఉన్నారు?", tamil:"நீங்கள் எப்படி இருக்கிறீர்கள்?", malayalam:"താങ്കൾ എങ്ങനെ ഉണ്ട്?", german:"Wie geht es Ihnen?", french:"Comment allez-vous?", spanish:"¿Cómo estás?" },
  "good morning":             { english:"Good morning!", hindi:"सुप्रभात!", telugu:"శుభోదయం!", tamil:"காலை வணக்கம்!", malayalam:"സുപ്രഭാതം!", german:"Guten Morgen!", french:"Bonjour!", spanish:"¡Buenos días!" },
  "good night":               { english:"Good night.", hindi:"शुभ रात्रि।", telugu:"శుభ రాత్రి.", tamil:"இனிய இரவு.", malayalam:"ശുഭ രാത്രി.", german:"Gute Nacht.", french:"Bonne nuit.", spanish:"Buenas noches." },
  "hello":                    { english:"Hello.", hindi:"नमस्ते।", telugu:"హలో.", tamil:"வணக்கம்.", malayalam:"ഹലോ.", german:"Hallo.", french:"Bonjour.", spanish:"Hola." },
  "bye":                      { english:"Goodbye.", hindi:"अलविदा।", telugu:"వీడ్కోలు.", tamil:"விடைபெறுகிறேன்.", malayalam:"വിടവാങ്ങൽ.", german:"Auf Wiedersehen.", french:"Au revoir.", spanish:"Adiós." },
  "thank you":                { english:"Thank you.", hindi:"धन्यवाद।", telugu:"ధన్యవాదాలు.", tamil:"நன்றி.", malayalam:"നന്ദി.", german:"Danke.", french:"Merci.", spanish:"Gracias." },
  "thank you very much":      { english:"Thank you very much.", hindi:"बहुत बहुत धन्यवाद।", telugu:"చాలా ధన్యవాదాలు.", tamil:"மிக்க நன்றி.", malayalam:"വളരെ നന്ദി.", german:"Vielen Dank.", french:"Merci beaucoup.", spanish:"Muchas gracias." },
  "you are welcome":          { english:"You are welcome.", hindi:"आपका स्वागत है।", telugu:"స్వాగతం.", tamil:"வரவேற்கிறேன்.", malayalam:"സ്വാഗതം.", german:"Bitte sehr.", french:"De rien.", spanish:"De nada." },
  "yes":                      { english:"Yes.", hindi:"हाँ।", telugu:"అవును.", tamil:"ஆம்.", malayalam:"അതെ.", german:"Ja.", french:"Oui.", spanish:"Sí." },
  "no":                       { english:"No.", hindi:"नहीं।", telugu:"లేదు.", tamil:"இல்லை.", malayalam:"ഇല്ല.", german:"Nein.", french:"Non.", spanish:"No." },
  "what is your name":        { english:"What is your name?", hindi:"आपका नाम क्या है?", telugu:"మీ పేరు ఏమిటి?", tamil:"உங்கள் பெயர் என்ன?", malayalam:"താങ്കളുടെ പേര് എന്താണ്?", german:"Wie heißen Sie?", french:"Comment vous appelez-vous?", spanish:"¿Cómo te llamas?" },
  "where do you live":        { english:"Where do you live?", hindi:"आप कहाँ रहते हैं?", telugu:"మీరు ఎక్కడ నివసిస్తున్నారు?", tamil:"நீங்கள் எங்கு வாழ்கிறீர்கள்?", malayalam:"താങ്കൾ എവിടെ താമസിക്കുന്നു?", german:"Wo wohnen Sie?", french:"Où habitez-vous?", spanish:"¿Dónde vives?" },
  "how old are you":          { english:"How old are you?", hindi:"आपकी उम्र क्या है?", telugu:"మీ వయసు ఎంత?", tamil:"உங்கள் வயது என்ன?", malayalam:"താങ്കൾക്ക് എത്ര വയസ്സായി?", german:"Wie alt sind Sie?", french:"Quel âge avez-vous?", spanish:"¿Cuántos años tienes?" },
  "excuse me":                { english:"Excuse me.", hindi:"माफ़ कीजिए।", telugu:"క్షమించండి.", tamil:"மன்னிக்கவும்.", malayalam:"ക്ഷമിക്കൂ.", german:"Entschuldigung.", french:"Excusez-moi.", spanish:"Disculpe." },
  "i am sorry":               { english:"I am sorry.", hindi:"मुझे खेद है।", telugu:"నన్ను క్షమించండి.", tamil:"மன்னிக்கவும்.", malayalam:"ക്ഷമിക്കൂ.", german:"Es tut mir leid.", french:"Je suis désolé.", spanish:"Lo siento." },
  "see you tomorrow":         { english:"See you tomorrow.", hindi:"कल मिलते हैं।", telugu:"రేపు కలుద్దాం.", tamil:"நாளை சந்திப்போம்.", malayalam:"നാളെ കാണാം.", german:"Bis morgen.", french:"À demain.", spanish:"Hasta mañana." },
  "i dont understand":        { english:"I don't understand.", hindi:"मुझे समझ नहीं आया।", telugu:"నాకు అర్థం కాలేదు.", tamil:"எனக்கு புரியவில்லை.", malayalam:"എനിക്ക് മനസ്സിലാകുന്നില്ല.", german:"Ich verstehe nicht.", french:"Je ne comprends pas.", spanish:"No entiendo." },
  "can you help me":          { english:"Can you help me?", hindi:"क्या आप मेरी मदद कर सकते हैं?", telugu:"మీరు నాకు సహాయం చేయగలరా?", tamil:"நீங்கள் என்னை உதவ முடியுமா?", malayalam:"നിങ്ങൾക്ക് എന്നെ സഹായിക്കാമോ?", german:"Können Sie mir helfen?", french:"Pouvez-vous m'aider?", spanish:"¿Puedes ayudarme?" },
  "please help me":           { english:"Please help me.", hindi:"कृपया मेरी मदद करें।", telugu:"దయచేసి నన్ను సహాయం చేయండి.", tamil:"தயவுசெய்து என்னை உதவுங்கள்.", malayalam:"ദയവായി എന്നെ സഹായിക്കൂ.", german:"Bitte helfen Sie mir.", french:"Aidez-moi s'il vous plaît.", spanish:"Por favor ayúdame." },
  "what time is it":          { english:"What time is it?", hindi:"अभी कितने बजे हैं?", telugu:"ఇప్పుడు సమయం ఎంత?", tamil:"இப்போது நேரம் என்ன?", malayalam:"ഇപ്പോൾ സമയം എത്ര ആണ്?", german:"Wie spät ist es?", french:"Quelle heure est-il?", spanish:"¿Qué hora es?" },
  "i am hungry":              { english:"I am hungry.", hindi:"मुझे भूख लगी है।", telugu:"నాకు ఆకలిగా ఉంది.", tamil:"எனக்கு பசிக்கிறது.", malayalam:"എനിക്ക് വിശക്കുന്നു.", german:"Ich habe Hunger.", french:"J'ai faim.", spanish:"Tengo hambre." },
  "i need water":             { english:"I need water.", hindi:"मुझे पानी चाहिए।", telugu:"నాకు నీళ్ళు కావాలి.", tamil:"எனக்கு தண்ணீர் வேண்டும்.", malayalam:"എനിക്ക് വെള്ളം വേണം.", german:"Ich brauche Wasser.", french:"J'ai besoin d'eau.", spanish:"Necesito agua." },
  "where is the hotel":       { english:"Where is the hotel?", hindi:"होटल कहाँ है?", telugu:"హోటల్ ఎక్కడ ఉంది?", tamil:"ஹோட்டல் எங்கே இருக்கிறது?", malayalam:"ഹോട്ടൽ എവിടെ ആണ്?", german:"Wo ist das Hotel?", french:"Où est l'hôtel?", spanish:"¿Dónde está el hotel?" },
  "how much does it cost":    { english:"How much does it cost?", hindi:"इसकी कीमत क्या है?", telugu:"ఇది ఎంత?", tamil:"இது எவ்வளவு?", malayalam:"ഇതിന് എത്ര വിലയുണ്ട്?", german:"Wie viel kostet das?", french:"Combien ça coûte?", spanish:"¿Cuánto cuesta?" },
  "i need a doctor":          { english:"I need a doctor.", hindi:"मुझे डॉक्टर की जरूरत है।", telugu:"నాకు వైద్యుడు కావాలి.", tamil:"எனக்கு மருத்துவர் தேவை.", malayalam:"എനിക്ക് ഒരു ഡോക്ടർ വേണം.", german:"Ich brauche einen Arzt.", french:"J'ai besoin d'un médecin.", spanish:"Necesito un médico." },
  "i have a headache":        { english:"I have a headache.", hindi:"मुझे सिरदर्द है।", telugu:"నాకు తలనొప్పి ఉంది.", tamil:"எனக்கு தலைவலி இருக்கிறது.", malayalam:"എനിക്ക് തലവേദന ഉണ്ട്.", german:"Ich habe Kopfschmerzen.", french:"J'ai mal à la tête.", spanish:"Tengo dolor de cabeza." },
  "i have a fever":           { english:"I have a fever.", hindi:"मुझे बुखार है।", telugu:"నాకు జ్వరం ఉంది.", tamil:"எனக்கு காய்ச்சல் இருக்கிறது.", malayalam:"എനിക്ക് പനി ഉണ്ട്.", german:"Ich habe Fieber.", french:"J'ai de la fièvre.", spanish:"Tengo fiebre." },
  "call an ambulance":        { english:"Call an ambulance!", hindi:"एम्बुलेंस बुलाओ!", telugu:"యాంబులెన్స్ పిలవండి!", tamil:"ஆம்புலன்ஸ் அழையுங்கள்!", malayalam:"ആംബുലൻസ് വിളിക്കൂ!", german:"Rufen Sie einen Krankenwagen!", french:"Appelez une ambulance!", spanish:"¡Llame a una ambulancia!" },
  "where is the hospital":    { english:"Where is the hospital?", hindi:"अस्पताल कहाँ है?", telugu:"ఆసుపత్రి ఎక్కడ ఉంది?", tamil:"மருத்துவமனை எங்கே இருக்கிறது?", malayalam:"ആശുപത്രി എവിടെ ആണ്?", german:"Wo ist das Krankenhaus?", french:"Où est l'hôpital?", spanish:"¿Dónde está el hospital?" },
  "let us schedule a meeting":{ english:"Let us schedule a meeting.", hindi:"चलिए एक बैठक तय करते हैं।", telugu:"మనం ఒక సమావేశం ఏర్పాటు చేద్దాం.", tamil:"ஒரு கூட்டம் திட்டமிடுவோம்.", malayalam:"നമുക്ക് ഒരു യോഗം ഷെഡ്യൂൾ ചെയ്യാം.", german:"Lassen Sie uns ein Meeting planen.", french:"Planifions une réunion.", spanish:"Programemos una reunión." },
  "please restart the server":{ english:"Please restart the server.", hindi:"कृपया सर्वर पुनः आरंभ करें।", telugu:"దయచేసి సర్వర్ పున:ప్రారంభించండి.", tamil:"சர்வரை மறுதொடக்கம் செய்யவும்.", malayalam:"ദയവായി സർവ്വർ പുനരാരംഭിക്കൂ.", german:"Bitte starten Sie den Server neu.", french:"Veuillez redémarrer le serveur.", spanish:"Por favor reinicie el servidor." },
  "there is a bug in the code":{ english:"There is a bug in the code.", hindi:"कोड में एक बग है।", telugu:"కోడ్‌లో బగ్ ఉంది.", tamil:"குறியீட்டில் ஒரு பிழை உள்ளது.", malayalam:"കോഡിൽ ഒരു ബഗ് ഉണ്ട്.", german:"Es gibt einen Fehler im Code.", french:"Il y a un bug dans le code.", spanish:"Hay un error en el código." },
  "the weather is nice today":{ english:"The weather is nice today.", hindi:"आज मौसम अच्छा है।", telugu:"ఈరోజు వాతావరణం చాలా అందంగా ఉంది.", tamil:"இன்று வானிலை நன்றாக உள்ளது.", malayalam:"ഇന്ന് കാലാവസ്ഥ നല്ലതാണ്.", german:"Das Wetter ist heute schön.", french:"Le temps est beau aujourd'hui.", spanish:"El clima está agradable hoy." },
  "i love reading books":     { english:"I love reading books.", hindi:"मुझे किताबें पढ़ना बहुत पसंद है।", telugu:"నాకు పుస్తకాలు చదవడం చాలా ఇష్టం.", tamil:"எனக்கு புத்தகங்கள் படிப்பது மிகவும் பிடிக்கும்.", malayalam:"എനിക്ക് പുസ്തകങ്ങൾ വായിക്കാൻ ഇഷ്ടമാണ്.", german:"Ich liebe es, Bücher zu lesen.", french:"J'adore lire des livres.", spanish:"Me encanta leer libros." },
  "when is the final exam":   { english:"When is the final exam?", hindi:"अंतिम परीक्षा कब है?", telugu:"ఫైనల్ పరీక్ష ఎప్పుడు?", tamil:"இறுதி தேர்வு எப்போது?", malayalam:"അന്തിമ പരീക്ഷ എന്നാണ്?", german:"Wann ist die Abschlussprüfung?", french:"Quand est l'examen final?", spanish:"¿Cuándo es el examen final?" },
  "i need a taxi":            { english:"I need a taxi.", hindi:"मुझे टैक्सी चाहिए।", telugu:"నాకు టాక్సీ కావాలి.", tamil:"எனக்கு டாக்சி வேண்டும்.", malayalam:"എനിക്ക് ഒരു ടാക്സി വേണം.", german:"Ich brauche ein Taxi.", french:"J'ai besoin d'un taxi.", spanish:"Necesito un taxi." },
};

// Build reverse lookup: normalized phrase → english key  (for non-English sources)
const REVERSE_LOOKUP = {};
function buildReverseLookup() {
  for (const [enKey, langs] of Object.entries(PHRASE_TABLE)) {
    for (const [lang, phrase] of Object.entries(langs)) {
      REVERSE_LOOKUP[normalize(phrase)] = enKey;
      REVERSE_LOOKUP[phrase.toLowerCase().trim()] = enKey;
    }
  }
}
buildReverseLookup();

function normalize(text) {
  return text.toLowerCase().trim().replace(/[^\w\s]/g, "").trim();
}

// ── DOM refs ──────────────────────────────────────────────────────────────────
const statusDot    = document.getElementById("statusDot");
const statusText   = document.getElementById("statusText");
const srcGroup     = document.getElementById("srcLangGroup");
const tgtGroup     = document.getElementById("tgtLangGroup");
const swapBtn      = document.getElementById("swapBtn");
const micBtn       = document.getElementById("micBtn");
const micHint      = document.getElementById("micHint");
const waveform     = document.getElementById("waveform");
const inputText    = document.getElementById("inputText");
const translateBtn = document.getElementById("translateBtn");
const srcLabel     = document.getElementById("srcLabel");
const tgtLabel     = document.getElementById("tgtLabel");
const originalText = document.getElementById("originalText");
const translatedText = document.getElementById("translatedText");
const playBtn      = document.getElementById("playBtn");
const metricLatency = document.getElementById("metricLatency");
const metricConf   = document.getElementById("metricConf");
const confFill     = document.getElementById("confFill");
const metricDir    = document.getElementById("metricDir");
const metricSrc    = document.getElementById("metricSrc");
const historyList  = document.getElementById("historyList");
const clearBtn     = document.getElementById("clearBtn");
const audioPlayer  = document.getElementById("audioPlayer");
const copyBtn      = document.getElementById("copyBtn");
const charCount    = document.getElementById("charCount");
const btnSpinner   = document.getElementById("btnSpinner");
const btnText      = document.querySelector(".btn-text");
const themeBtn     = document.getElementById("themeBtn");

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  setupLangPills();
  setupSwap();
  setupWebSocket();
  setupSpeech();
  updateLabels();
  setStatus("loading");
  setupTheme();
  setupCharCount();
});

// ── Language pills ────────────────────────────────────────────────────────────
function setupLangPills() {
  srcGroup.querySelectorAll(".lang-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      srcGroup.querySelectorAll(".lang-pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      srcLang = btn.dataset.lang;
      // Update speech recognition language
      if (recognition) recognition.lang = getSpeechLang(srcLang);
      updateLabels();
    });
  });
  tgtGroup.querySelectorAll(".lang-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      tgtGroup.querySelectorAll(".lang-pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      tgtLang = btn.dataset.lang;
      updateLabels();
    });
  });
}

function getSpeechLang(lang) {
  const map = { english:"en-US", hindi:"hi-IN", telugu:"te-IN",
                tamil:"ta-IN", malayalam:"ml-IN", german:"de-DE",
                french:"fr-FR", spanish:"es-ES" };
  return map[lang] || "en-US";
}

function updateLabels() {
  const s = LANG_META[srcLang], t = LANG_META[tgtLang];
  srcLabel.textContent = `${s.flag} Original (${s.label})`;
  tgtLabel.textContent = `${t.flag} ${t.label} Translation`;
  inputText.placeholder = `Type in ${s.label}…`;
  metricDir.textContent = `${s.label} → ${t.label}`;
}

// ── Swap ──────────────────────────────────────────────────────────────────────
function setupSwap() {
  swapBtn.addEventListener("click", () => {
    // Only swap if tgtLang is also a valid source language
    const srcLangs = ["english","hindi","telugu","tamil","malayalam"];
    if (!srcLangs.includes(tgtLang)) return;

    [srcLang, tgtLang] = [tgtLang, srcLang];

    srcGroup.querySelectorAll(".lang-pill").forEach(b => {
      b.classList.toggle("active", b.dataset.lang === srcLang);
    });
    tgtGroup.querySelectorAll(".lang-pill").forEach(b => {
      b.classList.toggle("active", b.dataset.lang === tgtLang);
    });
    updateLabels();
    // Swap displayed text too
    const tmp = inputText.value;
    inputText.value = translatedText.textContent === "—" ? "" : translatedText.textContent;
    if (tmp) originalText.textContent = tmp;
  });
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
function setupWebSocket() {
  try {
    ws = new WebSocket(WS_URL);
    ws.onopen    = () => setStatus("online");
    ws.onclose   = () => { setStatus("offline"); setTimeout(setupWebSocket, 3000); };
    ws.onerror   = () => setStatus("offline");
    ws.onmessage = (evt) => {
      const data = JSON.parse(evt.data);
      if (data.error) { showError(data.error); return; }
      renderResult(inputText.value, data);
    };
  } catch(e) { setStatus("offline"); }
}

function setStatus(state) {
  statusDot.className = `dot ${state}`;
  statusText.textContent = { online:"Backend Online", offline:"Backend Offline", loading:"Connecting…" }[state] || state;
}

// ── Translate ─────────────────────────────────────────────────────────────────
translateBtn.addEventListener("click", () => triggerTranslation(inputText.value.trim()));
inputText.addEventListener("keydown", e => { if (e.key==="Enter" && (e.ctrlKey||e.metaKey)) translateBtn.click(); });

async function triggerTranslation(text) {
  if (!text) return;
  translateBtn.disabled = true;
  btnText.style.display = "none";
  btnSpinner.style.display = "flex";
  try {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ text, src_lang: srcLang, tgt_lang: tgtLang }));
    } else {
      const res = await fetch(`${API_BASE}/translate`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ text, src_lang: srcLang, tgt_lang: tgtLang, tts: true }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      renderResult(text, await res.json());
    }
  } catch(e) {
    demoTranslate(text);
  } finally {
    translateBtn.disabled = false;
    btnText.style.display = "inline";
    btnSpinner.style.display = "none";
  }
}

// ── Offline demo using PHRASE_TABLE ──────────────────────────────────────────
function demoTranslate(text) {
  const normInput = normalize(text);
  let translated = null;

  // 1. Find english key from any language input
  let enKey = REVERSE_LOOKUP[normInput] || REVERSE_LOOKUP[text.toLowerCase().trim()];

  // 2. Partial match
  if (!enKey) {
    for (const [k, v] of Object.entries(REVERSE_LOOKUP)) {
      if (normInput && k && (normInput.includes(k) || k.includes(normInput))) {
        enKey = v; break;
      }
    }
  }

  // 3. Get target language translation
  if (enKey && PHRASE_TABLE[enKey]) {
    translated = PHRASE_TABLE[enKey][tgtLang];
  }

  const isOffline = !translated;
  if (!translated) translated = `⚠ Backend offline. Run "python app.py" for full AI translation.`;

  renderResult(text, {
    original: text, translated,
    src_lang: srcLang, tgt_lang: tgtLang,
    confidence: isOffline ? 0 : 0.97,
    latency_ms: Math.round(Math.random()*30+10),
    total_ms:   Math.round(Math.random()*30+12),
    source: isOffline ? "offline" : "dictionary",
    audio_b64: null,
  });
}

// ── Render result ─────────────────────────────────────────────────────────────
function renderResult(original, data) {
  originalText.textContent   = original || data.original || "—";
  translatedText.textContent = data.translated || "—";

  const latency = data.total_ms || data.latency_ms || 0;
  const conf    = parseFloat(data.confidence || 0);

  metricLatency.textContent = `${latency} ms`;
  metricConf.textContent    = `${Math.round(conf * 100)}%`;
  confFill.style.width      = `${Math.round(conf * 100)}%`;
  metricSrc.textContent     = data.source || "—";

  const s = LANG_META[data.src_lang || srcLang];
  const t = LANG_META[data.tgt_lang || tgtLang];
  metricDir.textContent = `${s?.label || srcLang} → ${t?.label || tgtLang}`;

  if (data.audio_b64) {
    audioPlayer.src = `data:${data.audio_mime || "audio/mpeg"};base64,${data.audio_b64}`;
    playBtn.style.display = "inline-flex";
    playBtn.onclick = () => audioPlayer.play();
  } else {
    playBtn.style.display = "none";
  }
  // Show copy button when there's a translation
  if (data.translated && !data.translated.startsWith("⚠")) {
    copyBtn.style.display = "inline-flex";
    copyBtn.classList.remove("copied");
    copyBtn.textContent = "📋 Copy";
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(data.translated).then(() => {
        copyBtn.textContent = "✅ Copied!";
        copyBtn.classList.add("copied");
        setTimeout(() => { copyBtn.textContent = "📋 Copy"; copyBtn.classList.remove("copied"); }, 2000);
      });
    };
  } else {
    copyBtn.style.display = "none";
  }

  addHistory({ original: original || data.original, translated: data.translated,
               src: data.src_lang || srcLang, tgt: data.tgt_lang || tgtLang, latency });
}

// ── History ───────────────────────────────────────────────────────────────────
function addHistory(entry) {
  history.unshift(entry);
  if (history.length > 40) history.pop();
  renderHistory();
}
function renderHistory() {
  if (!history.length) {
    historyList.innerHTML = `<div class="history-empty">No translations yet — start speaking or typing!</div>`;
    return;
  }
  const s = m => LANG_META[m]?.flag || "";
  historyList.innerHTML = history.map(h => `
    <div class="history-item">
      <span class="hi-lang">${s(h.src)} ${LANG_META[h.src]?.label||h.src}</span>
      <div class="hi-src">${escHtml(h.original)}</div>
      <div class="hi-arrow">→</div>
      <div class="hi-tgt">${escHtml(h.translated||"—")}</div>
      <span class="hi-lang">${s(h.tgt)} ${LANG_META[h.tgt]?.label||h.tgt}</span>
    </div>`).join("");
}
clearBtn.addEventListener("click", () => { history = []; renderHistory(); });

// ── Web Speech API ────────────────────────────────────────────────────────────
function setupSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { micHint.textContent = "Use Chrome for mic support"; return; }
  recognition = new SR();
  recognition.continuous     = false;
  recognition.interimResults = true;
  recognition.lang           = getSpeechLang(srcLang);

  recognition.onstart  = () => { isRecording=true; micBtn.classList.add("recording"); waveform.classList.add("active"); micHint.textContent="Listening…"; };
  recognition.onresult = (e) => {
    let interim="", final="";
    for (let i=e.resultIndex;i<e.results.length;i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) final+=t; else interim+=t;
    }
    inputText.value = final||interim;
    if (final) triggerTranslation(final);
  };
  recognition.onerror = () => stopRecording();
  recognition.onend   = () => stopRecording();

  micBtn.addEventListener("click", () => {
    recognition.lang = getSpeechLang(srcLang);
    if (isRecording) recognition.stop();
    else { try { recognition.start(); } catch(e){} }
  });
}
function stopRecording() {
  isRecording=false; micBtn.classList.remove("recording");
  waveform.classList.remove("active"); micHint.textContent="Click to start listening";
}

// ── Theme Toggle ─────────────────────────────────────────────────────────────
function setupTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "light") { document.body.classList.add("light"); themeBtn.textContent = "☀️"; }
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    themeBtn.textContent = isLight ? "☀️" : "🌙";
    localStorage.setItem("theme", isLight ? "light" : "dark");
  });
}

// ── Char Counter ──────────────────────────────────────────────────────────────
function setupCharCount() {
  inputText.addEventListener("input", () => {
    const len = inputText.value.length;
    charCount.textContent = `${len} / 500`;
    charCount.style.color = len > 450 ? "#ef4444" : "var(--text-muted)";
  });
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function showError(msg) { translatedText.textContent = `⚠ ${msg}`; }
function escHtml(s="") {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
