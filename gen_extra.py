#!/usr/bin/env python3
# Generates apikonnect.html (enterprise LLMs + API directory + tokens/connectors)
# and devzone.html (in-page terminal with Termux/ssh/Eel bridge).
import io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
import base64
FACE_B64 = base64.b64encode(open(os.path.join(ROOT,'assets','face-small.jpg'),'rb').read()).decode()
ORB_B64 = base64.b64encode(open(os.path.join(ROOT,'assets','face-orb.jpg'),'rb').read()).decode()

RAW_APIS = """Microsoft Azure Cognitive Services Ink Recognizer API
CrowdStrike Threat Graph API
Google Cloud AI Platform Pipelines API
SnatchBot API
CrowdStrike Falcon Respond API
zvelo API
Scale AI API
Plum Voice API
SEON API
Lastline Network API
Veritone API
Kubeflow Pipelines API
Google Cloud Video Intelligence API
AT&T Speech API
Everypixel OAuth API
Google Cloud Natural Language API
Deepomatic Weapon Detection API
Flow.ai WebSocket API
Testim Dev Kit JavaScript API
VergeSense API
Amazon Machine Learning API
Alexa Skill Management API
Alexa Device Address API
Amazon Alexa Customer Profile API
Amazon Alexa Music Skill API
Amazon Alexa Shopping and To Do List API
AWS Amazon Personalize API
Amazon List Skills API
Amazon Alexa Skill Voice Service API
Amazon Alexa Baby Activity Skill API
Android Neural Networks API
Bing Speech Recognition API
Microsoft Azure Cognitive Services Custom Vision Prediction API
Microsoft Cognitive Services Video API
Microsoft Azure Cognitive Services Form Recognizer API
Microsoft Azure Cognitive Services Anomaly Detector API
Figure-Eight API
Amadeus AI-Generated Photos API
Atomic Reach API
IBM Watson API
IBM Watson Speech to Text API
IBM Watson Discovery API
IBM Watson Assistant API
IBM Watson Natural Language Classifier API
Onfido API
Freelancer API
Proximity Events API
Mozilla Ambient Light Sensor API
Mozilla Screen Orientation API
Mozilla Battery Status API
Google Assistant API
Lilt API
Image Recognition API
AB Tasty API
expert.ai Natural Language API
Callsign API
Boxalino Data Intelligence API
FactSet PA Engine API
Labelbox API
Freshchat API
TypingDNA API
CrowdStrike Falcon Streaming API
Text API
CrowdStrike Falcon Intelligence API
CrowdStrike Falcon Management API
Slingshot Aerospace API
Infeed API
Rasa API
BlueShift Catalog API
BlueShift Campaign Create API
DeepAI Image Colorization API
DeepAI Text Summarization API
DeepAI Image Similarity API
DeepAI Sentiment Analysis API
DeepAI Nudity Detection API
DeepAI Neural Talk API
DeepAI Demographic Recognition API
DeepAI Image Inpainting API
DeepAI Video Recognition API
indico API
MonkeyLearn API
Intento API
Intento Translate API
Deepomatic Fashion Apparel Detection API
Deepomatic Furniture Detection API
Spectrum API
SophosLabs Intelix IP Category Lookup API
Wit.AI API
Amper Music API
Google Prediction API
Bold360 API
Jibo API
Bitvore Precision News Corporate API
Bitvore Precision News Economic API
Upstart Credit Decision API
Coralogix API
Replica API
Generated Photos API
Colormind API
Interact API
TasteDive API
Jukedeck API
SignalVine API
Simility API
BlueShift API
Trueface API
Optimove API
ForwardLane API
Ximilar API
Amio.io Webhooks API
Amio.io API
Pairaphrase Translation API
CarNET API
Violet API
Plume API
BigML API
Qloo API
Lastline Notification API
Lastline RADIUS API
Lastline Reporting API
AudD Music Recognition API
PicScout API
Fritz API
nativeMsg API
Seldon JavaScript API
Seldon REST API
ParallelDots Text Classification (Taxonomy) API
ParallelDots Named Entity Recognition API
ParallelDots Keyword Generator API
ParallelDots Semantic Analysis API
ParallelDots Sentiment Analysis API
ParallelDots Abusive Content Classifier API
ParallelDots Custom Classifier API
Aito API
Chooch API
Verdigris API
Q emotion Text to Emotions Premium API
Markable Lens API
Facesoft API
Swim API
VOIQ API
Tisane Labs Language Model API
Tisane Labs Analysis API
DefinedCrowd API
TupuTech API
Dialogflow Standard Webhooks API
Hacarus SPECTRO API
Jodie Insights API
Initai API
Allganize Alli API
Foxy AI API
AddStructure Tools API
Jenny StarChat API
Salesforce Einstein Language API
TransNational Payments API
Viettel AI TTS Text to Speech API
Nubentos MedicsenAPI API
Shotzr Image API
OCR Address Extractor API
DigitalOwl Text Similarity API
Myrrix API
Inbenta Knowledge Management API
Waila API
logoraisr API
AI-Compare Speech-To-Text API
NanoNets Image Classification API
PathSense API
soundpiece music composer API
SnapBuy Visual Search API
semanti.ca API
PredicSis API
SpeechText.AI API
SmartNotify API
Open PermID Open Calais Tagging API
BaseJumper API
Web Shrinker Website Categorization API
Cloudmersive Image Recognition and Processing API
Printed.com Platform API
Chattermill API
Vectorspace AI Hidden Relationships API
Google Assistant gRPC API
Vectorspace AI Correlated Stocks API
Objective Revision Evaluation Service API
Boundless Mind Reinforce API
iEngage.ai API
Cyanite.ai API
Digital Owl Text Classification API
Sajari API
Biometric Vision Facial Recognition API
Vectorspace AI Correlated Cryptocurrencies API
Mateverse API
GDELT TV 2.0 AI API
HADE Technologies DATA Feed API
LODGEA API
Hutoma AI API
BLiP Webhooks API
Doc-Pic API
TypeTravel Natural Language API
Inbenta Chatbot API
Alan API
Sony aibo Web API
Kommunicate API
Spot Intelligence API
AddStructure Scaffold API
Symbl.AI API
Inbenta Hyperchat API
HADE Technology Exclusive API
Heat Intelligence API
Smartly.ai API
RxNLP - Cluster Sentences and Short Texts API
Vectorspace AI Trending Popularity API
AI-Compare OCR API
Dentomo API
Inbenta Case Management API
Personal Remedies API
NewsRiver News Search API
Voysis API
Yenos API
GrayMeta Platform API
LOVO Open API
Uru API
Ubivar API
Aidlab API
Mighty AI API
EndlessMedical API
Hydrosphere.io API
Vectorspace AI Summarizer API
Broid API
Vemity API
Date Parser NLP API
NegativePositive Analyzer API
Ozlo API
PredictionIO API
Vectorspace AI API
Android NDK Native API
Bees360 API
Word Associator API
mlrequest API
Google Firebase ML Kit API
Materials Platform for Data Science API
CryptoMood Sentiment Analysis API
AddStructure Path API
DeepAffects API
Galiboo Music API
VocaliD API
DigitalOwl Text Classification API
Skim Technologies Data API
RxNLP NGramCounter API
Stickeroid AI API
SportScribe API
Holy Grail API
Klazify Website Categorization API
Plasticity Cortex Knowledge Graph API
PullString Web API
Prisma Image Analysis API
Base64.ai API
Mintec Import API
Dandelion dataTXT-NEX API
Alina API
Captcha.guru API
Dronecode API
Cochl. Sense API
AddStructure Signal API
10darts API
GetIntel IP Intelligence API
LandedCost.io HS Codes Search API
AI-Compare Translation API
UIB API
AI Bots API
From Data With Love API
Identity Link API
Smartable AI COVID-19 Stats and News API
Spatial Neighborhood API
Dialogflow Standard gRPC API
PropMix AppraisalQC API
Vize AI API
Blogcast API
Word Associations Network API
Nexosis Machine Learning API
Ciliar API
AI-Compare Object Detection API
Chatler.ai Chat API
Rosto API
Exister Cleverbot API
Dialogflow Standard API
Reconess API
Microsoft Project Oxford Speech API
Google Cloud User Account API
AI-Compare Sentiment Analysis API
Body Labs SOMA Shape API
AI-Compare Keyword Extraction API
What Cat API
Google Awareness API
Salesforce Einstein Vision API
Empath API
AZcaptcha API
Socialbakers API
Hotpot API
Google Cloud Machine Learning API"""

