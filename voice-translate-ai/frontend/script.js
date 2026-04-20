/**
 * script.js — VoiceTranslate AI v4
 * Features: Translator | Document Translation | Conversation Mode | BLEU Visualizer | Voice Speed
 */

const API_BASE = "https://voice-translator-2-1-4.onrender.com";
const WS_URL   = "wss://voice-translator-2-1-4.onrender.com/ws/translate";

let srcLang = "english";
let tgtLang = "telugu";
let isRecording = false;
let recognition = null;
let ws = null;
let history = [];

const LANG_META = {
  english:   { label:"English",   flag:"🇬🇧" },
  hindi:     { label:"Hindi",     flag:"🇮🇳" },
  telugu:    { label:"Telugu",    flag:"🇮🇳" },
  tamil:     { label:"Tamil",     flag:"🇮🇳" },
  malayalam: { label:"Malayalam", flag:"🇮🇳" },
  german:    { label:"German",    flag:"🇩🇪" },
  french:    { label:"French",    flag:"🇫🇷" },
  spanish:   { label:"Spanish",   flag:"🇪🇸" },
};

// Phrase table for offline fallback
const PHRASE_TABLE = {
  "how are you":{"english":"How are you?","hindi":"आप कैसे हैं?","telugu":"మీరు ఎలా ఉన్నారు?","tamil":"நீங்கள் எப்படி இருக்கிறீர்கள்?","malayalam":"താങ്കൾ എങ്ങനെ ഉണ്ട്?","german":"Wie geht es Ihnen?","french":"Comment allez-vous?","spanish":"¿Cómo estás?"},
  "good morning":{"english":"Good morning!","hindi":"सुप्रभात!","telugu":"శుభోదయం!","tamil":"காலை வணக்கம்!","malayalam":"സുപ്രഭാതം!","german":"Guten Morgen!","french":"Bonjour!","spanish":"¡Buenos días!"},
  "hello":{"english":"Hello.","hindi":"नमस्ते।","telugu":"హలో.","tamil":"வணக்கம்.","malayalam":"ഹലോ.","german":"Hallo.","french":"Bonjour.","spanish":"Hola."},
  "thank you":{"english":"Thank you.","hindi":"धन्यवाद।","telugu":"ధన్యవాదాలు.","tamil":"நன்றி.","malayalam":"നന്ദി.","german":"Danke.","french":"Merci.","spanish":"Gracias."},
  "bye":{"english":"Goodbye.","hindi":"अलविदा।","telugu":"వీడ్కోలు.","tamil":"விடைபெறுகிறேன்.","malayalam":"വിടവാങ്ങൽ.","german":"Auf Wiedersehen.","french":"Au revoir.","spanish":"Adiós."},
  "yes":{"english":"Yes.","hindi":"हाँ।","telugu":"అవును.","tamil":"ஆம்.","malayalam":"അതെ.","german":"Ja.","french":"Oui.","spanish":"Sí."},
  "no":{"english":"No.","hindi":"नहीं।","telugu":"లేదు.","tamil":"இல்லை.","malayalam":"ഇല്ല.","german":"Nein.","french":"Non.","spanish":"No."},
  "i need a doctor":{"english":"I need a doctor.","hindi":"मुझे डॉक्टर की जरूरत है।","telugu":"నాకు వైద్యుడు కావాలి.","tamil":"எனக்கு மருத்துவர் தேவை.","malayalam":"എനിക்ക് ഒരു ഡോക്ടർ വേണം.","german":"Ich brauche einen Arzt.","french":"J'ai besoin d'un médecin.","spanish":"Necesito un médico."},
  "where is the hospital":{"english":"Where is the hospital?","hindi":"अस्पताल कहाँ है?","telugu":"ఆసుపత్రి ఎక్కడ ఉంది?","tamil":"மருத்துவமனை எங்கே?","malayalam":"ആശുപത്രി എവിടെ?","german":"Wo ist das Krankenhaus?","french":"Où est l'hôpital?","spanish":"¿Dónde está el hospital?"},
};

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
  return text.toLowerCase().trim().replace(/[^\w\s]/g,"").trim();
}

