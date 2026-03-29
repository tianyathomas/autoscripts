"""
wskey转换脚本 - 青龙面板版
环境变量: JD_WSCK, QL_PORT
cron: 0 9 * * *
new Env('wskey转换');
"""
import base64
import hashlib
import hmac
import json
import logging
import os
import random
import re
import socket
import struct
import sys
import time
import uuid

WSKEY_MODE = 0
# 0 = Default / 1 = Debug!

if "WSKEY_DEBUG" in os.environ or WSKEY_MODE:
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    logger = logging.getLogger(__name__)
    logger.debug("\nDEBUG模式开启!\n")
else:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)

try:
    import requests
except Exception as e:
    logger.info(str(e) + "\n缺少requests模块, 请执行命令：pip3 install requests\n")
    sys.exit(1)

os.environ['no_proxy'] = '*'
requests.packages.urllib3.disable_warnings()

try:
    from notify import send
except Exception as err:
    logger.debug(str(err))
    logger.info("无推送文件")

ver = 40904


def ttotp(key):
    key = base64.b32decode(key.upper() + '=' * ((8 - len(key)) % 8))
    counter = struct.pack('>Q', int(time.time() / 30))
    mac = hmac.new(key, counter, 'sha1').digest()
    offset = mac[-1] & 0x0f
    binary = struct.unpack('>L', mac[offset:offset + 4])[0] & 0x7fffffff
    return str(binary)[-6:].zfill(6)


def sign_core(par):
    arr = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0xF, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
    key2 = b"80306f4370b39fd5630ad0529f77adb6"
    arr1 = [0 for _ in range(len(par))]
    for i in range(len(par)):
        r0 = int(par[i])
        r2 = arr[i & 0xf]
        r4 = int(key2[i & 7])
        r0 = r2 ^ r0
        r0 = r0 ^ r4
        r0 = r0 + r2
        r2 = r2 ^ r0
        r1 = int(key2[i & 7])
        r2 = r2 ^ r1
        arr1[i] = r2 & 0xff
    return bytes(arr1)


def get_sign(functionId, body, uuid, client, clientVersion, st, sv):
    all_arg = "functionId=%s&body=%s&uuid=%s&client=%s&clientVersion=%s&st=%s&sv=%s" % (
        functionId, body, uuid, client, clientVersion, st, sv)
    ret_bytes = sign_core(str.encode(all_arg))
    info = hashlib.md5(base64.b64encode(ret_bytes)).hexdigest()
    return info


def base64Encode(string):
    string1 = "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/"
    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    return base64.b64encode(string.encode("utf-8")).decode('utf-8').translate(str.maketrans(string1, string2))


def base64Decode(string):
    string1 = "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/"
    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    stringbase = base64.b64decode(string.translate(str.maketrans(string1, string2))).decode('utf-8')
    return stringbase


def genJDUA():
    st = round(time.time() * 1000)
    aid = base64Encode(''.join(str(uuid.uuid4()).split('-'))[16:])
    oaid = base64Encode(''.join(str(uuid.uuid4()).split('-'))[16:])
    ua = 'jdapp;android;11.1.4;;;appBuild/98176;ef/1;ep/{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=","ts":%s,"ridx":-1,"cipher":{"sv":"CJS=","ad":"%s","od":"%s","ov":"CzO=","ud":"%s"},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"};Mozilla/5.0 (Linux; Android 12; M2102K1C Build/SKQ1.220303.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36' % (st, aid, oaid, aid)
    return ua