seen = set()
APIS = []
for line in RAW_APIS.split('\n'):
    n = line.strip()
    if n and n not in seen:
        seen.add(n)
        APIS.append(n)

def cat(n):
    u = n.lower()
    for key, label in [
        ('alexa', 'Amazon / Alexa'), ('amazon', 'Amazon / Alexa'), ('aws ', 'Amazon / Alexa'),
        ('azure', 'Microsoft / Azure'), ('microsoft', 'Microsoft / Azure'), ('bing', 'Microsoft / Azure'),
        ('ibm watson', 'IBM Watson'), ('google', 'Google'), ('deepai', 'DeepAI'),
        ('crowdstrike', 'CrowdStrike'), ('paralleldots', 'ParallelDots'), ('lastline', 'Lastline'),
        ('vectorspace', 'Vectorspace AI'), ('inbenta', 'Inbenta'), ('deepomatic', 'Deepomatic'),
        ('mozilla', 'Mozilla'), ('salesforce', 'Salesforce'), ('dialogflow', 'Dialogflow'),
        ('seldon', 'Seldon'), ('blueshift', 'BlueShift'), ('addstructure', 'AddStructure'),
        ('ai-compare', 'AI-Compare'), ('digitalowl', 'DigitalOwl'), ('rxnlp', 'RxNLP'),
    ]:
        if key in u:
            return label
    return 'Independent'

