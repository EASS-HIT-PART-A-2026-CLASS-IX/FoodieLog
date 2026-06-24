"""
FoodieLog AI floating widget — a bottom-right button that opens a right-side
chat drawer. Injected into the Streamlit parent page via components.html
(height=0 iframe) so the chat talks to the API directly without Streamlit reruns.
"""
import os

import streamlit as st
import streamlit.components.v1 as components

# Browser-side URL (JavaScript fetch). Use 127.0.0.1 explicitly — on Windows,
# "localhost" may resolve to IPv6 (::1) which fails when uvicorn listens on IPv4.
_PUBLIC_API_BASE = os.environ.get("PUBLIC_API_BASE", "http://127.0.0.1:8000")

_CSS = """
#fl-fab{position:fixed;right:1.5rem;bottom:2rem;z-index:99999;width:58px;height:58px;
  border-radius:50%;background:#EA580C;border:none;cursor:pointer;font-size:1.5rem;
  box-shadow:0 6px 22px rgba(234,88,12,.45);transition:transform .2s,box-shadow .2s;
  display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;}
#fl-fab:hover{transform:scale(1.1);box-shadow:0 8px 30px rgba(234,88,12,.6);}
#fl-overlay{display:none;position:fixed;inset:0;background:rgba(28,25,23,.35);z-index:99998;backdrop-filter:blur(2px);}
#fl-overlay.open{display:block;}
#fl-drawer{position:fixed;top:0;right:0;height:100vh;width:390px;max-width:96vw;z-index:99999;
  background:#fff;border-left:1px solid #E7E5E4;box-shadow:-8px 0 40px rgba(0,0,0,.12);
  display:flex;flex-direction:column;transform:translateX(100%);
  transition:transform .3s cubic-bezier(.4,0,.2,1);font-family:'Inter',-apple-system,sans-serif;}
#fl-drawer.open{transform:translateX(0);}
#fl-hdr{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;
  border-bottom:1px solid #E7E5E4;background:linear-gradient(135deg,rgba(234,88,12,.08),transparent);}
#fl-hdr-title{font-size:1.05rem;font-weight:800;color:#1C1917;display:flex;align-items:center;gap:.5rem;}
.fl-badge{font-size:.6rem;background:rgba(234,88,12,.1);color:#EA580C;border:1px solid rgba(234,88,12,.25);
  border-radius:20px;padding:.12rem .5rem;font-weight:700;letter-spacing:.04em;}
#fl-close{background:#FAFAF9;border:1px solid #E7E5E4;color:#78716C;border-radius:8px;width:30px;height:30px;
  cursor:pointer;font-size:.9rem;display:flex;align-items:center;justify-content:center;transition:all .15s;}
#fl-close:hover{background:rgba(234,88,12,.1);color:#EA580C;border-color:rgba(234,88,12,.3);}
#fl-pills{display:flex;flex-wrap:wrap;gap:.35rem;padding:.65rem 1.25rem;border-bottom:1px solid #E7E5E4;}
.fl-pill{background:#FFF7ED;border:1px solid #FED7AA;color:#C2410C;border-radius:20px;
  padding:.25rem .7rem;font-size:.72rem;cursor:pointer;transition:all .15s;font-family:inherit;}
.fl-pill:hover{background:rgba(234,88,12,.12);border-color:rgba(234,88,12,.45);}
#fl-msgs{flex:1;overflow-y:auto;padding:1rem 1.25rem;display:flex;flex-direction:column;gap:.55rem;scroll-behavior:smooth;}
#fl-msgs::-webkit-scrollbar{width:5px;}
#fl-msgs::-webkit-scrollbar-thumb{background:#E7E5E4;border-radius:4px;}
.fl-row-user{display:flex;flex-direction:column;align-items:flex-end;}
.fl-row-ai{display:flex;flex-direction:column;align-items:flex-start;}
.fl-lbl{font-size:.66rem;font-weight:700;margin-bottom:.15rem;padding:0 .2rem;}
.fl-lbl.user{color:#EA580C;}.fl-lbl.ai{color:#A8A29E;}
.fl-bbl{max-width:90%;padding:.5rem .8rem;border-radius:12px;font-size:.85rem;line-height:1.5;}
.fl-bbl.user{background:#EA580C;color:#fff;font-weight:500;border-bottom-right-radius:3px;}
.fl-bbl.ai{background:#F5F5F4;border:1px solid #E7E5E4;color:#1C1917;border-bottom-left-radius:3px;white-space:pre-wrap;}
#fl-input-bar{display:flex;gap:.4rem;padding:.8rem 1.25rem;border-top:1px solid #E7E5E4;}
#fl-input{flex:1;background:#FAFAF9;border:1px solid #E7E5E4;border-radius:10px;color:#1C1917;
  font-size:.875rem;padding:.55rem .8rem;outline:none;font-family:inherit;transition:border-color .15s;}
#fl-input::placeholder{color:#A8A29E;}
#fl-input:focus{border-color:#EA580C;box-shadow:0 0 0 3px rgba(234,88,12,.12);}
#fl-send{background:#EA580C;border:none;border-radius:10px;color:#fff;width:42px;height:42px;
  cursor:pointer;font-size:.95rem;display:flex;align-items:center;justify-content:center;
  transition:transform .15s,box-shadow .15s;flex-shrink:0;font-weight:700;}
#fl-send:hover{transform:scale(1.08);box-shadow:0 4px 14px rgba(234,88,12,.4);}
#fl-send:disabled{opacity:.5;cursor:not-allowed;transform:none;}
"""


