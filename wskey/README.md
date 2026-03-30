# WSKEY 转换脚本

> 京东 WSKEY 转换为 JD Cookie 的青龙面板脚本，支持自动更新、账号管理、失效检测与推送通知。

## 功能特性

- ✅ WSKEY 转 JD Cookie（全自动）
- ✅ 自动更新 JD_COOKIE（覆盖旧账号）
- ✅ 支持多账号并发处理
- ✅ 账号有效性检查（支持按时间间隔判断）
- ✅ 失效账号自动禁用 + 推送通知
- ✅ 青龙新版/旧版 auth 文件自动适配（`_id` / `id`）
- ✅ 支持多种青龙挂载方式的 auth 文件路径
- ✅ Debug 调试模式
- ✅ 云端版本检测（预留）

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `JD_WSCK` | 京东 WSKEY，格式：`pin=xxx:wskey=xxx;`，多个账号用 `&` 分隔 | **必填** |
| `QL_PORT` | 青龙面板端口 | `5700` |
| `WSKEY_SLEEP` | 账号转换间隔秒数（避免风控） | `10` |
| `WSKEY_TRY_COUNT` | 单账号转换失败重试次数 | `1` |
| `WSKEY_UPDATE_HOUR` | Cookie 有效期（小时），到期前 10 分钟自动更新 | `23` |
| `WSKEY_AUTO_DISABLE` | 转换失败时是否自动禁用账号 | `False`（需设为任意值启用） |
| `WSKEY_DISCHECK` | 跳过账号有效性检查 | `False`（需设为任意值启用） |
| `WSKEY_SEND` | 禁用推送通知 | `False`（需设为 `disable` 禁用） |
| `WSKEY_DEBUG` | 开启 Debug 日志模式 | `False`（需设为任意值启用） |

## 获取 WSKEY

WSKEY 格式：`pin=xxx:wskey=xxx;`

获取方式：
1. **京东 APP** → 我的 → 右上角设置 → 账号与安全 → 了解更多安全级别
2. 或使用抓包工具（青空月明 / Nemotron 等）获取

## 青龙面板配置

### 1. 添加环境变量

- 名称：`JD_WSCK`
- 值：`pin=xxxx:wskey=xxxx;`
- 多个账号用 `&` 拼接：
  ```
  pin=账号1:wskey=xxxx;&pin=账号2:wskey=xxxx;
  ```

### 2. 创建定时任务

```bash
python3 /ql/data/scripts/wskey/wskey.py
```

推荐定时：`0 9 * * *`（每天早上 9 点自动转换）

## 脚本信息

- 版本：`40904`
- 兼容：青龙面板（新版 + 旧版）
- 支持 auth 文件路径：
  - `/ql/config/auth.json`
  - `/ql/data/config/auth.json`
  - `/data/config/auth.json`

## 注意事项

- WSKEY 有时效性，请定期运行转换脚本
- 建议设置每日定时任务自动续期
- 转换失败会自动推送通知（需青龙已配置通知）
- 遇到风控建议增加 `WSKEY_SLEEP` 间隔时间
