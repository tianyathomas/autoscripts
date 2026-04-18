# 活力伊利小程序签到

## 简介

基于青龙面板的活力伊利小程序自动签到脚本，每日自动签到获取积分。

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `hlyl` | 是 | access-token 值，多账户用 `#` 或换行分隔 |

### 获取 access-token

1. 打开微信 → 进入「活力伊利」小程序
2. 抓包工具抓取 `https://msmarket.msx.digitalyili.com/` 的请求
3. 从请求头中复制 `access-token` 的值

## 定时任务

建议 cron 表达式：`30 8 * * *`（每天早上 8:30 执行）

## ─── 青龙面板缺少 ../tools/env 模块处理 ───

### 问题现象

运行脚本时报错：

```
Error: Cannot find module '../tools/env'
```

这是因为脚本依赖青龙面板公共工具库 `Env` 类，但你的青龙环境中 `/ql/data/tools/env.js` 文件不存在。

### 解决方法一：手动创建最小版 env.js（推荐）

SSH 登录青龙面板容器，依次执行：

```bash
# 1. 创建 tools 目录
mkdir -p /ql/data/tools

# 2. 写入最小可用 env.js
cat > /ql/data/tools/env.js << 'EOF'
class Env {
  constructor(name) {
    this.name = name;
    this.userIdx = 0;
    this.userList = [];
  }

  checkEnv(ckName) {
    const envVal = process.env[ckName];
    if (!envVal) {
      console.log(`[WARN] 未找到环境变量 ${ckName}`);
      this.userList = [];
      return;
    }
    this.userList = envVal.includes("\n")
      ? envVal.split("\n").filter(Boolean)
      : envVal.split("#").filter(Boolean);
    console.log(`[${this.name}] 共找到 ${this.userList.length} 个账号`);
  }

  log(msg) {
    console.log(msg);
  }

  done() {
    console.log(`[${this.name}] 执行完毕`);
  }
}

module.exports = { Env };
EOF
```

然后重新运行脚本即可。

### 解决方法二：从公共库安装完整版 env.js

```bash
# 创建目录
mkdir -p /ql/data/tools

# 从常用青龙公共仓库下载完整版 env.js（带通知推送、调试等完整功能）
cd /ql/data/tools

# 方式 A：从 shufflewzc 仓库（需能访问 GitHub）
curl -fsSL https://raw.githubusercontent.com/shufflewzc/faker2/main/utils/env.js -o env.js

# 方式 B：如果无法访问 GitHub，使用镜像
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/shufflewzc/faker2/main/utils/env.js -o env.js
```

### 解决方法三：通过青龙面板 Web UI 操作

1. 打开青龙面板 → **脚本管理**
2. 新建文件，路径填写 `tools/env.js`
3. 将上面的最小版代码粘贴进去保存

### 验证是否修复

```bash
# 在青龙容器中执行
node -e "const { Env } = require('/ql/data/tools/env'); console.log('env.js 加载成功')"
```

如果输出 `env.js 加载成功`，说明模块已就绪。

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Cannot find module 'axios'` | 缺少 axios 依赖 | 在青龙依赖管理中添加 `axios` |
| 签到返回 403 | 被腾讯 WAF 拦截 | 需在移动端环境运行，电脑端 IP 可能被拦截 |
| token 无效 / 过期 | access-token 有有效期 | 重新抓包获取新 token |

## 文件结构

```
/ql/data/
├── scripts/
│   └── hlyl.js          ← 本签到脚本
├── tools/
│   └── env.js           ← 需要手动创建的公共模块
└── config/
    └── env.sh           ← 环境变量配置（hlyl=你的token）
```
