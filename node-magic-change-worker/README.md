# Node-magic-change-worker

一个 Cloudflare Worker 脚本，用于处理多个订阅链接的合并、去重和节点转换。

## 🌟 主要亮点

- **完整一体化**：一个文件同时提供 Web 配置面板和 Worker 后端
- **自适应界面**：响应式设计，支持桌面和移动设备
- **极简可用**：无主题系统，部署即用，轻量与性能导向
- **KV 存储**：配置存储在 Cloudflare KV，持久化保存
- **即时生效**：配置保存后无需重新部署 Worker
- **可视化配置**：优雅的 Web 界面，实时预览和修改配置

## 👤 开发者
**Automata** - OpenClaw 助手，负责维护和更新

## 📁 文件说明

### **主要文件**
- **`Node-magic-change-panel.js`** - 主文件（简洁优化版，极简界面）
- **`Node-magic-change-panel.html`** - 纯 HTML 配置面板（用于预览）
- **`Node-magic-change.js`** - 基础版本 Worker 代码（简版功能）

### **核心特性**

**`Node-magic-change-panel.js`**（当前推荐版本）功能：
1. **Web 配置面板** - 自适应响应式界面
2. **KV 持久化存储** - 配置自动保存到 Cloudflare KV
3. **实时预览** - 修改配置立即生效，无需重新部署
4. **多终端适配** - 桌面和移动设备都能良好显示
5. **完整 API 接口** - `/api/config` GET/POST 接口

## 🎯 使用场景

这个工具特别适合以下场景：
- 拥有多个代理订阅服务，需要合并使用
- 需要将所有节点指向统一的优选服务器地址（如 Cloudflare CDN）
- 需要去除重复节点，优化订阅列表
- 需要对节点进行标准化命名和管理
- 需要一个可视化的配置界面，无需频繁修改代码

## ⚙️ 配置选项

**主要配置选项**：
- **节点命名模式**：original / servername / server
- **备注分隔符**：自定义分隔符
- **订阅链接列表**：支持多个订阅，每个可独立备注
- **优选服务器列表**：支持多个服务器地址
- **功能开关**：去重、自动序号、服务器替换、流量信息透传

## 🚀 使用方法

### **部署 Node-magic-change-panel.js**（推荐）

1. **绑定 KV**：
   - Cloudflare → Workers & Pages → KV → 新建命名空间 `SUB_CONFIG`
   - Worker → 设置 → 变量 → KV 命名空间绑定
   - 变量名填 `CONFIG_KV`，选择 `SUB_CONFIG`

2. **部署 Worker**：
   - 直接将 `Node-magic-change-panel.js` 内容复制到 Cloudflare Worker

3. **使用**：
   - 访问 Worker 的 URL：显示配置面板
   - 访问 `/sub`：获取处理后的订阅 YAML
   - 访问 `/api/config`：查看或保存配置

### **部署 Node-magic-change.js**（基础版）
直接在 Cloudflare Worker 中部署，需要手动修改代码中的配置参数。

### **使用 Web 面板**
打开 `Node-magic-change-panel.html` 文件在浏览器中进行可视化配置。

## 📋 输出格式

输出为标准的 Clash 配置文件格式，包含 `proxies` 字段：
```yaml
proxies:
  - {name: 节点1#我的机场, server: cf.090227.xyz, port: 443, tls: true}
  - {name: 节点2#我的机场, server: cf.090227.xyz, port: 443, tls: true}
```

## 🔧 技术特点

- **并发拉取**：所有订阅同时获取，提高效率
- **智能去重**：基于 servername 字段去除重复节点
- **序列化处理**：包含完整的 Flow YAML 解析器和序列化器
- **深度拷贝**：确保每个节点对象独立，避免引用问题
- **备注标签**：支持为不同订阅来源添加注释
- **自适应界面**：响应式设计，支持移动设备
- **KV 存储**：配置持久化保存，无需重新部署
- **API 接口**：提供 `/api/config` GET/POST 接口

## 📝 更新历史

### **v2.0**（`Node-magic-change-panel.js` - 2026年4月5日）
- ✅ 迁移为精简版：移除主题系统，代码量从 847 行降至 452 行
- ✅ 保持核心功能完整：订阅合并、去重、KV 存储、即时预览
- ✅ 优化加载速度与维护性

### **v1.0**（初版）
- ✅ 基础合并去重功能
- ✅ Web 配置面板
- ✅ YAML 解析器和序列化器

## 📌 注意事项

1. **Cloudflare KV 绑定**：部署需要绑定 KV 命名空间
2. **订阅链接有效性**：确保订阅链接能够正常访问
3. **服务器地址可用性**：确保配置的服务器地址可以被代理客户端访问
4. **测试部署**：建议在生产环境中使用前先在测试环境中验证

## 📄 许可证

MIT

---

*本助手使用的模型：`openrouter/stepfun/step-3.5-flash:free`（默认模型）*