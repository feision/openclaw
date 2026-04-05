// ============================================================
// Cloudflare Worker - 多订阅合并 + 去重 + 节点处理
// ============================================================


// ── 配置区 ────────────────────────────────────────────────────

// 【节点名称模式】三选一，把不需要的两行注释掉
// "original"   → 保持原始 name 不变
// "servername" → 把 name 改成 servername 字段的值
// "server"     → 把 name 改成 server 字段的值（替换后的优选地址）
const NAME_MODE = "original";
// const NAME_MODE = "servername";
// const NAME_MODE = "server";

// 【优选服务器列表】支持多个地址
// 每个地址会生成一批独立节点，最终输出所有地址的节点合集
// 例如填两个地址 + 10个去重节点 → 输出 20 个节点
const UNIFIED_SERVERS = [
  "cf.090227.xyz",
  // "cloudflare.182682.xyz",
  // "162.159.192.1",
];

// 【订阅链接列表】
// 格式：链接#备注   （# 后面的文字拼在节点名末尾，可以不写）
const SUB_URS = [
  "https://123.tsm.cc.cd/sub/user/eyJ1IjoiZHVjayIsImUiOjE3Nzc4MDA2Njk3MDgsInMiOiJlNWI0NzQzNmMxYmUxNTY4In0#我的机场",
  // "https://example.com/sub/xxx#备用机场",
];

// ── 配置区结束 ─────────────────────────────────────────────────


