/*
 * 爱奇艺自动签到脚本 (青龙面板版)
 *
 * 功能:
 * - VIP 等级/成长值查询
 * - 每天摇一摇抽奖
 * - 白金抽奖
 * - V7 免费升级星钻
 * - 普通抽奖活动
 *
 * 青龙面板配置:
 * 变量名: IQIYI_COOKIE
 * 变量值: P00001=xxx; P00002=xxx; P00003=xxx; __dfp=xxx; QC005=xxx;
 *
 * 多账号配置:
 * IQIYI_COOKIE 用换行符分隔多个 Cookie，或使用:
 * IQIYI_COOKIE_1, IQIYI_COOKIE_2, ...
 */
const cron = "0 8 * * *"
const name = "爱奇艺签到"

const https = require('https');
const http = require('http');
const { URL } = require('url');

// ============ 青龙面板兼容 ============

// 检测是否在青龙面板环境
const isQingLong = process.env.QL_DIR || process.env.QL_BRANCH;

// 简单的通知函数 (青龙面板会自动处理 notify)
async function sendNotify(title, message) {
    console.log(`\n========== ${title} ==========`);
    console.log(message);
    
    // 如果青龙面板有 notify 模块，尝试加载
    try {
        const notify = require('./sendNotify');
        await notify.sendNotify(title, message);
    } catch (e) {
        // 青龙面板会自动捕获控制台输出
    }
}

// ============ 配置 ============

const REQUEST_TIMEOUT = 10000;
const REQUEST_DELAY = 1000;
const ENV_COOKIE_NAME = 'IQIYI_COOKIE';

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

        if (options.body) req.write(options.body);
        req.end();
    });
}

const generateUUID = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
});

const urlDecode = (str) => {
    try { return decodeURIComponent(str.replace(/\+/g, ' ')); } 
    catch (e) { return str; }
};

// ============ 爱奇艺 API ============

class IQIYI {
    constructor(cookie, index = 1) {
        this.cookie = cookie;
        this.index = index;
        const { p00001, p00002, p00003, __dfp, qyid } = parseCookie(cookie);
        this.p00001 = p00001;
        this.p00002 = p00002;
        this.p00003 = p00003;
        this.__dfp = __dfp;
        this.qyid = qyid;
    }

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

        try {
            const res = await request(`https://act.vip.iqiyi.com/shake-api/lottery?${params}`);
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

        if (drawType === 1) params.delete('lottery_chance');

        try {
            const res = await request(`https://iface2.iqiyi.com/aggregate/3.0/lottery_activity?${params}`);
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

    async levelRight() {
        try {
            const res = await request('https://act.vip.iqiyi.com/level-right/receive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': Buffer.byteLength(`code=k8sj74234c683f&P00001=${this.p00001}`)
                },
                body: `code=k8sj74234c683f&P00001=${this.p00001}`
            });
            return [{ name: 'V7 免费升级星钻', value: res.msg || '完成' }];
        } catch (e) {
            return [{ name: 'V7 免费升级星钻', value: `请求失败: ${e.message}` }];
        }
    }

    async giveTimes() {
        for (const timesCode of ['browseWeb', 'browseWeb', 'bookingMovie']) {
            try {
                await request(`https://pcell.iqiyi.com/lotto/giveTimes?actCode=bcf9d354bc9f677c&timesCode=${timesCode}&P00001=${this.p00001}`);
            } catch (e) {}
        }
    }

    async lottoLottery() {
        await this.giveTimes();
        const gifts = [];
        for (let i = 0; i < 5; i++) {
            try {
                const res = await request(`https://pcell.iqiyi.com/lotto/lottery?actCode=bcf9d354bc9f677c&P00001=${this.p00001}`);
                const giftName = res.data?.giftName || '';
                if (giftName && !giftName.includes('未中奖')) gifts.push(giftName);
            } catch (e) {}
        }
        return [{ name: '白金抽奖', value: gifts.length > 0 ? gifts.join('、') : '未中奖' }];
    }