// ── DOM refs ──────────────────────────────────────────────────────────────────
const statusDot      = document.getElementById("statusDot");
const statusText     = document.getElementById("statusText");
const srcGroup       = document.getElementById("srcLangGroup");
const tgtGroup       = document.getElementById("tgtLangGroup");
const swapBtn        = document.getElementById("swapBtn");
const micBtn         = document.getElementById("micBtn");
const micHint        = document.getElementById("micHint");
const waveform       = document.getElementById("waveform");
const inputText      = document.getElementById("inputText");
const translateBtn   = document.getElementById("translateBtn");
const srcLabel       = document.getElementById("srcLabel");
const tgtLabel       = document.getElementById("tgtLabel");
const originalText   = document.getElementById("originalText");
const translatedText = document.getElementById("translatedText");
const playBtn        = document.getElementById("playBtn");
const copyBtn        = document.getElementById("copyBtn");
const metricLatency  = document.getElementById("metricLatency");
const metricConf     = document.getElementById("metricConf");
const confFill       = document.getElementById("confFill");
const metricDir      = document.getElementById("metricDir");
const metricSrc      = document.getElementById("metricSrc");
const historyList    = document.getElementById("historyList");
const clearBtn       = document.getElementById("clearBtn");
const audioPlayer    = document.getElementById("audioPlayer");
const charCount      = document.getElementById("charCount");
const btnSpinner     = document.getElementById("btnSpinner");
const btnText        = document.querySelector(".btn-text");
const themeBtn       = document.getElementById("themeBtn");
const speedSlider    = document.getElementById("speedSlider");
const speedVal       = document.getElementById("speedVal");
const speedControl   = document.getElementById("speedControl");

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupLangPills();
  setupSwap();
  setupWebSocket();
  setupSpeech();
  updateLabels();
  setStatus("loading");
  setupTheme();
  setupCharCount();
  setupSpeedControl();
  setupDocumentTranslation();
  setupConversationMode();
  renderBleuChart();
});

// ── Tabs ──────────────────────────────────────────────────────────────────────
function setupTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });
}

// ── Language pills ────────────────────────────────────────────────────────────
function setupLangPills() {
  srcGroup.querySelectorAll(".lang-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      srcGroup.querySelectorAll(".lang-pill").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      srcLang = btn.dataset.lang;
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
  return {english:"en-US",hindi:"hi-IN",telugu:"te-IN",tamil:"ta-IN",malayalam:"ml-IN",german:"de-DE",french:"fr-FR",spanish:"es-ES"}[lang]||"en-US";
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
    const srcLangs = ["english","hindi","telugu","tamil","malayalam"];
    if (!srcLangs.includes(tgtLang)) return;
    [srcLang, tgtLang] = [tgtLang, srcLang];
    srcGroup.querySelectorAll(".lang-pill").forEach(b => b.classList.toggle("active", b.dataset.lang === srcLang));
    tgtGroup.querySelectorAll(".lang-pill").forEach(b => b.classList.toggle("active", b.dataset.lang === tgtLang));
    updateLabels();
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
  statusText.textContent = {online:"Backend Online",offline:"Backend Offline",loading:"Connecting…"}[state]||state;
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
      ws.send(JSON.stringify({ text, src_lang:srcLang, tgt_lang:tgtLang }));
    } else {
      const res = await fetch(`${API_BASE}/translate`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ text, src_lang:srcLang, tgt_lang:tgtLang, tts:true }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      renderResult(text, await res.json());
    }
  } catch(e) { demoTranslate(text); }
  finally {
    translateBtn.disabled = false;
    btnText.style.display = "inline";
    btnSpinner.style.display = "none";
  }
}

