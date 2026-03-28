/**
 * 爱奇艺自动签到脚本 (Node.js 版本)
 * 使用环境变量配置 Cookie
 * 
 * 环境变量格式：
 * IQIYI_COOKIE=P00001=xxx; P00002=xxx; P00003=xxx; __dfp=xxx; QC005=xxx;
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');
const { unescape } = require('querystring');

// ============ 配置区域 ============

/**
 * Cookie 环境变量名称
 */
const ENV_COOKIE_NAME = 'IQIYI_COOKIE';

/**
 * 请求超时时间 (毫秒)
 */
const REQUEST_TIMEOUT = 10000;

/**
 * 请求间隔时间 (毫秒)
 */
const REQUEST_DELAY = 1000;

// ============ 工具函数 ============

/**
 * 延迟函数
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * 解析 Cookie 字符串
 */
function parseCookie(cookie) {
    const extract = (name) => {
        const regex = new RegExp(`${name}=([^;]+)`, 'i');
        const match = cookie.match(regex);
        return match ? match[1] : '';
    };

    const p00001 = extract('P00001');
    const p00002 = extract('P00002');
    const p00003 = extract('P00003');
    let __dfp = extract('__dfp');
    __dfp = __dfp ? __dfp.split('@')[0] : '';
    const qyid = extract('QC005');

    return { p00001, p00002, p00003, __dfp, qyid };
}

/**
 * 通用请求函数
 */
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
            headers: options.headers || {},
            timeout: REQUEST_TIMEOUT
        };

        const req = lib.request(reqOptions, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    resolve({ raw: data, error: 'Invalid JSON' });
                }
            });
        });

        req.on('error', reject);
        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        if (options.body) {
            req.write(options.body);
        }
        req.end();
    });
}

/**
 * 生成 UUID
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * URL 解码 (中文支持)
 */
function urlDecode(str) {
    try {
        return decodeURIComponent(str.replace(/\+/g, ' '));
    } catch (e) {
        return str;
    }
}

// ============ 爱奇艺 API 类 ============

class IQIYI {
    constructor(cookie) {
        this.cookie = cookie;
        const { p00001, p00002, p00003, __dfp, qyid } = parseCookie(cookie);
        this.p00001 = p00001;
        this.p00002 = p00002;
        this.p00003 = p00003;
        this.__dfp = __dfp;
        this.qyid = qyid;
    }

    /**
     * 获取账号信息
     */
    async getUserInfo() {
        await sleep(REQUEST_DELAY);
        const url = `http://serv.vip.iqiyi.com/vipgrowth/query.action?P00001=${this.p00001}`;
        try {
            const res = await request(url);
            if (res.code === 'A00000') {
                const data = res.data || {};
                return [
                    { name: 'VIP 等级', value: data.level || 0 },
                    { name: '当前成长', value: data.growthvalue || 0 },
                    { name: '今日成长', value: data.todayGrowthValue || 0 },
                    { name: '升级还需', value: data.distance || 0 },
                    { name: 'VIP 到期', value: data.deadline || '非 VIP 用户' }
                ];
            }
            return [{ name: '账号信息', value: res.msg || '查询失败' }];
        } catch (e) {
            return [{ name: '账号信息', value: `请求失败: ${e.message}` }];
        }
    }

    /**
     * 每天摇一摇抽奖
     */
    async lottery(awardList = []) {
        const params = new URLSearchParams({
            P00001: this.p00001,
            deviceID: generateUUID(),
            version: '15.3.0',
            platform: generateUUID().substring(0, 16),
            lotteryType: '0',
            actCode: '0k9GkUcjqqj4tne8',
            extendParams: JSON.stringify({
                appIds: 'iqiyi_pt_vip_iphone_video_autorenew_12m_348yuan_v2',
                supportSk2Identity: true,
                testMode: '0',
                iosSystemVersion: '17.4',
                bundleId: 'com.qiyi.iphone'
            })
        });

        const url = `https://act.vip.iqiyi.com/shake-api/lottery?${params}`;

        try {
            const res = await request(url);
            if (res.code === 'A00000') {
                const award = res.data?.title;
                if (award) awardList.push(award);
                await sleep(REQUEST_DELAY);
                return this.lottery(awardList);
            } else if (res.msg === '抽奖次数用完') {
                return [{
                    name: '每天摇一摇',
                    value: awardList.length > 0 ? awardList.join('、') : '抽奖次数用完'
                }];
            }
            return [{ name: '每天摇一摇', value: res.msg || '未知错误' }];
        } catch (e) {
            return [{ name: '每天摇一摇', value: `请求失败: ${e.message}` }];
        }
    }

    /**
     * 查询/执行抽奖 (旧版)
     */
    async draw(drawType = 0) {
        const params = new URLSearchParams({
            lottery_chance: '1',
            app_k: 'b398b8ccbaeacca840073a7ee9b7e7e6',
            app_v: '11.6.5',
            platform_id: '10',
            dev_os: '8.0.0',
            dev_ua: 'FRD-AL10',
            net_sts: '1',
            qyid: this.qyid || '2655b332a116d2247fac3dd66a5285011102',
            psp_uid: this.p00003,
            psp_cki: this.p00001,
            psp_status: '3',
            secure_v: '1',
            secure_p: 'GPhone',
            req_sn: Date.now().toString()
        });

        if (drawType === 1) {
            params.delete('lottery_chance');
        }

        const url = `https://iface2.iqiyi.com/aggregate/3.0/lottery_activity?${params}`;

        try {
            const res = await request(url);
            if (!res.code) {
                return {
                    status: true,
                    msg: res.awardName || '',
                    chance: parseInt(res.daysurpluschance || '0', 10)
                };
            }
            return {
                status: false,
                msg: res.kv?.msg || res.errorReason || '未知错误',
                chance: 0
            };
        } catch (e) {
            return { status: false, msg: `请求失败: ${e.message}`, chance: 0 };
        }
    }

