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

string_for_log = "\n\nprogram started time: %s\n\n"%str(datetime.datetime.now())
f.write(strap)
f.write(string_for_log)
f.write(strap)
print(strap)
print(string_for_log)
print(strap)

# bilibili_start_url = "https://search.bilibili.com/all?keyword=韩国"
# bilibili = bilibili_crawl.crawler.Crawler(bilibili_start_url)
# bilibili_thread = Thread(target=bilibili.startCrawl)
# bilibili_thread.start()

# tieba_start_page = "&pn=0"
# tieba_start_name = "韩国"
# url_tieba_start_name = parse.quote(tieba_start_name)
# tieba = tieba_crawl.crawler.Crawler(url_tieba_start_name, tieba_start_page)
# #tieba_thread = Thread(target=tieba.startCrawl)
# #tieba_thread.start()
#
#
# tieba.startCrawl((60000, -1))

# bilibili_thread.join()
# string_for_log = "\n\nbilibili finished time: %s\n\n"%str(datetime.datetime.now())
# f.write(strap)
# f.write(string_for_log)
# f.write(strap)
# print(strap)
# print(string_for_log)
# print(strap)

# tieba_thread.join()
# string_for_log = "\n\ntieba finished time: %s\n\n"%str(datetime.datetime.now())
# f.write(strap)
# f.write(string_for_log)
# f.write(strap)
# print(strap)
# print(string_for_log)
# print(strap)

word_count = count.CountWords("demo", "racism_word_frequency")
word_count.add_dictionary_from(count.custom_dictionary)
word_count.get_all_data_file_name()
word_count.read_from_file_and_count()
word_count.filter_frequency_with(count.filters)
#word_count.save_frequency_to_sql()

string_for_log = "\n\nprogram finished time: %s\n\n"%str(datetime.datetime.now())
f.write(strap)
f.write(string_for_log)
f.write(strap)
print(strap)
print(string_for_log)
print(strap)

word_count.make_wordcloud("/image/korea-wordcloud-background.png")