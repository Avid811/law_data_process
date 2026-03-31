# config.py
# Cookie配置
# 建议使用三引号，防止字符串内包含特殊字符导致闭合错误
COOKIE_STR = ("pkulaw_v6_sessionid=qscgelwz2wjvduodmahi5hxp; cookieUUID=cookieUUID_1774945903868; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1774610400,1774611461,1774616497,1774945904; HMACCOUNT=D2D5ADE59D6F801B; WEIXIN_APP_LOGIN_KEY=1dcf562f-f9a9-4917-8960-bb73e676469a; CookieId=0795161c24a554b3785481901615cb70; SUB=3b62b06e-57fb-4786-856f-b556d6e7d4dc; preferred_username=carsi202603311630032454; loginType=carsi; session_state=7a9902ef-5a10-44f5-b95c-aedacbf2d552; userislogincookie=always; LoginAccount=carsi202603311630032454; UserAuthAssetAid=fc8a1d87-2a49-479e-abe7-5c67b582ed6d; authormes=f6e66a42fbf6894468531b5bd631bf20a9a3d4259b8b3d8c10ef73dbffb8c5fbafd7b55d56b710f4bdfb; Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2206%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22b573e91f-cd09-4e87-92db-c4fcddbf2e2c%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D; xCloseNew=1; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1774945953")
# ChromeDriver路径配置
CHROMEDRIVER_PATH = r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe'

# 其他配置
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DEFAULT_WINDOW_SIZE = '1920,1080'

# 超时设置
PAGE_LOAD_TIMEOUT = 30
IMPLICIT_WAIT_TIME = 10
SLEEP_AFTER_REFRESH = 5