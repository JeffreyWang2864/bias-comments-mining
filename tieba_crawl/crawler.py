from bs4 import BeautifulSoup as bs
from analyse import outputer
import util
from threading import Event, Thread
from concurrent.futures import ThreadPoolExecutor as tpe
from bilibili_crawl.crawler import UrlManager
from analyse import outputer
import re
import requests
from urllib import request

class Crawler:

    def __init__(self, url_tieba_start_name, tieba_start_page):
        assert isinstance(tieba_start_page, str)
        self.start_url = tieba_start_page
        self.thread_pool_size = 16
        self.main_page_body = "http://tieba.baidu.com/f?kw=%s&pn="%url_tieba_start_name
        self.interval_between_pages = 50
        self.page_end_suffix_number = -1
        self.trigger = Event()
        self.outputer = outputer.Outputer(self.trigger)
        self.url_manager = UrlManager()

    def _get_sub_page_full_url(self, page, start = 30):
        url = "https://tieba.baidu.com/mo/q----,sz@320_240-1-3---2/m?kz=%s&new_word=&pn=%s&lp=6005"%(page, start)
        return url

    def downloadMainPage(self, url):
        try:
            suffix = re.search("&pn=(\d+)", url).group(1)
            url = self.main_page_body + suffix
            return requests.get(url).text
        except:
            Warning("downloadMainPage Error")

    def downloadSubPage(self, url, return_url = False):
        try:
            page_number = re.search("p/(\d+)", url).group(1)
            url = self._get_sub_page_full_url(page_number)
            if return_url:
                return requests.get(url).text, url
            return requests.get(url).text
        except:
            Warning("downloadSubPage Error")

    def parseMainPage(self, html,  get_end_suffix = False):
        try:
            cells_url = list()
            soup = bs(html, 'html.parser')
            cells = soup.find_all("div", class_="threadlist_title pull_left j_th_tit ")
            for cell in cells:
                cells_url.append(cell.a['href'])
            if not get_end_suffix:
                return cells_url
            last_url_cell = soup.find("a", class_="last pagination-item ")['href']
            self.page_end_suffix_number = int(re.search("pn=(\d+)", last_url_cell).group(1))
            return cells_url
        except:
            Warning("parseMainPage Error")

    def parseSubPage(self, html, current_url):
        try:
            soup = bs(html, 'html.parser')
            raw_cells = soup.find_all("div", class_="i")
            if len(raw_cells) < 5:
                return list()
            for i in range(len(raw_cells)):
                raw_cells[i] = re.search("\d+楼. (.+)", raw_cells[i].find(text=True)).group(1)
            _next_page_find = soup.find("div", class_="h")
            next_page_target = _next_page_find.a if _next_page_find else None
            while next_page_target is not None and next_page_target.text == "下一页":
                next_page_partial_url = next_page_target['href']
                next_page_url = request.urljoin(current_url, next_page_partial_url)
                html = requests.get(next_page_url).text
                soup = bs(html, 'html.parser')
                current_raw_cells = soup.find_all("div", class_="i")
                if len(current_raw_cells) < 5:
                    break
                for i in range(len(current_raw_cells)):
                    if hasattr(current_raw_cells[i], "text"):
                        current_raw_cells[i] = re.search("\d+楼.\ *(.+)", current_raw_cells[i].find(text=True)).group(1)
                    else:
                        with open("/Users/Excited/Desktop/temp.html", "w") as f:
                            f.write(html)
                        raise ValueError()
                raw_cells.extend(current_raw_cells)
                _next_page_find = soup.find("div", class_="h")
                next_page_target = _next_page_find.a if _next_page_find else None
            return util.polishChineseSentences(raw_cells)
        except:
            Warning("parseSubPage Error")

    def startCrawl(self):
        def _check_if_enough_data_in_outputer():
            if self.outputer.current_count > self.outputer.buffer_size:
                self.trigger.set()

        def crawlSubPage(current):
            try:
                print("crawling detail: %s" % current)
                comments_page_source, polished_url = self.downloadSubPage(current, return_url=True)
                comments = self.parseSubPage(comments_page_source, polished_url)
                self.outputer.collect_data(comments)
                _check_if_enough_data_in_outputer()
            except:
                Warning("cannot get %s"%current)

            def _check_url_availability(self):
                rest_count = 0
                while self.url_manager.isEmpty():
                    print("It seems like url_manager is empty. The program pauses for 20 seconds")
                    util.rest(20)
                    rest_count += 1
                    if rest_count > 10:
                        print("The program will end because there's no enough url")
                        return True
                return False

        try:
            writing_thread = Thread(target=self.outputer.export_data, args=(None, None))
            writing_thread.start()
            current_main_page_end_index = 0
            main_page_html = self.downloadMainPage(self.start_url)
            subpage_raw_urls = self.parseMainPage(main_page_html, get_end_suffix=True)
            self.url_manager.addNewUrl(subpage_raw_urls)
            self.page_end_suffix_number = int(self.page_end_suffix_number * 0.33)
            executor = tpe(self.thread_pool_size)
            while True:
                if _check_if_enough_data_in_outputer():
                    break
                currents = self.url_manager.getUrls()
                executor.map(crawlSubPage, currents)
                if current_main_page_end_index < self.page_end_suffix_number:
                    current_main_page_end_index += self.interval_between_pages
                    main_page_html = self.downloadMainPage("&pn=" + str(current_main_page_end_index))
                    subpage_raw_urls = self.parseMainPage(main_page_html)
                    self.url_manager.addNewUrl(subpage_raw_urls)
                    util.print_progress("tieba", current_main_page_end_index/self.page_end_suffix_number)
                    util.rest(2)
                else:
                    break
        except:
            Warning("crawling tieba forced to end")
        executor.shutdown(wait=True)
        self.outputer.end_writing = True
        self.trigger.set()
        writing_thread.join()
        print("crawler closed.\n total data collected: %d" % self.outputer.total_count)