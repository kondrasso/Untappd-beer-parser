import os
import json
import pandas as pd
from time import sleep
from selenium import common
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
# from tqdm import tqdm
# import random


class ButtonPresser(object):
    """
    TODO
    """

    def __init__(self, driver, button_text='Show More Beers', sleep_time=1):
        self.drv = driver
        self.button_text = button_text
        self.sleep_time = sleep_time
        self.buttons_left = True
        self.banner = None
        self.buttons = None

    def banner_cutter(self):
        try:
            self.banner = self.drv.find_element_by_xpath('//*[contains(@class, "branch-animation")]')
            self.drv.execute_script("arguments[0].style.visibility='hidden'", self.banner)
            sleep(self.sleep_time)
        except (common.exceptions.NoSuchElementException,
                common.exceptions.ElementNotInteractableException):
            pass
        return None

    def press_all_buttons(self):
        sleep(5)
        while self.buttons_left:
            self.banner_cutter()
            sleep(1)
            self.drv.execute_script("window.scrollTo(0,Math.max(document.documentElement."
                                    "scrollHeight,document.body.scrollHeight,document.documentElement.clientHeight));")
            try:
                self.buttons = self.drv.find_elements_by_xpath('//*[contains(text(),"{}")]'.format(self.button_text))
            except common.exceptions.NoSuchElementException:
                self.buttons_left = False
            for self.button in self.buttons:
                sleep(self.sleep_time)
                self.drv.execute_script("window.scrollTo(0,Math.max(document.documentElement."
                                        "scrollHeight,document.body.scrollHeight,document."
                                        "documentElement.clientHeight));")
                sleep(self.sleep_time)
                try:
                    WebDriverWait(self.drv, 6).until(ec.element_to_be_clickable((By.XPATH,
                                                                                 '//*[contains(text(),'
                                                                                 '"{}")]'.format(self.button_text))))
                    self.drv.execute_script("arguments[0].click();", self.button)
                except common.exceptions.TimeoutException:
                    self.buttons_left = False


class LoginProcess(object):
    """
    Login to facebook & untappd for acquiring access to data from website via Selenium webdriver
    """

    def __init__(self, driver, userdata_path, sleep_time=1):
        """
        Grabbing login and password from external file,
        starting selenium web session
        """

        with open(userdata_path) as f:
            user_data = json.load(f)

        self.facebook_login = user_data['email']
        self.facebook_password = user_data['password']
        self.drv = driver
        self.sleep_time = sleep_time

    def facebook_log_in(self):
        self.drv.get('https://www.facebook.com/')
        sleep(self.sleep_time)
        self.drv.find_element_by_name('email').send_keys(self.facebook_login)
        sleep(self.sleep_time)
        self.drv.find_element_by_name('pass').send_keys(self.facebook_password)
        try:
            self.drv.find_element_by_id('loginbutton').click()
        except common.exceptions.NoSuchElementException:
            self.drv.find_element_by_name('login').click()

    def untappd_log_in(self):
        sleep(self.sleep_time)
        self.drv.get("https://untappd.com")
        self.drv.find_element_by_xpath('//*[contains(text(),"Sign")]').click()
        fb_auth = self.drv.find_element_by_xpath('//*[contains(@class, "button fb")]')
        sleep(self.sleep_time)
        fb_auth.click()

    def log_in(self):
        """
        Consequently login into facebook and untappd,
        last one does not require login and password due to using fb account as means to log in
        """
        self.facebook_log_in()
        self.untappd_log_in()


class BarsGeneralData(object):
    """
    Getting list of bars from user's created list via link from Untappd website
    """

    def __init__(self, driver, bar_list_link, to_df=False, to_csv=False):
        self.drv = driver
        self.bar_list = self.drv.get(bar_list_link)
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = ['name', 'link', 'type_of_bar', 'address']
        self.name, self.link, self.type_of_bar, self.address = [], [], [], []
        self.bars = None
        self.bars_df = None

    def bars_info_extraction(self):
        ButtonPresser(self.drv, button_text='Show More').press_all_buttons()
        self.bars = self.drv.find_elements_by_css_selector("div[""class^='beer-']")
        for self.bar in self.bars:
            self.name.append(self.bar.find_element_by_tag_name('h2').text)
            self.link.append(self.bar.find_element_by_tag_name('h2').find_element_by_tag_name('a').
                             get_attribute('href'))
            self.type_of_bar.append(self.bar.find_element_by_tag_name('h4').text)
            self.address.append(self.bar.find_element_by_tag_name('h3').text)
        if self.to_df:
            self.bars_df = pd.DataFrame(list(zip(self.name, self.link, self.type_of_bar, self.address)),
                                        columns=self.columns)
            if self.to_csv:
                self.bars_df.to_csv()
        return self


