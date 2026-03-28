/*
 * 爱奇艺 Cookie 自动保活脚本
 *
 * 功能:
 * - 定期访问爱奇艺 API 保持登录状态
 * - 延长 Cookie 有效期
 * - 发送过期提醒
 *
 * 青龙面板配置:
 * 变量名: IQIYI_COOKIE
 */
const cron = "0 6,18 * * *"
const name = "爱奇艺保活"

const https = require('https');
const http = require('http');
const { URL } = require('url');

// ============ 配置 ============

const REQUEST_TIMEOUT = 10000;
const ENV_COOKIE_NAME = 'IQIYI_COOKIE';

// Cookie 过期提醒阈值 (天)
const EXPIRE_WARNING_DAYS = 7;

// ============ 工具函数 ============

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function parseCookie(cookie) {
    const extract = (name) => {
        const regex = new RegExp(`${name}=([^;]+)`, 'i');
        const match = cookie.match(regex);
        return match ? match[1] : '';
    };

    return {
        p00001: extract('P00001'),
        p00002: extract('P00002'),
        p00003: extract('P00003'),
        p00004: extract('P00004'),
        p01010: extract('P01010'),
        __dfp: extract('__dfp').split('@')[0],
        qyid: extract('QC005')
    };
}

function request(urlString, options = {}) {
    return new Promise((resolve, reject) => {
        const url = new URL(urlString);
        const isHttps = url.protocol === 'https:';
        const lib = isHttps ? https : http;
        
        const reqOptions = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname + url.search,
            method: options.method || 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                ...options.headers
            },
            timeout: REQUEST_TIMEOUT
        };

        const req = lib.request(reqOptions, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(data) });
                } catch (e) {
                    resolve({ status: res.statusCode, raw: data });
                }
            });
        });

        req.on('error', reject);
        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        if (options.body) req.write(options.body);
        req.end();
    });
}

const urlDecode = (str) => {
    try { return decodeURIComponent(str.replace(/\+/g, ' ')); } 
    catch (e) { return str; }
};

// ============ 保活 API ============

class IQIYIKeepAlive {
    constructor(cookie, index = 1) {
        this.cookie = cookie;
        this.index = index;
        const parsed = parseCookie(cookie);
        Object.assign(this, parsed);
    }

    /**
     * 获取用户信息 (核心保活操作)
     */
    async getUserInfo() {
        const url = `http://serv.vip.iqiyi.com/vipgrowth/query.action?P00001=${this.p00001}`;
        try {
            const res = await request(url);
            if (res.data?.code === 'A00000') {
                return {
                    success: true,
                    level: res.data.data?.level || 0,
                    deadline: res.data.data?.deadline || '未知',
                    growthvalue: res.data.data?.growthvalue || 0
                };
            }
            return { success: false, error: res.data?.msg || '查询失败' };
        } catch (e) {
            return { success: false, error: e.message };
        }
    }

    /**
     * 访问首页 (保活)
     */
    async visitHomepage() {
        const url = 'https://www.iqiyi.com';
        try {
            const res = await request(url);
            return { success: res.status === 200 };
        } catch (e) {
            return { success: false, error: e.message };
        }
    }

    /**
     * 访问 VIP 页面 (保活)
     */
    async visitVipPage() {
        const url = `https://vip.iqiyi.com/member.html?P00001=${this.p00001}`;
        try {
            const res = await request(url);
            return { success: res.status === 200 };
        } catch (e) {
            return { success: false, error: e.message };
        }
    }

    /**
     * 检查 Cookie 是否即将过期
     */
    checkExpiration() {
        const warnings = [];
        
        // 检查 P01010 (会员到期时间戳)
        if (this.p01010) {
            const expireTimestamp = parseInt(this.p01010, 10) * 1000;
            const now = Date.now();
            const daysLeft = Math.ceil((expireTimestamp - now) / (1000 * 60 * 60 * 24));
            
            if (daysLeft <= EXPIRE_WARNING_DAYS) {
                warnings.push(`⚠️ VIP 将在 ${daysLeft} 天后到期 (${new Date(expireTimestamp).toLocaleDateString('zh-CN')})`);
            }
        }
        
        // 检查 P00004 (可能包含登录时间)
        if (this.p00004) {
            const match = this.p00004.match(/\.(\d+)\./);
            if (match) {
                const loginTimestamp = parseInt(match[1], 10) * 1000;
                const now = Date.now();
                const daysSinceLogin = Math.floor((now - loginTimestamp) / (1000 * 60 * 60 * 24));
                
                if (daysSinceLogin > 60) {
                    warnings.push(`⚠️ Cookie 已使用 ${daysSinceLogin} 天，建议更新`);
                }
            }
        }
        
        return warnings;
    }

