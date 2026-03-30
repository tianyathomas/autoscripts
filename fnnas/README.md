# 飞牛NAS论坛签到脚本

适用于青龙面板的飞牛NAS论坛自动签到脚本。

## 功能特性

- 自动签到打卡
- 获取打卡动态（积分、连续天数等）
- 支持已签到状态检测

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `FNNAS_COOKIE` | ✅ | 飞牛NAS论坛完整 Cookie 字符串 |

## Cookie 获取方式

1. 浏览器打开 [飞牛NAS论坛](https://club.fnnas.com) 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 **Network** 标签
4. 刷新页面，点击任意一个请求
5. 在右侧 **Headers** 里找到 **Cookie** 字段
6. 复制完整的 cookie 字符串

## Cookie 必需字段

`FNNAS_COOKIE` 需包含以下关键字段：

| 字段名 | 说明 | 必需 |
|--------|------|------|
| `pvRK_2132_auth` | 认证凭证（最重要） | ✅ 必需 |
| `pvRK_2132_saltkey` | 加密盐值 | ✅ 必需 |
| `pvRK_2132_sid` | 会话ID | ✅ 必需 |
| `pvRK_2132_ulastactivity` | 最后活动时间 | 建议有 |
| `accessToken` | 访问令牌 | 建议有 |

### Cookie 示例

```
pvRK_2132_auth=xxx; pvRK_2132_saltkey=xxx; pvRK_2132_sid=xxx; pvRK_2132_ulastactivity=xxx; accessToken=xxx
```

> 💡 建议：直接复制浏览器中的完整 Cookie 字符串，脚本会自动使用

## 定时任务

脚本默认每天 6:30 执行，cron 表达式：`30 6 * * *`

可在青龙面板自行修改执行时间。

## 使用说明

1. 添加环境变量 `FNNAS_COOKIE`
2. 手动运行一次测试是否正常
3. 检查签到结果和打卡动态

## 注意事项

1. Cookie 有效期有限，过期后需重新获取
2. 签到需要先访问页面获取 `sign` 参数，脚本会自动处理
3. 如提示获取 sign 参数失败，请检查 cookie 是否有效

## 更新日志

- 2026-03-30: 初始版本
