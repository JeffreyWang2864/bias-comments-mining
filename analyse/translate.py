from selenium import webdriver
import time

chrome_driver_path = "/Users/Excited/chromedriver"
translator_path = "http://fanyi.youdao.com/"

class Translator:
    def __init__(self):
        self.driver = webdriver.Chrome(chrome_driver_path)

    def open_web_translator(self):
        self.driver.get(translator_path)

    def get_translation(self, word):
        assert isinstance(word, str)
        self.driver.find_element(by="inputOriginal").send_keys(word)

