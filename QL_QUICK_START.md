# 青龙面板一键拉取命令

## 📥 拉取命令

### 方式一：ql repo 命令（推荐）

在青龙面板 **定时任务** → **添加任务** 中添加：

```
ql repo https://github.com/tianyathomas/autoscripts.git "autoscripts" "" "iqiyi"
```

**参数说明：**
- 第1个参数：仓库地址
- 第2个参数：仓库名称
- 第3个参数：拉取白名单（留空拉取全部）
- 第4个参数：脚本目录（只拉取 iqiyi 文件夹）

---

### 方式二：Docker 内执行

```bash
docker exec -it qinglong ql repo https://github.com/tianyathomas/autoscripts.git
```

---

### 方式三：完整命令（添加定时拉取）

```bash
# 添加订阅任务
docker exec -it qinglong bash -c "echo '0 0 * * * ql repo https://github.com/tianyathomas/autoscripts.git' >> /ql/config/crontab.list"

# 重启青龙使配置生效
docker restart qinglong
```

---

## 🍪 配置 Cookie

拉取成功后添加环境变量：

```bash
# 在青龙面板 环境变量 中添加
IQIYI_COOKIE=P00001=你的token; P00002=你的用户信息; P00003=你的用户ID;
```

---

## ⏰ 定时任务说明

脚本会自动识别内置的 Cron 表达式：

| 脚本 | Cron | 说明 |
|------|------|------|
| `iqiyi_ql.js` | `0 8 * * *` | 每天 8:00 签到 |
| `iqiyi_keepalive.js` | `0 6,18 * * *` | 每天 6:00 和 18:00 保活 |

---

## 🧪 测试

```bash
# 手动运行签到
docker exec -it qinglong task iqiyi/iqiyi_ql.js now

# 手动运行保活
docker exec -it qinglong task iqiyi/iqiyi_keepalive.js now
```

---

## 🔗 仓库地址

```
https://github.com/tianyathomas/autoscripts.git
```
