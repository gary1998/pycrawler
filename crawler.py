import json
import sys
import os

import requests
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class Crawler:

    rejections = ['javascript:void(0)', '#', '/./',
                  '/', 'javascript:void(0);', '/#']

    def __init__(self, host: str, rejections: list, targets: list, logging: int) -> None:
        self.link_collection = []
        self.crawled = []
        self.host = host
        self.session = HTMLSession()
        self.rejections.extend(rejections)
        self.targets = targets
        self.host_crawled = False
        self.download_folder = self.create_download_folder()
        self.browser_options = self.set_browser_options()
        self.logging = False
        if int(logging)>0:
            self.logging = True
        self.result = {
            'logs': [],
            'downloadDir': self.download_folder,
            'errors': []
        }

    def start_crawling(self):
        self.crawl_page(self.host)
        print(json.dumps(self.result))

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
        browser_prefs = {"profile.managed_default_content_settings.images": 2,
                         "download.default_directory": self.download_folder}
        browser_options.experimental_options["prefs"] = browser_prefs
        return browser_options

    def is_target(self, url: str) -> bool:
        urlSplitted = url.split('.')
        if len(urlSplitted):
            return (urlSplitted[-1] in self.targets) and (url not in self.crawled)
        return False

    def meaningful_page(self, url: str) -> bool:
        extension = url.split('/')[-1].split('.')[-1]
        if extension in self.targets:
            self.result['logs'].append(f"downloading {url} explicitly")
            self.download_explicitly(url)
            return False
        return (url not in self.crawled) and (url+'/' not in self.crawled) and (url+'/#' not in self.crawled) and (url+'#' not in self.crawled) and (url not in self.rejections) and (url.startswith('/') or (self.host in url))

    def has_possible_download_buttons(self, url: str) -> bool:
        driver = webdriver.Chrome(options=self.browser_options)
        driver.get(url)
        buttons = driver.find_elements_by_css_selector("button")
        for button in buttons:
            if 'download' in button.get_attribute('class') or 'download' in button.get_attribute('innerHTML') or 'Download' in button.get_attribute('innerHTML'):
                if self.logging:
                    self.result['logs'].append(f"clicking possible download button")
                ActionChains(driver).move_to_element(
                    button).click(button).perform()
        driver.close()
        driver.quit()

    def download_explicitly(self, url: str) -> None:
        if url.startswith('/./'):
            url = "{0}/{1}".format(self.host, url[3:])
        elif url.startswith('./'):
            url = "{0}/{1}".format(self.host, url[2:])
        elif url.startswith('/'):
            url = "{0}/{1}".format(self.host, url[1:])
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
                if self.logging:
                    self.result['logs'].append(f'crawling {url}')
                self.has_possible_download_buttons(url)
                r = self.session.get(url)
                r.html.render(sleep=1, keep_page=True,
                              scrolldown=1, timeout=3000)
                anchors = r.html.xpath('//a/@href')
                for anchor in anchors:
                    self.crawl_page(anchor)
            # elif self.is_target(url):
            #     print('{0}downloading file explicitly'.format(self.GREEN))
            #     self.download_explicitly(url)
            else:
                if self.logging:
                    self.result['logs'].append(f'rejecting {url}')
        except Exception as e:
            if self.logging:
                self.result['errors'].append(f'error occurred: {e}')

host = sys.argv[1]
rejections = sys.argv[2]
targets = sys.argv[3]
logging = sys.argv[4]
crawler = Crawler(host, rejections.split(','), targets.split(','), logging)
crawler.start_crawling()
