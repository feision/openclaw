// ============================================================
// Cloudflare Worker - 订阅转换器（前后端一体 + KV 持久化）
// 路由：GET / → 面板  GET /sub → YAML  GET|POST /api/config → 配置
// 部署前绑定 KV：变量名 CONFIG_KV
// ============================================================

const DEFAULT_CONFIG = {
  nameMode:      "original",
  labelSep:      "#",
  enableDedup:   true,
  enableAutoSeq: true,
  replaceServer: true,
  passUserinfo:  true,
  servers:  [],
  subList:  [],
};

export default {
  async fetch(request, env) {
    const url    = new URL(request.url);
    const method = request.method;
    const cfg    = await loadConfig(env);
    if (url.pathname === "/sub") return handleSub(cfg);
    if (url.pathname === "/api/config" && method === "GET")
      return new Response(JSON.stringify(cfg, null, 2), { headers: { "Content-Type": "application/json; charset=utf-8" } });
    if (url.pathname === "/api/config" && method === "POST") {
      try {
        await saveConfig(env, await request.json());
        return new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json" } });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: e.message }), { status: 400, headers: { "Content-Type": "application/json" } });
      }
    }
    return new Response(buildPanel(request), { headers: { "Content-Type": "text/html; charset=utf-8" } });
  },
};

async function loadConfig(env) {
  try { const r = await env.CONFIG_KV.get("config"); return r ? { ...DEFAULT_CONFIG, ...JSON.parse(r) } : { ...DEFAULT_CONFIG }; }
  catch { return { ...DEFAULT_CONFIG }; }
}
async function saveConfig(env, cfg) { await env.CONFIG_KV.put("config", JSON.stringify(cfg)); }

