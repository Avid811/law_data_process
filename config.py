# config.py
# Cookie配置
COOKIE_STR = ("cookieUUID=cookieUUID_1773564624542; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1773564625; "
              "HMACCOUNT=36328603FC75B06D; UserAuthAssetAid=fc8a1d87-2a49-479e-abe7-5c67b582ed6d; "
              "KEYCLOAK_EXIT_LEGACY=1; KEYCLOAK_EXIT=1; WEIXIN_APP_LOGIN_KEY=15ae4280-6a98-43a3-be78-2d8da4340e70; "
              "CookieId=991175bc52a44987df866e2446cfe162; SUB=b66a378d-a3b2-49e6-8de5-d9dc7188c243; "
              "preferred_username=phone202512221741514086; loginType=weixin; "
              "session_state=accd927d-4b94-45f4-843c-b353b625034c; activeRegisterSource=Sidebar; "
              "Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2206%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22f3c34106-fd7b-4820-8e28-31c242554e78%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D; "
              "Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1773565550")

# ChromeDriver路径配置
CHROMEDRIVER_PATH = r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe'

# 其他配置
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DEFAULT_WINDOW_SIZE = '1920,1080'

# 超时设置
PAGE_LOAD_TIMEOUT = 30
IMPLICIT_WAIT_TIME = 10
SLEEP_AFTER_REFRESH = 5