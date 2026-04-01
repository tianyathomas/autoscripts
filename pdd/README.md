# 拼多多果园自动化脚本

自动签到、浇水、领取任务奖励。支持青龙面板。

## 功能

- ✅ 自动签到（+水滴）
- ✅ 自动浇水（消耗水滴）
- ✅ 自动领取任务奖励
- ✅ Anti-Token 自动生成（无需手动更新）
- ✅ 支持青龙面板定时运行

## 环境要求

- Node.js 14+
- Python 3.6+
- requests 库（`pip install requests`）

## 使用方法

### 1. 获取 Cookie

在浏览器中打开拼多多果园页面，打开开发者工具（F12），在 Network 标签中找到任意请求，复制 Cookie 字符串。

需要的 Cookie 字段：
- `api_uid`
- `pdd_user_id`
- `PDDAccessToken`
- `pdd_user_uin`
- `tubetoken`（可选）

### 2. 本地运行

```bash
# 设置环境变量
export PDD_COOKIE="api_uid=...;pdd_user_id=...;PDDAccessToken=...;pdd_user_uin=...;tubetoken=..."

# 运行脚本
node pdd.js
```

### 3. 青龙面板运行

#### 3.1 添加环境变量

在青龙面板 → 环境变量 中添加：

```
PDD_COOKIE=api_uid=...;pdd_user_id=...;PDDAccessToken=...;pdd_user_uin=...;tubetoken=...
```

#### 3.2 添加定时任务

在青龙面板 → 定时任务 中添加：

**早上 7:00 签到 + 浇水**
```
0 7 * * * node /ql/scripts/pdd.js
```

**晚上 19:00 签到 + 浇水 + 领取任务**
```
0 19 * * * node /ql/scripts/pdd.js
```

#### 3.3 上传脚本

将 `pdd.js` 上传到青龙的 `/ql/scripts/` 目录。

## 工作原理

1. **Anti-Token 生成**：脚本自动下载拼多多的风控 SDK，在 Node.js 中模拟浏览器环境执行，生成有效的 Anti-Token
2. **API 调用**：使用 Python 的 requests 库调用拼多多 API
3. **自动化流程**：
   - 查询当前水滴数量
   - 签到（获得水滴）
   - 浇水（消耗水滴）
   - 获取任务列表（需要 Anti-Token）
   - 领取可领取的任务奖励

## 注意事项

- Cookie 会定期过期，需要更新
- Anti-Token 每次运行都会自动生成，无需手动更新
- 脚本会自动下载 SDK 文件（~100KB），首次运行较慢
- 建议设置两个定时任务（早晚各一次）以获得最多水滴

## 常见问题

**Q: 脚本运行失败，提示网络错误？**
A: 检查网络连接和代理设置。确保 `NO_PROXY` 环境变量已设置。

**Q: Cookie 过期了怎么办？**
A: 重新打开拼多多果园页面，复制新的 Cookie 字符串，更新环境变量。

**Q: 为什么任务列表为空？**
A: 可能是 Anti-Token 生成失败或 Cookie 过期。检查脚本日志。

## 更新日志

### v1.0 (2026-04-01)
- 初始版本
- 支持签到、浇水、任务领取
- 自动生成 Anti-Token

## 免责声明

本脚本仅供学习交流使用，不得用于商业目的。使用本脚本产生的一切后果由用户自行承担。

## 许可证

MIT
