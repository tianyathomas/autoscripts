# 百度网盘签到脚本

百度网盘自动签到脚本，支持青龙面板环境变量配置。

## 功能

- ✅ 每日签到（成长值）
- ✅ 每日答题（成长值）
- ✅ 会员等级查询

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `BD_COOKIE` | 百度系通用 Cookie（贴吧+网盘共用） |

## Cookie 获取

1. 电脑浏览器登录 [pan.baidu.com](https://pan.baidu.com)
2. 按 `F12` 打开开发者工具 → Network
3. 刷新页面 → 点击任意请求 → Headers → Cookie
4. 复制完整 Cookie 字符串

### 必要字段

只需保留以下三个字段即可：

```
BDUSS=xxx; STOKEN=xxx; BAIDUID=xxx
```

| 字段 | 作用 |
|------|------|
| `BDUSS` | 登录态令牌，核心认证凭证 |
| `STOKEN` | 安全令牌 |
| `BAIDUID` | 用户ID标识 |

## 青龙面板配置

### 1. 添加环境变量

- 名称：`BD_COOKIE`
- 值：你的百度 Cookie

### 2. 创建定时任务

```
命令：python3 /ql/scripts/baiduwp/baiduwp.py
```

建议定时：`0 9 * * *`（每天早上9点）

## 注意事项

- 贴吧和网盘签到可以共用同一个 `BD_COOKIE`
- Cookie 有时效性，失效后需重新获取
- 签到功能可能受限（非SVIP会员可能无法签到）