CATS = sorted(set(cat(a) for a in APIS))
api_js = '[' + ','.join('{"n":%r,"c":%r}' % (a, cat(a)) for a in APIS) + ']'

LLMS = [
    ("ChatGPT", "OpenAI", "#10a37f", "GPT-4o / o-series completions, tools and vision."),
    ("Gemini", "Google DeepMind", "#4285f4", "Multimodal long-context models with native tool use."),
    ("Grok", "xAI", "#f4f4f5", "Real-time-aware reasoning models from the X firehose."),
    ("Blackbox", "Blackbox AI", "#e8008d", "Code-first chat tuned for developers and agents."),
    ("Qwen", "Alibaba Cloud", "#ff6a00", "Tongyi Qianwen: Qwen-Max, Qwen-VL, Qwen-Agent — open weights available."),
    ("Kimi", "Moonshot AI", "#00c8ff", "Very long-context Chinese/English reasoning models."),
    ("Muse", "Meta Muse", "#a855f7", "Creative multimodal generation for media pipelines."),
    ("Copilot", "GitHub", "#8b949e", "In-editor completion, chat and code review via GitHub Models."),
    ("Vercel AI", "Vercel", "#000000", "AI SDK gateway: one call, many providers, streaming UI."),
    ("Cloudflare", "Workers AI", "#f6821f", "Serverless inference at the edge, zero cold starts."),
]
llm_js = '[' + ','.join('{"n":%r,"v":%r,"c":%r,"d":%r}' % t for t in LLMS) + ']'

