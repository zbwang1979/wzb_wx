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
    #群查找
    chat=ensure_one(bot.groups(contact_only=True).search('xx'))
    dict_puid['xx']=chat.puid
    #好友查找
    chat=ensure_one(bot.friends().search('xxx'))
    dict_puid['xxx']=chat.puid

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
            
        @sched.scheduled_job('cron',id='job_send',hour='6-8',minute='0-59/13')
        def scheduled_job():
            #itchat.send(''.join(random.choice(string.ascii_lowercase) for i in range(20)),'filehelper')
            #global word_msg
        sched.start()
    except:
        my_print('时间调度出错')
        
t = threading.Thread(target =new_scheduled)
t.start()

# 接受群聊和公众号的消息
@bot.register(Group, TEXT)
def print_gp_txt_msg(msg):
    pass


@bot.register(MP,SHARING)
def print_mp_sharing_msg(msg):
    pass

@bot.register(Group,SHARING)
def print_gp_sharing_msg(msg):
    pass
    
@bot.register(Group,PICTURE)
def print_picture_msg(msg):
    pass

@bot.register(Group,RECORDING)
def print_recording_msg(msg):
    pass

@bot.register(Group,VIDEO)
def print_video_msg(msg):
    pass
      
       


#bot.join()
embed()
# 最后，堵塞线程，让程序持续运行下去