class BarsPatrons(object):
    """
    TODO
    """

    def __init__(self, driver, bar_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.bar_link_list = bar_link_list
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = ['bar_name', 'bar_link', 'patron_name', 'patron_link', 'checkin_num']
        self.bar_name, self.bar_link, self.patron_name, self.patron_link, self.chekin_num = [], [], [], [], []
        self.current_bar_name = None
        self.patron_menu = None
        self.patrons_df = None

    def patron_extraction(self, bar_link):
        self.drv.get(bar_link)
        self.current_bar_name = self.drv.find_element_by_xpath('//*[contains(@class, "venue-name")]'
                                                               ).find_element_by_tag_name('h1').text
        try:
            WebDriverWait(self.drv, 5).until(ec.presence_of_element_located((By.CLASS_NAME, 'loyal')))
            self.patron_menu = self.drv.find_element_by_class_name('loyal').find_element_by_tag_name(
                'ul').find_elements_by_tag_name('li')
        except common.exceptions.TimeoutException:
            return None
        for patron in self.patron_menu:
            _ = patron.find_element_by_class_name('tip.track-click').get_attribute('title').split('(')
            self.bar_name.append(self.current_bar_name)
            self.bar_link.append(bar_link)
            self.patron_name.append(_[0])
            self.chekin_num.append(_[-1])
        return self

    def patrons_all_venues(self):
        for link in self.bar_link_list:
            self.patron_extraction(link)
        if self.to_df:
            self.patrons_df = pd.DataFrame(list(zip(self.bar_name, self.bar_link, self.patron_name,
                                                    self.patron_link, self.chekin_num)), columns=self.columns)
            if self.to_csv:
                self.patrons_df.to_csv()
        return self


class PatronInfo(object):
    """
    TODO
    """

    def __init__(self, driver, patron_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.patron_link_list = patron_link_list
        self.user_data = None
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = ['username', 'beer', 'brewery', 'rating', 'bar', 'checkin_text', 'serving', 'date',
                        'user_link', 'beer_link', 'brewery_link', 'bar_link']
        self.df = None
        self.user_text, self.beer_text, self.brewery_text, self.rating = [], [], [], []
        self.bar_text, self.comment, self.serving, self.date = [], [], [], []
        self.user_link, self.beer_link, self.brewery_link, self.bar_link = [], [], [], []
        self.user, self.beer, self.brewery, self.bar = None, None, None, None

    def patron_activity_extraction(self, patron):
        self.drv.get(patron)
        ButtonPresser(self.drv, 'Show More').press_all_buttons()
        self.user_data = self.drv.find_element_by_id('main-stream').find_elements_by_class_name('item')
        for _ in self.user_data:
            serving_css = "div[""class^='rating-serving']"
            caps_css = "div[""class^='caps']"
            try:
                self.rating.append(_.find_element_by_css_selector(serving_css).find_element_by_css_selector(
                    caps_css).get_attribute(
                    'data-rating'))
            except common.exceptions.NoSuchElementException:
                self.rating.append(None)

            try:
                self.serving.append(_.find_element_by_class_name('serving').find_element_by_tag_name('span').text)
            except common.exceptions.NoSuchElementException:
                self.serving.append('not_stated')

            try:
                self.comment.append(_.find_element_by_class_name('checkin-comment').text)
            except common.exceptions.NoSuchElementException:
                self.comment.append('empty')
            try:
                self.user, self.beer, self.brewery, self.bar = _.find_element_by_class_name(
                    'text').find_elements_by_tag_name('a')
                self.bar_text.append(self.bar.text)
                self.bar_link.append(self.bar.get_attribute('href'))
            except ValueError:
                self.user, self.beer, self.brewery = _.find_element_by_class_name('text').find_elements_by_tag_name('a')
                self.bar_text.append(None)
                self.bar_link.append(None)
            finally:
                self.user_text.append(self.user.text)
                self.user_link.append(self.user.get_attribute('href'))
                self.beer_text.append(self.beer.text)
                self.beer_link.append(self.beer.get_attribute('href'))
                self.brewery_text.append(self.brewery.text)
                self.brewery_link.append(self.brewery.get_attribute('href'))

            css = 'a.time.timezoner.track-click'
            self.date.append(_.find_element_by_class_name('bottom').find_element_by_css_selector(css).get_attribute(
                'data-gregtime'))
        return self

    def patrons_all_info(self):
        for patron in self.patron_link_list:
            self.patron_activity_extraction(patron)
        if self.to_df:
            self.df = pd.DataFrame(list(zip(self.user_text, self.beer_text, self.brewery_text, self.rating,
                                            self.bar_text, self.comment, self.serving, self.date, self.user_link,
                                            self.beer_link, self.brewery_link, self.bar_link)), columns=self.columns)
            if self.to_csv:
                self.df.to_csv()
        return self


class BeerStats(object):
    """
    TODO
    """
    def __init__(self, driver, beer_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.beer_link_list = beer_link_list
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = ['beer_name', 'brewery', 'sort', 'ABV', 'IBU', 'global_rating', 'num_of_ratings']
        self.df = None
        self.name, self.brewery, self.sort, self.abv = [], [], [], []
        self.ibu, self.global_rating, self.num_of_ratings = [], [], []
        self.details = None

    def beer_stat(self, url):
        self.drv.get(url)
        self.name.append(self.drv.find_element_by_class_name('name').find_element_by_tag_name('h1').text)
        self.brewery.append(self.drv.find_element_by_class_name('brewery').text)
        self.sort.append(self.drv.find_element_by_class_name('name').find_element_by_class_name('style').text)
        self.details = self.drv.find_element_by_class_name('details')
        self.abv.append(self.details.find_element_by_class_name('abv').text)
        self.ibu.append(self.details.find_element_by_class_name('ibu').text)
        self.global_rating.append(self.details.find_element_by_class_name('num').text)
        self.num_of_ratings.append(self.details.find_element_by_class_name('raters').text)

        return self

    def beer_all_info(self):
        for beer_link in self.beer_link_list:
            self.beer_stat(beer_link)
        if self.to_df:
            self.df = pd.DataFrame(list(zip(self.name, self.brewery, self.sort, self.abv,
                                            self.ibu, self.global_rating, self.num_of_ratings)),
                                   columns=self.columns)
            if self.to_csv:
                self.df.to_csv()

        return self


class BarsMenu(object):
    def __init__(self, driver, bar_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.bar_link_list = bar_link_list
        self.to_df = to_df
        self.to_csv = to_csv
        self.df = None
        self.columns = ['bar_name', 'name', 'beer_link', 'beer_sort', 'abv', 'ibu', 'brewery', 'brewery_link',
                        'beer_rating', 'section', 'drft']
        self.bar_name, self.name, self.beer_link, self.beer_sort, self.abv, self.ibu = [], [], [], [], [], []
        self.brewery, self.brewery_link, self.beer_rating, self.section, self.draft = [], [], [], [], []
        self.current_bar_name, self.current_draft, self.menu_elements, self.menu_section = None, None, None, None
        self.select = None
        self.select_options = None

    def parse_bar_beer_menu(self, url):
        self.drv.get(url)
        self.current_bar_name = self.drv.find_element_by_xpath('//*[contains(@class, "venue-name")]'
                                                               ).find_element_by_tag_name('h1').text
        try:
            WebDriverWait(self.drv, 5).until(ec.element_to_be_clickable((By.XPATH,
                                                                         '//*[contains(text(),'
                                                                         '"Show More Beers")]')))
            try:
                self.select = Select(self.drv.find_element_by_xpath('//*[contains(@class,"menu-selector")]'))
                self.select_options = self.select.options
                for menu_options in range(len(self.select_options)):
                    self.current_draft = self.select_options[menu_options].text
                    self.select.select_by_index(menu_options)
                    ButtonPresser(self.drv, 'Show More Beers').press_all_buttons()
                    self.menu_info_extraction(self.drv.find_elements_by_xpath('//*[contains(@class, "menu-section")]'))
            except common.exceptions.NoSuchElementException:
                ButtonPresser(self.drv, 'Show More Beers').press_all_buttons()
                self.draft = 'Not_stated'
                self.menu_info_extraction(self.drv.find_elements_by_xpath('//*[contains(@class, "menu-section")]'))
        except common.exceptions.TimeoutException:
            pass
        return self

    def menu_info_extraction(self, menu):
        for item in menu:
            for element in item.find_elements_by_class_name('menu-section-list'):
                # print(_.find_element_by_tag_name('h5').find_element_by_tag_name('a').text)
                self.menu_section = element.get_attribute('h4')
                self.menu_elements = element.find_elements_by_tag_name('li')
                self.bar_name.append(self.current_bar_name)
                self.name.append(element.find_element_by_tag_name('h5').find_element_by_tag_name('a').text),
                self.beer_link.append(element.find_element_by_tag_name('h5').find_element_by_tag_name(
                    'a').get_attribute('href')),
                self.beer_sort.append(element.find_element_by_tag_name('h5').find_element_by_tag_name('em').text),
                self.abv.append(
                    element.find_element_by_tag_name('h6').find_element_by_tag_name('span').text.split('•')[:-1]),
                self.ibu.append(
                    element.find_element_by_tag_name('h6').find_element_by_tag_name('span').text.split('•')[:-2])
                self.brewery_link.append(element.find_element_by_tag_name('h6').find_element_by_tag_name(
                    'a').get_attribute('href')),
                self.beer_rating.append(element.find_element_by_tag_name('h6').find_element_by_tag_name(
                    'div').get_attribute('data-rating')),
                self.section.append(self.menu_section),
                self.name.append(self.current_draft)
                # for element in _:
                #     self.bar_name.append(self.current_bar_name)
                #     self.name.append(element.find_element_by_tag_name('h5').find_element_by_tag_name('a').text),
                #     self.beer_link.append(element.find_element_by_tag_name('h5').find_element_by_tag_name(
                #         'a').get_attribute('href')),
                #     self.beer_sort.append(element.find_element_by_tag_name('h5').find_element_by_tag_name('em').text),
                #     self.abv.append(element.find_element_by_tag_name('h6').find_element_by_tag_name('span').text.split('•')[:-1]),
                #     self.ibu.append(element.find_element_by_tag_name('h6').find_element_by_tag_name('span').text.split('•')[:-2])
                #     self.brewery_link.append(element.find_element_by_tag_name('h6').find_element_by_tag_name(
                #         'a').get_attribute('href')),
                #     self.beer_rating.append(element.find_element_by_tag_name('h6').find_element_by_tag_name(
                #         'div').get_attribute('data-rating')),
                #     self.section.append(self.menu_section),
                #     self.name.append(self.current_draft)
        return self

    def parse_bars_menu(self):
        for bar in self.bar_link_list:
            self.parse_bar_beer_menu(bar)
        if self.to_df:
            self.df = pd.DataFrame(list(zip(self.bar_name, self.name, self.beer_link, self.beer_sort,
                                            self.abv, self.ibu, self.brewery, self.brewery_link,
                                            self.beer_rating, self.section, self.draft)),
                                   columns=self.columns)
            if self.to_csv:
                self.df.to_csv()
        return self


if __name__ == '__main__':
    options = Options()
    options.add_argument("--window-size=1920x1080")
    # options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    selenium_driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\steel\Desktop\chromedriver.exe')
    log_pass_file = os.path.join(os.getcwd(), 'log_pass')
    pub_list = ["https://untappd.com/user/kondrasso/lists/675857"]
    b_m = BarsMenu(selenium_driver, ['https://untappd.com/v/redrum-bar/2498830'], to_df=True).parse_bars_menu()
    print(b_m.df)