APIKONNECT_JS = r"""
(function(){
  var LS='aimv_apik';
  var st; try{ st=JSON.parse(localStorage.getItem(LS)||'{}'); }catch(e){ st={}; }
  st.sel = st.sel||{}; st.tok = st.tok||{}; st.up = st.up||{};
  function save(){ try{ localStorage.setItem(LS, JSON.stringify(st)); }catch(e){} }
  var $=function(s){return document.querySelector(s)}, $$=function(s){return [].slice.call(document.querySelectorAll(s))};
  var APIS=window.__APIS, LLMS=window.__LLMS;
  var q='', curCat='All';

  function tokenFor(name){
    var t=st.tok[name]; if(t) return t.tok;
    var rnd=function(n){var a=new Uint8Array(n); (window.crypto||{getRandomValues:function(x){for(var i=0;i<x.length;i++)x[i]=Math.floor(Math.random()*256)}}).getRandomValues(a); return Array.prototype.map.call(a,function(b){return b.toString(16).padStart(2,'0')}).join('')};
    t={tok:'ak_live_'+rnd(12)+'_'+rnd(20), at:new Date().toISOString(), scopes:['read','infer','connect']};
    st.tok[name]=t; save(); return t.tok;
  }
  function signRow(name){
    var tok=tokenFor(name);
    var box=$('#tok-'+CSS.escape(name));
    if(box){ box.innerHTML='<span class="tok">'+tok+'</span>'; }
    paintConnectors(); paintOnboarding();
  }
  function catChips(){
    var host=$('#cats'); if(!host) return;
    host.innerHTML=['All'].concat(window.__CATS).map(function(c){
      return '<button class="tag'+(c===curCat?' on':'')+'" data-cat="'+c+'" type="button" style="'+(c===curCat?'color:#070312;background:var(--grad);border-color:transparent':'')+'">'+c+'</button>';
    }).join('');
    $$('#cats [data-cat]').forEach(function(b){ b.addEventListener('click',function(){ curCat=b.dataset.cat; catChips(); paintApis(); }); });
  }
  function paintLlms(){
    $('#llms').innerHTML=LLMS.map(function(l){
      var on=!!st.sel['LLM:'+l.n];
      return '<button class="llm-card'+(on?' on':'')+'" data-llm="'+l.n+'" type="button" style="--lc:'+l.c+'">'+
        '<span class="lg"><i></i>'+l.n+'</span><p>'+l.d+'</p><span class="st">'+(on?'✓ selected · '+l.v:'tap to select · '+l.v)+'</span></button>';
    }).join('');
    $$('#llms [data-llm]').forEach(function(b){ b.addEventListener('click',function(){
      var k='LLM:'+b.dataset.llm; st.sel[k]=!st.sel[k]; if(!st.sel[k]) delete st.sel[k]; save(); paintLlms(); paintConnectors(); paintOnboarding(); }); });
  }
  function paintApis(){
    var list=APIS.filter(function(a){ return (curCat==='All'||a.c===curCat) && (!q || a.n.toLowerCase().indexOf(q)!==-1); });
    $('#api-count').textContent=list.length+' of '+APIS.length+' APIs shown · '+Object.keys(st.sel).length+' connectors selected';
    $('#apis').innerHTML=list.map(function(a){
      var on=!!st.sel[a.n];
      return '<button class="api-row'+(on?' on':'')+'" data-api="'+a.n+'" type="button"><span class="bx">'+(on?'✓':'')+'</span><span><span class="nm">'+a.n+'</span><span class="cat">'+a.c+'</span></span></button>';
    }).join('');
    $$('#apis [data-api]').forEach(function(b){ b.addEventListener('click',function(){
      var k=b.dataset.api; st.sel[k]=!st.sel[k]; if(!st.sel[k]) delete st.sel[k]; save();
      b.classList.toggle('on'); b.querySelector('.bx').textContent=st.sel[k]?'✓':'';
      paintConnectors(); paintOnboarding();
      $('#api-count').textContent=APIS.filter(function(a){ return (curCat==='All'||a.c===curCat) && (!q || a.n.toLowerCase().indexOf(q)!==-1); }).length+' of '+APIS.length+' APIs shown · '+Object.keys(st.sel).length+' connectors selected';
    }); });
  }
  function paintConnectors(){
    var names=Object.keys(st.sel).filter(function(k){return st.sel[k]});
    var host=$('#conn');
    if(!names.length){ host.innerHTML='<p style="color:var(--dim);font-size:13.4px">Select an enterprise LLM or tick APIs above — signed connectors appear here with tokens and upload / download / share actions.</p>'; return; }
    host.innerHTML=names.map(function(k){
      var label=k.replace(/^LLM:/,'');
      var t=st.tok[k];
      return '<div class="panel panel-tight" style="display:grid;gap:10px">'+
        '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between">'+
          '<b style="font-family:var(--font-head);font-size:14px">'+label+'</b>'+
          '<span class="chip '+(t?'':'hot')+'">'+(t?'signed · '+new Date(t.at).toLocaleDateString():'unsigned')+'</span></div>'+
        '<div id="tok-'+(window.CSS&&CSS.escape?CSS.escape(k):k)+'">'+(t?'<span class="tok">'+t.tok+'</span>':'')+'</div>'+
        '<div class="btn-row" style="gap:8px;flex-wrap:wrap">'+
          '<button class="btn btn-sm" data-act="sign" data-k="'+k+'" type="button">'+(t?'Re-sign token':'Sign & generate token')+'</button>'+
          (t?'<button class="btn btn-sm btn-ghost" data-act="copy" data-k="'+k+'" type="button">Copy</button>':'')+
          '<button class="btn btn-sm btn-ghost" data-act="up" data-k="'+k+'" type="button">Upload</button>'+
          '<button class="btn btn-sm btn-ghost" data-act="dl" data-k="'+k+'" type="button">Download</button>'+
          '<button class="btn btn-sm btn-ghost" data-act="share" data-k="'+k+'" type="button">Share</button>'+
          '<button class="btn btn-sm btn-ghost" data-act="rev" data-k="'+k+'" type="button">Revoke</button>'+
        '</div>'+
        (st.up[k]?'<p style="font-size:11.6px;color:var(--lime)">uploaded: '+st.up[k].name+' ('+Math.round(st.up[k].size/1024)+' KB) — stored as metadata only</p>':'')+
      '</div>';
    }).join('');
    $$('#conn [data-act]').forEach(function(b){
      b.addEventListener('click',function(){
        var k=b.dataset.k, label=k.replace(/^LLM:/,'');
        if(b.dataset.act==='sign'){ signRow(k); toast('Token signed for '+label); }
        if(b.dataset.act==='copy'){ var t=st.tok[k]; if(t&&navigator.clipboard) navigator.clipboard.writeText(t.tok); toast('Token copied'); }
        if(b.dataset.act==='up'){ var fi=$('#file-up'); fi.dataset.k=k; fi.click(); }
        if(b.dataset.act==='dl'){ dl(k.replace(/[^\w]+/g,'-')+'-connector.json', JSON.stringify({connector:k,token:st.tok[k]||null,scopes:(st.tok[k]||{}).scopes||[],upload:st.up[k]||null,generatedAt:new Date().toISOString()},null,2),'application/json'); }
        if(b.dataset.act==='share'){ var t2=st.tok[k]; var txt='AIMV connector · '+label+' · '+(t2?t2.tok:'unsigned')+' · https://aimetaverse.cloud/apikonnect.html'; if(navigator.clipboard) navigator.clipboard.writeText(txt); toast('Share text copied'); }
        if(b.dataset.act==='rev'){ delete st.tok[k]; save(); paintConnectors(); toast('Token revoked for '+label); }
      });
    });
  }
  function dl(name,text,mime){
    var b=new Blob([text],{type:mime||'text/plain'}); var a=document.createElement('a');
    a.href=URL.createObjectURL(b); a.download=name; document.body.appendChild(a); a.click();
    setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1200);
  }
  function toast(t){ if(window.AIMV_HUMANOID&&window.AIMV_HUMANOID.toast) return window.AIMV_HUMANOID.toast(t);
    var x=$('#toast2'); if(!x){x=document.createElement('div');x.id='toast2';x.className='toast';document.body.appendChild(x);} x.textContent=t; x.className='toast show'; clearTimeout(x._h); x._h=setTimeout(function(){x.className='toast'},4200); }
  function paintOnboarding(){
    var prof=false; try{ prof=!!localStorage.getItem('aimv_profile_v1'); }catch(e){}
    var toks=Object.keys(st.tok).length>0;
    var dev=false; try{ dev=!!localStorage.getItem('aimv_devz'); }catch(e){}
    var rem=false; try{ rem=(JSON.parse(localStorage.getItem('aimv_reminders')||'[]')).length>0; }catch(e){}
    var steps=[['Clone yourself virtually','avatar-create.html',prof],['Connect & sign at least one API','apikonnect.html',toks],['Open the DevZone terminal','devzone.html',dev],['Set a reminder with your companion','index.html',rem]];
    $('#onb').innerHTML=steps.map(function(s,i){
      return '<a class="api-row'+(s[2]?' on':'')+'" href="'+s[1]+'"><span class="bx">'+(s[2]?'✓':'')+'</span><span><span class="nm">'+(i+1)+'. '+s[0]+'</span><span class="cat">'+(s[2]?'done':'pending')+'</span></span></a>';
    }).join('');
  }
  document.addEventListener('DOMContentLoaded',function(){
    $('#file-up').addEventListener('change',function(e){
      var f=e.target.files&&e.target.files[0]; if(!f) return; var k=e.target.dataset.k;
      st.up[k]={name:f.name,size:f.size,at:new Date().toISOString()}; save(); paintConnectors(); toast('Connector payload registered: '+f.name);
      e.target.value='';
    });
    $('#search').addEventListener('input',function(){ q=this.value.trim().toLowerCase(); paintApis(); });
    $('#sign-all').addEventListener('click',function(){
      Object.keys(st.sel).forEach(function(k){ if(st.sel[k]) tokenFor(k); });
      save(); paintConnectors(); paintOnboarding(); toast('All selected connectors signed.');
    });
    paintLlms(); catChips(); paintApis(); paintConnectors(); paintOnboarding();
  });
})();
"""

