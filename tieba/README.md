# 百度贴吧签到脚本

用于青龙面板的百度贴吧自动签到脚本。

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `TIEBA_COOKIE` | 百度贴吧 BDUSS Cookie |

## 获取 Cookie 方法

### 方法一：浏览器开发者工具（推荐）

1. 打开百度贴吧网站 https://tieba.baidu.com
2. 登录你的百度账号
3. 按 `F12` 打开开发者工具
4. 切换到 `Application`（应用）标签
5. 在左侧展开 `Cookies`，选择 `https://tieba.baidu.com`
6. 找到名为 `BDUSS` 的 Cookie
7. 复制其值（注意：是 value，不是 name）

### 方法二：浏览器开发者工具（Network）

1. 打开百度贴吧网站 https://tieba.baidu.com
2. 登录你的百度账号
3. 按 `F12` 打开开发者工具
4. 切换到 `Network`（网络）标签
5. 刷新页面，点击任意一个请求
6. 在请求Headers中找到 `Cookie` 项
7. 复制完整的 Cookie 字符串

### Cookie 格式

脚本支持两种 Cookie 格式：

**格式一：完整的 Cookie 字符串**
```
BDUSS=你的BDUSS值; other_cookie=value; ...
```

**格式二：纯 BDUSS 值**
```
你的BDUSS值
```

## 在青龙面板配置

1. 进入青龙面板 → 环境变量
2. 新建变量：
   - 名称：`TIEBA_COOKIE`
   - 值：粘贴你的 BDUSS Cookie
3. 保存

## 定时任务

建议添加定时任务，每天自动执行：

- Cron 表达式：`0 8 * * *`（每天早上 8 点）

## 运行测试

在青龙面板手动运行一次任务，查看日志是否正常。

## 注意事项

- BDUSS Cookie 有效期较长，但建议定期更新
- 同一个账号多个贴吧签到可能需要较长时间（每10个贴吧会休息几秒）
- 签到结果会在日志中详细显示