async function handleSub(cfg) {
  const { nameMode, labelSep, enableDedup, enableAutoSeq, replaceServer, passUserinfo, servers, subList } = cfg;
  const tasks = subList.map(({ url, label }) =>
    fetch(url, { headers: { "User-Agent": "clash.meta" } })
      .then(r => r.ok ? r.text().then(text => ({ text, label, userinfo: r.headers.get("Subscription-Userinfo") })) : null)
      .catch(() => null)
  );
  const results = await Promise.all(tasks);
  const userinfoHeader = results.find(r => r?.userinfo)?.userinfo || null;
  const proxyEntries = [];
  for (const res of results) {
    if (!res) continue;
    let inP = false;
    for (const line of res.text.split("\n")) {
      if (/^proxies\s*:/.test(line)) { inP = true; continue; }
      if (inP) {
        if (/^\s+- \{/.test(line)) proxyEntries.push({ line: line.trim().replace(/^-\s*/, ""), label: res.label });
        else if (line.trim() && !/^\s/.test(line)) break;
      }
    }
  }
  const seen = new Set(), base = [];
  for (const { line, label } of proxyEntries) {
    const p = parseFlowObject(line), key = p.servername || p.server;
    if (enableDedup) { if (!key || seen.has(key)) continue; seen.add(key); }
    if (nameMode === "servername" && p.servername) p.name = p.servername;
    p._label = label; base.push(p);
  }
  const nc = {}, proxies = [];
  for (const sa of ((replaceServer && servers.length) ? servers : [null])) {
    for (const b of base) {
      const p = JSON.parse(JSON.stringify(b));
      if (sa) p.server = sa;
      if (nameMode === "server") p.name = p.server;
      if (p._label) p.name = p.name + labelSep + p._label;
      delete p._label;
      if (enableAutoSeq) { nc[p.name] = (nc[p.name] || 0) + 1; if (nc[p.name] > 1) p.name += "_" + nc[p.name]; }
      proxies.push(p);
    }
  }
  const lines = ["proxies:"]; for (const p of proxies) lines.push("  - " + toFlowYaml(p));
  const headers = new Headers({ "Content-Type": "text/yaml; charset=utf-8" });
  if (passUserinfo && userinfoHeader) headers.set("Subscription-Userinfo", userinfoHeader);
  return new Response(lines.join("\n") + "\n", { headers });
}

function parseFlowObject(str){str=str.trim();if(str.startsWith("{")&&str.endsWith("}"))str=str.slice(1,-1);return parseKVPairs(str);}
function parseKVPairs(str){
  const obj={};let i=0;
  while(i<str.length){
    while(i<str.length&&str[i]===" ")i++;if(i>=str.length)break;
    const ks=i;while(i<str.length&&str[i]!==":")i++;const key=str.slice(ks,i).trim();i++;
    while(i<str.length&&str[i]===" ")i++;
    let value;
    if(str[i]==="{"){const s=i;let d=0;while(i<str.length){if(str[i]==="{")d++;else if(str[i]==="}"){d--;if(d===0){i++;break;}}i++;}value=parseKVPairs(str.slice(s+1,i-1));}
    else{const s=i;while(i<str.length){if(str[i]===","&&str[i+1]===" ")break;i++;}const r=str.slice(s,i).trim();if(r==="true")value=true;else if(r==="false")value=false;else if(r!==""&&!isNaN(r))value=Number(r);else value=r;}
    if(key)obj[key]=value;
    if(str[i]===","){i++;while(i<str.length&&str[i]===" ")i++;}
  }
  return obj;
}
function toFlowYaml(obj){
  const parts=[];
  for(const[k,v]of Object.entries(obj)){
    if(v!==null&&typeof v==="object")parts.push(`${k}: ${toFlowYaml(v)}`);
    else if(typeof v==="boolean"||typeof v==="number")parts.push(`${k}: ${v}`);
    else{const nq=/[,:{}\[\]#&*?|<>=!%@`]/.test(String(v));parts.push(nq?`${k}: '${v}'`:`${k}: ${v}`);}
  }
  return`{${parts.join(", ")}}`;
}

function buildPanel(request) {
  const subUrl = new URL(request.url).origin + "/sub";
  return `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>订阅转换器</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
:root{--bg:#0d0f14;--surface:#151820;--surface2:#1c2030;--border:#252a35;--accent:#4fffb0;--accent2:#00b8ff;--danger:#ff4f6b;--warn:#ffb84f;--text:#e0e6f0;--muted:#5a6275;--topbar-bg:rgba(13,15,20,.92);--accent-dim:rgba(79,255,176,.12);--mono:'JetBrains Mono',monospace;--sans:'Noto Sans SC',sans-serif;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:var(--sans);font-size:14px;min-height:100vh;transition:background .25s,color .25s;}
.topbar{position:fixed;top:0;left:0;right:0;z-index:200;height:54px;background:var(--topbar-bg);backdrop-filter:blur(14px);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 20px;gap:14px;transition:background .25s,border-color .25s;}
.logo{width:30px;height:30px;background:var(--accent);border-radius:7px;display:grid;place-items:center;font-family:var(--mono);font-weight:700;font-size:12px;color:#000;flex-shrink:0;transition:background .25s;}
.topbar-title{font-size:15px;font-weight:500;color:var(--text);}
.top-nav{display:flex;gap:4px;margin-left:28px;}
.top-nav a{padding:6px 14px;border-radius:7px;font-size:13px;font-family:var(--mono);color:var(--muted);text-decoration:none;cursor:pointer;transition:background .15s,color .15s;white-space:nowrap;}
.top-nav a:hover{color:var(--text);}
.top-nav a.active{background:var(--accent-dim);color:var(--accent);font-weight:700;}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:10px;}
.save-status{font-family:var(--mono);font-size:12px;color:var(--muted);transition:color .25s;white-space:nowrap;}
.save-status.saved{color:var(--accent);}.save-status.saving{color:var(--warn);}.save-status.error{color:var(--danger);}
.theme-wrap{position:relative;}
.theme-btn{height:30px;padding:0 12px;background:var(--surface2);border:1px solid var(--border);border-radius:7px;color:var(--muted);font-family:var(--mono);font-size:12px;cursor:pointer;display:flex;align-items:center;gap:6px;transition:border-color .15s,color .15s;white-space:nowrap;}
.theme-btn:hover{border-color:var(--accent);color:var(--accent);}
.theme-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.theme-dropdown{display:none;position:absolute;top:calc(100% + 6px);right:0;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:8px;min-width:200px;box-shadow:0 8px 32px rgba(0,0,0,.4);z-index:300;}
.theme-dropdown.open{display:block;}
.theme-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:8px;}
.th-opt{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-family:var(--mono);color:var(--muted);transition:background .15s,color .15s;}
.th-opt:hover{background:var(--surface2);color:var(--text);}
.th-opt.active{background:var(--accent-dim);color:var(--accent);}
.th-dot{width:12px;height:12px;border-radius:50%;flex-shrink:0;}
.custom-block{border-top:1px solid var(--border);padding-top:8px;}
.custom-block h5{font-size:11px;color:var(--muted);font-family:var(--mono);margin-bottom:8px;padding-left:4px;}
.custom-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;padding:0 4px;}
.custom-row label{font-size:11px;color:var(--muted);font-family:var(--mono);flex:1;}
.custom-row input[type=color]{width:34px;height:26px;border:1px solid var(--border);border-radius:6px;background:none;cursor:pointer;padding:2px;}
.btn-apply{width:100%;padding:7px;background:var(--accent);color:#000;border:none;border-radius:7px;font-family:var(--mono);font-size:12px;font-weight:700;cursor:pointer;margin-top:2px;}
.bottom-nav{display:none;position:fixed;bottom:0;left:0;right:0;z-index:200;height:56px;background:var(--topbar-bg);backdrop-filter:blur(14px);border-top:1px solid var(--border);transition:background .25s;}
.bottom-nav-inner{display:flex;height:100%;}
.bn-item{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;color:var(--muted);transition:color .15s;font-family:var(--mono);font-size:10px;}
.bn-item.active{color:var(--accent);font-weight:700;}
.bn-icon{font-size:20px;line-height:1;}
@media(max-width:700px){.top-nav{display:none;}.bottom-nav{display:block;}body{padding-bottom:56px;}.topbar{padding:0 14px;}.topbar-title{font-size:14px;}}
.page-wrap{padding-top:54px;max-width:900px;margin:0 auto;padding-left:18px;padding-right:18px;}
@media(max-width:700px){.page-wrap{padding-left:12px;padding-right:12px;}}
.screen{display:none;padding:22px 0 40px;}
.screen.active{display:block;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;margin-bottom:14px;transition:background .25s,border-color .25s;}
.card-title{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:14px;display:flex;align-items:center;gap:8px;}
.card-title::after{content:'';flex:1;height:1px;background:var(--border);}
.card-desc{font-size:12px;color:var(--muted);margin-bottom:12px;line-height:1.7;font-family:var(--mono);}
.stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:14px;}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px 10px;text-align:center;transition:background .25s;}
.stat-num{font-size:26px;font-weight:700;font-family:var(--mono);color:var(--accent);line-height:1;}
.stat-label{font-size:10px;color:var(--muted);margin-top:4px;}
.sub-box{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:14px 16px;margin-bottom:12px;transition:background .25s;}
.sub-box-label{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-family:var(--mono);margin-bottom:7px;}
.sub-box-url{font-family:var(--mono);font-size:12px;color:var(--accent2);word-break:break-all;line-height:1.6;}
.btn{padding:9px 16px;border-radius:8px;font-family:var(--mono);font-size:13px;font-weight:700;cursor:pointer;border:none;transition:opacity .15s,transform .1s;display:inline-flex;align-items:center;justify-content:center;gap:6px;}
.btn:active{transform:scale(.97);}
.btn-p{background:var(--accent);color:#000;}
.btn-s{background:transparent;border:1px solid var(--border);color:var(--muted);}
.btn-row{display:flex;gap:8px;}
.btn-row .btn{flex:1;}
.btn:hover{opacity:.8;}
.btn.copied{background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent);}
.save-bar{position:sticky;bottom:0;background:linear-gradient(transparent,var(--bg) 40%);padding:20px 0 10px;margin-top:8px;}
@media(max-width:700px){.save-bar{bottom:56px;}}
.btn-save{width:100%;padding:13px;background:var(--accent);color:#000;border:none;border-radius:10px;font-family:var(--mono);font-size:14px;font-weight:700;cursor:pointer;transition:opacity .15s,transform .1s;}
.btn-save:hover{opacity:.85;}.btn-save:active{transform:scale(.98);}
input[type=text]{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:var(--mono);font-size:13px;padding:8px 11px;outline:none;transition:border-color .15s,background .25s;}
input[type=text]:focus{border-color:var(--accent);}
.list-head{display:flex;gap:7px;margin-bottom:5px;}
.list-head span{font-size:11px;color:var(--muted);font-family:var(--mono);}
.lh-u{flex:1;}.lh-l{flex:0 0 100px;}.lh-d{flex:0 0 32px;}
.list-item{display:flex;gap:7px;align-items:center;margin-bottom:7px;}
.list-item input{flex:1;}
.li-lbl{flex:0 0 100px !important;}
.btn-icon{width:32px;height:32px;flex-shrink:0;background:transparent;border:1px solid var(--border);border-radius:8px;color:var(--muted);cursor:pointer;display:grid;place-items:center;font-size:18px;line-height:1;transition:border-color .15s,color .15s;}
.btn-icon:hover{border-color:var(--danger);color:var(--danger);}
.btn-add{width:100%;padding:9px;margin-top:4px;background:transparent;border:1px dashed var(--border);border-radius:8px;color:var(--muted);font-size:12px;font-family:var(--mono);cursor:pointer;transition:border-color .15s,color .15s;}
.btn-add:hover{border-color:var(--accent);color:var(--accent);}
.preset-grid{display:flex;flex-direction:column;gap:7px;margin-bottom:12px;}
.preset-item{display:flex;align-items:center;gap:10px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;}
.preset-addr{font-family:var(--mono);font-size:12px;color:var(--text);flex:1;}
.preset-desc{font-size:11px;color:var(--muted);font-family:var(--mono);}
.btn-use{padding:5px 12px;background:transparent;border:1px solid var(--border);border-radius:6px;font-family:var(--mono);font-size:12px;color:var(--muted);cursor:pointer;transition:border-color .15s,color .15s,background .15s;white-space:nowrap;flex-shrink:0;}
.btn-use:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-dim);}
.btn-use.used{border-color:var(--accent);color:var(--accent);background:var(--accent-dim);}
.toggle-row{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border);}
.toggle-row:last-child{border-bottom:none;}
.ti .tl{font-size:13px;color:var(--text);}
.ti .td{font-size:11px;color:var(--muted);margin-top:3px;font-family:var(--mono);line-height:1.5;}
.toggle{position:relative;width:42px;height:24px;flex-shrink:0;margin-left:14px;}
.toggle input{opacity:0;width:0;height:0;position:absolute;}
.ttrack{position:absolute;inset:0;background:var(--border);border-radius:24px;cursor:pointer;transition:background .2s;}
.ttrack::after{content:'';position:absolute;left:4px;top:4px;width:16px;height:16px;background:var(--muted);border-radius:50%;transition:transform .2s,background .2s;}
.toggle input:checked+.ttrack{background:var(--accent-dim);}
.toggle input:checked+.ttrack::after{transform:translateX(18px);background:var(--accent);}
.radio-card-group{display:flex;flex-direction:column;gap:10px;}
.radio-card{display:block;cursor:pointer;position:relative;}
.radio-card input{position:absolute;opacity:0;width:0;height:0;}
.rc-content{padding:14px;background:var(--surface2);border:1px solid var(--border);border-radius:10px;transition:all .2s;}
.radio-card input:checked + .rc-content{border-color:var(--accent);background:var(--accent-dim);}
.rc-title{font-size:13px;color:var(--text);font-weight:700;margin-bottom:4px;}
.radio-card input:checked + .rc-content .rc-title{color:var(--accent);}
.rc-desc{font-size:11px;color:var(--muted);font-family:var(--mono);line-height:1.5;}
.sep-row{display:flex;align-items:center;gap:10px;margin-top:12px;}
.sep-row label{margin:0;white-space:nowrap;font-size:12px;color:var(--muted);font-family:var(--mono);}
.sep-row input{max-width:68px;}
.sep-prev{font-size:12px;color:var(--accent);font-family:var(--mono);}
#toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%) translateY(60px);background:var(--surface);border:1px solid var(--accent);color:var(--accent);font-family:var(--mono);font-size:13px;padding:9px 22px;border-radius:30px;transition:transform .3s cubic-bezier(.34,1.56,.64,1),opacity .3s;opacity:0;z-index:999;pointer-events:none;}
#toast.show{transform:translateX(-50%) translateY(0);opacity:1;}
#toast.err{border-color:var(--danger);color:var(--danger);}
@media(min-width:701px){#toast{bottom:22px;}}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">CF</div>
  <span class="topbar-title">订阅转换器</span>
  <nav class="top-nav">
    <a onclick="goto(0)" id="tn0" class="active">仪表盘</a>
    <a onclick="goto(1)" id="tn1">节点订阅</a>
    <a onclick="goto(2)" id="tn2">优选服务器</a>
    <a onclick="goto(3)" id="tn3">功能设置</a>
  </nav>
  <div class="topbar-right">
    <span class="save-status" id="save-status"></span>
    <div class="theme-wrap">
      <button class="theme-btn" id="theme-btn" onclick="toggleThemeMenu()">
        <span class="theme-dot" id="cur-dot" style="background:var(--accent)"></span>
        <span id="cur-name">暗色</span><span>▾</span>
      </button>
      <div class="theme-dropdown" id="theme-dd">
        <div class="theme-grid" id="theme-grid"></div>
        <div class="custom-block">
          <h5>自定义强调色</h5>
          <div class="custom-row"><label>主强调色</label><input type="color" id="c-accent" value="#4fffb0"></div>
          <div class="custom-row"><label>副强调色</label><input type="color" id="c-accent2" value="#00b8ff"></div>
          <div class="custom-row"><label>危险色</label><input type="color" id="c-danger" value="#ff4f6b"></div>
          <button class="btn-apply" onclick="applyCustom()">应用自定义</button>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="bottom-nav">
  <div class="bottom-nav-inner">
    <div class="bn-item active" id="bn0" onclick="goto(0)"><div class="bn-icon">◈</div><div>仪表盘</div></div>
    <div class="bn-item" id="bn1" onclick="goto(1)"><div class="bn-icon">☁</div><div>节点订阅</div></div>
    <div class="bn-item" id="bn2" onclick="goto(2)"><div class="bn-icon">⚡</div><div>优选服务器</div></div>
    <div class="bn-item" id="bn3" onclick="goto(3)"><div class="bn-icon">⚙</div><div>功能设置</div></div>
  </div>
</div>
<div class="page-wrap">
  <div class="screen active" id="screen0">
    <div class="stat-grid">
      <div class="stat"><div class="stat-num" id="st-sub">0</div><div class="stat-label">节点订阅</div></div>
      <div class="stat"><div class="stat-num" id="st-srv">0</div><div class="stat-label">优选地址</div></div>
    </div>
    <div class="card">
      <div class="card-title">订阅链接</div>
      <div class="sub-box"><div class="sub-box-label">将此链接填入客户端</div><div class="sub-box-url" id="sub-url-el">${subUrl}</div></div>
      <div class="btn-row">
        <button class="btn btn-p" id="copy-btn" onclick="copySub()">复制订阅链接</button>
        <button class="btn btn-s" onclick="window.open('${subUrl}','_blank')">预览 YAML</button>
      </div>
    </div>
    <div class="card">
      <div class="card-title">当前配置概览</div>
      <div id="cfg-overview" style="font-family:var(--mono);font-size:12px;line-height:2.2;color:var(--muted);">加载中…</div>
    </div>
  </div>
  <div class="screen" id="screen1">
    <div class="card">
      <div class="card-title">相关开关</div>
      <div class="toggle-row">
        <div class="ti"><div class="tl">按 servername 去重</div><div class="td">相同 SNI 域名只保留第一个节点，去除冗余</div></div>
        <label class="toggle"><input type="checkbox" id="sw-dedup"><div class="ttrack"></div></label>
      </div>
      <div class="toggle-row">
        <div class="ti"><div class="tl">透传流量信息</div><div class="td">将机场的 Subscription-Userinfo 头透传给客户端，显示剩余流量</div></div>
        <label class="toggle"><input type="checkbox" id="sw-userinfo"><div class="ttrack"></div></label>
      </div>
    </div>
    <div class="card">
      <div class="card-title">节点订阅来源</div>
      <div class="card-desc">支持多个订阅链接，备注会拼接在节点名称末尾，留空则不加</div>
      <div class="list-head"><span class="lh-u">订阅链接</span><span class="lh-l">备注（可留空）</span><span class="lh-d"></span></div>
      <div id="sub-list"></div>
      <button class="btn-add" onclick="addSub()">＋ 添加订阅</button>
    </div>
    <div class="save-bar"><button class="btn-save" onclick="saveConfig()">保存配置</button></div>
  </div>
  <div class="screen" id="screen2">
    <div class="card">
      <div class="card-title">相关开关</div>
      <div class="toggle-row">
        <div class="ti"><div class="tl">统一替换 server 地址</div><div class="td">把所有节点 server 改为优选地址，关闭则保持原始 server</div></div>
        <label class="toggle"><input type="checkbox" id="sw-server"><div class="ttrack"></div></label>
      </div>
    </div>
    <div class="card">
      <div class="card-title">常用优选地址</div>
      <div class="card-desc">点击「使用」快速添加到列表，已添加的高亮显示</div>
      <div class="preset-grid" id="preset-grid"></div>
    </div>
    <div class="card">
      <div class="card-title">自定义优选服务器</div>
      <div class="card-desc">每个地址生成一组节点，多地址输出多倍节点</div>
      <div id="server-list"></div>
      <button class="btn-add" onclick="addServer()">＋ 手动添加地址</button>
    </div>
    <div class="save-bar"><button class="btn-save" onclick="saveConfig()">保存配置</button></div>
  </div>
  <div class="screen" id="screen3">
    <div class="card">
      <div class="card-title">节点名称设置</div>
      <div class="card-desc">控制生成后节点在客户端显示的名称来源</div>
      <div class="radio-card-group">
        <label class="radio-card">
          <input type="radio" name="nm" id="nm-orig" value="original">
          <div class="rc-content">
            <div class="rc-title">保持原名</div>
            <div class="rc-desc">保留机场原始节点名称，仅在末尾拼接备注</div>
          </div>
        </label>
        <label class="radio-card">
          <input type="radio" name="nm" id="nm-sni" value="servername">
          <div class="rc-content">
            <div class="rc-title">改成 servername</div>
            <div class="rc-desc">节点名改为 servername（SNI 域名），适合按域名识别</div>
          </div>
        </label>
        <label class="radio-card">
          <input type="radio" name="nm" id="nm-srv" value="server">
          <div class="rc-content">
            <div class="rc-title">改成 server</div>
            <div class="rc-desc">节点名改为替换后的 server 地址（优选 IP 或域名）</div>
          </div>
        </label>
      </div>
      <div class="sep-row">
        <label>备注分隔符</label>
        <input type="text" id="labelSep" value="#" maxlength="5" style="max-width:68px" oninput="updateSepPreview()">
        <div class="sep-prev" id="sep-prev">节点名#备注</div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">其他设置</div>
      <div class="toggle-row">
        <div class="ti"><div class="tl">同名节点自动加序号</div><div class="td">名称冲突时加 _2/_3，防止客户端因同名节点报错</div></div>
        <label class="toggle"><input type="checkbox" id="sw-seq"><div class="ttrack"></div></label>
      </div>
    </div>
    <div class="save-bar"><button class="btn-save" onclick="saveConfig()">保存配置</button></div>
  </div>
</div>
<div id="toast"></div>
<script>
var CUR=0;
function goto(n){document.querySelectorAll('.screen').forEach(function(s,i){s.classList.toggle('active',i===n);});document.querySelectorAll('.top-nav a').forEach(function(a,i){a.classList.toggle('active',i===n);});document.querySelectorAll('.bn-item').forEach(function(b,i){b.classList.toggle('active',i===n);});CUR=n;window.scrollTo({top:0,behavior:'smooth'});}
var THEMES=[
  {key:'auto',name:'自动',dot:'conic-gradient(#0d0f14 0 50%,#f0f2f7 50% 100%)'},
  {key:'dark',name:'暗色',dot:'#4fffb0',v:{'--bg':'#0d0f14','--surface':'#151820','--surface2':'#1c2030','--border':'#252a35','--accent':'#4fffb0','--accent2':'#00b8ff','--danger':'#ff4f6b','--warn':'#ffb84f','--text':'#e0e6f0','--muted':'#5a6275','--topbar-bg':'rgba(13,15,20,.92)','--accent-dim':'rgba(79,255,176,.12)'}},
  {key:'light',name:'亮色',dot:'#00a86b',v:{'--bg':'#f0f2f7','--surface':'#ffffff','--surface2':'#eef1f7','--border':'#dde3ee','--accent':'#00a86b','--accent2':'#0069d9','--danger':'#e53935','--warn':'#e67e22','--text':'#1a1d26','--muted':'#7a8799','--topbar-bg':'rgba(240,242,247,.92)','--accent-dim':'rgba(0,168,107,.1)'}},
  {key:'ocean',name:'深海',dot:'#00e5ff',v:{'--bg':'#071320','--surface':'#0c1e30','--surface2':'#112840','--border':'#1a3550','--accent':'#00e5ff','--accent2':'#0091ea','--danger':'#ff5252','--warn':'#ffab40','--text':'#cce8ff','--muted':'#4a7a9b','--topbar-bg':'rgba(7,19,32,.92)','--accent-dim':'rgba(0,229,255,.12)'}},
  {key:'aurora',name:'极光',dot:'#a78bfa',v:{'--bg':'#0f0a1e','--surface':'#18102e','--surface2':'#20153e','--border':'#2d1f55','--accent':'#a78bfa','--accent2':'#34d399','--danger':'#f87171','--warn':'#fbbf24','--text':'#ede9fe','--muted':'#6d5a9c','--topbar-bg':'rgba(15,10,30,.92)','--accent-dim':'rgba(167,139,250,.12)'}},
  {key:'amber',name:'琥珀',dot:'#ffb300',v:{'--bg':'#1a1200','--surface':'#221800','--surface2':'#2c2000','--border':'#3d2f00','--accent':'#ffb300','--accent2':'#ff8f00','--danger':'#ff5252','--warn':'#ff6d00','--text':'#fff8e1','--muted':'#8d7040','--topbar-bg':'rgba(26,18,0,.92)','--accent-dim':'rgba(255,179,0,.12)'}},
  {key:'sakura',name:'樱花',dot:'#ff80ab',v:{'--bg':'#1a0d12','--surface':'#25121a','--surface2':'#2e1820','--border':'#401f2d','--accent':'#ff80ab','--accent2':'#f48fb1','--danger':'#ff4081','--warn':'#ffab40','--text':'#fce4ec','--muted':'#8d5a6a','--topbar-bg':'rgba(26,13,18,.92)','--accent-dim':'rgba(255,128,171,.12)'}},
  {key:'cyber',name:'赛博',dot:'#ffe600',v:{'--bg':'#090909','--surface':'#111111','--surface2':'#181818','--border':'#2a2a2a','--accent':'#ffe600','--accent2':'#00ffff','--danger':'#ff0044','--warn':'#ff6600','--text':'#f0f0f0','--muted':'#666666','--topbar-bg':'rgba(9,9,9,.92)','--accent-dim':'rgba(255,230,0,.12)'}},
  {key:'custom',name:'自定义',dot:'conic-gradient(#ff4f6b,#ffb84f,#4fffb0,#00b8ff,#a78bfa,#ff80ab,#ff4f6b)'},
];
function buildThemeGrid(){var g=document.getElementById('theme-grid');g.innerHTML='';THEMES.forEach(function(t){var el=document.createElement('div');el.className='th-opt';el.id='th-'+t.key;var dot=document.createElement('div');dot.className='th-dot';dot.style.background=t.dot;el.appendChild(dot);el.appendChild(document.createTextNode(t.name));el.addEventListener('click',function(){if(t.key!=='custom'){setTheme(t.key);closeThemeMenu();}});g.appendChild(el);});}
function setTheme(key,customVars){if(key==='auto'){var dark=window.matchMedia('(prefers-color-scheme:dark)').matches;setTheme(dark?'dark':'light');window.matchMedia('(prefers-color-scheme:dark)').onchange=function(e){if(getLS('theme')==='auto')setTheme(e.matches?'dark':'light');};setLS('theme','auto');markTheme('auto');return;}var t=THEMES.find(function(x){return x.key===key;});var vars=customVars||(t&&t.v);if(!vars)return;var root=document.documentElement;Object.keys(vars).forEach(function(k){root.style.setProperty(k,vars[k]);});var dot=document.getElementById('cur-dot');var nm=document.getElementById('cur-name');if(dot)dot.style.background=(t&&t.dot&&!t.dot.startsWith('conic'))?t.dot:'var(--accent)';if(nm)nm.textContent=t?t.name:'自定义';setLS('theme',key==='custom'?JSON.stringify({key:'custom',v:vars}):key);markTheme(key);}
function markTheme(key){document.querySelectorAll('.th-opt').forEach(function(el){el.classList.toggle('active',el.id==='th-'+key);});}
function applyCustom(){var base=THEMES.find(function(t){return t.key==='dark';}).v;var a=document.getElementById('c-accent').value,a2=document.getElementById('c-accent2').value,d=document.getElementById('c-danger').value;var vars=Object.assign({},base,{'--accent':a,'--accent2':a2,'--danger':d,'--accent-dim':hexRgba(a,.12)});setTheme('custom',vars);closeThemeMenu();}
function hexRgba(h,a){var r=parseInt(h.slice(1,3),16),g=parseInt(h.slice(3,5),16),b=parseInt(h.slice(5,7),16);return 'rgba('+r+','+g+','+b+','+a+')';}
function toggleThemeMenu(){document.getElementById('theme-dd').classList.toggle('open');}
function closeThemeMenu(){document.getElementById('theme-dd').classList.remove('open');}
document.addEventListener('click',function(e){if(!e.target.closest('.theme-wrap'))closeThemeMenu();});
function loadTheme(){var saved=getLS('theme')||'dark';if(saved.startsWith('{')){var d=JSON.parse(saved);setTheme('custom',d.v);if(d.v['--accent'])document.getElementById('c-accent').value=d.v['--accent'];if(d.v['--accent2'])document.getElementById('c-accent2').value=d.v['--accent2'];if(d.v['--danger'])document.getElementById('c-danger').value=d.v['--danger'];}else{setTheme(saved);}}
var PRESETS=[{addr:'d.cf.090227.xyz',desc:'优选 CDN'},{addr:'d.cloudflare.182682.xyz',desc:'优选 CDN'},{addr:'mfa.gov.ua',desc:'乌克兰外交部（优选IP）'},{addr:'www.shopify.com',desc:'Shopify（优选IP）'},{addr:'d.tencentapp.cn',desc:'腾讯优选'}];
function buildPresets(){var g=document.getElementById('preset-grid');g.innerHTML='';PRESETS.forEach(function(p){var row=document.createElement('div');row.className='preset-item';row.innerHTML='<div style="flex:1"><div class="preset-addr">'+esc(p.addr)+'</div><div class="preset-desc">'+esc(p.desc)+'</div></div><button class="btn-use" data-addr="'+esc(p.addr)+'" onclick="usePreset(this)">使用</button>';g.appendChild(row);});syncPresetBtns();}
function usePreset(btn){var addr=btn.getAttribute('data-addr');var ex=Array.from(document.querySelectorAll('#server-list .is')).map(function(i){return i.value.trim();});if(!ex.includes(addr)){addServerItem(addr);updateStats();}syncPresetBtns();}
function syncPresetBtns(){var ex=Array.from(document.querySelectorAll('#server-list .is')).map(function(i){return i.value.trim();});document.querySelectorAll('.btn-use').forEach(function(btn){var addr=btn.getAttribute('data-addr');var inList=ex.includes(addr);btn.textContent=inList?'已添加':'使用';btn.classList.toggle('used',inList);});}
async function loadConfig(){try{var res=await fetch('/api/config');var cfg=await res.json();applyConfig(cfg);setStatus('','· 已同步');}catch(e){showToast('加载失败：'+e.message,true);}}
function applyConfig(cfg){document.getElementById('sub-list').innerHTML='';(cfg.subList||[]).forEach(function(s){addSubItem(s.url,s.label);});document.getElementById('server-list').innerHTML='';(cfg.servers||[]).forEach(function(s){addServerItem(s);});var nm=document.querySelector('input[name="nm"][value="'+(cfg.nameMode||'original')+'"]');if(nm)nm.checked=true;document.getElementById('labelSep').value=cfg.labelSep||'#';updateSepPreview();document.getElementById('sw-dedup').checked=cfg.enableDedup!==false;document.getElementById('sw-seq').checked=cfg.enableAutoSeq!==false;document.getElementById('sw-server').checked=cfg.replaceServer!==false;document.getElementById('sw-userinfo').checked=cfg.passUserinfo!==false;syncPresetBtns();updateStats();updateOverview(cfg);}
function collectConfig(){var subList=Array.from(document.querySelectorAll('#sub-list .sub-row')).map(function(r){return{url:r.querySelector('.iu').value.trim(),label:r.querySelector('.il').value.trim()};}).filter(function(x){return x.url;});var servers=Array.from(document.querySelectorAll('#server-list .is')).map(function(i){return i.value.trim();}).filter(Boolean);var nmEl=document.querySelector('input[name="nm"]:checked');return{nameMode:nmEl?nmEl.value:'original',labelSep:document.getElementById('labelSep').value||'#',enableDedup:document.getElementById('sw-dedup').checked,enableAutoSeq:document.getElementById('sw-seq').checked,replaceServer:document.getElementById('sw-server').checked,passUserinfo:document.getElementById('sw-userinfo').checked,servers:servers,subList:subList};}
async function saveConfig(){var cfg=collectConfig();setStatus('saving','保存中…');try{var res=await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cfg)});var d=await res.json();if(d.ok){setStatus('saved','✓ 已保存');showToast('配置已保存，立即生效');updateOverview(cfg);setTimeout(function(){setStatus('','');},3000);}else{throw new Error(d.error||'未知');}}catch(e){setStatus('error','✗ 失败');showToast('保存失败：'+e.message,true);}}
function addSub(){addSubItem('','');updateStats();}
function addSubItem(url,label){var el=document.getElementById('sub-list');var row=document.createElement('div');row.className='list-item sub-row';row.innerHTML='<input class="iu" type="text" placeholder="https://订阅链接" value="'+esc(url)+'" oninput="updateStats()"><input class="il li-lbl" type="text" placeholder="备注" value="'+esc(label)+'"><button class="btn-icon" onclick="this.parentElement.remove();updateStats()" title="删除">×</button>';el.appendChild(row);}
function addServer(){addServerItem('');updateStats();}
function addServerItem(val){var el=document.getElementById('server-list');var row=document.createElement('div');row.className='list-item';row.innerHTML='<input class="is" type="text" placeholder="域名或 IP" value="'+esc(val)+'" oninput="syncPresetBtns();updateStats()"><button class="btn-icon" onclick="this.parentElement.remove();syncPresetBtns();updateStats()" title="删除">×</button>';el.appendChild(row);}
function updateStats(){
  var subs=document.querySelectorAll('#sub-list .iu').length;
  var srvs=document.querySelectorAll('#server-list .is').length;
  document.getElementById('st-sub').textContent=subs;
  document.getElementById('st-srv').textContent=srvs;
}
function updateSepPreview(){var sep=document.getElementById('labelSep').value||'#';document.getElementById('sep-prev').textContent='节点名'+sep+'备注';}
function updateOverview(cfg){
  var mm={original:'保持原名',servername:'改成 servername',server:'改成 server'};
  var stDedup = cfg.enableDedup !== false ? '开启' : '关闭';
  var stSeq = cfg.enableAutoSeq !== false ? '开启' : '关闭';
  var stServer = cfg.replaceServer !== false ? '开启' : '关闭';
  var stUserinfo = cfg.passUserinfo !== false ? '开启' : '关闭';
  
  document.getElementById('cfg-overview').innerHTML=
    row('节点订阅来源',(cfg.subList||[]).length+' 个')+
    row('优选服务器',(cfg.servers||[]).length+' 个')+
    row('节点命名模式',mm[cfg.nameMode]||cfg.nameMode)+
    row('备注分隔符','"'+(cfg.labelSep||'#')+'"')+
    row('按 servername 去重', stDedup)+
    row('透传流量信息', stUserinfo)+
    row('统一替换 server', stServer)+
    row('同名节点加序号', stSeq);
    
  function row(k,v){
    var vc = (v==='开启') ? 'var(--accent)' : (v==='关闭' ? 'var(--muted)' : 'var(--accent)');
    return'<span style="color:var(--muted)">'+k+'</span><span style="float:right;color:'+vc+'">'+v+'</span><br>';
  }
}
function copySub(){var url=document.getElementById('sub-url-el').textContent;var btn=document.getElementById('copy-btn');var fn=navigator.clipboard?function(){return navigator.clipboard.writeText(url);}:function(){var ta=document.createElement('textarea');ta.value=url;ta.style.cssText='position:fixed;opacity:0';document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);return Promise.resolve();};fn().then(function(){btn.textContent='✓ 已复制';btn.classList.add('copied');setTimeout(function(){btn.textContent='复制订阅链接';btn.classList.remove('copied');},2000);});}
function setStatus(cls,text){var e=document.getElementById('save-status');e.className='save-status '+cls;e.textContent=text;}
function showToast(msg,isErr){var e=document.getElementById('toast');e.textContent=msg;e.className='show'+(isErr?' err':'');clearTimeout(window._tt);window._tt=setTimeout(function(){e.className='';},3000);}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function getLS(k){try{return localStorage.getItem(k);}catch{return null;}}
function setLS(k,v){try{localStorage.setItem(k,v);}catch{}}
buildThemeGrid();buildPresets();loadTheme();loadConfig();
</script>
</body>
</html>`;
}
