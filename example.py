from source.beer import *


# Example of parser usage, showing how to interface with
# methods from beer.py to collect information from Untappd.
# You need pre-compiled list on Untappd website to start,
# if you dont have pre-compiled list of links to bar/beer page on Untappd
# it should look like this

untappd_list = ["https://untappd.com/user/XXXXX/lists/XXXXXX"]

# or you can use list of direct links to specific places, for example

bars_to_get_menu = ['https://untappd.com/v/redrum-bar/2498830', 'https://untappd.com/v/socle-craft-bar/8750585']

if __name__ == '__main__':
    # initiate driver
    drv = DriverSetup(headless=False).selenium_driver
    # you should modify log_pass_dummy to be able to login on FB, or specify path to your own file
    LoginProcess(drv, 'source', 'log_pass_dummy').log_in()
    # after logging in, we can collect info on menu of selected bars and save it to csv
    bars_menu = BarsMenu(drv, bars_to_get_menu, to_df=True, to_csv=True).parse_bars_menu()

