class ButtonPresser:
    """
    Class that contains method's to continuously press buttons
    because of ajax nature of the site

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    button_text : str
        Text that contains button to press.
    sleep_time : int
        Time to wait between various stages of webpage's loading.
        Used due to unstable nature of WebDiverWait while handling
        infinitely long pages.
    """

    def __init__(self, driver, button_text='Show More Beers', sleep_time=1):
        self.drv = driver
        self.button_text = button_text
        self.sleep_time = sleep_time
        self.buttons_left = True
        self.banner = None
        self.buttons = None
        self.button = None

    def banner_cutter(self):
        """
        Method used to execute javascript code to remove banner obstructing the DOM.

        Returns
        -------
        None
        """

        try:
            self.banner = self.drv.find_element_by_xpath(
                '//*[contains(@class, "branch-animation")]'
            )
            # script to remove banner
            self.drv.execute_script(
                "arguments[0].style.visibility='hidden'",
                self.banner
            )
            sleep(self.sleep_time)
        except (
                common.exceptions.NoSuchElementException,
        ):
            print('No banner found')
        return None

    def press_all_buttons(self):
        """
        Method that continuously presses all appearing buttons while they can be located

        Returns
        -------
        None
        """

        sleep(5)
        while self.buttons_left:
            self.banner_cutter()
            sleep(1)
            # script to scroll to the bottom of the page
            self.drv.execute_script(
                "window.scrollTo(0,Math.max(document.documentElement."
                "scrollHeight,document.body.scrollHeight,document."
                "documentElement.clientHeight));"
            )
            self.buttons = self.drv.find_elements_by_xpath(
                '//*[contains(text(),"{}")]'.format(
                    self.button_text
                )
            )
            try:
                self.buttons = self.drv.find_elements_by_xpath(
                    '//*[contains(text(),"{}")]'.format(
                        self.button_text
                    )
                )

            except common.exceptions.NoSuchElementException:
                self.buttons_left = False

            if len(self.buttons) == 0:
                self.buttons_left = False

            for self.button in self.buttons:
                sleep(self.sleep_time)
                # script to scroll to the bottom of the page
                self.drv.execute_script(
                    "window.scrollTo(0,Math.max(document.documentElement."
                    "scrollHeight,document.body.scrollHeight,document."
                    "documentElement.clientHeight));"
                )
                sleep(self.sleep_time)
                try:
                    WebDriverWait(
                        self.drv,
                        6
                    ).until(
                        ec.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//*[contains(text(),"
                                "\"{}\")]".format(
                                    self.button_text
                                )
                            )
                        )
                    )

                    self.drv.execute_script(
                        "arguments[0].click();",
                        self.button
                    )
                except common.exceptions.TimeoutException:
                    self.buttons_left = False


class LoginProcess:
    """
    Login to facebook & untappd for acquiring access
    to data from website via Selenium webdriver

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    userdata_path : str
        Path to JSON file that contains fb login information.
    sleep_time : int
        Time to wait between various actions.
    """

    def __init__(self, driver, userdata_path, sleep_time=1):
        with open(userdata_path) as f:
            user_data = json.load(f)

        self.facebook_login = user_data['email']
        self.facebook_password = user_data['password']
        self.drv = driver
        self.sleep_time = sleep_time

    def facebook_log_in(self):
        """
        Logging in to Facebook account via their homepage.

        Returns
        -------
        None
        """

        self.drv.get('https://www.facebook.com/')
        sleep(self.sleep_time)

        self.drv.find_element_by_name(
            'email'
        ).send_keys(
            self.facebook_login
        )
        sleep(self.sleep_time)

        self.drv.find_element_by_name(
            'pass'
        ).send_keys(
            self.facebook_password
        )

        try:
            self.drv.find_element_by_id('loginbutton').click()
        except common.exceptions.NoSuchElementException:
            self.drv.find_element_by_name('login').click()

    def untappd_log_in(self):
        """
        Logging in to Untappd via Facebook

        Returns
        -------
        None
        """

        sleep(self.sleep_time)
        self.drv.get("https://untappd.com")
        self.drv.find_element_by_xpath(
            '//*[contains(text(),"Sign")]'
        ).click()
        fb_auth = self.drv.find_element_by_xpath(
            '//*[contains(@class, "button fb")]'
        )
        sleep(self.sleep_time)
        fb_auth.click()

    def log_in(self):
        """
        Consequently login into facebook and untappd, last one does not require login and password
        due to using fb account as means to log in.

        Returns
        -------
        None
        """

        self.facebook_log_in()
        self.untappd_log_in()


