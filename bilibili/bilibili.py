"""
cron: 0 6 * * *
new Env('B站签到');
"""

import os
import time
import json
import requests

# ============ 环境变量配置 ============
# BILIBILI_COOKIE: B站完整cookie字符串（必填）
# BILIBILI_COIN_NUM: 每日投币数量，默认5（可选）
# BILIBILI_COIN_TYPE: 投币类型，1=关注UP主视频，其他=分区视频，默认1（可选）
# BILIBILI_SILVER2COIN: 是否银瓜子换硬币，true/false，默认false（可选）


class BiliBiliCheckIn:
    name = "Bilibili"

    def __init__(self):
        self.cookie_str = os.getenv("BILIBILI_COOKIE", "")
        self.coin_num = int(os.getenv("BILIBILI_COIN_NUM", "5"))
        self.coin_type = int(os.getenv("BILIBILI_COIN_TYPE", "1"))
        self.silver2coin = os.getenv("BILIBILI_SILVER2COIN", "false").lower() == "true"

        if not self.cookie_str:
            raise ValueError("未设置环境变量 BILIBILI_COOKIE，请先配置")

        # 解析cookie - 修复：支持多种分隔符，去重
        self.bilibili_cookie = {}
        # 支持 ; 和 ; 两种分隔符
        for item in self.cookie_str.replace("; ", ";").replace("; ", ";").split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                # 避免重复key覆盖
                if key not in self.bilibili_cookie:
                    self.bilibili_cookie[key] = value

        self.bili_jct = self.bilibili_cookie.get("bili_jct")
        if not self.bili_jct:
            raise ValueError("cookie 中未找到 bili_jct，请检查cookie是否完整")

        # 初始化session
        self.session = requests.Session()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, self.bilibili_cookie)
        self.session.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Origin": "https://www.bilibili.com",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        })

    @staticmethod
    def get_nav(session):
        """获取账号基本信息"""
        url = "https://api.bilibili.com/x/web-interface/nav"
        ret = session.get(url=url, timeout=10).json()
        data = ret.get("data", {})
        uname = data.get("uname", "未知")
        uid = data.get("mid", 0)
        is_login = data.get("isLogin", False)
        coin = data.get("money", 0)
        vip_type = data.get("vipType", 0)
        current_exp = data.get("level_info", {}).get("current_exp", 0)
        return uname, uid, is_login, coin, vip_type, current_exp

    @staticmethod
    def get_today_exp(session):
        """获取今日经验信息"""
        url = "https://api.bilibili.com/x/member/web/exp/log?jsonp=jsonp"
        today = time.strftime("%Y-%m-%d", time.localtime())
        ret = session.get(url=url, timeout=10).json()
        data_list = ret.get("data", {}).get("list", [])
        return [x for x in data_list if x.get("time", "").split()[0] == today]

    @staticmethod
    def vip_privilege_my(session):
        """获取大会员权益信息"""
        url = "https://api.bilibili.com/x/vip/privilege/my"
        ret = session.get(url=url, timeout=10).json()
        return ret

    @staticmethod
    def live_sign(session):
        """B站直播签到"""
        try:
            url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
            ret = session.get(url=url, timeout=10).json()
            if ret["code"] == 0:
                data = ret["data"]
                msg = f"签到成功，{data['text']}，本月已签到{data['hadSignDays']}天"
            elif ret["code"] == 1011040:
                msg = "今日已签到过"
            else:
                msg = f"签到失败: {ret['message']}"
        except Exception as e:
            msg = f"签到异常: {e}"
        print(f"[直播签到] {msg}")
        return msg

    @staticmethod
    def manga_sign(session, platform="android"):
        """B站漫画签到"""
        try:
            url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
            post_data = {"platform": platform}
            ret = session.post(url=url, data=post_data, timeout=10).json()
            if ret["code"] == 0:
                msg = "签到成功"
            elif ret.get("msg") == "clockin clockin is duplicate":
                msg = "今天已经签到过了"
            else:
                msg = f"签到失败: {ret.get('msg', '未知错误')}"
        except Exception as e:
            msg = f"签到异常: {e}"
        print(f"[漫画签到] {msg}")
        return msg

    @staticmethod
    def vip_privilege_receive(session, bili_jct, receive_type=1):
        """领取大会员权益"""
        url = "https://api.bilibili.com/x/vip/privilege/receive"
        post_data = {"type": receive_type, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data, timeout=10).json()
        return ret

    @staticmethod
    def get_followings(session, uid, pn=1, ps=50):
        """获取关注列表"""
        params = {
            "vmid": uid,
            "pn": pn,
            "ps": ps,
            "order": "desc",
            "order_type": "attention",
        }
        url = "https://api.bilibili.com/x/relation/followings"
        ret = session.get(url=url, params=params, timeout=10).json()
        return ret

    @staticmethod
    def space_arc_search(session, uid, pn=1, ps=30):
        """获取UP主投稿视频"""
        params = {
            "mid": uid,
            "pn": pn,
            "ps": ps,
            "tid": 0,
            "order": "pubdate",
            "keyword": "",
        }
        url = "https://api.bilibili.com/x/space/arc/search"
        ret = session.get(url=url, params=params, timeout=10).json()
        vlist = ret.get("data", {}).get("list", {}).get("vlist", [])
        data_list = [
            {
                "aid": one.get("aid"),
                "cid": 0,
                "title": one.get("title"),
                "owner": one.get("author"),
            }
            for one in vlist[:2]  # 取前2个
        ]
        return data_list, len(data_list)

    @staticmethod
    def get_region(session, rid=1, num=6):
        """获取分区视频"""
        url = f"https://api.bilibili.com/x/web-interface/dynamic/region?ps={num}&rid={rid}"
        ret = session.get(url=url, timeout=10).json()
        archives = ret.get("data", {}).get("archives", [])
        data_list = [
            {
                "aid": one.get("aid"),
                "cid": one.get("cid"),
                "title": one.get("title"),
                "owner": one.get("owner", {}).get("name"),
            }
            for one in archives
        ]
        return data_list

    def coin_add(self, aid, num=1, select_like=1):
        """投币 - 修复版"""
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        post_data = {
            "aid": aid,
            "multiply": num,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": self.bili_jct,
        }
        
        # 添加更完整的请求头
        headers = {
            "Referer": "https://www.bilibili.com",
            "Origin": "https://www.bilibili.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        
        ret = self.session.post(url=url, data=post_data, headers=headers, timeout=10).json()
        return ret

    def report_task(self, aid, cid, progres=300):
        """上报观看进度 - 修复版"""
        url = "http://api.bilibili.com/x/v2/history/report"
        post_data = {"aid": aid, "cid": cid, "progres": progres, "csrf": self.bili_jct}
        
        headers = {
            "Referer": "https://www.bilibili.com",
            "Origin": "https://www.bilibili.com",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        
        ret = self.session.post(url=url, data=post_data, headers=headers, timeout=10).json()
        return ret

    @staticmethod
    def share_task(session, bili_jct, aid):
        """分享视频"""
        url = "https://api.bilibili.com/x/web-interface/share/add"
        post_data = {"aid": aid, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data, timeout=10).json()
        return ret

    @staticmethod
    def silver2coin(session, bili_jct):
        """银瓜子换硬币"""
        url = "https://api.live.bilibili.com/xlive/revenue/v1/wallet/silver2coin"
        post_data = {"csrf": bili_jct}
        ret = session.post(url=url, data=post_data, timeout=10).json()
        return ret

    @staticmethod
    def live_status(session):
        """获取直播资产"""
        url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
        ret = session.get(url=url, timeout=10).json()
        data = ret.get("data", {})
        return [
            {"name": "硬币数量", "value": data.get("coin", 0)},
            {"name": "金瓜子数", "value": data.get("gold", 0)},
            {"name": "银瓜子数", "value": data.get("silver", 0)},
        ]

    def main(self):
        """主函数"""
        print("=" * 40)
        print("【B站签到任务开始】")
        print("=" * 40)

        # 获取账号信息
        uname, uid, is_login, coin, vip_type, current_exp = self.get_nav(self.session)
        if not is_login:
            print("[FAIL] 登录失败，请检查cookie是否过期")
            return

        print(f"[OK] 账号: {uname} (UID: {uid})")
        print(f"   硬币: {coin} | VIP类型: {vip_type}")
        print()

        # 直播签到
        live_msg = self.live_sign(self.session)

        # 漫画签到
        manga_msg = self.manga_sign(self.session)

        # 领取大会员权益
        privilege_msg = "无需领取"
        try:
            vip_privilege_my_ret = self.vip_privilege_my(self.session)
            welfare_list = vip_privilege_my_ret.get("data", {}).get("list", [])
            for welfare in welfare_list:
                if welfare.get("state") == 0 and welfare.get("vip_type") == vip_type:
                    ret = self.vip_privilege_receive(
                        self.session, self.bili_jct, welfare.get("type")
                    )
                    if ret.get("code") == 0:
                        privilege_msg = "领取成功"
                        print(f"[大会员权益] 领取成功: {welfare.get('type')}")
        except Exception as e:
            privilege_msg = f"领取异常: {e}"
            print(f"[大会员权益] {privilege_msg}")

        # 统计今日已投币数
        today_exp_list = self.get_today_exp(self.session)
        coins_av_count = len([x for x in today_exp_list if x.get("reason") == "视频投币奖励"])

        # 准备投币视频列表
        aid_list = []
        need_coin = self.coin_num - coins_av_count

        if need_coin > 0 and coin > 0:
            need_coin = min(need_coin, coin)  # 不超过当前硬币数

            if self.coin_type == 1:
                # 从关注的UP主获取视频
                try:
                    following_ret = self.get_followings(self.session, uid)
                    count = 0
                    for following in following_ret.get("data", {}).get("list", []):
                        mid = following.get("mid")
                        if mid:
                            tmplist, tmpcount = self.space_arc_search(self.session, mid)
                            aid_list.extend(tmplist)
                            count += tmpcount
                            if count >= need_coin:
                                print(f"[投币] 已获取足够关注UP主视频 ({count}个)")
                                break
                except Exception as e:
                    print(f"[投币] 获取关注列表失败: {e}")

            # 如果关注列表不够，从分区补充
            if len(aid_list) < need_coin:
                try:
                    region_list = self.get_region(self.session)
                    aid_list.extend(region_list)
                except Exception as e:
                    print(f"[投币] 获取分区视频失败: {e}")

            # 执行投币
            success_count = 0
            for video in aid_list[::-1]:  # 倒序投
                if need_coin <= 0:
                    break
                try:
                    ret = self.coin_add(video.get("aid"))
                    print(f"[DEBUG] 投币返回: {ret}")  # 添加调试信息
                    if ret["code"] == 0:
                        print(f"[投币] 成功投币: {video.get('title')}")
                        success_count += 1
                        need_coin -= 1
                    elif ret["code"] == 34005:
                        print(f"[投币] 已达上限，跳过: {video.get('title')}")
                        continue
                    elif ret["code"] == -104:
                        print("[投币] 硬币不足，停止投币")
                        break
                    else:
                        print(f"[投币] 失败 ({ret.get('message')}), 停止投币")
                        break
                except Exception as e:
                    print(f"[投币] 异常: {e}")

            coin_msg = f"今日投币 {success_count + coins_av_count}/{self.coin_num}"
        else:
            coin_msg = f"今日投币 {coins_av_count}/{self.coin_num} (已完成或硬币不足)"

        print(f"[投币任务] {coin_msg}")

        # 观看视频任务
        report_msg = "任务失败"
        share_msg = "分享失败"
        if aid_list:
            video = aid_list[0]
            aid, cid = video.get("aid"), video.get("cid")
            title = video.get("title", "未知")

            # 如果没有cid，尝试获取
            if not cid:
                try:
                    detail_url = f"https://api.bilibili.com/x/web-interface/view?aid={aid}"
                    detail = self.session.get(detail_url, timeout=10).json()
                    cid = detail.get("data", {}).get("cid", 0)
                except:
                    cid = 0

            try:
                ret = self.report_task(aid, cid)
                print(f"[DEBUG] 观看任务返回: {ret}")  # 添加调试信息
                report_msg = f"观看《{title}》300秒" if ret.get("code") == 0 else f"任务失败: {ret.get('message')}"
            except Exception as e:
                report_msg = f"任务异常: {e}"
            print(f"[观看任务] {report_msg}")

            try:
                ret = self.share_task(self.session, self.bili_jct, aid)
                share_msg = "分享成功" if ret.get("code") == 0 else "分享失败"
            except Exception as e:
                share_msg = f"分享异常: {e}"
            print(f"[分享任务] {share_msg}")

        # 银瓜子兑换
        s2c_msg = "不兑换"
        if self.silver2coin:
            try:
                ret = self.silver2coin(self.session, self.bili_jct)
                s2c_msg = ret.get("message", "未知结果")
            except Exception as e:
                s2c_msg = f"兑换异常: {e}"
            print(f"[瓜子兑换] {s2c_msg}")

        # 获取最终状态
        _, _, _, new_coin, _, new_current_exp = self.get_nav(self.session)
        today_exp = sum(x.get("delta", 0) for x in today_exp_list)
        live_stats = self.live_status(self.session)

        # 升级预估（LV6经验上限28800，简单估算）
        update_days = (28800 - new_current_exp) // (today_exp if today_exp else 1)

        # 汇总输出
        print()
        print("=" * 40)
        print("【任务执行完成】")
        print("=" * 40)
        print(f"账号信息: {uname}")
        print(f"漫画签到: {manga_msg}")
        print(f"直播签到: {live_msg}")
        print(f"大会员权益: {privilege_msg}")
        print(f"观看任务: {report_msg}")
        print(f"分享任务: {share_msg}")
        print(f"瓜子兑换: {s2c_msg}")
        print(f"投币任务: {coin_msg}")
        print(f"今日经验: +{today_exp}")
        print(f"当前经验: {new_current_exp}")
        print(f"升级预估: {update_days}天")
        for stat in live_stats:
            print(f"{stat['name']}: {stat['value']}")
        print("=" * 40)


if __name__ == "__main__":
    try:
        checkin = BiliBiliCheckIn()
        checkin.main()
    except Exception as e:
        print(f"[FAIL] 执行失败: {e}")
        import traceback
        traceback.print_exc()