DEVZONE_JS = r"""
(function(){
  try{ localStorage.setItem('aimv_devz','1'); }catch(e){}
  var $=function(s){return document.querySelector(s)};
  var out=$('#tout'), inp=$('#tin');
  var hist=[], hi=-1;
  var FS={
    'index.html':'landing + app page (hero, Metabox, companion dock)',
    'avatar-create.html':'the forge: selfie -> voice -> birthday -> agent',
    'avatar.html':'dashboard of your stored clone',
    'agents/agent.html':'in-browser home of your forged agent',
    'apikonnect.html':'enterprise LLMs + API directory + signed connectors',
    'devzone.html':'this terminal',
    'py/main.py':'Python/Eel backend: desktop TTS/STT + local/OpenAI/Ollama brain',
    'assets/humanoid.js':'companion: faces, personas, talk, reminders, ads, suggestions',
    'assets/avatar.js':'clone pipeline + standalone agent page generator'
  };
  function print(txt, cls){ var d=document.createElement('div'); if(cls) d.className=cls; d.textContent=txt; out.appendChild(d); out.scrollTop=out.scrollHeight; }
  function promptLine(cmd){ print('aimv@metaverse:~$ '+cmd,'p'); }
  function run(cmd){
    promptLine(cmd); hist.push(cmd); hi=hist.length;
    var a=cmd.trim().split(/\s+/), c=(a[0]||'').toLowerCase(), rest=cmd.trim().slice(c.length).trim();
    switch(c){
      case '': break;
      case 'help': print('commands: help ls cd cat connect bridge status apis reminders tasks forge open echo whoami date clear\n'+
        '  connect termux      -> pairing steps + one-liner for Termux\n'+
        '  connect ssh u@h     -> register a terminal bridge host\n'+
        '  forge               -> jump to the clone pipeline\n'+
        '  open <page>         -> navigate the site'); break;
      case 'ls': print(Object.keys(FS).join('\n')); break;
      case 'cd': print('(virtual fs is flat — everything lives at ~/aimetaverse)'); break;
      case 'cat':
        if(rest==='spec'||rest==='agent'){
          if(window.AIMV_PROFILE&&window.AIMV_PROFILE.get().agent) print(JSON.stringify(window.AIMV_PROFILE.spec(),null,2));
          else print('no forged agent yet — run: forge','w');
        } else if(FS[rest]) print('# '+rest+'\n'+FS[rest]);
        else print('cat: '+rest+': no such file','e');
        break;
      case 'connect':
        if(a[1]==='termux'){
          var one='pkg update && pkg install python git && pip install eel pyttsx3 SpeechRecognition && git clone <this-repo> && python py/main.py --no-window';
          print('Termux pairing:\n 1. install Termux (F-Droid build)\n 2. run:\n    '+one+'\n 3. phone and browser on same LAN -> http://<phone-ip>:8080\n 4. the page detects window.eel and the companion switches to desktop voice.');
          if(navigator.clipboard) navigator.clipboard.writeText(one);
          print('(one-liner copied to clipboard)','w');
        } else if(a[1]==='ssh'){
          if(!rest.replace('ssh ','')) { print('usage: connect ssh user@host','e'); break; }
          var h=(a[2]||''); try{ localStorage.setItem('aimv_ssh',h); }catch(e){}
          print('bridge host registered: '+h+'\nrun on that machine:  ssh -R 8080:localhost:8080 '+h+'\nthen py/main.py --no-window serves this UI with the eel bridge live.');
        } else print('usage: connect termux | connect ssh user@host','e');
        break;
      case 'bridge':
        print('eel bridge: '+((window.eel&&window.eel.user_said)?'LIVE (python backend detected)':'not connected — start py/main.py')+'\nssh host: '+((function(){try{return localStorage.getItem('aimv_ssh')||'none'}catch(e){return 'none'}})())+'\nwebsocket stub: ws://localhost:8080/term (reserved for the bridge daemon)');
        break;
      case 'status':
        var P=window.AIMV_PROFILE?window.AIMV_PROFILE.get():null;
        print('companion: face='+(window.AIMV_HUMANOID?window.AIMV_HUMANOID.face():'?')+' persona='+(window.AIMV_HUMANOID?window.AIMV_HUMANOID.persona():'?')+' voice='+(window.AIMV_HUMANOID&&window.AIMV_HUMANOID.voiceOn()?'on':'off')+
          '\nclone: '+(P&&P.agent?('agent '+P.agent.id+' ('+P.agent.name+')'):'none')+
          '\nreminders: '+(window.AIMV_HUMANOID?window.AIMV_HUMANOID.reminders().filter(function(x){return !x.done}).length:0)+' pending · tasks: '+(window.AIMV_HUMANOID?window.AIMV_HUMANOID.tasks().filter(function(x){return !x.done}).length:0)+' open');
        break;
      case 'apis': print('signed connectors: '+((function(){try{return Object.keys(JSON.parse(localStorage.getItem('aimv_apik')||'{}').tok||{}).join(', ')||'none'}catch(e){return 'none'}})())+'\nmanage them in apikonnect.html'); break;
      case 'reminders': print((window.AIMV_HUMANOID?window.AIMV_HUMANOID.reminders():[]).map(function(r){return (r.done?'[done] ':'[due '+new Date(r.due).toLocaleString()+'] ')+r.t}).join('\n')||'no reminders'); break;
      case 'tasks': print((window.AIMV_HUMANOID?window.AIMV_HUMANOID.tasks():[]).map(function(t){return (t.done?'[x] ':'[ ] ')+t.t}).join('\n')||'no tasks'); break;
      case 'forge': print('opening the forge…'); setTimeout(function(){location.href='avatar-create.html'},500); break;
      case 'open': if(FS[rest]||rest==='index.html'){ location.href=rest; } else print('unknown page: '+rest,'e'); break;
      case 'echo': print(rest); break;
      case 'whoami': print('aimv — humanoid companion operator (guest session, local-only)'); break;
      case 'date': print(new Date().toString()); break;
      case 'sudo': print('nice try. the companion has more permissions than you.','w'); break;
      case 'clear': out.innerHTML=''; break;
      default: print(c+': command not found — try: help','e');
    }
  }
  document.addEventListener('DOMContentLoaded',function(){
    print('Ai Metaverse DevZone — type `help` for commands, `connect termux` to pair a phone shell.');
    print('bridge status: '+((window.eel&&window.eel.user_said)?'eel LIVE':'local demo mode'),'w');
    $('#tform').addEventListener('submit',function(e){ e.preventDefault(); var v=inp.value; inp.value=''; run(v); });
    inp.addEventListener('keydown',function(e){
      if(e.key==='ArrowUp'){ if(hi>0){hi--; inp.value=hist[hi]||''; e.preventDefault();} }
      if(e.key==='ArrowDown'){ if(hi<hist.length-1){hi++; inp.value=hist[hi]||'';} else {hi=hist.length; inp.value='';} e.preventDefault(); }
    });
    [].slice.call(document.querySelectorAll('#quick-cmds button')).forEach(function(b){ b.addEventListener('click',function(){ run(b.dataset.cmd); }); });
  });
})();
"""