class BarsGeneralData:
    """
    Getting list of bars from user's created list via link from Untappd website, as well as their general data.

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    bar_list_link : list[str]
        List of links to existing list of bars via Untappd lists in user profile.
    to_df : bool
        Save results as Pandas DataFrame
    to_csv : bool
        Import results to csv
    """

    def __init__(self, driver, bar_list_link, to_df=False, to_csv=False):
        self.drv = driver
        self.bar_list = self.drv.get(bar_list_link)
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = [
            'name',
            'link',
            'type_of_bar',
            'address'
        ]
        self.name, self.link, self.type_of_bar, self.address = [], [], [], []
        self.bars, self.bars_df, self.bar = None, None, None

    def bars_info_extraction(self):
        """
        Pressing all buttons on the page via ButtonPresser, then extract data into the text format,
        updating class variables.

        Returns
        -------
        self
        """

        ButtonPresser(self.drv, button_text='Show More').press_all_buttons()
        self.bars = self.drv.find_elements_by_css_selector(
                "div[""class^='beer-']"
            )
        for self.bar in self.bars:
            self.name.append(
                self.bar.find_element_by_tag_name(
                    'h2'
                ).text
            )
            self.link.append(
                self.bar.find_element_by_tag_name(
                    'h2'
                ).find_element_by_tag_name(
                    'a'
                ).get_attribute(
                    'href'
                )
            )
            self.type_of_bar.append(
                self.bar.find_element_by_tag_name(
                    'h4'
                ).text
            )
            self.address.append(
                self.bar.find_element_by_tag_name(
                    'h3'
                ).text
            )
        return self

    def to_df_or_csv(self):
        """
        Saving results to df or/and csv

        Returns
        -------
        self
        """

        if self.to_df:
            self.bars_df = pd.DataFrame(list(zip(
                self.name,
                self.link,
                self.type_of_bar,
                self.address)
            ), columns=self.columns)
            if self.to_csv:
                self.bars_df.to_csv()
        return self


