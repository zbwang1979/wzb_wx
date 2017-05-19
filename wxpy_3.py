# 导入模块
from apscheduler.schedulers.blocking import BlockingScheduler
import apscheduler
import emoji
from bs4 import BeautifulSoup
import urllib.request
import urllib.error 
import threading
import datetime
import pytz
import requests
import re
import random, string
import time
import sqlite3
import sys
from wxpy import *
import logging
from wxpy import WeChatLoggingHandler


def get_tuling(pattern,msg):
#######图灵机器
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : '08af3b8d03d64643804a8360bd5e3cbe',
        'info'   : msg,
        'userid' : 'itchat-111',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        result=pattern.search(r.get('text'))
        if bool(result):
            return result.group(1)
        else:
            return 
    except:
        return
    
def get_short_url(url):
#######短链接
    apiUrl = 'http://dwz.cn/create.php'
    data = {
        'url'    : url,
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        if bool(r['status']==0):
            return r['tinyurl']
        else:
            return 'short_url_error'
    except:
        return 'short_url_error'

def get_txt_1(suffix=''):
#######获取日历天气
    tz = pytz.timezone(pytz.country_timezones('cn')[0])
    day=datetime.datetime.now(tz)
    today=day.strftime('%Y-%m-%d')
    p1=re.compile(r"农历是：\d+年(.*)")
    txt_d=get_tuling(p1,'今天农历多少')
    txt_d=txt_d if bool(txt_d) else ''
    time.sleep(1)
    p2=re.compile(r'周.*?,(.*?);')
    txt_w=get_tuling(p2,'沈阳天气')
    txt_w='沈阳天气:'+txt_w if bool(txt_w) else ''
    format_txt='您好,今天是%s%s\n%s\n%s'%(today,txt_d,txt_w,suffix)
    return format_txt

def download_page(url,user_agent='Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',num_retries=2):
#######下载页面   
    headers={'User-Agent':user_agent}
    request=urllib.request.Request(url,headers=headers)
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    try:
        html=urllib.request.urlopen(request).read().decode().translate(non_bmp_map)
    except urllib.error.URLError as e:
        print('Download error:',e.reason)
        html=None
        if num_retries>0:
            if hasattr(e,'code') and 500<=e.code<600:
                return download_page(url,user_agent,num_retries-1)
    return html

def get_share_content(content,is_short_url=False):
#######获取分享url并加入随机emoji
    result=re.findall(r"<item>.*?<title><!\[CDATA\[(.*?)\]\]></title>.*?<url><!\[CDATA\[(.*?)\]\]></url>.*?</item>",content,re.DOTALL)
    if bool(result):
        try:
            res = requests.get('https://api.github.com/emojis').json()
            name_list=['%s\n%s'%(a,get_short_url(b) if is_short_url else b) for (a,b) in result]            
            return ''.join([txt+'\n%s\n'%''.join([re.sub(r":.*?:",'',emoji.emojize(':%s:'%random.choice(list(res)))) for i in range(10)])   for txt in name_list[:-1]]+[name_list[-1]])
        except:
            return

def get_short_url(url):
#######获取短地址    
    apiUrl = 'http://127.0.0.1/for_python.php'
    data = {
        'state'    : 'gh_cac8d916ca22',
        'long_url':url
    }
    try:
        r = requests.post(apiUrl, data=data)
        if bool(r):
            return r.text
        else:
            return 'short_url_server_error'
    except:
        return 'short_url_requests_error'
    
def my_print(txt):
#######系统打印
    tz = pytz.timezone(pytz.country_timezones('cn')[0])
    day=datetime.datetime.now(tz)
    today=day.strftime('%m/%d/%H:%M:%S-')
    print('%s%s\n'%(today,txt))
    
# 初始化机器人，扫码登陆
bot = Bot(cache_path=True,console_qr=True)
bot.enable_puid()
# 这是你现有的 Logger
logger = logging.getLogger(__name__)

# 初始化一个微信 Handler
wechat_handler = WeChatLoggingHandler(bot)
# 加到入现有的 Logger
logger.addHandler(wechat_handler)

logger.warning('登陆成功!')


# 定位puid
dict_puid={}
try:
    chat=ensure_one(bot.groups(contact_only=True).search('16届'))
    dict_puid['16届']=chat.puid
    chat=ensure_one(bot.groups(contact_only=True).search('王家大院'))
    dict_puid['王家大院']=chat.puid
    chat=ensure_one(bot.groups(contact_only=True).search('技术'))
    dict_puid['技术']=chat.puid
    chat=ensure_one(bot.groups(contact_only=True).search('北京沈阳'))
    dict_puid['名称=']=chat.puid
    chat=ensure_one(bot.groups(contact_only=True).search('竖大'))
    dict_puid['竖大']=chat.puid
    chat=ensure_one(bot.friends().search('徐晨'))
    dict_puid['徐晨']=chat.puid

except:
    logger.warning('puid获取失败自动退出')
    sys.exit()
#boss = ensure_one(my_group.search('大名'))
#全局时间调度
sched=''
def new_scheduled():
    global sched
    try:
        sched = BlockingScheduler(timezone='Asia/Shanghai')
        my_print('sched job start!')
        @sched.scheduled_job('cron',id='job_resume_send',hour='4')
        def scheduled_timer():
            global sched
            sched.resume_job(job_id='job_send')
            my_print('job_resume_send')
            
        @sched.scheduled_job('cron',id='job_send',hour='6-8',minute='0-59/13')
        def scheduled_job():
            #itchat.send(''.join(random.choice(string.ascii_lowercase) for i in range(20)),'filehelper')
            #global word_msg
            time.sleep(random.randrange(30,45))
            mp=ensure_one(bot.mps().search('每日天气'))
            mp.send('北京')
            my_print('job_send')
        sched.start()
    except:
        my_print('时间调度出错')
        
t = threading.Thread(target =new_scheduled)
t.start()

# 接受群聊和公众号的消息
@bot.register(Group, TEXT)
def print_gp_txt_msg(msg):
    try:
        global dict_puid                                                  
        school_group = ensure_one(bot.groups().search(puid=dict_puid['16届']))
        my_friend=ensure_one(bot.friends().search(puid=dict_puid['徐晨']))
        teacher = ensure_one(school_group.search('张文宇'))
    except:
        logger.warning('获取群失败')
        return
    if msg.member == teacher:
        time.sleep(random.randrange(1,10))
        msg.forward(my_friend, prefix='张老师发言：')
        msg.forward(bot.file_helper, prefix='张老师发言：')


@bot.register(MP,SHARING)
def print_mp_sharing_msg(msg):
    try:
        global dict_puid 
        work_group=ensure_one(bot.groups().search(puid=dict_puid['技术']))
        tz = pytz.timezone(pytz.country_timezones('cn')[0])
        day=datetime.datetime.now(tz)
    except:
        logger.warning('获取工作群失败')
        return
    if msg.chat.nick_name in ['风云之声','凤凰科技','知乎']:
        time.sleep(random.randrange(1,10))
        txt=get_share_content(msg.raw['Content'],True)
        if bool(txt):
            send_txt='转自%s:\n%s'%(msg.chat.nick_name,txt)
            work_group.send(send_txt)
        else:
            bot.file_helper.send('work_group格式化share失败')
    elif msg.chat.nick_name=='每日天气' and day.hour in [5,6,7,8]:
        global sched
        url_res=re.findall(r"<item>.*?<title><!\[CDATA\[(.*?)\]\]></title>.*?<url><!\[CDATA\[(.*?)\]\]></url>.*?</item>",msg.raw['Content'],re.DOTALL)
        if bool(url_res):
            name,url_find=url_res[0]
        else:
            bot.file_helper.send('day sched url failed')
        html=download_page(url_find)
        try:
            soup=BeautifulSoup(html, "html.parser")
            div=soup.find_all('p')
            for p in div:
                if '【晨曦悟语】' in p.get_text():
                    res=p.next_sibling.get_text()
                    if bool(res):
                        time.sleep(random.randrange(2,5))
                        work_group.send(get_txt_1('%s【晨曦悟语】%s'%('\ue148',res)))
##                        bot.file_helper.send(get_txt_1('%s【晨曦悟语】%s'%('\ue148',res)))
                        sched.pause_job(job_id='job_send')
                        my_print('job paused')
                        return
                    else:
                        time.sleep(random.randrange(1,10))
                        bot.file_helper.send('【晨曦悟语】查找失败!')
                        return
            time.sleep(random.randrange(1,10))
            bot.file_helper.send('未找到【晨曦悟语】')
            return 
        except:
            time.sleep(random.randrange(1,10))
            bot.file_helper.send('【晨曦悟语】获取过程有误')
            return
    else:
        time.sleep(random.randrange(1,10))
        txt=get_share_content(msg.raw['Content'])
        if bool(txt):
            bot.file_helper.send(txt)
        else:
            bot.file_helper.send('格式化share失败')
@bot.register(Group,SHARING)
def print_gp_sharing_msg(msg):
    pass
    
@bot.register(Group,PICTURE)
def print_picture_msg(msg):
    try:
        global dict_puid
        school_group = ensure_one(bot.groups().search(puid=dict_puid['16届']))
        my_friend=ensure_one(bot.friends().search(puid=dict_puid['徐晨']))
        teacher = ensure_one(school_group.search('张文宇'))
    except:
        logger.warning('获取学校群失败')
        return
    if msg.member == teacher:
        time.sleep(random.randrange(1,10))
        msg.forward(my_friend, prefix='张老师发图：')
@bot.register(Group,RECORDING)
def print_recording_msg(msg):
    pass

@bot.register(Group,VIDEO)
def print_video_msg(msg):
    pass
      
       


#bot.join()
embed()
# 最后，堵塞线程，让程序持续运行下去