# ---------- self-contained inlining (GitHub Pages: every page must stand alone) ----------
def _rd(p):
    with io.open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()
FACE_URL = 'data:image/jpeg;base64,' + FACE_B64
ORB_URL = 'data:image/jpeg;base64,' + ORB_B64
SITE_CSS = _rd('assets/site.css')
HUM_CSS = _rd('assets/humanoid.css').replace('url("face-orb.jpg")', 'url("%s")' % ORB_URL).replace('url("face-real.jpg")', 'url("%s")' % FACE_URL)
SITE_JS = _rd('assets/site.js')
HUM_JS = _rd('assets/humanoid.js')
AVA_JS = _rd('assets/avatar.js')
FACES_SNIPPET = 'window.AIMV_FACES={real:"%s"};' % FACE_URL
def inline_css():
    return '<style>\n' + SITE_CSS + '\n' + HUM_CSS + '\n</style>\n'
def inline_js(scripts=()):
    out = '<script data-humanoid="js">\n' + SITE_JS + '\n' + FACES_SNIPPET + '\n' + HUM_JS + '\n</script>\n'
    if 'avatar' in scripts:
        out += '<script>\n' + AVA_JS + '\n</script>\n'
    return out


KNOWN = ['index.html','why-ai.html','enterprise.html','tools.html','labs.html','education.html',
         'worlds.html','shop.html','metabox.html','news.html','contact.html','signup.html','signin.html',
         'privacy.html','terms.html','developers.html','avatar-create.html','avatar.html','apikonnect.html',
         'devzone.html','agents/agent.html',
         'ai-education.html','prompter.html','twin-studio.html','voice-lipsync.html']