_CSS_DARK = """
#fl-drawer{background:#211D18 !important;border-left-color:#3A332C !important;}
#fl-hdr{border-bottom-color:#3A332C !important;background:linear-gradient(135deg,rgba(234,88,12,.14),transparent) !important;}
#fl-hdr-title{color:#F5F1EB !important;}
#fl-close{background:#2A251F !important;border-color:#3A332C !important;color:#B8AFA4 !important;}
#fl-pills{border-bottom-color:#3A332C !important;}
.fl-pill{background:#2A1C12 !important;border-color:rgba(234,88,12,.4) !important;color:#FB923C !important;}
#fl-msgs::-webkit-scrollbar-thumb{background:#3A332C !important;}
.fl-bbl.ai{background:#2A251F !important;border-color:#3A332C !important;color:#F5F1EB !important;}
.fl-lbl.ai{color:#A8A29E !important;}
#fl-input-bar{border-top-color:#3A332C !important;}
#fl-input{background:#16130F !important;border-color:#3A332C !important;color:#F5F1EB !important;}
"""


def render(token: str, theme: str = "light") -> None:
    """Inject the AI floating widget into the Streamlit parent window."""
    safe_token = token.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    base = _CSS + (_CSS_DARK if theme == "dark" else "")
    css = base.replace("`", "\\`").replace("${", "\\${")

    components.html(f"""<script>
(function(){{
  var par=window.parent,doc=par.document;
  par._flCreds={{token:`{safe_token}`}};
  var oldStyle=doc.getElementById('fl-style');
  if(oldStyle)oldStyle.remove();
  var s=doc.createElement('style');s.id='fl-style';s.textContent=`{css}`;doc.head.appendChild(s);
  if(doc.getElementById('fl-root'))return;
  var root=doc.createElement('div');root.id='fl-root';
  root.innerHTML=`
    <div id="fl-overlay" onclick="window._flClose()"></div>
    <button id="fl-fab" onclick="window._flToggle()" title="FoodieLog AI">🤖</button>
    <div id="fl-drawer">
      <div id="fl-hdr">
        <div id="fl-hdr-title"><span>🍽️ FoodieLog AI</span><span class="fl-badge">ONLINE</span></div>
        <button id="fl-close" onclick="window._flClose()">✕</button>
      </div>
      <div id="fl-pills">
        <button class="fl-pill" onclick="window._flQuick('What is my highest-rated restaurant?')">Top rated</button>
        <button class="fl-pill" onclick="window._flQuick('Suggest where to eat next from my list')">Where next?</button>
        <button class="fl-pill" onclick="window._flQuick('Summarize my collection')">My stats</button>
        <button class="fl-pill" onclick="window._flQuick('What cuisine should I try next?')">Try new</button>
      </div>
      <div id="fl-msgs">
        <div class="fl-row-ai">
          <div class="fl-lbl ai">FoodieLog AI</div>
          <div class="fl-bbl ai">Hi! I'm your FoodieLog assistant 🍽️ Ask me about your restaurants or anything food-related.</div>
        </div>
      </div>
      <div id="fl-input-bar">
        <input id="fl-input" type="text" placeholder="Ask anything…"/>
        <button id="fl-send" onclick="window._flSend()">➤</button>
      </div>
    </div>
  `;
  doc.body.appendChild(root);
  doc.getElementById('fl-input').addEventListener('keydown',function(e){{
    if(e.key==='Enter'&&!e.shiftKey){{e.preventDefault();par._flSend();}}
  }});
  par._flToggle=function(){{doc.getElementById('fl-drawer').classList.contains('open')?par._flClose():par._flOpen();}};
  par._flOpen=function(){{
    doc.getElementById('fl-drawer').classList.add('open');
    doc.getElementById('fl-overlay').classList.add('open');
    doc.getElementById('fl-fab').textContent='✕';
    setTimeout(function(){{doc.getElementById('fl-input').focus();}},350);
  }};
  par._flClose=function(){{
    doc.getElementById('fl-drawer').classList.remove('open');
    doc.getElementById('fl-overlay').classList.remove('open');
    doc.getElementById('fl-fab').textContent='🤖';
  }};
  par._flQuick=function(t){{doc.getElementById('fl-input').value=t;par._flSend();}};
  par._flSend=async function(){{
    var c=par._flCreds||{{}},inp=doc.getElementById('fl-input'),btn=doc.getElementById('fl-send'),txt=inp.value.trim();
    if(!txt)return;
    inp.value='';btn.disabled=true;_flAdd('user',txt);
    var typing=_flTyping();
    try{{
      var res=await par.fetch('{_PUBLIC_API_BASE}/ai/chat',{{method:'POST',
        headers:{{'Content-Type':'application/json','Authorization':'Bearer '+c.token}},
        body:JSON.stringify({{message:txt}})}});
      typing.remove();
      if(res.ok){{var d=await res.json();_flAdd('ai',d.reply||'No response');}}
      else if(res.status===401){{_flAdd('ai','⚠️ Session expired — please sign in again.');}}
      else if(res.status===503){{_flAdd('ai','⚠️ AI is not configured (missing API key on the server).');}}
      else{{var e=await res.json().catch(function(){{return {{}};}});_flAdd('ai','⚠️ '+(e.detail||res.statusText));}}
    }}catch(e){{typing.remove();_flAdd('ai','⚠️ Connection error — is the backend running?');}}
    btn.disabled=false;inp.focus();
  }};
  function _flAdd(role,text){{
    var msgs=doc.getElementById('fl-msgs');
    var row=doc.createElement('div');row.className='fl-row-'+role;
    var lbl=doc.createElement('div');lbl.className='fl-lbl '+role;lbl.textContent=role==='user'?'You':'FoodieLog AI';
    var bbl=doc.createElement('div');bbl.className='fl-bbl '+role;bbl.textContent=text;
    row.appendChild(lbl);row.appendChild(bbl);msgs.appendChild(row);
    msgs.scrollTop=msgs.scrollHeight;return row;
  }}
  function _flTyping(){{
    var msgs=doc.getElementById('fl-msgs');
    var row=doc.createElement('div');row.className='fl-row-ai';
    var lbl=doc.createElement('div');lbl.className='fl-lbl ai';lbl.textContent='FoodieLog AI';
    var d=doc.createElement('div');d.className='fl-bbl ai';d.style.cssText='display:flex;gap:4px;width:fit-content;';
    if(!doc.getElementById('fl-bounce-style')){{
      var ks=doc.createElement('style');ks.id='fl-bounce-style';
      ks.textContent='@keyframes fl-bounce{{0%,60%,100%{{transform:translateY(0);opacity:.4;}}30%{{transform:translateY(-5px);opacity:1;}}}}';
      doc.head.appendChild(ks);
    }}
    var dot='<span style="width:6px;height:6px;background:#A8A29E;border-radius:50%;display:inline-block;animation:fl-bounce 1.2s infinite;"></span>';
    d.innerHTML=dot+dot.replace('infinite','1.2s .2s infinite')+dot.replace('infinite','1.2s .4s infinite');
    row.appendChild(lbl);row.appendChild(d);msgs.appendChild(row);msgs.scrollTop=msgs.scrollHeight;return row;
  }}
}})();
</script>""", height=0)
