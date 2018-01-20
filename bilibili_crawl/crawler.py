import re
import requests
from bs4 import BeautifulSoup as bs
from analyse import outputer
import util
from threading import Event, Thread
from concurrent.futures import ThreadPoolExecutor as tpe

class UrlManager:

    def __init__(self):
        self.archived_url = set()
        self.queue = set()

    def addNewUrl(self, urls):
        if urls is None:
            return
        if isinstance(urls, list) or isinstance(urls, tuple):
            urls = list(filter(lambda item: item != "javascript:;", urls))
            new_urls = set(urls) - (set(urls) & self.archived_url)
            self.queue = self.queue | new_urls
        else:
            if urls not in self.archived_url:
                if urls == "javascript:;":
                    return
                self.queue.add(urls)

    def isEmpty(self):
        return len(self.queue) == 0

    def getUrl(self):
        ret = self.queue.pop()
        self.archived_url.add(ret)
        return ret

    def getUrls(self):
        self.archived_url.update(self.queue)
        ret = list(self.queue)
        self.queue = set()
        return ret

class Crawler:

    def __init__(self, start_url, country):
        assert isinstance(start_url, str)
        self.start_url = start_url
        self.thread_pool_size = 4
        self.suffix = "&page="
        self.home_page_number = 50
        self.trigger = Event()
        self.outputer = outputer.Outputer(self.trigger)
        self.outputer.current_country = country
        self.url_manager = UrlManager()

    def downloadComments(self, url):
        try:
            av = re.search(r"av(\d+)", url).group(1)
            url = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=1&oid=" + av + "&sort=0&_=1496477384198"
            return requests.get(url).text
        except:
            Warning("downloadComments error")

    def downloadMainPage(self, url):
        try:
            res = requests.get(url)
            return res.text
        except:
            Warning("downloadMainPage error")

    def downloadDanmu(self, url):
        try:
            url = re.search(r"www.bilibili.com/video/av\d+", url).group()
            headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)", }
            u = requests.get(url= "https://" + url, headers=headers)
            html = u.text
            return html
        except:
            Warning("downloadDanmu error")

    def parseComments(self, html):
        contents = re.findall('"uname":"(.*?)","sex":.*?"content":{"message":"(.*?)","plat"', html)
        return util.polishChineseSentences(contents)

    def parseDammu(self, html):
        cid = re.findall(r'cid=(.*?)&aid=', html)[0]
        dmurl = "http://comment.bilibili.com/" + str(cid) + ".xml"
        dmhtml = requests.get(dmurl).text
        soup = bs(dmhtml, 'xml')
        dmlist = soup.find_all('d')
        return util.polishChineseSentences(dmlist)

    def parseMainPage(self, html):
        bsp = bs(html, 'html.parser', from_encoding='utf8')
        videosSelector = bsp.find_all('li', class_="video matrix ")
        videoLinks = list()
        for video in videosSelector:
            videoLinks.append(video.a["href"])
        return videoLinks

    def startCrawl(self):
        def _check_if_enough_data_in_outputer():
            if self.outputer.current_count > self.outputer.buffer_size:
                self.trigger.set()

        def crawlHomePage(i):
            print("crawling bilibili homepage number %d"%i)
            mainPage = self.downloadMainPage(self.start_url + self.suffix + str(i))
            videoLinks = self.parseMainPage(mainPage)
            self.url_manager.addNewUrl(videoLinks)

        def dammuParsing(current):
            print("crawling dammu: %s"%current)
            danmu_page_source = self.downloadDanmu(current)
            danmus = self.parseDammu(danmu_page_source)
            self.outputer.collect_data(danmus)
            _check_if_enough_data_in_outputer()

        def commentsParsing(current):
            print("crawling comments: %s" % current)
            comments_page_source = self.downloadComments(current)
            comments = self.parseComments(comments_page_source)
            self.outputer.collect_data(comments)
            _check_if_enough_data_in_outputer()

        try:
            writing_thread = Thread(target=self.outputer.export_data, args=(None, None))
            writing_thread.start()
            current_home_page = 1
            crawlHomePage(current_home_page)
            while not self.url_manager.isEmpty():
                executor = tpe(self.thread_pool_size)
                currents = self.url_manager.getUrls()
                executor.map(dammuParsing, currents)
                executor.map(commentsParsing, currents)
                executor.shutdown(wait=True)
                if current_home_page + 1 < self.home_page_number:
                    current_home_page += 1
                    crawlHomePage(current_home_page)
                util.print_progress("bilibili", current_home_page/self.home_page_number)
                util.rest(2)
        except:
            Warning("crawl bilibili forced to end")
        finally:
            self.outputer.end_writing = True
            self.trigger.set()
            writing_thread.join()
            print("crawler closed.\n total data collected: %d"%self.outputer.total_count)