def _dirmap(k): return 'index.html' if k=='index.html' else k[:-5]+'/index.html'
def dirform(html, ownflat):
    import re as _re
    for k in sorted(KNOWN, key=len, reverse=True):
        d = _dirmap(k)
        html = _re.sub(r'href="%s#([^"]*)"' % _re.escape(k), lambda m: 'href="%s#%s"' % (d, m.group(1)), html)
        html = html.replace('href="%s"' % k, 'href="%s"' % d)
    html = _re.sub(r'href="#([^"]+)"', lambda m: 'href="%s#%s"' % (ownflat, m.group(1)), html)
    return html
CHARSET = '<meta charset="UTF-8" />\n'
def with_base(html, base):
    return html.replace(CHARSET, CHARSET + '<base href="%s" />\n' % base, 1)
def depth(name): return name.count('/')
def emit(name, html):
    flat = with_base(html, '../' * depth(name) or './')
    folder = with_base(html, '../' * (depth(name) + 1))
    with io.open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f: f.write(flat)
    fdir = os.path.join(ROOT, name[:-5], 'index.html')
    os.makedirs(os.path.dirname(fdir), exist_ok=True)
    with io.open(fdir, 'w', encoding='utf-8') as f: f.write(folder)
    print('%-24s %6d + %6d bytes (flat + folder)' % (name, len(flat), len(folder)))

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta name="theme-color" content="#070312" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23070312'/%3E%3Ccircle cx='32' cy='32' r='17' fill='none' stroke='%2300f0ff' stroke-width='4'/%3E%3Ccircle cx='32' cy='32' r='6' fill='%23ff2fb9'/%3E%3C/svg%3E">
{INLINE_CSS}
</head>
<body>
<div class="scroll-progress" id="scroll-progress"></div>
<main>
<section class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span class="sep">/</span><span class="current">{crumb}</span></nav>
    <span class="eyebrow"><span class="dot"></span> {eyebrow}</span>
    <h1>{h1} <span class="grad-text">{grad}</span></h1>
    <p class="prose" style="font-size:clamp(1rem,1.7vw,1.15rem)">{lead}</p>
  </div>
</section>
{body}
</main>
<input type="file" id="file-up" hidden />
<script>window.__APIS={api_js};window.__LLMS={llm_js};window.__CATS={cats_js};</script>
{INLINE_JS_AV}
<script defer>{inline}</script>
</body>
</html>
"""

apiconnect_body = """
<section class="sec-tight" id="onboarding"><div class="wrap">
  <div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Onboarding</span>
  <h2 class="h-lg">Your setup, <span class="grad-text">four steps</span></h2>
  <p class="lead">Live checklist — it reads your browser storage and ticks itself off.</p></div>
  <div class="api-grid reveal" id="onb" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))"></div>
</div></section>
<section class="sec" id="llms-sec"><div class="wrap">
  <div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Enterprise LLMs</span>
  <h2 class="h-lg">Pick your <span class="grad-text">brains</span></h2>
  <p class="lead">Tap to select. Selected models become signable connectors below — the companion can route prompts to any of them once tokens exist.</p></div>
  <div class="grid-4 reveal" id="llms"></div>
</div></section>
<section class="sec" id="apis-sec" style="background:linear-gradient(180deg,transparent,rgba(124,92,255,.07),transparent)"><div class="wrap">
  <div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> API directory</span>
  <h2 class="h-lg">Tick the APIs your agent <span class="grad-text">may touch</span></h2>
  <p class="lead">Every checkbox becomes a connector: sign it, generate a token, attach uploads, download the bundle, share it.</p></div>
  <div class="field reveal" style="max-width:460px;margin:0 auto 18px"><label for="search">Search the directory</label><input id="search" type="search" placeholder="watson, alexa, deepai, vision…" /></div>
  <div class="tag-row reveal" id="cats" style="justify-content:center;margin-bottom:18px"></div>
  <p class="center reveal" id="api-count" style="font-size:12.6px;color:var(--dim);margin-bottom:16px"></p>
  <div class="api-grid reveal" id="apis"></div>
</div></section>
<section class="sec" id="conn-sec"><div class="wrap">
  <div class="sec-head reveal"><span class="eyebrow"><span class="dot"></span> Connectors</span>
  <h2 class="h-lg">Signed connectors &amp; <span class="grad-text">tokens</span></h2>
  <p class="lead">Tokens are generated and stored in this browser only. Download a connector bundle to hand it to your backend.</p>
  <div class="btn-row" style="margin-top:18px"><button class="btn" id="sign-all" type="button">Sign all selected</button></div></div>
  <div class="grid-2 reveal" id="conn"></div>
