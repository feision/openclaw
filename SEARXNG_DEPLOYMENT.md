# 🔍 私有 SearXNG 部署与 OpenClaw 集成指南

**版本**: 1.0  
**最后更新**: 2026-04-07  
**适用环境**: Docker, Zeabur, VPS  

---

## 1. 为什么需要私有 SearXNG？

- ✅ **隐私保护**：无追踪、无用户画像
- ✅ **OpenClaw 集成**：作为 AI 助手的搜索后端（通过工具调用）
- ✅ **自定义引擎**：可配置多个搜索引擎，去广告
- ✅ **无商业化**：完全掌控搜索结果

---

## 2. 部署方式选择

| 方式 | 适合人群 | 复杂度 | 推荐度 |
|------|---------|--------|--------|
| **Docker Compose** | 大多数用户 | ⭐⭐ | ✅ **首选** |
| Zeabur/云平台 | 已有平台 | ⭐ | ✅ 如果你在用 |
| 原生安装 | 高级用户 | ⭐⭐⭐ | ⚠️ 不推荐新手 |

**本文重点**：Docker Compose 官方标准流程。

---

## 3. Docker Compose 部署（推荐）

### 3.1 前置条件
- 已安装 Docker 或 Podman
- 有 shell 访问权限（可执行 `docker compose`）
- 确保端口 8080（或其他）未被占用

### 3.2 创建目录结构
```bash
mkdir -p ./searxng/core-config/
cd ./searxng
```

### 3.3 下载官方模板
```bash
curl -fsSL \
  -O https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml \
  -O https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example
```

### 3.4 配置环境变量
```bash
cp .env.example .env
nano .env  # 或使用 vim/vscode
```

**关键配置项**（按需修改）：
```bash
# Web 访问端口（宿主机:容器）
SEARXNG_PORT=8080

# 实例的 Base URL（如果通过域名访问）
# SEARXNG_BASE_URL=https://searx.your-domain.com

# 是否开启 Redis 缓存（可选）
SEARXNG_REDIS_URL=redis://valkey:6379/0
```

保存并退出。

### 3.5 启动服务
```bash
docker compose up -d
```

### 3.6 检查状态
```bash
docker compose ps
```
应看到两个服务 `core` 和 `valkey` 都处于 `Up` 状态。

---

## 4. 核心配置详解（避免常见坑）

### 4.1 编辑 `core-config/settings.yml`

这是最关键的一步！很多人在这一步出错。

```bash
nano ./core-config/settings.yml
```

找到以下两个配置段，**必须修改**：

#### a) `search.formats` → 启用 JSON API

**错误配置**（默认）：
```yaml
search:
  formats:
    - html
```

**正确配置**：
```yaml
search:
  formats:
    - html   # 保留网页访问
    - json   # ⭐ 必须：OpenClaw 工具需要 JSON 格式
```

**原因**：SearXNG 默认只允许 HTML 格式访问。OpenClaw 通过工具调用需要 `format=json`，如果不加 `json`，会返回 403 Forbidden。

#### b) `server.bind_address` → 允许内网访问

**错误配置**（默认）：
```yaml
server:
  bind_address: "127.0.0.1"  # 仅本地
```

**正确配置**（内网环境）：
```yaml
server:
  bind_address: "0.0.0.0"    # 监听所有接口
```

**原因**：`127.0.0.1` 使得只有容器内部能访问。在内网环境下，你需要所有内网主机能访问，所以改为 `0.0.0.0`。

#### c) `server.public_instance` → 启用公开实例功能

**错误配置**（默认）：
```yaml
server:
  public_instance: false
```

**正确配置**：
```yaml
server:
  public_instance: true
```

**原因**：设为 `true` 会启用公开实例特性（包括 JSON API 的限流处理等），确保外部工具能正常调用。

#### 完整示例
```yaml
search:
  safe_search: 0
  autocomplete: ""
  favicon_resolver: ""
  default_lang: ""
  ban_time_on_fail: 5
  max_page: 0
  max_ban_time_on_fail: 120
  suspended_times:
    SearxEngineAccessDenied: 86400
    SearxEngineCaptcha: 86400
    SearxEngineTooManyRequests: 3600
    cf_SearxEngineCaptcha: 1296000
    cf_SearxEngineAccessDenied: 86400
    recaptcha_SearxEngineCaptcha: 604800
  formats:
    - html
    - json   # ⭐ 添加这行

server:
  base_url: ""           # 内网可留空
  port: 8080
  bind_address: "0.0.0.0"      # ⭐ 改为 0.0.0.0
  secret_key: "请务必修改为随机字符串"  # ⚠️ 生产环境必须改
  limiter: false
  public_instance: true          # ⭐ 改为 true
  image_proxy: false
  method: "POST"
  default_http_headers:
    X-Content-Type-Options: nosniff
    X-Download-Options: noopen
    X-Robots-Tag: noindex, nofollow
    Referrer-Policy: no-referrer
```

### 4.2 重启服务
```bash
docker compose down
docker compose up -d
```

---

## 5. 验证部署

### 5.1 测试主页（HTML）
```bash
curl http://localhost:8080/ | head -10
```
应返回 HTML 内容，看到 `<!DOCTYPE html>` 等。

### 5.2 测试搜索 API（JSON）
```bash
curl "http://localhost:8080/search?q=test&format=json" | jq .
```

