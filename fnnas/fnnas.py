"""
cron: 30 6 * * *
new Env('飞牛论坛签到');
"""

import os
import re
import time
import requests

# ============ 环境变量配置 ============
# FNNAS_COOKIE: 飞牛NAS论坛完整cookie字符串（必填）


class FnNasClubCheckIn:
    name = "飞牛NAS论坛"

    def __init__(self):
        self.cookie_str = os.getenv("FNNAS_COOKIE", "")

        if not self.cookie_str:
            raise ValueError("未设置环境变量 FNNAS_COOKIE，请先配置")

        # 初始化session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://club.fnnas.com/portal.php",
            "Content-Type": "text/html; charset=utf-8",
        })
        self.session.headers["Cookie"] = self.cookie_str

    def get_sign_param(self):
        """访问签到页面，提取sign参数和签到时间"""
        url = "https://club.fnnas.com/plugin.php?id=zqlj_sign"
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            html = response.text

            # 匹配签到按钮中的sign参数（点击打卡 或 今日已打卡）
            pattern = re.compile(r'<a href="plugin\.php\?id=zqlj_sign&sign=([0-9a-fA-F]+)"')
            match = pattern.search(html)

            sign_time = None
            # 已签到时，提取签到时间（格式：最近打卡：2026-03-30 20:57:56）
            if "今日已打卡" in html:
                time_match = re.search(r"最近打卡[：:]\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", html)
                if time_match:
                    sign_time = time_match.group(1).strip()
                return match.group(1) if match else None, True, sign_time
            elif "点击打卡" in html:
                return match.group(1) if match else None, False, None

            return None, False, None
        except Exception as e:
            print(f"[获取签到参数] 异常: {e}")
            return None, False, None

    def sign(self, sign_param):
        """执行签到"""
        if not sign_param:
            return False, "签到失败，未能获取sign参数", None

        url = f"https://club.fnnas.com/plugin.php?id=zqlj_sign&sign={sign_param}"
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            html = response.text

            if "恭喜您，打卡成功" in html:
                sign_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                return True, "签到成功", sign_time
            elif "您今天已经打过卡了" in html or "今日已打卡" in html:
                return True, "今日已签到", None
            else:
                # 尝试提取错误信息
                error_match = re.search(r'<div[^>]*class="alert_error"[^>]*>(.*?)</div>', html, re.S)
                if error_match:
                    return False, f"签到失败: {error_match.group(1).strip()}", None
                return False, "签到失败，未知原因", None
        except Exception as e:
            return False, f"签到异常: {e}", None

    def get_info(self):
        """获取打卡动态信息"""
        url = "https://club.fnnas.com/plugin.php?id=zqlj_sign"
        info = []

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            html = response.text

            # 精确匹配用户打卡信息的 ul（包含"最近打卡"的唯一区块）
            pattern = re.compile(r'<ul class="xl xl1">\s*<li>最近打卡[：:].*?</ul>', re.S)
            match = pattern.search(html)

            if not match:
                info.append({"name": "提示", "value": "未获取到用户打卡信息，请检查cookie是否包含有效用户"})
                return info

            block_html = match.group(0)

            # 提取每个 <li> 里的内容
            li_pattern = re.compile(r"<li>([^<]+)</li>")
            for li_match in li_pattern.finditer(block_html):
                text = li_match.group(1).strip()
                # 格式：名称：值
                if "：" in text:
                    name, value = text.split("：", 1)
                    info.append({"name": name.strip(), "value": value.strip()})

            if not info:
                info.append({"name": "提示", "value": "打卡信息解析失败"})

        except Exception as e:
            info.append({"name": "获取信息失败", "value": str(e)})

        return info

    def main(self):
        """主函数"""
        print("=" * 40)
        print("【飞牛NAS论坛签到任务开始】")
        print("=" * 40)

        # 获取签到参数
        sign_param, already_signed, sign_time = self.get_sign_param()

        if sign_param is None:
            print("[签到] 获取sign参数失败，请检查cookie是否有效")
            print("=" * 40)
            return

        if already_signed:
            print("[签到] 今日已签到")
            sign_msg = "今日已签到"
            if sign_time:
                print(f"[签到时间] {sign_time}")
        else:
            # 执行签到
            sign_success, sign_msg, sign_time = self.sign(sign_param)
            print(f"[签到] {sign_msg}")
            if sign_time:
                print(f"[签到时间] {sign_time}")

        # 获取打卡信息
        print()
        print("【打卡动态】")
        info = self.get_info()
        for item in info:
            print(f"{item['name']}: {item['value']}")

        # 汇总
        print()
        print("=" * 40)
        print("【任务执行完成】")
        print("=" * 40)
        print(f"签到结果: {sign_msg}")
        if sign_time:
            print(f"签到时间: {sign_time}")
        for item in info:
            print(f"{item['name']}: {item['value']}")
        print("=" * 40)


if __name__ == "__main__":
    try:
        checkin = FnNasClubCheckIn()
        checkin.main()
    except Exception as e:
        print(f"[FAIL] 执行失败: {e}")
        import traceback
        traceback.print_exc()
