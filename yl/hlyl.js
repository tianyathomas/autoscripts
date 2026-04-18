/*
------------------------------------------
@Author: sm
@Date: 2024.06.07 19:15
@Description: 活力伊利小程序签到
cron: 30 8 * * *
------------------------------------------
变量名 hlyl
抓取 https://msmarket.msx.digitalyili.com/请求头access-token 多账户&或换行
*/

// ===== Env 内联（无需外部依赖） =====
class Env {
  constructor(name) {
    this.name = name;
    this.userIdx = 0;
    this.userList = [];
  }
  checkEnv(ckName) {
    const envVal = process.env[ckName];
    if (!envVal) {
      console.log(`[WARN] 未找到环境变量 ${ckName}`);
      this.userList = [];
      return;
    }
    this.userList = envVal.includes("\n")
      ? envVal.split("\n").filter(Boolean)
      : envVal.split("#").filter(Boolean);
    console.log(`[${this.name}] 共找到 ${this.userList.length} 个账号`);
  }
  log(msg) {
    console.log(msg);
  }
  done() {
    console.log(`[${this.name}] 执行完毕`);
  }
}
// ===== Env 内联结束 =====

const $ = new Env("活力伊利小程序");
let ckName = `hlyl`;
const strSplitor = "#";
const axios = require("axios");
const defaultUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.31(0x18001e31) NetType/WIFI Language/zh_CN miniProgram"


class Task {
 constructor(env) {
 this.index = $.userIdx++
 this.user = env.split(strSplitor);
 this.token = this.user[0];

 }

 async run() {

 await this.signIn()
 }

 async signIn() {
 let options = {
 method: 'POST',
 url: `https://msmarket.msx.digitalyili.com/gateway/api/member/daily/sign`,
 headers: {

 "accept": "*/*",
 "accept-language": "zh-CN,zh;q=0.9",
 "access-token": "" + this.token,
 "atv-page": "",
 "content-type": "application/json",
 "forward-appid": "",
 "priority": "u=1, i",
 "register-source": "",
 "scene": "1145",
 "sec-fetch-dest": "empty",
 "sec-fetch-mode": "cors",
 "sec-fetch-site": "cross-site",
 "source-type": "",
 "tenant-id": "",
 "xweb_xhr": "1"


 , data: {

 }
 }
 }
 let { data: result } = await axios.request(options);
 if (result?.status == true) {
 $.log(`🌸账号[${this.index}]` + `🕊签到获得${result.data.dailySign.bonusPoint}分🎉`);
 } else {
 $.log(`🌸账号[${this.index}] 签到-失败:${result.error}❌`)
 }




 }








}

!(async () => {
 await getNotice()
 $.checkEnv(ckName);

 for (let user of $.userList) {
 await new Task(user).run();
 }
})()
 .catch((e) => console.log(e))
 .finally(() => $.done());

async function getNotice() {
 try {
 let options = {
 url: `https://ghproxy.net/https://raw.githubusercontent.com/smallfawn/Note/refs/heads/main/Notice.json`,
 headers: {
 "User-Agent": defaultUserAgent,
 },
 timeout: 3000
 }
 let {
 data: res
 } = await axios.request(options);
 $.log(res)
 return res
 } catch (e) { }

}
