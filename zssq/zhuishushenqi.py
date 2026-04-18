"""
追书神器 - 签到 + 成语小秀才 + 金币检测
============================================================
任务名称: 追书神器
定时: 每天 07:25 执行
环境变量: foglamb_zssq = token1@token2@token3
达到 88888 金币自动停止
============================================================
Author: ttlsky
cron: 0 25 7 * * ?
"""

import requests
import json
import time
import base64
import os
import random
from Crypto.Cipher import AES

# ==================== 公用配置 ====================
CHANNEL = "zssqydtf11"
VERSION = "3.45.92"
UID = "69d3c6f8392d74fcc09b3bec"

KD_A = "F1d36851BC0e5943042b261dFcFEd0e5"
KD_B = "5fFf6D94079904826ab080B8179E9376"

TASK_INTERVAL = 5
LOOP_INTERVAL = 8
LIMIT_KEYWORDS = ["已达上限", "今日已完成", "次数已达上限", "limit", "max", "已领取", "已满"]
TARGET_GOLD = 88888

# 任务配置
TASKS = [
 {"name": "成语小秀才", "action": "rw-self-chengyu", "task_name": "成语小秀才", "taskVersion": 2011, "gold": 300},
]


# ==================== 工具函数 ====================
def generate_android_id():
 return ''.join(random.choices('0123456789abcdef', k=16))

def android_id_to_base64(android_id):
 return base64.b64encode(android_id.encode('utf-8')).decode('utf-8')

def generate_zs_login_id():
 return ''.join(random.choices('0123456789abcdef', k=24))

def parse_accounts():
 env_str = os.environ.get("foglamb_zssq", "")
 if not env_str:
 raise Exception("请设置环境变量 foglamb_zssq，格式: token1@token2@token3")
 accounts = []
 for token in env_str.split("@"):
 token = token.strip()
 if token:
 accounts.append({
 "token": token,
 "stopped": False,
 "total_earned": 0
 })
 print(f"✅ 加载 {len(accounts)} 个账号，目标: {TARGET_GOLD} 金币")
 return accounts

def generate_third_token():
 timestamp = int(time.time() * 1000)
 plaintext = json.dumps({"time": timestamp})
 key = KD_B.encode('utf-8')
 iv = os.urandom(12)
 cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
 cipher.update(KD_A.encode('utf-8'))
 ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
 return f"{KD_A}:{iv.hex()}{ciphertext.hex()}{tag.hex()}", timestamp

def build_ext_data(task_name=None, task_progress=1):
 android_id = generate_android_id()
 android_id_b64 = android_id_to_base64(android_id)
 zs_login_id = generate_zs_login_id()
 channel_id = f"100206825-{random.randint(1000000000000, 9999999999999)}"
 
 ext = {
 "platform": "2", "product_line": 6, "apk_channel": "FXiaomi", "is_vip": False,
 "zs_login_id": zs_login_id, "business_name": "shichangbu", "channel_name": CHANNEL,
 "channel_id": channel_id, "child_channel_name": "youdao-6539045", "child_channel_id": "6539045",
 "ad_click_time": "2026-04-12 22:05:01", "new_user_welfare": False,
 "pub_app_first_install_time": "2026-04-12 23:11:35", "graytest_mark": VERSION,
 "active_time": "2026-04-06 22:45:12", "$app_version": VERSION,
 "ua_channel_id": channel_id, "ua_channel_name": CHANNEL, "ua_ad_click_time": "2026-04-12 22:05:01",
 "red_user_current_level": 0, "red_strategy_number": 0, "red_user_getmoney_initial_level": 1,
 "user_ad_strategypositionId": str(random.randint(300, 500)), "attribution_type": "device",
 "user_uid": UID, "ab_testname": "空白用户", "ab_groupname": "空白用户",
 "is_charging": False, "battery_power": -1,
 "media_type": random.choice(["oceanengine", "youdao", "gdt"]), "user_type": "老用户",
 "feature_code": "Welfare", "group_assignment": "default",
 "UpDownPage_Feature_Code": "UpDownPage", "UpDownPage_Group_Assignment": "default组",
 "audiobook_feature_abtest": "Listen", "audiobook_feature_abtest_group": "A组",
 "ccid_cipher": android_id_b64, "first_install_time": "2026-04-12 23:11:35",
 "uid": UID, "attributionType": "device", "androidid_cipher": android_id_b64,
 "device_os": "Android", "device_os_version": str(random.choice([11, 12, 13, 14, 15, 16])),
 }
 if task_name:
 ext["task_name"] = task_name
 ext["task_progress"] = task_progress
 return ext, android_id_b64


# ==================== 获取金币 ====================
def get_account_gold(account):
 try:
 _, device_id = build_ext_data()
 params = {"token": account["token"], "b-zssq": device_id}
 headers = {
 "User-Agent": "Mozilla/5.0 (Linux; Android 16; wv) AppleWebKit/537.36",
 "Origin": "https://h5.zhuishushenqi.com",
 "X-Requested-With": "com.ushaqi.zhuishushenqi.adfree"
 }
 resp = requests.get(
 "https://goldcoinnew.zhuishushenqi.com/account/profile",
 params=params, headers=headers, timeout=10
 )
 result = resp.json()
 if result.get("ecode") == 0:
 return result.get("data", {}).get("gold", 0)
 except:
 pass
 return 0


