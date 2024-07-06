
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
import logging
import re
import argparse
import cleantext
import time


def get_browser_preferences():
    yield "dom.push.enabled", False

def get_driver():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
 #   options.add_argument("dom.push.enabled", False)
    fp = webdriver.FirefoxProfile()
    for k, v in get_browser_preferences():
        fp.set_preference(k, v)
    return webdriver.Firefox(firefox_profile=fp)
    

class TVScraper:
    def safe_find_element_by_id(self, elem_id):
        try:
            return self.driver.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def __init__(self):
        self.driver = get_driver()
        self.driver.implicitly_wait(5);

    def login(self, email, password):
        cvdm_path = "https://login.spotr.media"
        self.driver.get(cvdm_path)
        self.driver.maximize_window()
        #self.driver.find_element_by_id('u_0_h').click()

        self.driver.find_element("id",'UserName').send_keys(username)
        self.driver.find_element("id",'Password').send_keys(password)
        self.driver.find_element("css selector", "input.ui-button").click()

    def setup(self):
        self.driver.find_element("xpath", "//collapse-panel-vertical/div/h2[contains(text(), 'Browse')]").click()
        self.driver.find_element("css selector", 'span.ui-selectmenu-text').click()
        #self.driver.find_element("xpath", "//ui-menu-item/li/div[containt(text(),'RTV Oost')]").click()
        self.driver.find_element("xpath", "//div[@class='ui-menu-item-wrapper' and contains(text(), 'NOS Journaal')]").click()
        self.driver.find_element("xpath", "//span[@class='ui-button-text' and contains(text(), 'Export')]").click()
    
    def playlist(self, naam):
        element = self.driver.find_element("xpath", "//div[@class='input']/base-textbox/input[@placeholder='Playlist name']")
        element.send_keys(naam)


    def collect_items(self, datum, begintijd, eindtijd):
        elements = self.driver.find_elements("xpath", "//custom-button[@class='set']")
        elements[0].click()
        elements[1].click()
        time.sleep(2)
        print(begintijd, eindtijd)
        element = self.driver.find_elements("xpath", "//base-textbox[@class='datetime']/input")
        input_clear_and_value(element[0], begintijd)
        input_clear_and_value(element[1], eindtijd)
        element = self.driver.find_element("xpath", "//div[@class='input']/base-textbox/input")
        element.send_keys(datum)
        self.driver.find_element("xpath", "//span[@class='ui-button-text' and contains(text(), 'Add to playlist')]").click()
        self.driver.implicitly_wait(2)
        

    def export(self):
        elements = self.driver.find_elements("xpath", "//div[@class='export-action-selector']/selectbox/span")
        elements[1].click()
        elements = self.driver.find_elements("xpath", "//div[text() = 'Export 576p' and @role = 'option']")
        elements[1].click()
        self.driver.find_element("xpath", "//span[@class='ui-button-text' and contains(text(), 'Export playlist')]").click()


def input_clear_and_value(element, value):
    while element.get_attribute('value') != value:
        element.click()
        while element.get_attribute('value'):
            element.clear() 
            time.sleep(1)
        time.sleep(1)
        element.send_keys(value)


def get_datums():
    maand = range(1,3)
    dag = range(1,32)
    for m in maand:
        for d in dag:
            begintijd = f"{m}/{d}/2023 5:00:00:00 PM"
            eindtijd = f"{m}/{d}/2023 6:00:00:00 PM"
            datum = f"{m}/{d}"
            print(datum, begintijd, eindtijd)
            yield begintijd, eindtijd, datum

if __name__ == '__main__':
    username = "CVDM07"
    password = "HufrDBe36NnrFQ2c"
    scraper = TVScraper()
    scraper.login(username, password)
    scraper.setup()
    scraper.playlist("avondspits")
    for begintijd,eindtijd, datum in get_datums():
        time.sleep(2)
        scraper.collect_items(datum, begintijd,eindtijd)
    scraper.export()

