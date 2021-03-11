from requests_html import HTMLSession
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import json
import os
import threading
import time
import requests

class Crawler:

    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'
    RED = '\033[91m'
    WHITE = '\033[0m'
    rejections = ['javascript:void(0)', '#', '/./', '/', 'javascript:void(0);', '/#']
    worker_count = 1

    def __init__(self, host: str, rejections: list, targets: list) -> None:
        self.link_collection = []
        self.crawled = []
        self.host = host
        self.session = HTMLSession()
        self.rejections.extend(rejections)
        self.targets = targets
        self.host_crawled = False
        self.download_folder = self.create_download_folder()
        self.browser_options = self.set_browser_options()
        self.crawl_page(self.host)

    def create_download_folder(self) -> None:
        cur_dir = os.getcwd()
        path = '{0}/downloads/{1}'.format(cur_dir, self.host[8:])
        if not os.path.exists(path):
            os.mkdir(path)
        return path
        
    def set_browser_options(self) -> None:
        browser_options = Options()
        browser_options.add_argument("--headless")
        browser_options.add_argument("--no-sandbox")
        browser_options.add_argument("--disable-dev-shm-usage")
        browser_prefs = {"profile.managed_default_content_settings.images": 2, "download.default_directory": self.download_folder}
        browser_options.experimental_options["prefs"] = browser_prefs
        return browser_options

    def is_target(self, url: str) -> bool:
        urlSplitted = url.split('.')
        if len(urlSplitted):
            return (urlSplitted[-1] in self.targets) and (url not in self.crawled)
        return False

    def meaningful_page(self, url: str) -> bool:
        return (url not in self.crawled) and (url+'/' not in self.crawled) and (url+'/#' not in self.crawled) and (url+'#' not in self.crawled) and (url not in self.rejections) and (url.startswith('/') or (self.host in url) and (not len(url.split(".")) > 3))
    
    def has_possible_download_buttons(self, url: str) -> bool:
        driver = webdriver.Chrome(options=self.browser_options)
        driver.get(url)
        buttons = driver.find_elements_by_css_selector("button")
        for button in buttons:
            if 'download' in button.get_attribute('class'):
                print(f"{self.GREEN}clicking possible download button")
                ActionChains(driver).move_to_element(button).click(button).perform()
        driver.close()
        driver.quit()

    def download_explicitly(self, url: str) -> None:
        fileName = url.split('/')[-1]
        resp = requests.get(url)
        with open('{0}/{1}'.format(self.download_folder, fileName), 'wb') as file:
            file.write(resp.content)

    def crawl_page(self, url: str) -> None:
        try:
            if self.meaningful_page(url):
                #     print('{0}got target {1}{2}'.format(self.GREEN, self.host, url))
                #     self.api_docs.append('{0}{1}'.format(self.host, url))
                # if(not self.host_crawled):
                #     self.host_crawled = True
                self.crawled.append(url)
                if url.startswith('/./'):
                    url = "{0}/{1}".format(self.host, url[3:])
                elif url.startswith('./'):
                    url = "{0}/{1}".format(self.host, url[2:])
                elif url.startswith('/'):
                    url = "{0}/{1}".format(self.host, url[1:])
                print('{0}crawling {1}'.format(self.CYAN, url))
                self.has_possible_download_buttons(url)
                r = self.session.get(url)
                r.html.render(sleep=1, keep_page=True, scrolldown=1, timeout=30)
                anchors = r.html.xpath('//a/@href')
                for anchor in anchors:
                    self.crawl_page(anchor)
            elif self.is_target(url):
                print('{0}downloading file explicitly'.format(self.GREEN))
                self.download_explicitly(url)
            else:
                print('{0}rejecting {1}'.format(self.YELLOW, url))
        except Exception as e:
            print('{0}error occurred: {1}'.format(self.RED, e))

start = time.time()
targets = os.getenv('TARGETS', 'json,yaml,yml')
rejections = os.getenv('REJECTIONS', '#,/,/#')
host = os.getenv('HOST', 'https://bankofapis.com')
if host.endswith('/'):
    host = host[:len(host)-1]
crawler = Crawler(host, rejections.split(','), targets.split(','))
end = time.time()
time = end-start
print("finished within {:.2f} s".format(time))
