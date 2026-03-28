# 自动签到脚本合集

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

青龙面板自动签到脚本合集，支持多平台自动签到和 Cookie 保活。

## 📁 脚本列表

### 爱奇艺 (iqiyi)

| 文件 | 说明 | Cron |
|------|------|------|
| `iqiyi_ql.js` | 青龙面板签到脚本 | `0 8 * * *` |
| `iqiyi_keepalive.js` | Cookie 保活脚本 | `0 6,18 * * *` |

#### ✨ 功能特性

- 🎯 **自动签到** - VIP 等级/成长值查询、每日抽奖
- 🎁 **抽奖活动** - 每天摇一摇、白金抽奖、普通抽奖
- ⭐ **VIP 特权** - V7 免费升级星钻
- 🔄 **自动保活** - 延长 Cookie 有效期
- ⚠️ **过期提醒** - 提前 7 天警告
- 👥 **多账号支持** - 支持多账号同时签到

## 🚀 快速开始

### 青龙面板使用

#### 1. 添加脚本

将 `iqiyi_ql.js` 上传到青龙面板脚本目录

#### 2. 配置环境变量

**变量名**: `IQIYI_COOKIE`

**Cookie 格式**:
```
P00001=你的token; P00002=你的用户信息; P00003=你的用户ID; __dfp=设备指纹; QC005=设备ID;
```

#### 3. 设置定时任务

| 脚本 | Cron | 说明 |
|------|------|------|
| `iqiyi_ql.js` | `0 8 * * *` | 每天 8:00 签到 |
| `iqiyi_keepalive.js` | `0 6,18 * * *` | 每天保活 |

### 本地使用

```bash
# 设置环境变量
export IQIYI_COOKIE="P00001=xxx; P00002=xxx; P00003=xxx;"

# 运行签到
node iqiyi_ql.js

# 运行保活
node iqiyi_keepalive.js
```

## 🍪 获取 Cookie

1. 打开 [爱奇艺官网](https://www.iqiyi.com) 并登录
2. 按 `F12` 打开开发者工具
3. **Application** → **Cookies** → `https://www.iqiyi.com`
4. 复制以下字段:
   - `P00001` ✅ 必需
   - `P00002` ✅ 必需
   - `P00003` ✅ 必需
   - `__dfp` (可选)
   - `QC005` (可选)

## 👥 多账号配置

### 方式一：换行分隔

```
P00001=账号1; P00002=账号1; P00003=账号1;
P00001=账号2; P00002=账号2; P00003=账号2;
```

### 方式二：多变量名

```
IQIYI_COOKIE_1=P00001=账号1; ...
IQIYI_COOKIE_2=P00001=账号2; ...## 📊 运行示例
```



## ⚠️ 注意事项

1. **Cookie 有效期** - 约 30-90 天，过期需重新获取
2. **隐私安全** - Cookie 包含敏感信息，请勿泄露
3. **活动时效** - 部分抽奖活动可能已下线

## 📄 License

[MIT License](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

⭐ 如果觉得有用，请给个 Star！
