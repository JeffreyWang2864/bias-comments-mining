import bilibili_crawl.crawler
import tieba_crawl.crawler
from threading import Event
from threading import Thread
from analyse import count
from urllib import parse
import datetime
import os

desktop_path = "/Users/Excited/Desktop/"
os.chdir(desktop_path)
f = open("./crawl_log.txt", "w")
strap = "\n==========================================\n"

CURRENT_COUNTRY = "black"
CURRENT_COUNTRY_CHINESE = "黑人"

string_for_log = "\n\nprogram started time: %s\n\n"%str(datetime.datetime.now())
f.write(strap)
f.write(string_for_log)
f.write(strap)
print(strap)
print(string_for_log)
print(strap)

def run_bilibili():
    bilibili_start_url = "https://search.bilibili.com/all?keyword=%s"%CURRENT_COUNTRY_CHINESE
    bilibili = bilibili_crawl.crawler.Crawler(bilibili_start_url, CURRENT_COUNTRY)
    bilibili.startCrawl()
    string_for_log = "\n\nbilibili finished time: %s\n\n" % str(datetime.datetime.now())
    f.write(strap)
    f.write(string_for_log)
    f.write(strap)
    print(strap)
    print(string_for_log)
    print(strap)

def run_tieba():
    tieba_start_page = "&pn=0"
    tieba_start_name = CURRENT_COUNTRY_CHINESE
    url_tieba_start_name = parse.quote(tieba_start_name)
    tieba = tieba_crawl.crawler.Crawler(url_tieba_start_name, tieba_start_page, CURRENT_COUNTRY)
    tieba.startCrawl((20000, 80000))
    string_for_log = "\n\ntieba finished time: %s\n\n"%str(datetime.datetime.now())
    f.write(strap)
    f.write(string_for_log)
    f.write(strap)
    print(strap)
    print(string_for_log)
    print(strap)

# bilibili_thread = Thread(target=run_bilibili)
# bilibili_thread.start()
tieba_thread = Thread(target=run_tieba)
tieba_thread.start()
# bilibili_thread.join()
tieba_thread.join()


def enable_treatment():
    if CURRENT_COUNTRY == "korea":
        word_count.korea_treatment()
    elif CURRENT_COUNTRY == "japan":
        word_count.japan_treatment()
    elif CURRENT_COUNTRY == "india":
        word_count.india_treatment()

# word_count = count.CountWords("demo", "racism_word_frequency_%s"%CURRENT_COUNTRY, CURRENT_COUNTRY)
# word_count.add_dictionary_from(count.custom_dictionary)
# word_count.get_all_data_file_name()
# word_count.read_from_file_and_count()
# word_count.filter_frequency_with(count.filters)
# enable_treatment()
# word_count.make_wordcloud("/image/%s-wordcloud-background.png"%CURRENT_COUNTRY)
# word_count.save_frequency_to_sql()

string_for_log = "\n\nprogram finished time: %s\n\n"%str(datetime.datetime.now())
f.write(strap)
f.write(string_for_log)
f.write(strap)
print(strap)
print(string_for_log)
print(strap)

f.close()