function demoTranslate(text) {
  const normInput = normalize(text);
  let translated = null;
  let enKey = REVERSE_LOOKUP[normInput] || REVERSE_LOOKUP[text.toLowerCase().trim()];
  if (!enKey) {
    for (const [k,v] of Object.entries(REVERSE_LOOKUP)) {
      if (normInput && k && (normInput.includes(k)||k.includes(normInput))) { enKey=v; break; }
    }
  }
  if (enKey && PHRASE_TABLE[enKey]) translated = PHRASE_TABLE[enKey][tgtLang];
  const isOffline = !translated;
  if (!translated) translated = `⚠ Backend offline. Start backend to translate.`;
  renderResult(text, { original:text, translated, src_lang:srcLang, tgt_lang:tgtLang,
    confidence:isOffline?0:0.97, latency_ms:20, total_ms:22, source:isOffline?"offline":"dictionary", audio_b64:null });
}

// ── Render result ─────────────────────────────────────────────────────────────
function renderResult(original, data) {
  originalText.textContent   = original || data.original || "—";
  translatedText.textContent = data.translated || "—";
  const latency = data.total_ms || data.latency_ms || 0;
  const conf    = parseFloat(data.confidence || 0);
  metricLatency.textContent = `${latency} ms`;
  metricConf.textContent    = `${Math.round(conf*100)}%`;
  confFill.style.width      = `${Math.round(conf*100)}%`;
  metricSrc.textContent     = data.source || "—";
  const s = LANG_META[data.src_lang||srcLang], t = LANG_META[data.tgt_lang||tgtLang];
  metricDir.textContent = `${s?.label||srcLang} → ${t?.label||tgtLang}`;

  if (data.audio_b64) {
    audioPlayer.src = `data:${data.audio_mime||"audio/mpeg"};base64,${data.audio_b64}`;
    playBtn.style.display = "inline-flex";
    speedControl.style.display = "block";
    playBtn.onclick = () => { audioPlayer.playbackRate = parseFloat(speedSlider.value); audioPlayer.play(); };
  } else {
    playBtn.style.display = "none";
    speedControl.style.display = "none";
  }
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
  } else { copyBtn.style.display = "none"; }

  addHistory({ original:original||data.original, translated:data.translated,
               src:data.src_lang||srcLang, tgt:data.tgt_lang||tgtLang, latency });
}

// ── History ───────────────────────────────────────────────────────────────────
function addHistory(entry) {
  history.unshift(entry);
  if (history.length > 40) history.pop();
  renderHistory();
}
function renderHistory() {
  if (!history.length) { historyList.innerHTML=`<div class="history-empty">No translations yet — start speaking or typing!</div>`; return; }
  const f = m => LANG_META[m]?.flag||"";
  historyList.innerHTML = history.map(h => `
    <div class="history-item">
      <span class="hi-lang">${f(h.src)} ${LANG_META[h.src]?.label||h.src}</span>
      <div class="hi-src">${escHtml(h.original)}</div>
      <div class="hi-arrow">→</div>
      <div class="hi-tgt">${escHtml(h.translated||"—")}</div>
      <span class="hi-lang">${f(h.tgt)} ${LANG_META[h.tgt]?.label||h.tgt}</span>
    </div>`).join("");
}
clearBtn.addEventListener("click", () => { history=[]; renderHistory(); });

// ── Web Speech API ────────────────────────────────────────────────────────────
function setupSpeech() {
  const SR = window.SpeechRecognition||window.webkitSpeechRecognition;
  if (!SR) { micHint.textContent="Use Chrome for mic support"; return; }
  recognition = new SR();
  recognition.continuous=false; recognition.interimResults=true;
  recognition.lang=getSpeechLang(srcLang);
  recognition.onstart  = () => { isRecording=true; micBtn.classList.add("recording"); waveform.classList.add("active"); micHint.textContent="Listening…"; };
  recognition.onresult = (e) => {
    let interim="", final="";
    for (let i=e.resultIndex;i<e.results.length;i++) {
      const t=e.results[i][0].transcript;
      if (e.results[i].isFinal) final+=t; else interim+=t;
    }
    inputText.value=final||interim;
    if (final) triggerTranslation(final);
  };
  recognition.onerror = () => stopRecording();
  recognition.onend   = () => stopRecording();
  micBtn.addEventListener("click", () => {
    recognition.lang=getSpeechLang(srcLang);
    if (isRecording) recognition.stop();
    else { try { recognition.start(); } catch(e){} }
  });
}
function stopRecording() {
  isRecording=false; micBtn.classList.remove("recording");
  waveform.classList.remove("active"); micHint.textContent="Click to start listening";
}

