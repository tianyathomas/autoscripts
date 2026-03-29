# WSKEY 转换脚本

京东 WSKEY 转换为 JD Cookie 的青龙面板脚本。

## 功能

- ✅ WSKEY 转 JD Cookie
- ✅ 自动更新 JD_COOKIE
- ✅ 支持多账号
- ✅ 账号有效性检查
- ✅ 失效账号自动禁用（可选）

## 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `JD_WSCK` | 京东 WSKEY，格式：`pin=xxx:wskey=xxx;`，多个用 `&` 分隔 | 是 |
| `QL_PORT` | 青龙面板端口，默认 5700 | 否 |
| `WSKEY_SLEEP` | 重试间隔秒数，默认 10 | 否 |
| `WSKEY_TRY_COUNT` | 重试次数，默认 1 | 否 |
| `WSKEY_UPDATE_HOUR` | 更新间隔小时 | 否 |
| `WSKEY_AUTO_DISABLE` | 失效自动禁用 | 否 |

## 获取 WSKEY

WSKEY 格式：`pin=xxx:wskey=xxx;`

获取方式：
1. 京东 APP → 我的 → 右上角设置 → 账号与安全 → 了解更多安全级别
2. 或使用抓包工具获取

## 青龙面板配置

### 1. 添加环境变量

- 名称：`JD_WSCK`
- 值：`pin=xxx:wskey=xxx;` 格式

### 2. 创建定时任务

- 命令：`python3 /ql/scripts/wskey/wskey.py`
- 
## 注意事项

- WSKEY 有时效性，需定期转换
- 建议设置定时任务自动运行
- 转换失败会自动推送通知
