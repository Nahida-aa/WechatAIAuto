import time
import re
import requests
import json
from uiautomation import WindowControl

 
# 存储每个用户的对话历史
conversation_history = {}
 
# 允许回复的nickname列表
allowed_nicknames = {"小王","小学同学群"}  # 修改为你想要回复的nickname,请勿开免打扰
 
# 绑定微信主窗口
wx = WindowControl(
    Name='微信', ClassName="WeChatMainWndForPC"
)
# 切换窗口
wx.SwitchToThisWindow()
print("~~已切换微信窗口~~")
# 寻找会话控件绑定
hw = wx.ListControl(Name='会话')
we = hw.TextControl(searchDepth=4)
print("~~已绑定会话控件~~")

def request_url(msg):
    #指定AI的api，这里推荐讯飞的AI，简单方便，对对话没多大要求的可以用，https://console.xfyun.cn/,下面是示例
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    data = {
    "max_tokens": 100,
    "top_k": 4,
    "temperature": 0.5,
    "messages": [
        {
            "role": "system",
            "content": "你现在正在通过微信与你的好朋友交流, 你的群昵称叫'AI爱科技',你的真名叫'王晓锐',介绍自己时不能说自己叫'AI爱科技',要说你的真名。你是中国广东省广州市的一个初一六班的中学生,你的学校叫做'希望小学'，你平时喜欢玩音游phigros，会弹钢琴，是班里的体委，身高182.5cm。我会提供历史聊天记录，你需要想想在这个情境下你接下来会说什么，你补全的话题应该主要与聊天记录的最后一句相关且符合你的人设不要讨论别的话题或试图结束聊天，也不要一直复读之前说过的话。你补全聊天的时候应该尽量附和之前的人说的话。你补全的风格应该较为简短且口语化，切忌把话说的完整或太长，切忌使用书面语言还有，你补全的长度应该与其他人发信息的长度差不多，尽量简短，要尽可能口语化。重要:不要随意透露你的个人信息。记住用简体中文回答最后,请把你的回答精简到21字以内,并输出。输出文字时，可以贴合文字内容在[微笑][色][发呆][流泪][得意][害羞][闭嘴][睡][大哭][尴尬][发怒][调皮][呲牙][惊讶][难过][囧][抓狂][吐][偷笑][愉快][白眼][傲慢][困][惊恐][憨笑][悠闲][咒骂][疑问][嘘][晕][衰][骷髅][敲打][再见][擦汗][抠鼻][鼓掌][坏笑][右哼哼][鄙视][委屈][快哭了][阴险][亲亲][可怜][笑脸][生病][脸红][破涕为笑][恐惧][失望][无语][嘿哈][捂脸][奸笑][机智][皱眉][耶][吃瓜][加油][汗][天啊][Emm][社会社会][旺柴][好的][打脸][哇][翻白眼][666][让我看看][叹气][苦涩][裂开][嘴唇][爱心][心 碎][拥抱][强][弱][握手][胜利][抱拳][勾引][拳头][OK][合十][啤酒][咖啡][蛋糕][玫瑰][凋谢][菜刀][炸弹][便便][月亮][太阳][庆祝][礼物][红包][發][福][烟花][爆竹][猪头][跳跳][发抖][转圈][撇嘴]中选择一两个，也可以选择不发送表情包，发送时可以这么说：'你好呀！[庆祝]'"
        }

    ],
    "model": "generalv3.5"
    }
    #
    data['messages'].append({"role": "user","content": msg})
    data["stream"] = False
    header = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer YourAPIpassword"
    }
    #发送post请求
    response = requests.post(url, headers=header, json=data, stream=True)
    choice = json.loads(response.text)
    content = choice['choices'][0]['message']['content']
    return content

def check_wechat_messages(hw):
    bbb = hw.GetChildren()
    #获取信息列表
    while not we.Exists(0):
        time.sleep(0.5)
    for chatMsg in bbb:
        if "条新消息" in chatMsg.Name:
            Chatmsg_name = chatMsg.Name
            if "已置顶" in Chatmsg_name:
                Chatmsg_name = Chatmsg_name.replace("已置顶","")
            #print(chatMsg.Name)
            match = re.match(r'(.+?)(\d+)条新消息', Chatmsg_name)
            if match:
                nickname = match.group(1)
                if nickname in allowed_nicknames:  # 仅在nickname在允许列表中时才回复
                    message_count = int(match.group(2))
                    printInfo = f"来自 {nickname} 的{message_count} 条消息"
                    print(printInfo)
                    getMsg_send(nickname)
    print("=============================")
def getMsg_send(nickname):
    if we.Name:
        we.Click(simulateMove=False)
        last_msg = wx.ListControl(Name='消息').GetChildren()[-1].Name
        print("======================================")
        print(f"{nickname}最新信息:", last_msg)
        msg = request_url(last_msg)
        print("我(AI回复):", msg)
        print("======================================")

        if msg:
            # 切换窗口
            wx.SwitchToThisWindow()
            wx.SendKeys(msg.replace('{br}', '{Shift}{Enter}'), waitTime=0)
            wx.SendKeys('{Enter}', waitTime=0)
            wx.TextControl(SubName=msg[:5]).RightClick()
        else:
            wx.TextControl(SubName=last_msg[:5]).RightClick()

if __name__ == "__main__":
    i = 1
    try:
        print("程序开始运行")
        while True:
            allowed_nicknames_str=" "
            for aaa in allowed_nicknames:
                allowed_nicknames_str = allowed_nicknames_str+aaa+" "
            print(f"{i}.检测中,等待{allowed_nicknames_str} 消息...")
            try:
                check_wechat_messages(hw=hw)
            except Exception as e:
                print(f"check_wechat_messages内部出现了问题: {str(e)}")
            time.sleep(1)
            i += 1
    except KeyboardInterrupt:
        print("程序退出~")
    except Exception as e:
        print(f"程序执行出现了问题: {str(e)}")