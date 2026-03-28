# Autoscripts 自动签到脚本合集

适用于青龙面板的各类签到脚本集合。

## 🚀 青龙面板拉库方法

### 方式一：订阅管理（推荐）

1. 青龙面板 → 订阅管理 → 新建订阅
2. 填写以下信息：
   - **名称**：`autoscripts`
   - **类型**：公开仓库
   - **链接**：`https://github.com/tianyathomas/autoscripts.git`
   - **分支**：`main`
   - **定时规则**：`0 0 * * *`（每天拉取一次）
3. 保存后点击运行，即可自动拉取所有脚本

### 方式二：手动添加仓库

在青龙面板 → 定时任务 → 添加任务：

```
ql repo https://github.com/tianyathomas/autoscripts.git
```

### 方式三：SSH 命令行

```bash
cd /ql/scripts
git clone https://github.com/tianyathomas/autoscripts.git
```

## 📦 脚本列表

| 脚本 | 说明 | 环境变量 |
|------|------|----------|
| [爱奇艺签到](iqiyi/iqiyi_checkin.py) | VIP成长值、抽奖、摇一摇 | `IQIYI_COOKIE` |
| [百度贴吧签到](tieba/tieba.py) | 自动签到所有关注的贴吧 | `TIEBA_COOKIE` |

## ⚙️ 环境变量配置

在青龙面板 → 环境变量 中添加对应变量：

### 爱奇艺签到

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `IQIYI_COOKIE` | 爱奇艺完整 Cookie | 浏览器登录爱奇艺后，F12 开发者工具 → Network → 任意请求 → Headers → Cookie |

### 百度贴吧签到

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `TIEBA_COOKIE` | 百度贴吧 BDUSS Cookie | 浏览器登录百度贴吧后，F12 开发者工具 → Application → Cookies → 找到 BDUSS 值 |

## 📝 使用说明

1. 拉取仓库后，脚本会自动出现在定时任务列表
2. 根据脚本需求配置对应的环境变量
3. 手动运行一次测试是否正常
4. 根据需要修改定时规则

## 📅 定时建议

| 脚本 | 建议时间 | Cron 表达式 |
|------|----------|-------------|
| 爱奇艺签到 | 每天凌晨 | `5 0 * * *` |
| 百度贴吧签到 | 每天早上 | `0 8 * * *` |

## 🤝 贡献

欢迎提交 Issue 或 PR 添加新的签到脚本。

## ⚠️ 免责声明

本仓库脚本仅供学习交流使用，请勿用于商业用途。使用本仓库脚本所产生的一切后果由使用者自行承担。

## 📜 License

MIT License
