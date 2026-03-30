# B站签到脚本

适用于青龙面板的B站自动签到脚本，支持直播签到、漫画签到、投币、观看视频、分享等任务。

## 功能特性

- 直播签到
- 漫画签到
- 自动投币（支持关注UP主视频或分区视频）
- 观看视频任务
- 分享视频任务
- 银瓜子兑换硬币（可选）
- 大会员权益领取

## 环境变量

| 变量名 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| `BILIBILI_COOKIE` | ✅ | B站完整 Cookie 字符串 | - |
| `BILIBILI_COIN_NUM` | ❌ | 每日投币数量 | `5` |
| `BILIBILI_COIN_TYPE` | ❌ | 投币类型：`1`=关注UP主视频，其他=分区视频 | `1` |
| `BILIBILI_SILVER2COIN` | ❌ | 是否银瓜子换硬币：`true`/`false` | `false` |

## Cookie 获取方式

1. 浏览器打开 [B站](https://www.bilibili.com) 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 **Network** 标签
4. 刷新页面，点击任意一个请求
5. 在右侧 **Headers** 里找到 **Cookie** 字段
6. 复制完整的 cookie 字符串

> ⚠️ 注意：cookie 字符串较长，确保复制完整，不要有换行

## Cookie 必需字段

`BILIBILI_COOKIE` 需包含以下关键字段才能正常运行：

| 字段名 | 说明 | 必需 |
|--------|------|------|
| `SESSDATA` | 登录凭证，最重要 | ✅ 必需 |
| `bili_jct` | CSRF Token，用于POST请求 | ✅ 必需 |
| `DedeUserID` | 用户ID | ✅ 必需 |
| `buvid3` | 设备标识 | 建议有 |
| `buvid4` | 设备标识 | 建议有 |

### 最小 Cookie 示例

```
SESSDATA=xxx; bili_jct=xxx; DedeUserID=xxx; buvid3=xxx; buvid4=xxx
```

### 完整 Cookie 示例

```
buvid3=xxx; buvid4=xxx; SESSDATA=xxx; bili_jct=xxx; DedeUserID=xxx; DedeUserID__ckMd5=xxx; sid=xxx; ...
```

> 💡 建议：直接复制浏览器中的完整 Cookie 字符串，脚本会自动解析所需字段

## 定时任务

脚本默认每天 6:00 执行，cron 表达式：`0 6 * * *`

可在青龙面板自行修改执行时间。

## 使用示例

### 青龙面板配置

1. 添加环境变量 `BILIBILI_COOKIE`，值为完整 cookie 字符串
2. 可选添加 `BILIBILI_COIN_NUM`、`BILIBILI_COIN_TYPE`、`BILIBILI_SILVER2COIN`
3. 手动运行一次测试是否正常

### 多账号支持

如需多账号，可添加多条环境变量记录，或使用分隔符（视青龙面板版本而定）。

## 注意事项

1. Cookie 有效期有限，过期后需重新获取
2. 投币数量受B站每日上限限制
3. 直播签到活动可能结束，届时会跳过
4. 建议不要设置过高的投币数量，避免触发风控

## 更新日志

- 2026-03-30: 初始版本，支持基础签到功能
