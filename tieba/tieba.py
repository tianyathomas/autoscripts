"""
百度贴吧签到脚本 - 青龙面板版
环境变量: TIEBA_COOKIE
cron: 0 8 * * *
new Env('百度贴吧签到');
"""

import hashlib
import json
import os
import random
import time
from typing import Optional, List, Dict

import requests


# 青龙通知函数
def sendNotify(title, content):
    """发送通知到青龙"""
    try:
        from notify import send
        send(title, content)
    except ImportError:
        print(f"\n通知: {title}\n{content}")


class Tieba:
    name = "百度贴吧"

    def __init__(self, cookie: str = ""):
        self.TBS_URL = "http://tieba.baidu.com/dc/common/tbs"
        self.LIKE_URL = "http://c.tieba.baidu.com/c/f/forum/like"
        self.SIGN_URL = "http://c.tieba.baidu.com/c/c/forum/sign"
        self.LOGIN_INFO_URL = "https://zhidao.baidu.com/api/loginInfo"
        self.SIGN_KEY = "tiebaclient!!!"

        self.HEADERS = {
            "Host": "tieba.baidu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
        }

        self.SIGN_DATA = {
            "_client_type": "2",
            "_client_version": "9.7.8.0",
            "_phone_imei": "000000000000000",
            "model": "MI+5",
            "net_type": "1",
        }

        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.cookie = cookie
        self.user_name = "未知用户"

        self._init_cookie(cookie)

    def _init_cookie(self, cookie: str):
        """初始化Cookie"""
        if not cookie:
            raise ValueError("未提供 Cookie，请检查环境变量 TIEBA_COOKIE")

        cookie = cookie.strip()
        cookie_dict = {}

        # 兼容两种格式：BDUSS=xxx 或 完整的 cookie 字符串
        if "BDUSS=" in cookie:
            for item in cookie.split(";"):
                if "=" in item:
                    key = item.split("=")[0].strip()
                    value = item.split("=", 1)[1].strip()
                    cookie_dict[key] = value
        else:
            # 可能是纯BDUSS值
            cookie_dict["BDUSS"] = cookie

        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookie_dict)
        self.bduss = cookie_dict.get("BDUSS", "")

        if not self.bduss:
            raise ValueError("Cookie 中未找到 BDUSS，请检查格式")

        print(f"[TIEBA] Cookie 初始化成功")

    def request(
        self, url: str, method: str = "get", data: Optional[dict] = None, retry: int = 3
    ) -> dict:
        """带重试的请求"""
        for i in range(retry):
            try:
                if method.lower() == "get":
                    response = self.session.get(url, timeout=15)
                else:
                    response = self.session.post(url, data=data, timeout=15)

                response.raise_for_status()

                if not response.text.strip():
                    raise ValueError("空响应内容")

                return response.json()

            except requests.exceptions.Timeout:
                print(f"[TIEBA] 请求超时，正在重试 ({i + 1}/{retry})...")
            except requests.exceptions.RequestException as e:
                print(f"[TIEBA] 请求异常: {e}，正在重试 ({i + 1}/{retry})...")
            except json.JSONDecodeError:
                print(f"[TIEBA] JSON解析失败，响应内容: {response.text[:200]}")
                raise ValueError("响应内容不是有效的JSON")
            except Exception as e:
                print(f"[TIEBA] 未知错误: {e}")
                if i == retry - 1:
                    raise

            wait_time = 1.5 * (2**i) + random.uniform(0, 1)
            time.sleep(wait_time)

        raise Exception(f"请求失败，已达最大重试次数 {retry}")

    def encode_data(self, data: dict) -> dict:
        """生成签名"""
        s = ""
        for key in sorted(data.keys()):
            s += f"{key}={data[key]}"
        sign = hashlib.md5((s + self.SIGN_KEY).encode("utf-8")).hexdigest().upper()
        data.update({"sign": sign})
        return data

    def get_user_info(self) -> tuple:
        """获取用户信息"""
        try:
            result = self.request(self.TBS_URL)
            if result.get("is_login", 0) == 0:
                return False, "登录失败，Cookie可能已过期"

            tbs = result.get("tbs", "")

            try:
                user_info = self.request(self.LOGIN_INFO_URL)
                self.user_name = user_info.get("userName", "未知用户")
            except Exception:
                self.user_name = "未知用户"

            return tbs, self.user_name
        except Exception as e:
            return False, f"登录验证异常: {e}"

    def get_favorite(self) -> List[dict]:
        """获取关注的贴吧列表"""
        forums = []
        page_no = 1
        max_pages = 50

        print(f"[TIEBA] 开始获取关注的贴吧列表...")

        while page_no <= max_pages:
            data = {
                "BDUSS": self.bduss,
                "_client_type": "2",
                "_client_id": "wappc_1534235498291_488",
                "_client_version": "9.7.8.0",
                "_phone_imei": "000000000000000",
                "from": "1008621y",
                "page_no": str(page_no),
                "page_size": "200",
                "model": "MI+5",
                "net_type": "1",
                "timestamp": str(int(time.time())),
                "vcode_tag": "11",
            }
            data = self.encode_data(data)

            try:
                res = self.request(self.LIKE_URL, "post", data)

                if "forum_list" in res:
                    for forum_type in ["non-gconforum", "gconforum"]:
                        if forum_type in res["forum_list"]:
                            items = res["forum_list"][forum_type]
                            if isinstance(items, list):
                                forums.extend(items)
                            elif isinstance(items, dict):
                                forums.append(items)

                has_more = res.get("has_more", "0")
                print(f"[TIEBA] 第 {page_no} 页获取完成，当前共 {len(forums)} 个贴吧")

                if has_more != "1":
                    break

                page_no += 1
                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"[TIEBA] 获取贴吧列表出错: {e}")
                break

        print(f"[TIEBA] 共获取到 {len(forums)} 个关注的贴吧")
        return forums

    def sign_forums(self, forums: List[dict], tbs: str) -> Dict[str, int]:
        """签到所有贴吧"""
        success_count = 0
        error_count = 0
        exist_count = 0
        shield_count = 0
        total = len(forums)

        print(f"[TIEBA] 开始签到 {total} 个贴吧，这可能需要几分钟...")
        last_request_time = time.time()

        for idx, forum in enumerate(forums):
            # 智能延时
            elapsed = time.time() - last_request_time
            delay = max(0, 1.0 + random.uniform(0.5, 1.5) - elapsed)
            time.sleep(delay)
            last_request_time = time.time()

            # 每签到10个贴吧休息一下
            if (idx + 1) % 10 == 0:
                extra_delay = random.uniform(5, 10)
                print(f"[TIEBA] 已签到 {idx + 1}/{total} 个，休息 {extra_delay:.2f} 秒...")
                time.sleep(extra_delay)

            forum_name = forum.get("name", "未知")
            forum_id = forum.get("id", "")

            try:
                data = self.SIGN_DATA.copy()
                data.update({
                    "BDUSS": self.bduss,
                    "fid": forum_id,
                    "kw": forum_name,
                    "tbs": tbs,
                    "timestamp": str(int(time.time())),
                })
                data = self.encode_data(data)
                result = self.request(self.SIGN_URL, "post", data)

                error_code = result.get("error_code", "")

                if error_code == "0":
                    success_count += 1
                    if "user_info" in result:
                        rank = result["user_info"].get("user_sign_rank", "?")
                        print(f"[TIEBA] 【{forum_name}】({idx + 1}/{total}) 签到成功，第{rank}个签到")
                    else:
                        print(f"[TIEBA] 【{forum_name}】({idx + 1}/{total}) 签到成功")

                elif error_code == "160002":
                    exist_count += 1
                    print(f"[TIEBA] 【{forum_name}】({idx + 1}/{total}) 今日已签到")

                elif error_code == "340006":
                    shield_count += 1
                    print(f"[TIEBA] 【{forum_name}】({idx + 1}/{total}) 贴吧已被屏蔽")

                else:
                    error_count += 1
                    error_msg = result.get("error_msg", "未知错误")
                    print(f"[TIEBA] 【{forum_name}】({idx + 1}/{total}) 签到失败: {error_code} - {error_msg}")

            except Exception as e:
                error_count += 1
                print(f"[TIEBA] 【{forum_name}】({idx + 1}/{total}) 签到异常: {e}")

        return {
            "total": total,
            "success": success_count,
            "exist": exist_count,
            "shield": shield_count,
            "error": error_count,
        }

    def main(self) -> str:
        """主函数"""
        print("=" * 40)
        print("[TIEBA] 百度贴吧自动签到开始")
        print("=" * 40)

        try:
            # 获取用户信息
            tbs, user_name = self.get_user_info()
            if not tbs:
                print(f"[TIEBA] 登录验证失败: {user_name}")
                return f"登录失败\n原因: {user_name}"

            print(f"[TIEBA] 登录成功，用户: {user_name}")

            # 获取关注的贴吧
            forums = self.get_favorite()

            if not forums:
                print("[TIEBA] 未获取到任何贴吧，可能是没有关注任何贴吧")
                return f"用户: {user_name}\n状态: 未关注任何贴吧"

            # 开始签到
            stats = self.sign_forums(forums, tbs)

            # 汇总结果
            print("=" * 40)
            print("[TIEBA] 签到完成！")
            print(f"[TIEBA] 总计: {stats['total']} 个贴吧")
            print(f"[TIEBA] 签到成功: {stats['success']}")
            print(f"[TIEBA] 今日已签: {stats['exist']}")
            print(f"[TIEBA] 被屏蔽: {stats['shield']}")
            print(f"[TIEBA] 签到失败: {stats['error']}")
            print("=" * 40)

            # 构建返回消息
            msg = [
                f"用户: {user_name}",
                f"贴吧总数: {stats['total']}",
                f"签到成功: {stats['success']}",
                f"今日已签: {stats['exist']}",
                f"被屏蔽: {stats['shield']}",
                f"签到失败: {stats['error']}",
            ]

            return "\n".join(msg)

        except ValueError as e:
            print(f"[TIEBA] 配置错误: {e}")
            return f"配置错误\n{str(e)}"

        except requests.exceptions.RequestException as e:
            print(f"[TIEBA] 网络错误: {e}")
            return f"网络错误\n{str(e)}"

        except Exception as e:
            print(f"[TIEBA] 未知错误: {e}")
            return f"执行异常\n{str(e)}"


if __name__ == "__main__":
    # 从环境变量获取 Cookie
    cookie = os.environ.get("TIEBA_COOKIE", "")

    if not cookie:
        print("[TIEBA] 未设置环境变量 TIEBA_COOKIE，请先在青龙面板添加")
        sendNotify("百度贴吧签到失败", "未设置环境变量 TIEBA_COOKIE")
        exit(1)

    print("[TIEBA] 开始执行百度贴吧签到任务...")
    result = Tieba(cookie=cookie).main()
    print(result)
    sendNotify("百度贴吧签到", result)