export default {
  async fetch(request) {

    // ── 第一步：并发拉取所有订阅内容 ─────────────────────────
    const tasks = SUB_URS.map((raw) => {
      const sharpIndex = raw.indexOf("#");
      const url   = sharpIndex === -1 ? raw : raw.slice(0, sharpIndex);
      const label = sharpIndex === -1 ? ""  : raw.slice(sharpIndex + 1);

      return fetch(url.trim(), { headers: { "User-Agent": "clash.meta" } })
        .then((r) => r.ok ? r.text().then((text) => ({ text, label })) : null)
        .catch(() => null);
    });
    const results = await Promise.all(tasks);


    // ── 第二步：从每个订阅中提取节点行 ──────────────────────
    const proxyEntries = []; // [{ line: "{...}", label: "备注" }]

    for (const res of results) {
      if (!res) continue;
      const { text, label } = res;
      let inProxies = false;

      for (const line of text.split("\n")) {
        if (/^proxies\s*:/.test(line)) { inProxies = true; continue; }
        if (inProxies) {
          if (/^\s+- \{/.test(line)) {
            proxyEntries.push({
              line: line.trim().replace(/^-\s*/, ""),
              label,
            });
          } else if (line.trim() && !/^\s/.test(line)) {
            break;
          }
        }
      }
    }


    // ── 第三步：解析 + 按 servername 去重 ────────────────────
    // 注意：这里只做去重，不处理 name 和 server 字段
    // name 和 server 的修改统一放到第四步，保证顺序正确
    const seen        = new Set(); // 记录已出现的 servername，用于去重
    const baseProxies = [];        // 去重后的基础节点列表（含原始 label）

    for (const { line, label } of proxyEntries) {
      const proxy = parseFlowObject(line);

      const key = proxy.servername || proxy.server;
      if (!key || seen.has(key)) continue;
      seen.add(key);

      // 只处理 servername 模式的 name，因为它不依赖 server 的值
      if (NAME_MODE === "servername" && proxy.servername) {
        proxy.name = proxy.servername;
      }
      // original 模式：name 保持原样，不动
      // server 模式：先不动，等第四步替换完 server 再设置

      // 把备注标签存起来，第四步拼接用
      proxy._label = label;

      baseProxies.push(proxy);
    }


    // ── 第四步：按 UNIFIED_SERVERS 展开，生成多组节点 ────────
    // 正确顺序：① 替换 server → ② 根据新 server 设置 name → ③ 拼接备注 → ④ 处理同名序号
    const nameCount = {}; // 记录每个名称出现的次数，用于生成序号
    const proxies   = []; // 最终节点列表

    for (const serverAddr of UNIFIED_SERVERS) {
      for (const base of baseProxies) {
        // 深拷贝，避免多个 server 地址共用同一个对象
        const proxy = JSON.parse(JSON.stringify(base));

        // ① 先替换 server 为优选地址
        proxy.server = serverAddr;

        // ② 再根据新 server 设置 name（server 模式在这里才处理）
        if (NAME_MODE === "server") {
          proxy.name = serverAddr; // 此时 server 已经是优选地址了，逻辑正确
        }

        // ③ 拼接备注（之前存在 _label 里的），然后删掉临时字段
        if (proxy._label) proxy.name = proxy.name + "#" + proxy._label;
        delete proxy._label;

        // ④ 处理同名冲突：第一次出现正常用，之后加 _2, _3 ...
        if (nameCount[proxy.name] === undefined) {
          nameCount[proxy.name] = 1;
        } else {
          nameCount[proxy.name]++;
          proxy.name = proxy.name + "_" + nameCount[proxy.name];
        }

        proxies.push(proxy);
      }
    }


    // ── 第五步：序列化成 Clash YAML 并返回 ───────────────────
    const lines = ["proxies:"];
    for (const p of proxies) {
      lines.push("  - " + toFlowYaml(p));
    }
    const output = lines.join("\n") + "\n";

    return new Response(output, {
      headers: { "Content-Type": "text/yaml; charset=utf-8" },
    });
  },
};


// ============================================================
// 工具函数：Flow YAML 解析器
// ============================================================
// 把单行 flow YAML 字符串解析成 JS 对象
// 输入："{name: 节点1, server: 1.2.3.4, port: 443, tls: true}"
// 输出：{ name: "节点1", server: "1.2.3.4", port: 443, tls: true }

function parseFlowObject(str) {
  str = str.trim();
  if (str.startsWith("{") && str.endsWith("}")) str = str.slice(1, -1);
  return parseKVPairs(str);
}

function parseKVPairs(str) {
  const obj = {};
  let i = 0;

  while (i < str.length) {
    while (i < str.length && str[i] === " ") i++;
    if (i >= str.length) break;

    // 读取 key
    const keyStart = i;
    while (i < str.length && str[i] !== ":") i++;
    const key = str.slice(keyStart, i).trim();
    i++;
    while (i < str.length && str[i] === " ") i++;

    // 读取 value
    let value;
    if (str[i] === "{") {
      // 嵌套对象，找到对应的 } 结束位置
      const start = i;
      let depth = 0;
      while (i < str.length) {
        if (str[i] === "{") depth++;
        else if (str[i] === "}") { depth--; if (depth === 0) { i++; break; } }
        i++;
      }
      value = parseKVPairs(str.slice(start + 1, i - 1));
    } else {
      // 普通值，读到 ", " 或末尾
      const start = i;
      while (i < str.length) {
        if (str[i] === "," && str[i + 1] === " ") break;
        i++;
      }
      const raw = str.slice(start, i).trim();
      if (raw === "true")                 value = true;
      else if (raw === "false")           value = false;
      else if (raw !== "" && !isNaN(raw)) value = Number(raw);
      else                                value = raw;
    }

    if (key) obj[key] = value;
    if (str[i] === ",") { i++; while (i < str.length && str[i] === " ") i++; }
  }

  return obj;
}


// ============================================================
// 工具函数：Flow YAML 序列化器
// ============================================================
// 把 JS 对象转换回单行 flow YAML 字符串
// 输入：{ name: "节点1", server: "1.2.3.4, port: 443, tls: true }
// 输出："{name: 节点1, server: 1.2.3.4, port: 443, tls: true}"

function toFlowYaml(obj) {
  const parts = [];
  for (const [k, v] of Object.entries(obj)) {
    if (v !== null && typeof v === "object") {
      parts.push(`${k}: ${toFlowYaml(v)}`);
    } else if (typeof v === "boolean" || typeof v === "number") {
      parts.push(`${k}: ${v}`);
    } else {
      const needsQuote = /[,:{}\[\]#&*?|<>=!%@`]/.test(String(v));
      parts.push(needsQuote ? `${k}: '${v}'` : `${k}: ${v}`);
    }
  }
  return `{${parts.join(", ")}}`;
}