# ==================== 签到 ====================
def do_sign(account):
 print(" [签到] ", end="")
 ext, device_id = build_ext_data()
 ext.pop("task_name", None)
 ext.pop("task_progress", None)
 params = {
 "token": account["token"], "taskAttach": "1",
 "b-zssq": device_id, "extData": json.dumps(ext, separators=(',', ':'))
 }
 headers = {
 "User-Agent": "Mozilla/5.0 (Linux; Android 16; wv) AppleWebKit/537.36",
 "Origin": "https://h5.zhuishushenqi.com",
 "X-Requested-With": "com.ushaqi.zhuishushenqi.adfree"
 }
 resp = requests.get("https://goldcoin.zhuishushenqi.com/user/do-sign", params=params, headers=headers, timeout=30)
 result = resp.json()
 if result.get("ok"):
 print("✅ 成功")
 elif result.get("message") == "HAS_SIGN":
 print("⏭️ 已签到")
 else:
 print(f"❌ {result.get('message')}")


# ==================== 成语小秀才 ====================
def parse_reward(result):
 data = result.get("data", {})
 reward = data.get("reward", data.get("gold", data))
 if isinstance(reward, dict):
 return reward.get("num", reward.get("gold", 0))
 return reward if isinstance(reward, (int, float)) else 0

def complete_task(account, task_config):
 token = account["token"]
 third_token, _ = generate_third_token()
 ext, device_id = build_ext_data(task_config["task_name"], 1)
 
 body = {
 "action": task_config["action"], 
 "channel": "FXiaomi", 
 "position": "goldTask",
 "taskVersion": task_config["taskVersion"], 
 "version": VERSION,
 "thirdToken": third_token, 
 "extData": json.dumps(ext, separators=(',', ':')),
 "token": token, 
 "b-zssq": device_id
 }
 headers = {
 "User-Agent": "Mozilla/5.0 (Linux; Android 16; wv) AppleWebKit/537.36",
 "Content-Type": "application/json;charset=UTF-8",
 "Origin": "https://h5.zhuishushenqi.com",
 "X-Requested-With": "com.ushaqi.zhuishushenqi.adfree"
 }
 resp = requests.post("https://goldcoinnew.zhuishushenqi.com/redPacket/v3/completeTask", json=body, headers=headers, timeout=10)
 result = resp.json()
 if result.get("ecode") == 0:
 num = parse_reward(result)
 return True, num, False
 else:
 msg = result.get("message", "")
 is_limit = any(kw in msg for kw in LIMIT_KEYWORDS)
 return False, 0, is_limit

def run_tasks(account):
 limits = {t["name"]: False for t in TASKS}
 round_num = 1
 earned_this_session = 0
 
 while not all(limits.values()):
 if account["stopped"]:
 print(f" 🛑 账号已达目标金币，停止任务")
 break
 
 print(f"\n --- 第 {round_num} 轮 ---")
 
 for task in TASKS:
 if account["stopped"]:
 break
 if limits[task["name"]]:
 print(f" ⏭️ {task['name']}: 已达上限，跳过")
 continue
 
 print(f" 📝 {task['name']}: ", end="", flush=True)
 success, gold, is_limit = complete_task(account, task)
 
 if success:
 earned_this_session += gold
 account["total_earned"] += gold
 print(f"✅ +{gold} 金币 (本轮: {earned_this_session}, 总计: {account['total_earned']})")
 
 if account["total_earned"] >= TARGET_GOLD:
 account["stopped"] = True
 print(f" 🎉 已达到目标 {TARGET_GOLD} 金币！")
 break
 elif is_limit:
 print(f"🏁 已达上限")
 limits[task["name"]] = True
 else:
 print(f"❌ 失败")
 
 time.sleep(TASK_INTERVAL)
 
 round_num += 1
 
 if not all(limits.values()) and not account["stopped"]:
 time.sleep(LOOP_INTERVAL)
 
 if all(limits.values()):
 print(" ✅ 任务已达上限")
 
 return earned_this_session


# ==================== 主流程 ====================
def run_account(account, index, total):
 print(f" 🆔 账号 {index}/{total}")
 print(f" 🎯 目标: {TARGET_GOLD} 金币")
 
 initial_gold = get_account_gold(account)
 print(f" 💰 当前金币: {initial_gold}")
 
 if initial_gold >= TARGET_GOLD:
 print(f" ✅ 账号金币已达目标，跳过")
 account["stopped"] = True
 account["total_earned"] = initial_gold
 return
 
 account["total_earned"] = initial_gold
 
 print(f"\n [1] 签到")
 do_sign(account)
 time.sleep(2)
 
 print(f"\n [2] 成语小秀才")
 run_tasks(account)
 
 final_gold = get_account_gold(account)
 print(f"\n 💰 最终金币: {final_gold} (本次获得: {final_gold - initial_gold})")


def main():
 accounts = parse_accounts()
 
 print("=" * 50)
 print(f"追书神器 - 签到 + 成语小秀才")
 print(f"账号: {len(accounts)} | 目标: {TARGET_GOLD} 金币/号")
 print("=" * 50)
 
 for i, acc in enumerate(accounts, 1):
 print(f"\n[{i}/{len(accounts)}] 开始执行...")
 print("-" * 40)
 run_account(acc, i, len(accounts))
 
 if i < len(accounts):
 print("\n 切换到下一个账号...")
 time.sleep(3)
 
 print("\n" + "=" * 50)
 print("执行汇总:")
 print("=" * 50)
 for i, acc in enumerate(accounts, 1):
 status = "✅ 完成" if acc["stopped"] else "⏳ 未达目标"
 print(f" 账号{i}: {status} | 累计: {acc['total_earned']} 金币")
 print("=" * 50)


if __name__ == "__main__":
 main()