**预期输出**：
```json
{
  "query": "test",
  "results": [
    {
      "title": "...",
      "url": "...",
      "content": "..."
    }
  ]
}
```

### 5.3 确保返回 JSON 且有 `results` 字段
如果返回 `403` 或 HTML，说明配置仍有问题，回到第 4 步检查。

---

## 6. 与 OpenClaw 集成

### 6.1 创建工具文件
```bash
mkdir -p ~/.openclaw/tools
nano ~/.openclaw/tools/searxng.js
```

### 6.2 粘贴以下代码

根据你的实际服务地址修改 `baseUrl`：

```javascript
export default {
 id: "searxng",
 description: "Search via private SearXNG instance",
 parameters: {
   query: { type: "string", description: "Search query text" }
 },
 async run({ query }) {
   // ⚙️ 修改这里的地址：如果服务不在 localhost:8080，请调整
   const baseUrl = "http://searxng.zeabur.internal:8080"; // 内网域名
   // const baseUrl = "http://localhost:8080"; // 本地测试
   // const baseUrl = "https://searx.your-domain.com"; // 公网域名

   const url = `${baseUrl}/search?q=${encodeURIComponent(query)}&format=json`;

   const res = await fetch(url, {
     headers: { "User-Agent": "OpenClaw-SearXNG-Tool" },
     // 如果 SearXNG 有基本认证，可添加：
     // headers: { "Authorization": "Basic xxx" }
   });

   if (!res.ok) {
     return `SearXNG error: ${res.status} - ${res.statusText}`;
   }

   const data = await res.json();

   // 只返回前 5 条最相关结果
   const results = data.results?.slice(0, 5).map(r => ({
     title: r.title,
     url: r.url,
     snippet: r.content
   }));

   return {
     query,
     results: results || []
   };
 }
};
```

保存并退出。

### 6.3 使用方式

**直接在聊天里说**：
- "搜索 OpenClaw 官方文档"
- "帮我查一下今天东京天气"

OpenClaw 会自动识别搜索意图，调用 `searxng.js` 工具并返回结果。

**无需修改 `openclaw.json`**，工具是独立加载的。

---

## 7. 常见问题排查

| 问题 | 现象 | 原因 | 解决 |
|------|------|------|------|
| **403 Forbidden** | `"format=json"` 返回 403 | `search.formats` 未包含 `json` | 编辑 `settings.yml` 添加 `json` |
| **连接被拒绝** | `curl: (7) Failed to connect` | `bind_address: 127.0.0.1` | 改为 `0.0.0.0` 并重启 |
| **返回空结果** | JSON 中有 `"results": []` | `public_instance: false` 或引擎未启用 | 改为 `public_instance: true` |
| **JSON parse error** | `unexpected token <` | 接口返回 HTML（通常是 404） | 检查 URL 和端口是否正确 |
| **工具不调用** | OpenClaw 忽略搜索请求 | 工具文件不在 `~/.openclaw/tools/` | 检查文件路径和权限 |

---

## 8. 维护建议

### 8.1 定期更新
```bash
docker compose down
docker compose pull
docker compose up -d
```

### 8.2 查看日志
```bash
docker compose logs -f core
```

### 8.3 备份配置
```bash
cp ./core-config/settings.yml ./core-config/settings.yml.backup
```

### 8.4 清理无用资源
```bash
docker system df  # 查看磁盘使用
docker system prune -a --volumes  # 清理未使用镜像/容器（谨慎）
```

---

## 9. 安全提醒

⚠️ **如果暴露到公网**：
- 必须设置 `server.secret_key` 为随机字符串（不要用默认值）
- 建议配置反向代理（Nginx/Caddy）加 HTTPS
- 考虑添加身份验证（基本 auth 或 IP 白名单）
- 定期查看日志，防止滥用

---

## 10. 与 OpenClaw 的完整集成清单

- [ ] SearXNG 服务运行正常（主页可访问）
- [ ] `search.formats` 包含 `json`
- [ ] `server.bind_address` 设为 `0.0.0.0`
- [ ] `server.public_instance` 设为 `true`
- [ ] 测试 `curl "http://.../search?q=test&format=json"` 返回 JSON
- [ ] 创建 `~/.openclaw/tools/searxng.js`
- [ ] 在 OpenClaw 聊天中测试搜索："搜索 OpenClaw 教程"

✅ 全部完成后，你的私有搜索引擎就 ready 了！

---

## 11. 附录：Zeabur 部署的特殊说明

如果你在 Zeabur 平台部署：

1. **环境变量设置**（而非修改 `settings.yml`）：
   - `SEARXNG_BASE_URL`: 你的公网域名
   - `SEARXNG_PORT`: `8080`（Zeabur 会自动映射）
   - `SEARXNG_PUBLIC_INSTANCE`: `true`

2. **持久化配置**：
   - Zeabur 会自动挂载 `/data` 目录（对应 Docker 的 `/var/cache/searxng/`）
   - 你需要通过 Zeabur 的 "Config Files" 功能上传 `settings.yml`
   - 路径选择：`/etc/searxng/settings.yml`

3. **内网域名**：
   - Zeabur 提供的内网域名通常是 `service-name.platform.zeabur.internal`
   - 示例：`searxng.zeabur.internal:8080`

4. **验证步骤**（同第 5 节，使用内网域名测试）

---

**保持简洁，快速部署。** 🎯
