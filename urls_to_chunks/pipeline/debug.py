from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
from urllib.parse import urlparse

# 更新后的新 Cookie 字符串
COOKIE_STR = ("Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1774610400,1774611461,1774616497; "
              "HMACCOUNT=D2D5ADE59D6F801B; cookieUUID=cookieUUID_1774616497520; "
              "WEIXIN_APP_LOGIN_KEY=c5632b92-fdc1-4ab7-9e75-5a4cdf14eeda; "
              "CookieId=59efe6c9cdab3036ee92553c0eadf905; SUB=b66a378d-a3b2-49e6-8de5-d9dc7188c243; "
              "preferred_username=phone202512221741514086; loginType=weixin; "
              "session_state=69e5bed7-d51b-40eb-b5ec-41ccf7810450; UserAuthAssetAid=; "
              "Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1774616514; "
              "Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2201%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22f3c34106-fd7b-4820-8e28-31c242554e78%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D")


def fetch_page_with_cookies(target_url, cookie_str, chromedriver_path=None, headless=False):
    """
    改进版：解决 Cookie 注入无效的问题
    """
    chrome_options = Options()

    # 调试建议：如果显示未登录，先将 headless 设为 False，肉眼观察页面状态
    if headless:
        chrome_options.add_argument('--headless')

    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = None
    try:
        if chromedriver_path is None:
            # 自动寻找驱动路径逻辑（保持原样）
            possible_paths = [r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe',
                              r'./driver/chromedriver.exe', 'chromedriver.exe']
            for path in possible_paths:
                if os.path.exists(path):
                    chromedriver_path = path
                    break

        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 隐藏自动化特征
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

        # --- 【关键修改 1：建立域名上下文】 ---
        # 必须先访问一次域名，才能添加该域名的 Cookie
        parsed_url = urlparse(target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        print(f"正在建立域名连接: {base_url}")
        driver.get(base_url)
        time.sleep(2)  # 等待页面加载，确保域名被浏览器识别

        # --- 【关键修改 2：健壮的 Cookie 解析与注入】 ---
        print("正在注入登录凭证...")
        # 清除当前域名下可能存在的旧 Cookie（防止冲突）
        driver.delete_all_cookies()

        cookie_list = [c.strip() for c in cookie_str.split(';') if c.strip()]
        for item in cookie_list:
            if '=' in item:
                # 只拆分第一个等号，防止 value 中包含等号导致错误
                name, value = item.split('=', 1)
                try:
                    driver.add_cookie({
                        'name': name.strip(),
                        'value': value.strip(),
                        'path': '/',  # 通常设置为根路径
                        # 如果是跨域，有时需要指定 'domain': parsed_url.netloc
                    })
                except Exception as e:
                    print(f"✗ 注入 {name} 失败: {e}")

        # --- 【关键修改 3：再次跳转至目标 URL】 ---
        print(f"凭证注入完成，正在跳转目标页面: {target_url}")
        driver.get(target_url)

        # 等待 body 加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 模拟滚动以触发动态内容
        print("执行页面滚动以触发懒加载...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # 获取最终源码
        page_html = driver.execute_script("return document.documentElement.outerHTML;")

        # 简单检查是否包含“登录”字样（可选，用于验证注入是否成功）
        if "请登录" in page_html or "立即登录" in page_html:
            print("⚠️  警告：页面似乎仍显示未登录状态，请检查 Cookie 是否过期或被封禁。")
        else:
            print("✅ 页面登录态检测正常（未发现明显登录提示）")

        print(f"\n成功获取内容，长度: {len(page_html)}")
        return page_html

    except Exception as e:
        print(f"程序运行出错: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")


# 调用示例
if __name__ == "__main__":
    url = "L"
    # 测试时建议先 headless=False
    content = fetch_page_with_cookies(url, COOKIE_STR, headless=False)