class BarsPatrons:
    """
    Getting info of users in "top patrons" section of bar's webpage at Untappd.

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    bar_list_link : list[str]
        Link to existing list of bars via Untappd lists in user profile.
    to_df : bool
        Save results as Pandas DataFrame
    to_csv :
        Import results to csv
    """

    def __init__(self, driver, bar_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.bar_link_list = bar_link_list
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = [
            'bar_name',
            'bar_link',
            'patron_name',
            'patron_link',
            'checkin_num'
        ]
        self.bar_name, self.bar_link, self.patron_name, self.patron_link, self.chekin_num = [], [], [], [], []
        self.current_bar_name = None
        self.patron_menu = None
        self.patrons_df = None

    def patron_extraction(self, bar_link):
        """
        Extracting all fields of user's profile page in Untappd and appending it to respected class variables.

        Parameters
        ----------
        bar_link : str
            Link to a bar's page on Untappd.

        Returns
        -------
        self
        """

        self.drv.get(bar_link)
        self.current_bar_name = \
            self.drv.find_element_by_xpath(
                '//*[contains(@class, "venue-name")]'
            ).find_element_by_tag_name('h1').text
        try:
            WebDriverWait(self.drv, 5).until(
                ec.presence_of_element_located(
                    (
                        By.CLASS_NAME, 'loyal'
                    )
                )
            )
            self.patron_menu = self.drv.find_element_by_class_name(
                'loyal'
            ).find_element_by_tag_name(
                'ul'
            ).find_elements_by_tag_name(
                'li'
            )
        except common.exceptions.TimeoutException:
            return None

        for patron in self.patron_menu:
            _ = patron.find_element_by_class_name(
                    'tip.track-click'
                ).get_attribute(
                    'title'
                ).split(
                    '('
                )
            self.bar_name.append(self.current_bar_name)
            self.bar_link.append(bar_link)
            self.patron_name.append(_[0])
            self.chekin_num.append(_[-1])
        return self

    def patrons_all_venues(self):
        """
        Extracting patrons info from all venues in bar_link_list.

        Returns
        -------
        self
        """

        for link in tqdm(self.bar_link_list):
            self.patron_extraction(link)
        self.to_df_or_csv()
        return self

    def to_df_or_csv(self):
        """
        Saving results to df or/and csv.

        Returns
        -------
        self
        """

        if self.to_df:
            self.patrons_df = pd.DataFrame(list(zip(
                self.bar_name,
                self.bar_link,
                self.patron_name,
                self.patron_link,
                self.chekin_num
            )), columns=self.columns)
            if self.to_csv:
                self.patrons_df.to_csv()
        return self


class PatronChekinParser:
    """
    Getting all available check-ins from user's profile in Untappd .

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    patron_link_list : list[str]
        List of links to existing list of bars via Untappd lists in user profile.
    to_df : bool
        Save results as Pandas DataFrame
    to_csv : bool
        Import results to csv
    """

    def __init__(self, driver, patron_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.patron_link_list = patron_link_list
        self.user_data = None
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = [
            'username',
            'beer',
            'brewery',
            'rating',
            'bar',
            'checkin_text',
            'serving',
            'date',
            'user_link',
            'beer_link',
            'brewery_link',
            'bar_link'
        ]
        self.df = None
        self.user_text, self.beer_text, self.brewery_text, self.rating = [], [], [], []
        self.bar_text, self.comment, self.serving, self.date = [], [], [], []
        self.user_link, self.beer_link, self.brewery_link, self.bar_link = [], [], [], []
        self.user, self.beer, self.brewery, self.bar = None, None, None, None

    def patron_activity_extraction(self, patron):
        """

        Parameters
        ----------
        patron : str
            Link to a patron's page on Untappd.

        Returns
        -------
        self
        """

        self.drv.get(patron)
        ButtonPresser(self.drv, 'Show More').press_all_buttons()
        self.user_data = self.drv.find_element_by_id(
                'main-stream'
            ).find_elements_by_class_name(
                'item'
            )
        for _ in self.user_data:
            serving_css = "div[""class^='rating-serving']"
            caps_css = "div[""class^='caps']"
            try:
                self.rating.append(
                    _.find_element_by_css_selector(
                        serving_css
                    ).find_element_by_css_selector(
                        caps_css
                    ).get_attribute(
                        'data-rating'
                    )
                )
            except common.exceptions.NoSuchElementException:
                self.rating.append(None)

            try:
                self.serving.append(
                    _.find_element_by_class_name(
                        'serving'
                    ).find_element_by_tag_name(
                        'span'
                    ).text
                )
            except common.exceptions.NoSuchElementException:
                self.serving.append('not_stated')

            try:
                self.comment.append(
                    _.find_element_by_class_name('checkin-comment').text
                )
            except common.exceptions.NoSuchElementException:
                self.comment.append('empty')
            try:
                self.user, self.beer, self.brewery, self.bar = _.find_element_by_class_name(
                        'text'
                    ).find_elements_by_tag_name(
                        'a'
                    )
                self.bar_text.append(
                    self.bar.text
                )
                self.bar_link.append(
                    self.bar.get_attribute(
                        'href'
                    )
                )
            except ValueError:
                self.user, self.beer, self.brewery = _.find_element_by_class_name(
                        'text'
                    ).find_elements_by_tag_name(
                        'a'
                    )
                self.bar_text.append(None)
                self.bar_link.append(None)
            finally:
                self.user_text.append(
                    self.user.text
                )
                self.user_link.append(
                    self.user.get_attribute(
                        'href'
                    )
                )
                self.beer_text.append(
                    self.beer.text
                )
                self.beer_link.append(
                    self.beer.get_attribute(
                        'href'
                    )
                )
                self.brewery_text.append(
                    self.brewery.text
                )
                self.brewery_link.append(
                    self.brewery.get_attribute(
                        'href'
                    )
                )

            css = 'a.time.timezoner.track-click'

            self.date.append(
                _.find_element_by_class_name(
                    'bottom'
                ).find_element_by_css_selector(css).get_attribute(
                    'data-gregtime'
                )
            )

        return self

    def patrons_all_info(self):
        """
        Extracting patrons info from all patrons in patron_link_list.

        Returns
        -------
        self
        """

        for patron in tqdm(self.patron_link_list):
            self.patron_activity_extraction(patron)
        self.to_df_or_csv()
        return self

    def to_df_or_csv(self):
        """
        Saving results to df or/and csv

        Returns
        -------
        self
        """

        if self.to_df:
            self.df = pd.DataFrame(list(zip(
                self.user_text,
                self.beer_text,
                self.brewery_text,
                self.rating,
                self.bar_text,
                self.comment,
                self.serving,
                self.date,
                self.user_link,
                self.beer_link,
                self.brewery_link,
                self.bar_link
            )), columns=self.columns)
            if self.to_csv:
                self.df.to_csv()
        return self


class BarChekinParser(PatronChekinParser):
    """
    Getting all available check-ins from bar's profile in Untappd .
    """

    def parse_bar_chekin(self):
        """
        Extracting all check-ins from bar's page on Untappd.

        Returns
        -------
        self
        """

        for bar in tqdm(self.patron_link_list):
            self.patron_activity_extraction(bar)
        self.to_df_or_csv()
        return self


class BeerStats:
    """
    Getting info on each beer presented by link in beer_link_list and extracting it into text data.

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    beer_link_list : list[str]
        List of links to beer's on Untappd.
    to_df : bool
        Save results as Pandas DataFrame
    to_csv : bool
        Import results to csv
    """

    def __init__(self, driver, beer_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.beer_link_list = beer_link_list
        self.to_df = to_df
        self.to_csv = to_csv
        self.columns = [
            'beer_name',
            'brewery',
            'sort',
            'ABV',
            'IBU',
            'global_rating',
            'num_of_ratings'
        ]
        self.df = None
        self.name, self.brewery, self.sort, self.abv = [], [], [], []
        self.ibu, self.global_rating, self.num_of_ratings = [], [], []
        self.details = None

    def beer_stat(self, url):
        """
        Extracting beer's info from its webpage on Untappd and getting it into text data,
        updating respectable class variables.
        Parameters
        ----------
        url : str
            Link to a beer's webpage on Untappd.

        Returns
        -------
        self
        """

        self.drv.get(url)
        self.name.append(
            self.drv.find_element_by_class_name(
                'name'
            ).find_element_by_tag_name(
                'h1'
            ).text
        )
        self.brewery.append(
            self.drv.find_element_by_class_name(
                'brewery'
            ).text
        )
        self.sort.append(
            self.drv.find_element_by_class_name(
                'name'
            ).find_element_by_class_name(
                'style'
            ).text
        )
        self.details = self.drv.find_element_by_class_name(
            'details'
        )
        self.abv.append(
            self.details.find_element_by_class_name(
                'abv'
            ).text
        )
        self.ibu.append(
            self.details.find_element_by_class_name(
                'ibu'
            ).text
        )
        self.global_rating.append(
            self.details.find_element_by_class_name(
                'num'
            ).text
        )
        self.num_of_ratings.append(
            self.details.find_element_by_class_name(
                'raters'
            ).text
        )

        return self

    def beer_all_info(self):
        """
        Extracting all beer's info from beer's page on Untappd.

        Returns
        -------
        self
        """

        for beer_link in tqdm(self.beer_link_list):
            self.beer_stat(beer_link)
        self.to_df_or_csv()
        return self

    def to_df_or_csv(self):
        """
        Saving results to df or/and csv

        Returns
        -------
        self
        """

        if self.to_df:
            self.df = pd.DataFrame(list(zip(
                self.name,
                self.brewery,
                self.sort,
                self.abv,
                self.ibu,
                self.global_rating,
                self.num_of_ratings
            )
            ), columns=self.columns)
            if self.to_csv:
                self.df.to_csv()
        return self


class BarsMenu:
    """
    Getting all info from bar's webpage menu section on Untappd.

    Arguments
    ----------
    driver : SeleniumWebDriver
        Selenium web driver, that's contains current session.
    bar_link_list : list[str]
        List of links to bar's webpage on Untappd.
    to_df : bool
        Save results as Pandas DataFrame
    to_csv : bool
        Import results to csv
    """

    def __init__(self, driver, bar_link_list, to_df=False, to_csv=False):
        self.drv = driver
        self.bar_link_list = bar_link_list
        self.to_df = to_df
        self.to_csv = to_csv
        self.df = None
        self.columns = [
            'bar_name',
            'name',
            'beer_link',
            'beer_sort',
            'abv',
            'ibu',
            'brewery',
            'brewery_link',
            'beer_rating',
            'section',
            'drft'
        ]
        self.bar_name, self.name, self.beer_link, self.beer_sort, self.abv, self.ibu = [], [], [], [], [], []
        self.brewery, self.brewery_link, self.beer_rating, self.section, self.draft = [], [], [], [], []
        self.current_bar_name, self.current_draft, self.menu_elements, self.menu_section = None, None, None, None
        self.select, self.select_text_options, self.select_options = None, None, None

    def parse_bar_beer_menu(self, url):
        """
        Cycling through all dropdown menus on bar's webpage menu section on Untappd, getting text info from it and
        update respectable class variables.

        Parameters
        ----------
        url : str
            Link to bar's webpage on Untappd.

        Returns
        -------
        self
        """

        self.drv.get(url)
        self.current_bar_name = \
            self.drv.find_element_by_xpath(
                '//*[contains(@class, "venue-name")]'
            ).find_element_by_tag_name(
                'h1'
            ).text
        try:
            # trying to get list of options if there are more than one
            self.select = \
                Select(
                    self.drv.find_element_by_xpath(
                        '//*[contains(@class,"menu-selector")]'
                    )
                )
            self.select_options = self.select.options
            self.select_text_options = [_.text for _ in self.select_options]
            # cycling through menu options and selecting each one
            for menu_options in range(len(self.select_options)):
                self.select = \
                    Select(
                        self.drv.find_element_by_xpath(
                            '//*[contains(@class,"menu-selector")]'
                        )
                    )
                self.current_draft = self.select_text_options[menu_options]
                self.select.select_by_index(menu_options)
                ButtonPresser(self.drv, 'Show More Beers').press_all_buttons()
                # extracting current menu dropdown section
                self.menu_info_extraction(
                    self.drv.find_element_by_class_name(
                        'menu-area'
                    ).find_element_by_class_name(
                        'section-area'
                    )
                )
        except common.exceptions.NoSuchElementException:
            # if only none or one options present
            ButtonPresser(self.drv, 'Show More Beers').press_all_buttons()
            self.current_draft = 'Not_stated'
            self.menu_info_extraction(
                self.drv.find_element_by_class_name(
                    'menu-area'
                ).find_element_by_class_name(
                    'section-area'
                )
            )

        return self

    def menu_info_extraction(self, menu):
        """
        Extracting info from current selected option in bar webpage menu section on Untappd and updating
        respectable class variables.

        Parameters
        ----------
        menu : SeleniumWebDriver

        Returns
        -------
        self
        """

        for menu_section in menu.find_elements_by_class_name('menu-section-list'):
            for element in menu_section.find_elements_by_tag_name('li'):
                self.bar_name.append(self.current_bar_name)
                self.name.append(
                    element.find_element_by_tag_name(
                        'h5'
                    ).find_element_by_tag_name(
                        'a'
                    ).text
                )
                self.beer_link.append(
                    element.find_element_by_tag_name(
                        'h5'
                    ).find_element_by_tag_name(
                        'a'
                    ).get_attribute(
                        'href'
                    )
                )
                self.beer_sort.append(
                    element.find_element_by_tag_name(
                        'h5'
                    ).find_element_by_tag_name(
                        'em'
                    ).text
                )
                self.abv.append(
                    element.find_element_by_tag_name(
                        'h6'
                    ).find_element_by_tag_name(
                        'span'
                    ).text.split('•')[0]
                )
                self.ibu.append(
                    element.find_element_by_tag_name(
                        'h6'
                    ).find_element_by_tag_name(
                        'span'
                    ).text.split('•')[1]
                )
                self.brewery.append(
                    element.find_element_by_tag_name(
                        'h6'
                    ).find_element_by_tag_name(
                        'span'
                    ).text.split('•')[2]
                )
                try:
                    self.brewery_link.append(
                        element.find_element_by_tag_name(
                            'h6'
                        ).find_element_by_tag_name(
                            'a'
                        ).get_attribute(
                            'href'
                        )
                    )
                except common.exceptions.NoSuchElementException:
                    self.brewery_link.append(None)
                try:
                    self.beer_rating.append(
                        element.find_element_by_tag_name(
                            'h6'
                        ).find_element_by_tag_name(
                            'div'
                        ).get_attribute(
                            'data-rating'
                        )
                    )
                except common.exceptions.NoSuchElementException:
                    self.beer_rating.append(0)
                try:
                    self.section.append(element.get_attribute('h4'))
                except common.exceptions.NoSuchElementException:
                    self.section.append('Not stated')
                self.draft.append(self.current_draft)
        return self

    def parse_bars_menu(self):
        """
        Extracting all menus from bar's page on Untappd.

        Returns
        -------
        self
        """

        for bar in tqdm(self.bar_link_list):
            self.parse_bar_beer_menu(bar)
            self.to_df_or_csv()
        return self

    def to_df_or_csv(self):
        """
        Saving results to df or/and csv

        Returns
        -------
        self
        """

        if self.to_df:
            self.df = pd.DataFrame(list(zip(
                self.bar_name,
                self.name,
                self.beer_link,
                self.beer_sort,
                self.abv,
                self.ibu,
                self.brewery,
                self.brewery_link,
                self.beer_rating,
                self.section,
                self.draft
            )
            ), columns=self.columns)
            if self.to_csv:
                self.df.to_csv()
        return self


class DriverSetup:
    def __init__(self, window_size="--window-size=1920x1080", headless=True, logging=True):
        """

        Parameters
        ----------
        window_size : str
            Parameter for selenium options, describing window size. Note: full hd is recommended due to visibility
            issues with lesser resolution
        headless : bool
            Option for headless usage of webdriver
        logging : bool
            Option for built-in selenium logger
        """
        self.options = Options()
        self.options.add_argument(window_size)
        if logging:
            self.options.add_experimental_option(
                'excludeSwitches',
                ['enable-logging']
            )
        if headless:
            self.options.add_argument("--headless")
        self.selenium_driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=self.options
        )