def genParams():
    suid = ''.join(str(uuid.uuid4()).split('-'))[16:]
    buid = base64Encode(suid)
    st = round(time.time() * 1000)
    sv = random.choice(["102", "111", "120"])
    ep = json.dumps({
        "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
        "ts": st,
        "ridx": -1,
        "cipher": {
            "area": "CV8yEJUzXzU0CNG0XzK=",
            "d_model": "JWunCVVidRTr",
            "wifiBssid": "dW5hbw93bq==",
            "osVersion": "CJS=",
            "d_brand": "WQvrb21f",
            "screen": "CJuyCMenCNq=",
            "uuid": buid,
            "aid": buid,
            "openudid": buid
        },
        "ciphertype": 5,
        "version": "1.2.0",
        "appname": "com.jingdong.app.mall"
    }).replace(" ", "")
    body = '{"to":"https%3a%2f%2fplogin.m.jd.com%2fjd-mlogin%2fstatic%2fhtml%2fappjmp_blank.html"}'
    sign = get_sign("genToken", body, suid, "android", "11.1.4", st, sv)
    params = {
        'functionId': 'genToken',
        'clientVersion': '11.1.4',
        'build': '98176',
        'client': 'android',
        'partner': 'google',
        'oaid': suid,
        'sdkVersion': '31',
        'lang': 'zh_CN',
        'harmonyOs': '0',
        'networkType': 'UNKNOWN',
        'uemps': '0-2',
        'ext': '{"prstate": "0", "pvcStu": "1"}',
        'eid': 'eidAcef08121fds9MoeSDdMRQ1aUTyb1TyPr2zKHk5Asiauw+K/WvS1Ben1cH6N0UnBd7lNM50XEa2kfCcA2wwThkxZc1MuCNtfU/oAMGBqadgres4BU',
        'ef': '1',
        'ep': ep,
        'st': st,
        'sign': sign,
        'sv': sv
    }
    return params


def ql_send(text):
    if "WSKEY_SEND" in os.environ and os.environ["WSKEY_SEND"] == 'disable':
        return True
    else:
        try:
            send('WSKEY转换', text)
        except Exception as err:
            logger.debug(str(err))
            logger.info("通知发送失败")


