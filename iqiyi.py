import json
import os
import re
import time
from urllib.parse import unquote
from uuid import uuid4

import requests


class IQIYI:
    name = "爱奇艺"

    def __init__(self, check_item):
        self.check_item = check_item

    @staticmethod
    def parse_cookie(cookie):
        p00001 = re.findall(r"P00001=(.*?);", cookie)[0] if re.findall(r"P00001=(.*?);", cookie) else ""
        p00002 = re.findall(r"P00002=(.*?);", cookie)[0] if re.findall(r"P00002=(.*?);", cookie) else ""
        p00003 = re.findall(r"P00003=(.*?);", cookie)[0] if re.findall(r"P00003=(.*?);", cookie) else ""
        __dfp = re.findall(r"__dfp=(.*?);", cookie)[0] if re.findall(r"__dfp=(.*?);", cookie) else ""
        __dfp = __dfp.split("@")[0]
        qyid = re.findall(r"QC005=(.*?);", cookie)[0] if re.findall(r"QC005=(.*?);", cookie) else ""
        return p00001, p00002, p00003, __dfp, qyid

    @staticmethod
    def user_information(p00001):
        """
        账号信息查询
        """
        time.sleep(1)
        url = "http://serv.vip.iqiyi.com/vipgrowth/query.action"
        params = {"P00001": p00001}
        res = requests.get(url=url, params=params, timeout=10).json()
        if res["code"] == "A00000":
            try:
                res_data = res.get("data", {})
                level = res_data.get("level", 0)
                growthvalue = res_data.get("growthvalue", 0)
                distance = res_data.get("distance", 0)
                deadline = res_data.get("deadline", "非 VIP 用户")
                today_growth_value = res_data.get("todayGrowthValue", 0)
                msg = [
                    {"name": "VIP 等级", "value": level},
                    {"name": "当前成长", "value": growthvalue},
                    {"name": "今日成长", "value": today_growth_value},
                    {"name": "升级还需", "value": distance},
                    {"name": "VIP 到期", "value": deadline},
                ]
            except Exception as e:
                msg = [
                    {"name": "账号信息", "value": str(e)},
                ]
        else:
            msg = [
                {"name": "账号信息", "value": res.get("msg")},
            ]
        return msg

    def lottery(self, p00001, award_list=[]):
        url = "https://act.vip.iqiyi.com/shake-api/lottery"
        params = {
            "P00001": p00001,
            "deviceID": str(uuid4()),
            "version": "15.3.0",
            "platform": str(uuid4())[:16],
            "lotteryType": "0",
            "actCode": "0k9GkUcjqqj4tne8",
            "extendParams": json.dumps(
                {
                    "appIds": "iqiyi_pt_vip_iphone_video_autorenew_12m_348yuan_v2",
                    "supportSk2Identity": True,
                    "testMode": "0",
                    "iosSystemVersion": "17.4",
                    "bundleId": "com.qiyi.iphone",
                }
            ),
        }
        try:
            res = requests.get(url, params=params, timeout=10).json()
        except Exception as e:
            return [{"name": "每天摇一摇", "value": f"请求失败: {e}"}]
            
        msgs = []
        if res.get("code") == "A00000":
            award_info = res.get("data", {}).get("title")
            award_list.append(award_info)
            time.sleep(1)
            return self.lottery(p00001=p00001, award_list=award_list)
        elif res.get("msg") == "抽奖次数用完":
            if award_list:
                msgs = [{"name": "每天摇一摇", "value": "、".join(award_list)}]
            else:
                msgs = [{"name": "每天摇一摇", "value": res.get("msg")}]
        else:
            msgs = [{"name": "每天摇一摇", "value": res.get("msg")}]
        return msgs

    @staticmethod
    def draw(draw_type, p00001, p00003):
        """
        查询抽奖次数(必),抽奖
        :param draw_type: 类型 0 查询次数 1 抽奖
        :param p00001: 关键参数
        :param p00003: 关键参数
        :return: {status, msg, chance}
        """
        url = "https://iface2.iqiyi.com/aggregate/3.0/lottery_activity"
        params = {
            "lottery_chance": 1,
            "app_k": "b398b8ccbaeacca840073a7ee9b7e7e6",
            "app_v": "11.6.5",
            "platform_id": 10,
            "dev_os": "8.0.0",
            "dev_ua": "FRD-AL10",
            "net_sts": 1,
            "qyid": "2655b332a116d2247fac3dd66a5285011102",
            "psp_uid": p00003,
            "psp_cki": p00001,
            "psp_status": 3,
            "secure_v": 1,
            "secure_p": "GPhone",
            "req_sn": round(time.time() * 1000),
        }
        if draw_type == 1:
            del params["lottery_chance"]
        try:
            res = requests.get(url=url, params=params, timeout=10).json()
        except Exception as e:
            return {"status": False, "msg": f"请求失败: {e}", "chance": 0}
            
        if not res.get("code"):
            chance = int(res.get("daysurpluschance", 0))
            msg = res.get("awardName", "")
            return {"status": True, "msg": msg, "chance": chance}
        else:
            try:
                msg = res.get("kv", {}).get("msg")
            except Exception as e:
                msg = res.get("errorReason", str(e))
            return {"status": False, "msg": msg, "chance": 0}

    def level_right(self, p00001):
        data = {"code": "k8sj74234c683f", "P00001": p00001}
        try:
            res = requests.post(url="https://act.vip.iqiyi.com/level-right/receive", data=data, timeout=10).json()
            msg = res.get("msg", "未知错误")
        except Exception as e:
            msg = str(e)
        return [{"name": "V7 免费升级星钻", "value": msg}]

    def give_times(self, p00001):
        url = "https://pcell.iqiyi.com/lotto/giveTimes"
        times_code_list = ["browseWeb", "browseWeb", "bookingMovie"]
        for times_code in times_code_list:
            params = {
                "actCode": "bcf9d354bc9f677c",
                "timesCode": times_code,
                "P00001": p00001,
            }
            try:
                requests.get(url, params=params, timeout=10)
            except:
                pass

    def lotto_lottery(self, p00001):
        self.give_times(p00001=p00001)
        gift_list = []
        for _ in range(5):
            url = "https://pcell.iqiyi.com/lotto/lottery"
            params = {"actCode": "bcf9d354bc9f677c", "P00001": p00001}
            try:
                response = requests.get(url, params=params, timeout=10)
                gift_name = response.json().get("data", {}).get("giftName", "")
                if gift_name and "未中奖" not in gift_name:
                    gift_list.append(gift_name)
            except:
                pass
        if gift_list:
            return [{"name": "白金抽奖", "value": "、".join(gift_list)}]
        else:
            return [{"name": "白金抽奖", "value": "未中奖"}]

    def main(self):
        p00001, p00002, p00003, dfp, qyid = self.parse_cookie(self.check_item.get("cookie"))
        try:
            user_info = json.loads(unquote(p00002, encoding="utf-8"))
            user_name = user_info.get("user_name", "未知")
            user_name = user_name.replace(user_name[3:7], "****")
            nickname = user_info.get("nickname", "未知")
        except Exception as e:
            print(f"获取账号信息失败，错误信息: {e}")
            nickname = "未获取到，请检查 Cookie 中 P00002 字段"
            user_name = "未获取到，请检查 Cookie 中 P00002 字段"
        
        _user_msg = self.user_information(p00001=p00001)
        lotto_lottery_msg = self.lotto_lottery(p00001=p00001)
        
        if _user_msg[4].get("value") != "非 VIP 用户":
            level_right_msg = self.level_right(p00001=p00001)
        else:
            level_right_msg = [
                {
                    "name": "V7 免费升级星钻",
                    "value": "非 VIP 用户",
                }
            ]
        
        chance = self.draw(draw_type=0, p00001=p00001, p00003=p00003)["chance"]
        lottery_msgs = self.lottery(p00001=p00001, award_list=[])
        
        if chance:
            draw_msg = ""
            for _ in range(chance):
                ret = self.draw(draw_type=1, p00001=p00001, p00003=p00003)
                draw_msg += ret["msg"] + ";" if ret["status"] else ""
                time.sleep(0.5)
        else:
            draw_msg = "抽奖机会不足"

        user_msg = self.user_information(p00001=p00001)

        msg = [
            {"name": "用户账号", "value": user_name},
            {"name": "用户昵称", "value": nickname},
            *user_msg,
            {"name": "抽奖奖励", "value": draw_msg},
            *lottery_msgs,
            *level_right_msg,
            *lotto_lottery_msg,
        ]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    # Cookie 配置
    cookie_str = """QC234=816d3b828a488e7919a14f740ae20949; QC005=8ad044da9dd21d4af37b08a6016127b7; QP0037=0; T00404=2af0836b660fe404fb336f8e418a519c; QC235=1d5cbc070e3b4f52a9aae0cdc22725ef; P00004=.1745975619.180cc4bd88; QC170=1; QC006=45136eb5692c285c993e4f6c6bc46941; QP0038=500; QP0035=4; __uuid=e61b37ac-a4a4-663e-e0da-0bd59105ee27; QP0042={"v":3,"cpu":4,"avc":{"de":2,"wv":1},"av1":{"de":1,"wv":1},"av110":{"de":1,"wv":0}}; __dfp=a1ce53613ea6f641e7abe37c14e330610a7a52847011babf10d63b69564df88ad4@1759626432370@1758330433370; agreementUpdate=V1; QC008=Kqr81mXRKI4g0Juc; QC007=DIRECT; curDeviceState=width%3D1920%3BconduitId%3D%3Bscale%3D100%3Bbrightness%3Ddark%3BisLowPerformPC%3D0%3Bos%3DWindows%3Bosv%3D10.0; acc_abTest=6249_C; P00001=29im3GWB1cPtyYXBivr6adnbHAzAjSflld6ngLtJq4M0B4d6Q6Xnm3EN8gw0UQbgWGtgeb; P00007=29im3GWB1cPtyYXBivr6adnbHAzAjSflld6ngLtJq4M0B4d6Q6Xnm3EN8gw0UQbgWGtgeb; P00003=1210617706; P00010=1210617706; P01010=1774713600; P00PRU=1210617706; vipTypes=0; vipLevel=1; P00002=%7B%22uid%22%3A%221210617706%22%2C%22pru%22%3A1210617706%2C%22user_name%22%3A%22138****5800%22%2C%22nickname%22%3A%22138****5800_m2392%22%2C%22pnickname%22%3A%22138****5800_m2392%22%2C%22type%22%3A11%2C%22email%22%3Anull%7D; IMS=IggQABj_9Z_OBiomCiAzMjQzMWM2MjEwZGU0MDg0YmZhNmQ0NTNmZjdmMzJiNRAAIgByJAogMzI0MzFjNjIxMGRlNDA4NGJmYTZkNDUzZmY3ZjMyYjUQAIIBBCICEAqKASQKIgogYWRiMDQ5YzYwMTIwNGM0NmIzN2M5Njc5ODAyMmQ5NDA"""
    
    _check_item = {"cookie": cookie_str}
    print("=" * 50)
    print("爱奇艺自动签到开始")
    print("=" * 50)
    result = IQIYI(check_item=_check_item).main()
    print(result)
    print("=" * 50)