    /**
     * V7 免费升级星钻
     */
    async levelRight() {
        const url = 'https://act.vip.iqiyi.com/level-right/receive';
        const body = `code=k8sj74234c683f&P00001=${this.p00001}`;
        
        try {
            const res = await request(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': Buffer.byteLength(body)
                },
                body
            });
            return [{ name: 'V7 免费升级星钻', value: res.msg || '完成' }];
        } catch (e) {
            return [{ name: 'V7 免费升级星钻', value: `请求失败: ${e.message}` }];
        }
    }

    /**
     * 白金抽奖 - 获取次数
     */
    async giveTimes() {
        const timesCodes = ['browseWeb', 'browseWeb', 'bookingMovie'];
        const url = 'https://pcell.iqiyi.com/lotto/giveTimes';
        
        for (const timesCode of timesCodes) {
            const params = new URLSearchParams({
                actCode: 'bcf9d354bc9f677c',
                timesCode,
                P00001: this.p00001
            });
            try {
                await request(`${url}?${params}`);
            } catch (e) {
                // 忽略错误
            }
        }
    }

    /**
     * 白金抽奖
     */
    async lottoLottery() {
        await this.giveTimes();
        const gifts = [];
        const url = 'https://pcell.iqiyi.com/lotto/lottery';
        
        for (let i = 0; i < 5; i++) {
            const params = new URLSearchParams({
                actCode: 'bcf9d354bc9f677c',
                P00001: this.p00001
            });
            try {
                const res = await request(`${url}?${params}`);
                const giftName = res.data?.giftName || '';
                if (giftName && !giftName.includes('未中奖')) {
                    gifts.push(giftName);
                }
            } catch (e) {
                // 忽略错误
            }
        }

        return [{
            name: '白金抽奖',
            value: gifts.length > 0 ? gifts.join('、') : '未中奖'
        }];
    }

    /**
     * 执行签到主流程
     */
    async run() {
        console.log('==================================================');
        console.log('爱奇艺自动签到开始');
        console.log('==================================================');

        // 解析用户信息
        let userName = '未知';
        let nickname = '未知';

        try {
            const userInfo = JSON.parse(urlDecode(this.p00002));
            userName = userInfo.user_name || '未知';
            userName = userName.substring(0, 3) + '****' + userName.substring(7);
            nickname = userInfo.nickname || '未知';
        } catch (e) {
            console.log('解析用户信息失败，请检查 P00002 字段');
        }

        // 查询账号信息
        const userInfo1 = await this.getUserInfo();
        const isVip = userInfo1[4]?.value !== '非 VIP 用户';

        // 白金抽奖
        const lottoMsg = await this.lottoLottery();

        // V7 升级星钻
        let levelMsg;
        if (isVip) {
            levelMsg = await this.levelRight();
        } else {
            levelMsg = [{ name: 'V7 免费升级星钻', value: '非 VIP 用户' }];
        }

        // 查询抽奖次数
        const drawInfo = await this.draw(0);
        let drawMsg = '抽奖机会不足';

        if (drawInfo.chance > 0) {
            const awards = [];
            for (let i = 0; i < drawInfo.chance; i++) {
                const result = await this.draw(1);
                if (result.status && result.msg) {
                    awards.push(result.msg);
                }
                await sleep(500);
            }
            drawMsg = awards.length > 0 ? awards.join(';') : '未中奖';
        }

        // 摇一摇抽奖
        const lotteryMsg = await this.lottery();

        // 再次查询账号信息（显示今日成长）
        const userInfo2 = await this.getUserInfo();

        // 组装结果
        const results = [
            { name: '用户账号', value: userName },
            { name: '用户昵称', value: nickname },
            ...userInfo2,
            { name: '抽奖奖励', value: drawMsg },
            ...lotteryMsg,
            ...levelMsg,
            ...lottoMsg
        ];

        // 输出结果
        const output = results.map(item => `${item.name}: ${item.value}`).join('\n');
        console.log(output);
        console.log('==================================================');

        return results;
    }
}

// ============ 主程序入口 ============

async function main() {
    // 从环境变量读取 Cookie
    const cookie = process.env[ENV_COOKIE_NAME];

    if (!cookie) {
        console.error(`错误: 未设置环境变量 ${ENV_COOKIE_NAME}`);
        console.error('');
        console.error('请设置环境变量后运行:');
        console.error('');
        console.error('Windows CMD:');
        console.error(`  set ${ENV_COOKIE_NAME}=P00001=xxx; P00002=xxx; P00003=xxx; __dfp=xxx; QC005=xxx;`);
        console.error('');
        console.error('Windows PowerShell:');
        console.error(`  $env:${ENV_COOKIE_NAME}="P00001=xxx; P00002=xxx; P00003=xxx; __dfp=xxx; QC005=xxx;"`);
        console.error('');
        console.error('Linux/macOS:');
        console.error(`  export ${ENV_COOKIE_NAME}="P00001=xxx; P00002=xxx; P00003=xxx; __dfp=xxx; QC005=xxx;"`);
        console.error('');
        process.exit(1);
    }

    try {
        const iqiyi = new IQIYI(cookie);
        await iqiyi.run();
    } catch (e) {
        console.error('签到失败:', e.message);
        process.exit(1);
    }
}

// 导出模块
module.exports = { IQIYI, parseCookie };

// 直接运行时执行
if (require.main === module) {
    main();
}
