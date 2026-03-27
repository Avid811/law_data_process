from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os


def fetch_page_with_cookies(target_url, cookie_str, chromedriver_path=None, headless=True):
    """
    使用Selenium自动化浏览器获取指定URL的页面内容
    """
    # 配置Chrome选项
    chrome_options = Options()

    # 是否启用无头模式
    if headless:
        chrome_options.add_argument('--headless')

    # 禁用自动化控制特征，避免被检测
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 添加常见的用户代理
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # 其他有用的选项
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = None
    try:
        # 如果没有提供chromedriver路径，则尝试自动查找
        if chromedriver_path is None:
            possible_paths = [
                r'C:\Users\Administrator\PycharmProjects\FinalHomeWork\driver\chromedriver.exe',
                r'./driver/chromedriver.exe',
                r'./chromedriver.exe',
                'chromedriver.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    chromedriver_path = path
                    break

            if chromedriver_path is None or not os.path.exists(chromedriver_path):
                raise FileNotFoundError(f"未找到chromedriver.exe文件。请检查文件路径。")

        print(f"正在启动Chrome浏览器 (使用chromedriver: {chromedriver_path})...")
        service = Service(executable_path=chromedriver_path)

        # 初始化Chrome驱动
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 执行CDP命令，进一步隐藏自动化特征
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })

        print(f"正在访问URL: {target_url}")
        driver.get(target_url)

        # 添加cookie到浏览器
        print("\n正在添加cookie...")
        # 先按分号拆分，再处理每个键值对
        items = [i.strip() for i in cookie_str.split(';') if i.strip()]

        for item in items:
            if '=' in item:
                # 限制只拆分第一个等号，防止 value 里面包含等号导致报错
                name, value = item.split('=', 1)
                cookie_dict = {
                    'name': name.strip(),
                    'value': value.strip(),
                    # 也可以尝试指定 domain，如果还是失效的话
                    # 'domain': '.yourdomain.com'
                }
                try:
                    driver.add_cookie(cookie_dict)
                except Exception as e:
                    print(f"✗ 添加cookie失败 {name.strip()}: {e}")

        # 刷新页面以使cookie生效
        print("刷新页面以使cookie生效...")
        driver.refresh()

        # 【修改点1】显式等待：等待页面主体加载完成，而不是死等
        print("等待页面加载完成...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 【修改点2】模拟滚动：滚动到页面底部，触发可能存在的懒加载/异步数据请求
        print("模拟向下滚动以触发动态加载...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 给网络请求留一点缓冲时间

        # 再滚动回顶部（有些页面的数据可能需要这样触发）
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # 【修改点3】获取源码：使用 JS 获取整个 DOM 的 outerHTML
        # 这种方式比 driver.page_source 更稳定，不容易在长文本属性处截断
        page_html = driver.execute_script("return document.documentElement.outerHTML;")

        print("\n" + "=" * 50)
        print("页面获取成功!")
        print(f"页面内容长度: {len(page_html)} 字符")
        print("=" * 50)

        return page_html

    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if driver:
            try:
                driver.quit()
                print("浏览器已关闭")
            except:
                pass