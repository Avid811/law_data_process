# config.py
# Cookie配置
# 建议使用三引号，防止字符串内包含特殊字符导致闭合错误
COOKIE_STR = ("path=/; __tst_status=2830935573#; EO_Bot_Ssid=4019388416; referer=; div_display=none; xCloseNew=28; f3c34106-fd7b-4820-8e28-31c242554e78_law=false; isTip_topSub=true; pkulaw_v6_sessionid=cacnwn0rm0iii1zqb1p3p4tg; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1774610400,1774611461,1774616497; HMACCOUNT=D2D5ADE59D6F801B; cookieUUID=cookieUUID_1774616497520; WEIXIN_APP_LOGIN_KEY=c5632b92-fdc1-4ab7-9e75-5a4cdf14eeda; CookieId=59efe6c9cdab3036ee92553c0eadf905; SUB=b66a378d-a3b2-49e6-8de5-d9dc7188c243; preferred_username=phone202512221741514086; loginType=weixin; session_state=69e5bed7-d51b-40eb-b5ec-41ccf7810450; userislogincookie=always; LoginAccount=phone202512221741514086; UserAuthAssetAid=; authormes=2f758d9d4465d21a82bc9eacabca00a5d60b6614e631b995a860a8fa91af155b0ee6265cb2c89daebdfb; Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2201%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22f3c34106-fd7b-4820-8e28-31c242554e78%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1774617434")
# ChromeDriver路径配置
CHROMEDRIVER_PATH = r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe'

# 其他配置
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DEFAULT_WINDOW_SIZE = '1920,1080'

# 超时设置
PAGE_LOAD_TIMEOUT = 30
IMPLICIT_WAIT_TIME = 10
SLEEP_AFTER_REFRESH = 5