def get_qltoken(username, password, twoFactorSecret):
    logger.info("Token失效, 新登陆\n")
    if twoFactorSecret:
        try:
            twoCode = ttotp(twoFactorSecret)
        except Exception as err:
            logger.debug(str(err))
            logger.info("TOTP异常")
            sys.exit(1)
        url = ql_url + "api/user/login"
        body = {
            'username': username,
            'password': password
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 200 and res.json()["code"] == 420:
                url = ql_url + 'api/user/two-factor/login'
                body = {
                    'username': username,
                    'password': password,
                    'code': twoCode
                }
                res = requests.put(url=url, headers=headers, json=body)
                if res.status_code == 200 and res.json()["code"] == 200:
                    token = res.json()["data"]['token']
                    return token
                else:
                    logger.info("两步校验失败\n")
                    sys.exit(1)
            elif res.status_code == 200 and res.json()["code"] == 200:
                token = res.json()["data"]['token']
                return token
        except Exception as err:
            logger.debug(str(err))
            sys.exit(1)
    else:
        url = ql_url + 'api/user/login'
        body = {
            'username': username,
            'password': password
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            res = requests.post(url=url, headers=headers, json=body)
            if res.status_code == 200 and res.json()["code"] == 200:
                token = res.json()["data"]['token']
                return token
            else:
                ql_send("青龙登录失败!")
                sys.exit(1)
        except Exception as err:
            logger.debug(str(err))
            logger.info("使用旧版青龙登录接口")
            url = ql_url + 'api/login'
            try:
                res = requests.post(url=url, headers=headers, json=body)
                token = json.loads(res.text)["data"]['token']
            except Exception as err:
                logger.debug(str(err))
                logger.info("青龙登录失败, 请检查面板状态!")
                ql_send('青龙登陆失败, 请检查面板状态.')
                sys.exit(1)
            else:
                return token


def ql_login() -> str:
    possible_paths = [
        '/ql/config/auth.json',
        '/ql/data/config/auth.json',
        '/data/config/auth.json',
        '/ql/config/auth.json',
    ]

    for path in possible_paths:
        if os.path.isfile(path):
            logger.info(f"✅ 找到auth文件 → {path}")
            with open(path, "r", encoding="utf-8") as file:
                auth = file.read()
                file.close()
            auth = json.loads(auth)
            username = auth["username"]
            password = auth["password"]
            token = auth["token"]
            try:
                twoFactorSecret = auth["twoFactorSecret"]
            except Exception as err:
                logger.debug(str(err))
                twoFactorSecret = ''
            if token == '':
                return get_qltoken(username, password, twoFactorSecret)
            else:
                url = ql_url + 'api/user'
                headers = {
                    'Authorization': 'Bearer {0}'.format(token),
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'
                }
                res = requests.get(url=url, headers=headers)
                if res.status_code == 200:
                    return token
                else:
                    return get_qltoken(username, password, twoFactorSecret)

    logger.info("❌ 未找到auth文件！当前目录文件列表：")
    try:
        logger.info("当前工作目录: " + os.getcwd())
        logger.info("/ql/config/: " + str(os.listdir('/ql/config/')))
    except:
        pass
    try:
        logger.info("/ql/data/config/: " + str(os.listdir('/ql/data/config/')))
    except:
        pass
    logger.info("你这是青龙吗??? 请确认在青龙容器内以任务形式运行！")
    sys.exit(0)


def get_wskey() -> list:
    if "JD_WSCK" in os.environ:
        wskey_list = os.environ['JD_WSCK'].split('&')
        if len(wskey_list) > 0:
            return wskey_list
        else:
            logger.info("JD_WSCK变量未启用")
            sys.exit(1)
    else:
        logger.info("未添加JD_WSCK变量")
        sys.exit(0)


def get_ck() -> list:
    if "JD_COOKIE" in os.environ:
        ck_list = os.environ['JD_COOKIE'].split('&')
        if len(ck_list) > 0:
            return ck_list
        else:
            logger.info("JD_COOKIE变量未启用")
            sys.exit(1)
    else:
        logger.info("未添加JD_COOKIE变量")
        sys.exit(0)


def check_ck(ck) -> bool:
    searchObj = re.search(r'pt_pin=([^;\s]+)', ck, re.M | re.I)
    if searchObj:
        pin = searchObj.group(1)
    else:
        pin = ck.split(";")[1]
    if "WSKEY_UPDATE_HOUR" in os.environ:
        updateHour = 23
        if os.environ["WSKEY_UPDATE_HOUR"].isdigit():
            updateHour = int(os.environ["WSKEY_UPDATE_HOUR"])
        nowTime = time.time()
        updatedAt = 0.0
        searchObj = re.search(r'__time=([^;\s]+)', ck, re.M | re.I)
        if searchObj:
            updatedAt = float(searchObj.group(1))
        if nowTime - updatedAt >= (updateHour * 60 * 60) - (10 * 60):
            logger.info(str(pin) + ";即将到期或已过期\n")
            return False
        else:
            remainingTime = (updateHour * 60 * 60) - (nowTime - updatedAt)
            hour = int(remainingTime / 60 / 60)
            minute = int((remainingTime % 3600) / 60)
            logger.info(str(pin) + ";未到期，{0}时{1}分后更新\n".format(hour, minute))
            return True
    elif "WSKEY_DISCHECK" in os.environ:
        logger.info("不检查账号有效性\n--------------------\n")
        return False
    else:
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfo_union'
        headers = {
            'Cookie': ck,
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'user-agent': genJDUA()
        }
        try:
            res = requests.get(url=url, headers=headers, verify=False, timeout=10, allow_redirects=False)
        except Exception as err:
            logger.debug(str(err))
            logger.info("JD接口错误 请重试或者更换IP")
            return False
        else:
            if res.status_code == 200:
                try:
                    code = int(json.loads(res.text)['retcode'])
                except Exception as err:
                    logger.debug(str(err))
                    logger.info("JD接口风控, 建议更换IP或增加间隔时间")
                    return False
                if code == 0:
                    logger.info(str(pin) + ";状态正常\n")
                    return True
                else:
                    logger.info(str(pin) + ";状态失效\n")
                    return False
            else:
                logger.info("JD接口错误码: " + str(res.status_code))
                return False


def getToken(wskey):
    params = genParams()
    headers = {
        'cookie': wskey,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'charset': 'UTF-8',
        'accept-encoding': 'br,gzip,deflate',
        'user-agent': genJDUA()
    }
    url = 'https://api.m.jd.com/client.action'
    data = 'body=%7B%22to%22%3A%22https%253a%252f%252fplogin.m.jd.com%252fjd-mlogin%252fstatic%252fhtml%252fappjmp_blank.html%22%7D&'
    try:
        res = requests.post(url=url, params=params, headers=headers, data=data, verify=False, timeout=10)
        res_json = json.loads(res.text)
        tokenKey = res_json['tokenKey']
    except Exception as err:
        logger.info("JD_WSKEY接口抛出错误 尝试重试 更换IP")
        logger.info(str(err))
        return False
    else:
        return appjmp(wskey, tokenKey)


def appjmp(wskey, tokenKey):
    wskey = "pt_" + str(wskey.split(";")[0])
    if tokenKey == 'xxx':
        logger.info(str(wskey) + ";疑似IP风控等问题 默认为失效\n--------------------\n")
        return False
    headers = {
        'User-Agent': genJDUA(),
        'accept': 'accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'x-requested-with': 'com.jingdong.app.mall'
    }
    params = {
        'tokenKey': tokenKey,
        'to': 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html'
    }
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'
    try:
        res = requests.get(url=url, headers=headers, params=params, verify=False, allow_redirects=False, timeout=20)
    except Exception as err:
        logger.info("JD_appjmp 接口错误 请重试或者更换IP\n")
        logger.info(str(err))
        return False
    else:
        try:
            res_set = res.cookies.get_dict()
            pt_key = 'pt_key=' + res_set['pt_key']
            pt_pin = 'pt_pin=' + res_set['pt_pin']
            if WSKEY_UPDATE_BOOL:
                jd_ck = str(pt_key) + ';' + str(pt_pin) + ';__time=' + str(time.time()) + ';'
            else:
                jd_ck = str(pt_key) + ';' + str(pt_pin) + ';'
        except Exception as err:
            logger.info("JD_appjmp提取Cookie错误 请重试或者更换IP\n")
            logger.info(str(err))
            return False
        else:
            if 'fake' in pt_key:
                logger.info(str(wskey) + ";WsKey状态失效\n")
                return False
            else:
                logger.info(str(wskey) + ";WsKey状态正常\n")
                return jd_ck


def update():
    up_ver = int(cloud_arg['update'])
    if ver >= up_ver:
        logger.info("当前脚本版本: " + str(ver))
        logger.info("--------------------\n")
    else:
        logger.info("当前脚本版本: " + str(ver) + "新版本: " + str(up_ver))
        logger.info("存在新版本, 请更新脚本后执行")
        logger.info("--------------------\n")
        text = '当前脚本版本: {0}新版本: {1}, 请更新脚本~!'.format(ver, up_ver)
        ql_send(text)


def ql_api(method, api, body=None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    url = ql_url + api
    for retry_count in range(3):
        try:
            if type(body) == dict:
                res = ql_session.request(method, url=url, headers=headers, json=body).json()
            else:
                res = ql_session.request(method, url=url, headers=headers, data=body).json()
        except Exception as err:
            logger.debug(str(err))
            logger.info(f"\n青龙{api}接口错误，重试次数：{retry_count + 1}")
            continue
        else:
            return res
    logger.info(f"\n青龙{api}接口多次重试仍然失败")
    sys.exit(1)


def ql_check(port) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(('127.0.0.1', port))
    except Exception as err:
        logger.debug(str(err))
        sock.close()
        return False
    else:
        sock.close()
        return True


def serch_ck(pin):
    for i in range(len(envlist)):
        if "name" not in envlist[i] or envlist[i]["name"] != "JD_COOKIE":
            continue
        if pin in envlist[i]['value']:
            value = envlist[i]['value']
            id = envlist[i][ql_id]
            logger.info(str(pin) + "检索成功\n")
            return value, id
        else:
            continue
    logger.info(str(pin) + "检索失败\n")
    return False


def get_env():
    api = 'api/envs'
    res = ql_api("GET", api)
    data = res['data']
    return data


def check_id() -> str:
    api = 'api/envs'
    res = ql_api("GET", api)
    if '_id' in res['data'][0]:
        logger.info("使用 _id 键值")
        return '_id'
    else:
        logger.info("使用 id 键值")
        return 'id'


def ql_update(eid, newck):
    api = 'api/envs'
    body = {
        'name': 'JD_COOKIE',
        'value': newck,
        ql_id: eid
    }
    ql_api("PUT", api, body)
    ql_enable(eid)


def ql_enable(eid):
    api = 'api/envs/enable'
    body = f'[{eid}]'
    res = ql_api("PUT", api, body)
    if res['code'] == 200:
        logger.info("\n账号启用\n--------------------\n")
        return True
    else:
        logger.info("\n账号启用失败\n--------------------\n")
        return False


def ql_disable(eid):
    api = 'api/envs/disable'
    body = f'[{eid}]'
    res = ql_api("PUT", api, body)
    if res['code'] == 200:
        logger.info("\n账号禁用成功\n--------------------\n")
    else:
        logger.info("\n账号禁用失败\n--------------------\n")


def ql_insert(i_ck):
    api = 'api/envs'
    body = json.dumps([{"value": i_ck, "name": "JD_COOKIE"}])
    res = ql_api("POST", api, body)
    if res['code'] == 200:
        logger.info("\n账号添加完成\n--------------------\n")
    else:
        logger.info("\n账号添加失败\n--------------------\n")


def check_port():
    logger.info("\n--------------------\n")
    port = int(os.environ.get("QL_PORT", "5700") if str(os.environ.get("QL_PORT")).isdigit() else "5700")
    if ql_check(port):
        logger.info(str(port) + "端口检查通过")
        return port
    else:
        logger.info(str(port) + "端口检查失败, 如果改过端口, 请在变量中声明端口")
        logger.info("\n如果你很确定端口没错, 还是无法执行, 在GitHub给我发issues\n--------------------\n")
        sys.exit(1)


if __name__ == '__main__':
    port = check_port()
    ql_url = f'http://127.0.0.1:{port}/'
    ql_session = requests.session()
    token = ql_login()
    ql_id = check_id()
    wslist = get_wskey()
    envlist = get_env()
    sleepTime = int(os.environ.get("WSKEY_SLEEP", "30") if str(os.environ.get("WSKEY_SLEEP")).isdigit() else "30")
    tryCount = int(os.environ.get("WSKEY_TRY_COUNT", "1") if str(os.environ.get("WSKEY_TRY_COUNT")).isdigit() else "1")
    WSKEY_UPDATE_BOOL = bool(os.environ.get("WSKEY_UPDATE_HOUR"))
    WSKEY_AUTO_DISABLE = bool(os.environ.get("WSKEY_AUTO_DISABLE"))

    for ws in wslist:
        wspin = ws.split(";")[0]
        if "pin" in wspin:
            wspin = "pt_" + wspin + ";"
            return_serch = serch_ck(wspin)
            if return_serch:
                jck, eid = return_serch
                if not check_ck(jck):
                    for count in range(tryCount):
                        count += 1
                        return_ws = getToken(ws)
                        if return_ws:
                            break
                        if count < tryCount:
                            logger.info("{0} 秒后重试，剩余次数：{1}\n".format(sleepTime, tryCount - count))
                            time.sleep(sleepTime)
                    if return_ws:
                        logger.info("wskey转换成功")
                        ql_update(eid, return_ws)
                    else:
                        if WSKEY_AUTO_DISABLE:
                            logger.info(str(wspin) + "账号失效")
                            text = f"账号: {wspin} WsKey疑似失效"
                        else:
                            logger.info(str(wspin) + "账号禁用")
                            ql_disable(eid)
                            text = f"账号: {wspin} WsKey疑似失效, 已禁用Cookie"
                        ql_send(text)
                else:
                    logger.info(str(wspin) + "账号有效")
                    ql_enable(eid)
                    logger.info("--------------------\n")
            else:
                logger.info("\n新wskey\n")
                return_ws = getToken(ws)
                if return_ws:
                    logger.info("wskey转换成功\n")
                    ql_insert(return_ws)
                    logger.info(f"暂停{sleepTime}秒\n")
                    time.sleep(sleepTime)
                else:
                    logger.info("WSKEY格式错误\n--------------------\n")
    logger.info("执行完成\n--------------------")
    sys.exit(0)
