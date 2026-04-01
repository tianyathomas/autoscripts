#!/usr/bin/env node
/**
 * 拼多多果园自动化脚本 - 青龙面板版
 * 环境变量：PDD_COOKIE
 * 用法：node pdd.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const util = require('util');

// ===== 配置 =====
const COOKIE_STR = process.env.PDD_COOKIE || '';
const PDDUID = process.env.PDD_UID || '3902581294';

// 真实 UA（Chrome 146 on Windows 10）
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36';

function log(msg) {
    const time = new Date().toLocaleTimeString('zh-CN');
    console.log(`[${time}] ${msg}`);
}

log('=== PDD Orchard Auto ===');
log(`UID: ${PDDUID}`);

// ===== 生成 Anti-Token =====
async function generateAntiToken() {
    try {
        log('[AntiToken] Generating...');
        
        // 设置浏览器环境
        const windowObj = {
            webpackChunkmobile_cartoon_activity: [],
            navigator: {
                userAgent: USER_AGENT,
                platform: 'Win32', language: 'zh-CN', languages: ['zh-CN', 'zh'],
                cookieEnabled: true, hardwareConcurrency: 8, maxTouchPoints: 0,
                vendor: 'Google Inc.', appVersion: '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                appName: 'Netscape', onLine: true,
                plugins: { length: 3 }, mimeTypes: { length: 2 },
                connection: null, getBattery: null, sendBeacon: () => true,
            },
            document: {
                cookie: `pdd_user_id=${PDDUID}`,
                referrer: '', title: 'test', domain: 'mobile.pinduoduo.com',
                readyState: 'complete', visibilityState: 'visible', hidden: false,
                createElement: (tag) => ({ style: {}, setAttribute: ()=>{}, getAttribute: ()=>null, addEventListener: ()=>{}, removeEventListener: ()=>{}, appendChild: ()=>{}, removeChild: ()=>{}, getContext: ()=>null, tagName: tag.toUpperCase() }),
                getElementById: ()=>null, querySelector: ()=>null, querySelectorAll: ()=>[],
                getElementsByTagName: ()=>[], addEventListener: ()=>{}, removeEventListener: ()=>{},
                createEvent: ()=>({ initEvent: ()=>{} }),
                body: { appendChild: ()=>{}, removeChild: ()=>{}, style: {}, scrollTop: 0, scrollLeft: 0, clientWidth: 1920, clientHeight: 1080, offsetWidth: 1920, offsetHeight: 1080 },
                head: { appendChild: ()=>{}, removeChild: ()=>{} },
                documentElement: { scrollTop: 0, scrollLeft: 0, clientWidth: 1920, clientHeight: 1080, offsetWidth: 1920, offsetHeight: 1080, style: {} },
            },
            location: { href: 'https://mobile.pinduoduo.com/garden_index_lz_0.html', hostname: 'mobile.pinduoduo.com', protocol: 'https:', pathname: '/garden_index_lz_0.html', search: '', hash: '', host: 'mobile.pinduoduo.com', origin: 'https://mobile.pinduoduo.com' },
            screen: { width: 1920, height: 1080, colorDepth: 24, availWidth: 1920, availHeight: 1040, pixelDepth: 24 },
            performance: { now: () => Date.now() - 1000, timing: { navigationStart: Date.now() - 3000, domContentLoadedEventEnd: Date.now() - 1000, loadEventEnd: Date.now() - 500, responseEnd: Date.now() - 2000 }, getEntriesByType: ()=>[], mark: ()=>{}, measure: ()=>{} },
            history: { length: 3, state: null, pushState: ()=>{}, replaceState: ()=>{} },
            innerWidth: 1920, innerHeight: 1080, outerWidth: 1920, outerHeight: 1080,
            devicePixelRatio: 1, pageXOffset: 0, pageYOffset: 0, scrollX: 0, scrollY: 0,
            ontouchstart: undefined, ontouchend: undefined, ontouchmove: undefined,
            localStorage: { getItem: ()=>null, setItem: ()=>{}, removeItem: ()=>{}, clear: ()=>{}, length: 0, key: ()=>null },
            sessionStorage: { getItem: ()=>null, setItem: ()=>{}, removeItem: ()=>{}, clear: ()=>{}, length: 0, key: ()=>null },
            crypto: { getRandomValues: (arr) => { for(let i=0;i<arr.length;i++) arr[i]=Math.floor(Math.random()*256); return arr; }, subtle: null },
            addEventListener: ()=>{}, removeEventListener: ()=>{}, dispatchEvent: ()=>true,
            setTimeout, clearTimeout, setInterval, clearInterval,
            requestAnimationFrame: (cb) => setTimeout(cb, 16), cancelAnimationFrame: clearTimeout,
            fetch: () => Promise.resolve({ ok: true, json: ()=>Promise.resolve({}), text: ()=>Promise.resolve('') }),
            XMLHttpRequest: function() { this.open=()=>{}; this.send=()=>{}; this.setRequestHeader=()=>{}; this.readyState=4; this.status=200; this.responseText='{}'; this.onreadystatechange=null; this.onload=null; this.onerror=null; },
            Promise, JSON, Math, Date, Array, Object, String, Number, Boolean, RegExp, Error,
            Uint8Array, Uint16Array, Int32Array, ArrayBuffer, DataView, Function,
            Map, Set, WeakMap, WeakSet, Symbol,
            Element: function Element() {}, HTMLElement: function HTMLElement() {}, Node: function Node() {},
            Event: function Event(type) { this.type=type; this.preventDefault=()=>{}; this.stopPropagation=()=>{}; },
            EventTarget: function EventTarget() {}, HTMLCanvasElement: function HTMLCanvasElement() {},
            TextEncoder: util.TextEncoder, TextDecoder: util.TextDecoder,
            encodeURIComponent, decodeURIComponent, encodeURI, decodeURI,
            parseInt, parseFloat, isNaN, isFinite, console,
            MutationObserver: function() { this.observe=()=>{}; this.disconnect=()=>{}; this.takeRecords=()=>[]; },
            IntersectionObserver: function() { this.observe=()=>{}; this.disconnect=()=>{}; },
            URL: typeof URL !== 'undefined' ? URL : function(u) { this.href=u; this.toString=()=>u; },
            Blob: typeof Blob !== 'undefined' ? Blob : function() {},
            FormData: function() { this.append=()=>{}; },
            DeviceOrientationEvent: undefined, DeviceMotionEvent: undefined, TouchEvent: undefined,
            get self() { return windowObj; }, get window() { return windowObj; },
            get top() { return windowObj; }, get parent() { return windowObj; },
        };
        
        global.self = windowObj;
        global.window = windowObj;
        global.document = windowObj.document;
        global.location = windowObj.location;
        global.screen = windowObj.screen;
        global.performance = windowObj.performance;
        global.localStorage = windowObj.localStorage;
        global.sessionStorage = windowObj.sessionStorage;
        global.fetch = windowObj.fetch;
        global.XMLHttpRequest = windowObj.XMLHttpRequest;
        global.MutationObserver = windowObj.MutationObserver;
        global.requestAnimationFrame = windowObj.requestAnimationFrame;
        global.cancelAnimationFrame = windowObj.cancelAnimationFrame;
        global.TextEncoder = windowObj.TextEncoder;
        global.TextDecoder = windowObj.TextDecoder;
        global.Element = windowObj.Element;
        global.HTMLElement = windowObj.HTMLElement;
        global.Node = windowObj.Node;
        global.Event = windowObj.Event;
        global.EventTarget = windowObj.EventTarget;
        global.HTMLCanvasElement = windowObj.HTMLCanvasElement;
        
        // 下载 SDK
        log('[SDK] Downloading...');
        const https = require('https');
        const sdkUrl = 'https://static.pddpic.com/assets/js/risk_control_anti_dac600d707bbff03e560.js';
        
        const sdkCode = await new Promise((resolve, reject) => {
            https.get(sdkUrl, { rejectUnauthorized: false, timeout: 30000 }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    log(`[SDK] Downloaded ${data.length} bytes`);
                    resolve(data);
                });
            }).on('error', reject);
        });
        
        // 执行 SDK
        eval(sdkCode);
        
        const chunks = windowObj.webpackChunkmobile_cartoon_activity;
        if (!chunks || chunks.length === 0) {
            throw new Error('SDK chunks not loaded');
        }
        
        const [, modules] = chunks[0];
        
        // webpack require
        const moduleCache = {};
        function webpackRequire(id) {
            if (moduleCache[id]) return moduleCache[id].exports;
            const mod = { i: id, l: false, exports: {} };
            moduleCache[id] = mod;
            if (modules[id]) { modules[id].call(mod.exports, mod, mod.exports, webpackRequire); mod.l = true; }
            return mod.exports;
        }
        webpackRequire.r = (e) => { if(typeof Symbol!=='undefined'&&Symbol.toStringTag) Object.defineProperty(e,Symbol.toStringTag,{value:'Module'}); Object.defineProperty(e,'__esModule',{value:true}); };
        webpackRequire.d = (e,n,g) => { if(!Object.prototype.hasOwnProperty.call(e,n)) Object.defineProperty(e,n,{enumerable:true,get:g}); };
        webpackRequire.o = (o,p) => Object.prototype.hasOwnProperty.call(o,p);
        webpackRequire.n = (m) => { const g = m&&m.__esModule ? ()=>m.default : ()=>m; webpackRequire.d(g,'a',g); return g; };
        webpackRequire.p = '';
        
        const sdk = webpackRequire(96636);
        const SDKClass = sdk.default;
        const instance = new SDKClass({ serverTime: Date.now(), _2827c887a48a351a: false });
        
        const token = await instance.messagePackSync({
            touchEventData: true, clickEventData: true, focusblurEventData: true,
            changeEventData: true, locationInfo: true, referrer: true,
            browserSize: true, browserInfo: true, token: true, fingerprint: true
        });
        
        log(`[AntiToken] Generated: ${token.substring(0, 40)}...`);
        return token;
    } catch(e) {
        log(`[AntiToken] Error: ${e.message}`);
        return null;
    }
}

// ===== 主函数 =====
async function main() {
    try {
        // 生成 Anti-Token
        const antiToken = await generateAntiToken();
        
        if (!antiToken) {
            log('Failed to generate Anti-Token');
            process.exit(1);
        }
        
        // 生成 Python 脚本并执行
        const pythonScript = `
import requests
import json
import os
import time
from datetime import datetime

os.environ['NO_PROXY'] = '*'

COOKIE_STR = '''${COOKIE_STR}'''
PDDUID = '${PDDUID}'
ANTI_TOKEN = '''${antiToken}'''
USER_AGENT = '''${USER_AGENT}'''

COOKIE = {}
for item in COOKIE_STR.split('; '):
    if '=' in item:
        k, v = item.split('=', 1)
        COOKIE[k] = v

TUBETOKEN = COOKIE.get('tubetoken', '')

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

def make_headers(anti_token=None):
    h = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://mobile.pinduoduo.com',
        'Referer': 'https://mobile.pinduoduo.com/garden_index_lz_0.html',
    }
    if anti_token:
        h['Anti-Token'] = anti_token
    return h

def get_water():
    url = f'https://mobile.pinduoduo.com/proxy/api/api/manor-gateway/manor/query/user/water?pdduid={PDDUID}&is_back=1'
    try:
        resp = requests.post(url, cookies=COOKIE, headers=make_headers(), json={}, timeout=15)
        return resp.json().get('water_amount', 0)
    except:
        return 0

def check_in():
    log('[Sign] Checking in...')
    url = f'https://mobile.pinduoduo.com/proxy/api/api/manor/common/apply/activity?pdduid={PDDUID}&is_back=1'
    data = {"tubetoken": TUBETOKEN, "fun_pl": 2}
    try:
        resp = requests.post(url, cookies=COOKIE, headers=make_headers(), json=data, timeout=15)
        result = resp.json()
        if result.get('success'):
            log(f'[Sign] Success! +{result.get("water_amount", 0)} water')
            return True
        log('[Sign] Already checked in today')
        return False
    except Exception as e:
        log(f'[Sign] Error: {e}')
        return False

def water_tree(max_times=50):
    water = get_water()
    log(f'[Water] Current: {water}')
    if water < 10:
        log('[Water] Not enough water')
        return 0
    
    url = f'https://mobile.pinduoduo.com/proxy/api/api/manor/water/cost?pdduid={PDDUID}&is_back=1'
    count = min(max_times, water // 10)
    watered = 0
    
    for i in range(count):
        try:
            resp = requests.post(url, cookies=COOKIE, headers=make_headers(), json={}, timeout=15)
            result = resp.json()
            if result.get('success'):
                left = result.get('water', 0)
                watered += 1
                if i % 10 == 0:
                    log(f'[Water] {watered}/{count}, left: {left}')
                if left < 10:
                    break
                time.sleep(0.2)
            else:
                break
        except:
            break
    
    final = get_water()
    log(f'[Water] Done! Watered {watered} times, final: {final}')
    return watered

def get_mission_list():
    log('[Mission] Fetching...')
    url = f'https://mobile.pinduoduo.com/proxy/api/api/manor/mission/list?pdduid={PDDUID}&is_back=1'
    data = {
        "activity_id_list": [201036],
        "mission_types": [38160, 38242, 38090, 38451, 37859, 38428],
        "request_params": {
            "act201036EntryInfo": {
                "4": {"needRefresh": True},
                "5": {"needRefresh": True},
                "6": {"needRefresh": True}
            }
        },
        "lower_end_device": False,
        "tubetoken": TUBETOKEN,
        "fun_pl": 2
    }
    try:
        resp = requests.post(url, cookies=COOKIE, headers=make_headers(ANTI_TOKEN), json=data, timeout=15)
        result = resp.json()
        
        if 'mission_list' in result:
            missions = result['mission_list']
            tasks = []
            for key, items in missions.items():
                if isinstance(items, list):
                    for m in items:
                        tasks.append({
                            'id': m.get('mission_id'),
                            'type': m.get('mission_type'),
                            'status': m.get('status'),
                            'reward': m.get('reward', 0),
                            'desc': m.get('mission_desc', '')[:20]
                        })
            
            can_claim = [t for t in tasks if t['status'] == 250]
            log(f'[Mission] Total: {len(tasks)}, can claim: {len(can_claim)}')
            for t in can_claim:
                log(f'  - {t["id"]}: reward={t["reward"]}, {t["desc"]}')
            return tasks
        else:
            log(f'[Mission] Error: {result.get("error_code")} - {result.get("error_msg", "")}')
            return []
    except Exception as e:
        log(f'[Mission] Error: {e}')
        return []

def claim_mission(mission_id):
    url = f'https://mobile.pinduoduo.com/proxy/api/api/manor/mission/draw?pdduid={PDDUID}&is_back=1'
    data = {"mission_id": mission_id, "tubetoken": TUBETOKEN, "fun_pl": 2}
    try:
        resp = requests.post(url, cookies=COOKIE, headers=make_headers(ANTI_TOKEN), json=data, timeout=15)
        result = resp.json()
        if result.get('success'):
            log(f'[Mission] Claimed {mission_id}: +{result.get("water", 0)} water')
            return True
        else:
            log(f'[Mission] Claim {mission_id} failed: {result.get("error_code")}')
            return False
    except Exception as e:
        log(f'[Mission] Error: {e}')
        return False

# 主流程
water = get_water()
log(f'Water: {water}')

check_in()
time.sleep(0.5)

if water >= 10:
    water_tree(min(50, water // 10))

tasks = get_mission_list()
can_claim = [t for t in tasks if t['status'] == 250]
if can_claim:
    log(f'\\n[Mission] Claiming {len(can_claim)} tasks...')
    for t in can_claim:
        claim_mission(t['id'])
        time.sleep(0.3)

log(f'\\nFinal water: {get_water()}')
log('Done!')
`;
        
        // 写入临时 Python 脚本
        const tmpPy = process.env.TEMP ? `${process.env.TEMP}\\pdd_run.py` : 'pdd_run.py';
        fs.writeFileSync(tmpPy, pythonScript);
        
        // 执行 Python 脚本
        log('[Python] Running...');
        execSync(`python ${tmpPy}`, { stdio: 'inherit' });
        
        // 清理
        try { fs.unlinkSync(tmpPy); } catch(e) {}
        
    } catch(e) {
        log(`Fatal error: ${e.message}`);
        process.exit(1);
    }
}

main().then(() => process.exit(0)).catch(e => {
    log(`Error: ${e.message}`);
    process.exit(1);
});
