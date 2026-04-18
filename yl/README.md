# 活力伊利小程序签到

## 简介

基于青龙面板的活力伊利小程序自动签到脚本，每日自动签到获取积分。

**已内联 Env 类，无需安装 `../tools/env` 外部依赖，放哪都能跑。**

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `hlyl` | 是 | access-token 值，多账户用 `#` 或换行分隔 |

### 获取 access-token

1. 打开微信 → 进入「活力伊利」小程序
2. 抓包工具（如 HttpCanary、Stream、Charles）抓取 `https://msmarket.msx.digitalyili.com/` 的请求
3. 从请求头中复制 `access-token` 的值

## 定时任务

建议 cron 表达式：`30 8 * * *`（每天早上 8:30 执行）

## 依赖

- `axios`（青龙面板依赖管理中添加）

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Cannot find module 'axios'` | 缺少 axios 依赖 | 在青龙依赖管理中添加 `axios` |
| 签到返回 403 | 被腾讯 WAF 拦截 | 需在移动端环境运行，电脑端 IP 可能被拦截 |
| token 无效 / 过期 | access-token 有有效期 | 重新抓包获取新 token |