    async run() {
        console.log(`\n========== 开始签到 [账号 ${this.index}] ==========`);

        // 解析用户信息
        let userName = '未知', nickname = '未知';
        try {
            const userInfo = JSON.parse(urlDecode(this.p00002));
            userName = (userInfo.user_name || '未知').replace(/(.{3}).*(.{4})/, '$1****$2');
            nickname = userInfo.nickname || '未知';
        } catch (e) {
            console.log('⚠️ 解析用户信息失败');
        }

        // 查询账号信息
        const userInfo1 = await this.getUserInfo();
        const isVip = userInfo1[4]?.value !== '非 VIP 用户';

        // 白金抽奖
        const lottoMsg = await this.lottoLottery();

        // V7 升级星钻
        const levelMsg = isVip ? await this.levelRight() : [{ name: 'V7 免费升级星钻', value: '非 VIP 用户' }];

        // 查询抽奖次数并抽奖
        const drawInfo = await this.draw(0);
        let drawMsg = '抽奖机会不足';
        if (drawInfo.chance > 0) {
            const awards = [];
            for (let i = 0; i < drawInfo.chance; i++) {
                const result = await this.draw(1);
                if (result.status && result.msg) awards.push(result.msg);
                await sleep(500);
            }
            drawMsg = awards.length > 0 ? awards.join(';') : '未中奖';
        }

        // 摇一摇抽奖
        const lotteryMsg = await this.lottery();

        // 再次查询账号信息
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

        const output = results.map(item => `${item.name}: ${item.value}`).join('\n');
        console.log(output);

        return { userName, nickname, results, output };
    }
}

// ============ 获取 Cookie 列表 ============

function getCookies() {
    const cookies = [];
    
    // 方式1: IQIYI_COOKIE (多行分隔)
    if (process.env[ENV_COOKIE_NAME]) {
        const lines = process.env[ENV_COOKIE_NAME].split('\n').filter(line => line.trim());
        cookies.push(...lines);
    }
    
    // 方式2: IQIYI_COOKIE_1, IQIYI_COOKIE_2, ...
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
    console.log('爱奇艺自动签到脚本');
    console.log('==================================================');

    const cookies = getCookies();

    if (cookies.length === 0) {
        const errMsg = `未设置环境变量 ${ENV_COOKIE_NAME}\n\n配置方法:\n变量名: IQIYI_COOKIE\n变量值: P00001=xxx; P00002=xxx; P00003=xxx; __dfp=xxx; QC005=xxx;\n\n多账号: 使用换行分隔或 IQIYI_COOKIE_1, IQIYI_COOKIE_2, ...`;
        console.log(errMsg);
        await sendNotify('爱奇艺签到失败', errMsg);
        return;
    }

    const results = [];
    let successCount = 0;

    for (let i = 0; i < cookies.length; i++) {
        try {
            const iqiyi = new IQIYI(cookies[i], i + 1);
            const result = await iqiyi.run();
            results.push(result);
            successCount++;
        } catch (e) {
            console.log(`❌ 账号 ${i + 1} 签到失败: ${e.message}`);
            results.push({ error: e.message });
        }
    }

    // 汇总通知
    const summary = results.map((r, i) => {
        if (r.error) return `账号 ${i + 1}: 签到失败 (${r.error})`;
        return `账号 ${i + 1} (${r.nickname}): 签到成功`;
    }).join('\n');

    console.log('\n==================================================');
    console.log(`签到完成: ${successCount}/${cookies.length} 成功`);
    console.log('==================================================');

    await sendNotify(`爱奇艺签到 (${successCount}/${cookies.length})`, summary);
}

// 导出
module.exports = { IQIYI, getCookies };

// 运行
if (require.main === module) {
    main().catch(e => {
        console.error('脚本执行失败:', e);
        process.exit(1);
    });
}
