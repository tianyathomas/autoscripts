#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
百度网盘签到脚本 - 青龙面板适配版
支持环境变量配置: BAIDUWP_COOKIES (多个cookie用#分割)
或配置文件: config.json 中的 BAIDUWP 字段
"""

import json
import os
import re
import time

import requests


class BaiduWP:
    name = "百度网盘"
    
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
            "Referer": "https://pan.baidu.com/wap/svip/growth/task",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": self.cookie,
        }

    def signin(self) -> tuple:
        """签到"""
        url = "https://pan.baidu.com/rest/2.0/membership/level?app_id=250528&web=5&method=signin"
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            sign_point = None
            signin_error_msg = ""
            
            if resp.status_code == 200:
                data = resp.json()
                sign_point = data.get("points")
                if data.get("error_msg"):
                    signin_error_msg = data["error_msg"]
            else:
                signin_error_msg = f"签到请求失败: {resp.status_code}"
            
            return sign_point, signin_error_msg
        except Exception as e:
            return None, f"签到异常: {str(e)}"

    def get_question(self) -> tuple:
        """获取每日答题"""
        url = "https://pan.baidu.com/act/v2/membergrowv2/getdailyquestion?app_id=250528&web=5"
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("ask_id"), data.get("answer")
        except Exception as e:
            pass
        return None, None

    def answer_question(self, ask_id: int, answer: int) -> tuple:
        """提交答题答案"""
        url = f"https://pan.baidu.com/act/v2/membergrowv2/answerquestion?app_id=250528&web=5&ask_id={ask_id}&answer={answer}"
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("score"), data.get("show_msg")
        except Exception as e:
            pass
        return None, ""

    def get_userinfo(self) -> tuple:
        """获取会员信息"""
        url = "https://pan.baidu.com/rest/2.0/membership/user?app_id=250528&web=5&method=query"
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("current_level"), data.get("current_value")
        except Exception as e:
            pass
        return None, None

    def main(self) -> str:
        """执行签到流程"""
        # 签到
        sign_point, signin_error_msg = self.signin()
        
        # 延迟获取答题
        time.sleep(2)
        
        # 获取并回答问题
        ask_id, answer = self.get_question()
        answer_score, answer_msg = None, ""
        
        if ask_id and answer is not None:
            time.sleep(1)
            answer_score, answer_msg = self.answer_question(ask_id, answer)
        
        # 获取用户信息
        time.sleep(1)
        current_level, current_value = self.get_userinfo()
        
        # 格式化输出
        msg_parts = []
        if sign_point:
            msg_parts.append(f"签到获得 +{sign_point} 成长值")
        if signin_error_msg:
            msg_parts.append(f"签到: {signin_error_msg}")
        
        if answer_score:
            msg_parts.append(f"答题获得 +{answer_score} 成长值")
        if answer_msg:
            msg_parts.append(f"答题: {answer_msg}")
        
        if current_level:
            msg_parts.append(f"当前等级: VIP{current_level}")
        if current_value:
            msg_parts.append(f"成长值: {current_value}")
        
        return " | ".join(msg_parts) if msg_parts else "执行完成，但无返回数据"


def load_cookies() -> list:
    """从环境变量或配置文件加载cookie"""
    cookies = []
    
    # 优先从环境变量读取
    env_cookies = os.getenv("BAIDUWP_COOKIES", "")
    if env_cookies:
        # 支持 # 分隔多账号
        cookies.extend([c.strip() for c in env_cookies.split("#") if c.strip()])
    
    # 备选从配置文件读取
    if not cookies:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, encoding="utf-8") as f:
                    data = json.load(f)
                    config_cookies = data.get("BAIDUWP", [])
                    if config_cookies:
                        cookies.extend([c.get("cookie", "") for c in config_cookies if c.get("cookie")])
            except Exception:
                pass
    
    return cookies


def main():
    """主函数 - 青龙面板入口"""
    print("=" * 50)
    print("百度网盘签到开始")
    print("=" * 50)
    
    cookies = load_cookies()
    
    if not cookies:
        print("❌ 未找到有效的Cookie，请配置环境变量 BAIDUWP_COOKIES 或 config.json")
        return
    
    print(f"📋 共检测到 {len(cookies)} 个账号\n")
    
    results = []
    for i, cookie in enumerate(cookies, 1):
        print(f"\n--- 账号 {i} ---")
        try:
            baidu = BaiduWP(cookie)
            msg = baidu.main()
            print(f"✅ {msg}")
            results.append(f"账号{i}: {msg}")
        except Exception as e:
            error_msg = f"❌ 账号{i} 执行失败: {str(e)}"
            print(error_msg)
            results.append(error_msg)
        
        # 账号间延迟，避免请求过快
        if i < len(cookies):
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("百度网盘签到完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
