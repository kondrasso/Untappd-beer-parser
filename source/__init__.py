import json
import pandas as pd
from time import sleep
from tqdm.auto import tqdm
from selenium import common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as ec
from source.beer import (
    ButtonPresser,
    LoginProcess,
    BarsGeneralData,
    BarsPatrons,
    PatronChekinParser,
    BarChekinParser,
    BeerStats,
    BarsMenu,
    DriverSetup,
)