    /**
     * 执行保活操作
     */
    async keepalive() {
        console.log(`\n========== 保活检查 [账号 ${this.index}] ==========`);

        // 解析用户信息
        let userName = '未知', nickname = '未知';
        try {
            const userInfo = JSON.parse(urlDecode(this.p00002));
            userName = (userInfo.user_name || '未知').replace(/(.{3}).*(.{4})/, '$1****$2');
            nickname = userInfo.nickname || '未知';
        } catch (e) {}

        console.log(`用户: ${nickname} (${userName})`);

        // 检查过期
        const warnings = this.checkExpiration();
        warnings.forEach(w => console.log(w));

        // 执行保活操作
        const results = [];

        // 1. 获取用户信息 (核心保活)
        console.log('📡 正在访问用户信息接口...');
        const userInfoResult = await this.getUserInfo();
        results.push({ action: '用户信息查询', ...userInfoResult });
        
        if (userInfoResult.success) {
            console.log(`✅ VIP 等级: ${userInfoResult.level}, 成长值: ${userInfoResult.growthvalue}`);
            console.log(`   VIP 到期: ${userInfoResult.deadline}`);
        } else {
            console.log(`❌ 用户信息查询失败: ${userInfoResult.error}`);
        }

        await sleep(500);

        // 2. 访问首页
        console.log('📡 正在访问爱奇艺首页...');
        const homeResult = await this.visitHomepage();
        results.push({ action: '首页访问', ...homeResult });
        console.log(homeResult.success ? '✅ 首页访问成功' : `❌ 首页访问失败: ${homeResult.error}`);

        await sleep(500);

        // 3. 访问 VIP 页面
        console.log('📡 正在访问 VIP 页面...');
        const vipResult = await this.visitVipPage();
        results.push({ action: 'VIP页面访问', ...vipResult });
        console.log(vipResult.success ? '✅ VIP 页面访问成功' : `❌ VIP 页面访问失败: ${vipResult.error}`);

        // 汇总
        const successCount = results.filter(r => r.success).length;
        console.log(`\n保活结果: ${successCount}/${results.length} 操作成功`);

        return {
            userName,
            nickname,
            warnings,
            results,
            success: successCount === results.length
        };
    }
}

// ============ 获取 Cookie 列表 ============

function getCookies() {
    const cookies = [];
    
    if (process.env[ENV_COOKIE_NAME]) {
        const lines = process.env[ENV_COOKIE_NAME].split('\n').filter(line => line.trim());
        cookies.push(...lines);
    }
    
    for (let i = 1; ; i++) {
        const cookie = process.env[`${ENV_COOKIE_NAME}_${i}`];
        if (!cookie) break;
        cookies.push(cookie);
    }
    
    return cookies;
}

// ============ 主程序 ============

async function main() {
    console.log('==================================================');
    console.log('爱奇艺 Cookie 自动保活');
    console.log(`时间: ${new Date().toLocaleString('zh-CN')}`);
    console.log('==================================================');

    const cookies = getCookies();

    if (cookies.length === 0) {
        console.log(`❌ 未设置环境变量 ${ENV_COOKIE_NAME}`);
        return;
    }

    let successCount = 0;
    const allWarnings = [];

    for (let i = 0; i < cookies.length; i++) {
        try {
            const keepalive = new IQIYIKeepAlive(cookies[i], i + 1);
            const result = await keepalive.keepalive();
            
            if (result.success) successCount++;
            if (result.warnings.length > 0) {
                allWarnings.push(...result.warnings.map(w => `[账号${i + 1}] ${w}`));
            }
        } catch (e) {
            console.log(`❌ 账号 ${i + 1} 保活失败: ${e.message}`);
        }
    }

    // 显示警告汇总
    if (allWarnings.length > 0) {
        console.log('\n⚠️ ============ 过期提醒 ============');
        allWarnings.forEach(w => console.log(w));
        console.log('====================================');
    }

    console.log('\n==================================================');
    console.log(`保活完成: ${successCount}/${cookies.length} 成功`);
    console.log('==================================================');
}

// 导出
module.exports = { IQIYIKeepAlive };

// 运行
if (require.main === module) {
    main().catch(e => {
        console.error('脚本执行失败:', e);
        process.exit(1);
    });
}