// ── Theme ─────────────────────────────────────────────────────────────────────
function setupTheme() {
  const saved = localStorage.getItem("theme");
  if (saved==="light") { document.body.classList.add("light"); themeBtn.textContent="☀️"; }
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    themeBtn.textContent = isLight?"☀️":"🌙";
    localStorage.setItem("theme", isLight?"light":"dark");
  });
}

// ── Char Counter ──────────────────────────────────────────────────────────────
function setupCharCount() {
  inputText.addEventListener("input", () => {
    const len = inputText.value.length;
    charCount.textContent = `${len} / 500`;
    charCount.style.color = len>450?"#ef4444":"var(--text-muted)";
  });
}

// ── ⑥ Voice Speed Control ─────────────────────────────────────────────────────
function setupSpeedControl() {
  speedSlider.addEventListener("input", () => {
    speedVal.textContent = `${parseFloat(speedSlider.value).toFixed(1)}x`;
    if (audioPlayer.src) audioPlayer.playbackRate = parseFloat(speedSlider.value);
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// ③ DOCUMENT TRANSLATION
// ══════════════════════════════════════════════════════════════════════════════
function setupDocumentTranslation() {
  const uploadZone   = document.getElementById("uploadZone");
  const docFile      = document.getElementById("docFile");
  const docPreview   = document.getElementById("docPreview");
  const docFileName  = document.getElementById("docFileName");
  const docWordCount = document.getElementById("docWordCount");
  const docOrigText  = document.getElementById("docOriginalText");
  const docTransBtn  = document.getElementById("docTranslateBtn");
  const docProgress  = document.getElementById("docProgress");
  const docProgFill  = document.getElementById("docProgressFill");
  const docProgText  = document.getElementById("docProgressText");
  const docResult    = document.getElementById("docResult");
  const docTransText = document.getElementById("docTranslatedText");
  const docDlBtn     = document.getElementById("docDownloadBtn");
  const docSrcLang   = document.getElementById("docSrcLang");
  const docTgtLang   = document.getElementById("docTgtLang");

  let docContent = "";

  uploadZone.addEventListener("click", () => docFile.click());
  uploadZone.addEventListener("dragover", e => { e.preventDefault(); uploadZone.style.borderColor="var(--accent)"; });
  uploadZone.addEventListener("dragleave", () => { uploadZone.style.borderColor=""; });
  uploadZone.addEventListener("drop", e => { e.preventDefault(); uploadZone.style.borderColor=""; if (e.dataTransfer.files[0]) loadFile(e.dataTransfer.files[0]); });
  docFile.addEventListener("change", () => { if (docFile.files[0]) loadFile(docFile.files[0]); });

  function loadFile(file) {
    if (!file.name.endsWith(".txt")) { alert("Please upload a .txt file"); return; }
    const reader = new FileReader();
    reader.onload = (e) => {
      docContent = e.target.result;
      const words = docContent.trim().split(/\s+/).length;
      docFileName.textContent = file.name;
      docWordCount.textContent = `${words} words`;
      docOrigText.textContent = docContent.substring(0, 500) + (docContent.length > 500 ? "…" : "");
      docPreview.style.display = "block";
      docTransBtn.style.display = "flex";
      docResult.style.display = "none";
    };
    reader.readAsText(file);
  }

  docTransBtn.addEventListener("click", async () => {
    if (!docContent) return;
    const src = docSrcLang.value;
    const tgt = docTgtLang.value;
    const paragraphs = docContent.split("\n").filter(p => p.trim().length > 0);
    docProgress.style.display = "block";
    docResult.style.display = "none";
    docTransBtn.disabled = true;
    let translated = [];
    for (let i = 0; i < paragraphs.length; i++) {
      const pct = Math.round(((i+1)/paragraphs.length)*100);
      docProgFill.style.width = `${pct}%`;
      docProgText.textContent = `Translating paragraph ${i+1} of ${paragraphs.length}…`;
      try {
        const res = await fetch(`${API_BASE}/translate`, {
          method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({ text:paragraphs[i], src_lang:src, tgt_lang:tgt, tts:false }),
        });
        if (res.ok) {
          const data = await res.json();
          translated.push(data.translated || paragraphs[i]);
        } else { translated.push(paragraphs[i]); }
      } catch(e) { translated.push(`[${paragraphs[i]}]`); }
    }
    docProgress.style.display = "none";
    docTransBtn.disabled = false;
    const finalText = translated.join("\n\n");
    docTransText.textContent = finalText;
    docResult.style.display = "block";
    docDlBtn.onclick = () => {
      const blob = new Blob([finalText], { type:"text/plain;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `translated_${tgt}.txt`;
      a.click();
    };
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// ④ CONVERSATION MODE
// ══════════════════════════════════════════════════════════════════════════════
function setupConversationMode() {
  const convChat   = document.getElementById("convChat");
  const convLangA  = document.getElementById("convLangA");
  const convLangB  = document.getElementById("convLangB");
  const convInputA = document.getElementById("convInputA");
  const convInputB = document.getElementById("convInputB");
  const convSendA  = document.getElementById("convSendA");
  const convSendB  = document.getElementById("convSendB");
  const convClear  = document.getElementById("convClearBtn");

  let convEmpty = convChat.querySelector(".conv-empty");

  async function sendConvMessage(text, fromLang, toLang, side) {
    if (!text.trim()) return;
    if (convEmpty) { convEmpty.remove(); convEmpty = null; }

    // Add bubble immediately with original
    const bubble = document.createElement("div");
    bubble.className = `conv-bubble conv-bubble-${side}`;
    bubble.innerHTML = `
      <div class="conv-bubble-original">${LANG_META[fromLang]?.flag||""} ${escHtml(text)}</div>
      <div class="conv-bubble-translated">⏳ Translating…</div>
      <div class="conv-bubble-lang">${LANG_META[fromLang]?.label||fromLang} → ${LANG_META[toLang]?.label||toLang}</div>
    `;
    convChat.appendChild(bubble);
    convChat.scrollTop = convChat.scrollHeight;

    try {
      const res = await fetch(`${API_BASE}/translate`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ text, src_lang:fromLang, tgt_lang:toLang, tts:false }),
      });
      if (res.ok) {
        const data = await res.json();
        bubble.querySelector(".conv-bubble-translated").textContent = data.translated || text;
      } else { bubble.querySelector(".conv-bubble-translated").textContent = `[Translation failed]`; }
    } catch(e) {
      bubble.querySelector(".conv-bubble-translated").textContent = `[Offline — backend needed]`;
    }
    convChat.scrollTop = convChat.scrollHeight;
  }

  convSendA.addEventListener("click", () => {
    const text = convInputA.value.trim();
    if (!text) return;
    sendConvMessage(text, convLangA.value, convLangB.value, "a");
    convInputA.value = "";
  });
  convSendB.addEventListener("click", () => {
    const text = convInputB.value.trim();
    if (!text) return;
    sendConvMessage(text, convLangB.value, convLangA.value, "b");
    convInputB.value = "";
  });
  convInputA.addEventListener("keydown", e => { if (e.key==="Enter") convSendA.click(); });
  convInputB.addEventListener("keydown", e => { if (e.key==="Enter") convSendB.click(); });
  convClear.addEventListener("click", () => {
    convChat.innerHTML = `<div class="conv-empty">Start a conversation by typing below ↓</div>`;
    convEmpty = convChat.querySelector(".conv-empty");
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// ⑤ BLEU SCORE VISUALIZER
// ══════════════════════════════════════════════════════════════════════════════
function renderBleuChart() {
  const data = [
    { lang:"Hindi",   baseline:47.93, finetuned:68.85 },
    { lang:"German",  baseline:13.73, finetuned:46.80 },
    { lang:"French",  baseline:28.30, finetuned:36.85 },
    { lang:"Spanish", baseline:15.90, finetuned:47.27 },
  ];
  const maxVal = 80;
  const chart = document.getElementById("bleuChart");
  chart.innerHTML = data.map(d => `
    <div class="bleu-row">
      <div class="bleu-lang">${d.lang}</div>
      <div class="bleu-bars">
        <div class="bleu-bar-wrap">
          <span class="bleu-bar-label">Baseline</span>
          <div class="bleu-bar-bg">
            <div class="bleu-bar-fill bleu-bar-baseline" style="width:${(d.baseline/maxVal)*100}%">${d.baseline}</div>
          </div>
          <span class="bleu-val">${d.baseline}</span>
        </div>
        <div class="bleu-bar-wrap">
          <span class="bleu-bar-label">Fine-tuned</span>
          <div class="bleu-bar-bg">
            <div class="bleu-bar-fill bleu-bar-finetuned" style="width:${(d.finetuned/maxVal)*100}%">${d.finetuned}</div>
          </div>
          <span class="bleu-val">${d.finetuned}</span>
        </div>
      </div>
      <div style="font-size:.8rem;color:var(--success);font-weight:700;align-self:center">+${(d.finetuned-d.baseline).toFixed(2)}</div>
    </div>
  `).join("");

  // Loss curve SVG
  const lossData = [
    {epoch:1,train:2.45,val:2.31},
    {epoch:2,train:1.82,val:1.74},
    {epoch:3,train:1.43,val:1.39},
  ];
  const W=600, H=140, padL=40, padB=30, padT=10, padR=20;
  const xs = lossData.map((_,i)=> padL + i*((W-padL-padR)/2));
  const maxL=2.6, minL=1.2;
  const yScale = v => padT + (H-padT-padB)*(1-(v-minL)/(maxL-minL));
  const trainPath = lossData.map((d,i)=>`${i===0?"M":"L"}${xs[i]},${yScale(d.train)}`).join(" ");
  const valPath   = lossData.map((d,i)=>`${i===0?"M":"L"}${xs[i]},${yScale(d.val)}`).join(" ");

  document.getElementById("lossChart").innerHTML = `
    <div class="loss-svg-wrap">
      <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
        <!-- Grid lines -->
        ${[1.4,1.8,2.2].map(v=>`
          <line x1="${padL}" y1="${yScale(v)}" x2="${W-padR}" y2="${yScale(v)}" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
          <text x="${padL-4}" y="${yScale(v)+4}" text-anchor="end" fill="#94a3b8" font-size="10">${v}</text>
        `).join("")}
        <!-- X labels -->
        ${lossData.map((d,i)=>`<text x="${xs[i]}" y="${H-6}" text-anchor="middle" fill="#94a3b8" font-size="10">Epoch ${d.epoch}</text>`).join("")}
        <!-- Train loss -->
        <path d="${trainPath}" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
        <!-- Val loss -->
        <path d="${valPath}" fill="none" stroke="#10b981" stroke-width="2.5" stroke-dasharray="6 3"/>
        <!-- Dots -->
        ${lossData.map((d,i)=>`
          <circle cx="${xs[i]}" cy="${yScale(d.train)}" r="4" fill="#3b82f6"/>
          <circle cx="${xs[i]}" cy="${yScale(d.val)}"   r="4" fill="#10b981"/>
        `).join("")}
      </svg>
    </div>
    <div style="display:flex;gap:20px;margin-top:10px;font-size:.78rem">
      <span style="color:#3b82f6">● Training Loss</span>
      <span style="color:#10b981">● Validation Loss (dashed)</span>
    </div>
  `;
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function showError(msg) { translatedText.textContent = `⚠ ${msg}`; }
function escHtml(s="") {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