</div></section>
"""

devzone_body = """
<section class="sec-tight"><div class="wrap">
  <div class="grid-2" style="grid-template-columns:1.5fr .9fr;align-items:start">
    <div class="term reveal">
      <div class="tbar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i> aimv@metaverse — devzone — 80×24</div>
      <div class="tout" id="tout" aria-live="polite"></div>
      <form class="tin" id="tform" autocomplete="off"><span>❯</span><label for="tin" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">terminal input</label><input id="tin" spellcheck="false" placeholder="type `help` …" /></form>
    </div>
    <div style="display:grid;gap:16px">
      <div class="panel reveal"><h3>Bridge a real terminal</h3>
        <p style="font-size:13.4px;color:var(--muted)">This shell is in-page. To drive a <b style="color:var(--txt)">real</b> terminal — Termux on a phone, or any user shell over ssh — pair it with the Python backend:</p>
        <code class="blk" style="margin-top:12px;font-size:12px">pip install -r py/requirements.txt
python py/main.py --no-window
# phone (Termux): same one-liner, then
#   http://&lt;phone-ip&gt;:8080
# any box:
ssh -R 8080:localhost:8080 you@host</code>
        <p style="font-size:12.4px;color:var(--dim);margin-top:10px">When <code>window.eel</code> appears, the companion and this terminal flip to bridge mode automatically (<code>bridge</code> to check).</p>
      </div>
      <div class="panel reveal"><h3>Quick commands</h3>
        <div class="tag-row" id="quick-cmds" style="margin-top:10px">
          <button class="tag" data-cmd="help" type="button">help</button>
          <button class="tag" data-cmd="status" type="button">status</button>
          <button class="tag" data-cmd="connect termux" type="button">connect termux</button>
          <button class="tag" data-cmd="bridge" type="button">bridge</button>
          <button class="tag" data-cmd="cat spec" type="button">cat spec</button>
          <button class="tag" data-cmd="reminders" type="button">reminders</button>
          <button class="tag" data-cmd="apis" type="button">apis</button>
          <button class="tag" data-cmd="forge" type="button">forge</button>
        </div>
      </div>
      <div class="panel reveal"><h3>Agentic shortcuts</h3>
        <p style="font-size:13.2px;color:var(--muted)">The companion takes natural language anywhere on the site: “remind me to ship in 10 minutes”, “add task write the demo”, “deliver a message to Ada: the build is live”, “plan my day”. Reminders fire out loud on any open page.</p>
      </div>
    </div>
  </div>
</div></section>
"""

pages = {
 'apikonnect.html': dict(
   crumb='APIKonnect', eyebrow='Onboarding · APIKonnect', h1='Connect every brain,', grad='sign every token',
   lead='Enterprise LLMs (ChatGPT, Gemini, Grok, Blackbox, Qwen, Kimi, Muse, Copilot, Vercel, Cloudflare) plus a curated directory of AI APIs — tick what your agent may use, sign connectors, generate tokens, and wire uploads, downloads and shares.',
   title='APIKonnect — Enterprise LLMs, API Directory & Signed Connectors | Ai Metaverse',
   desc='Onboarding tab: select ChatGPT, Gemini, Grok, Blackbox, Qwen, Kimi, Muse, Copilot, Vercel, Cloudflare and 200+ AI APIs; sign connectors, generate tokens, upload/download/share.',
   body=apiconnect_body, inline=APIKONNECT_JS),
 'devzone.html': dict(
   crumb='DevZone', eyebrow='DevZone', h1='A terminal for', grad='your agent',
   lead='In-page shell over the whole repo: inspect files, cat your agent spec, check reminders and signed APIs — and bridge to a real Linux shell on Termux or any user terminal over ssh.',
   title='DevZone — Terminal, Termux & ssh Bridge | Ai Metaverse',
   desc='Developer terminal with virtual filesystem, agent spec inspector, reminder/task commands, and pairing steps for Termux or ssh terminal bridges.',
   body=devzone_body, inline=DEVZONE_JS),
}

cats_js = '[' + ','.join('%r' % c for c in CATS) + ']'
for name, d in pages.items():
    INLINE_CSS = inline_css()
    INLINE_JS_AV = inline_js(('avatar',)) if d.get('avatar') else inline_js()
    html = TPL.format(title=d['title'], desc=d['desc'], crumb=d['crumb'], eyebrow=d['eyebrow'],
                      h1=d['h1'], grad=d['grad'], lead=d['lead'], body=dirform(d['body'], name),
                      api_js=api_js if name == 'apikonnect.html' else '[]',
                      llm_js=llm_js if name == 'apikonnect.html' else '[]',
                      cats_js=cats_js if name == 'apikonnect.html' else '[]',
                      inline=d['inline'], INLINE_CSS=INLINE_CSS, INLINE_JS_AV=INLINE_JS_AV)
    emit(name, html)
