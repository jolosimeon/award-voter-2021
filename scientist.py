from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import os
import time
from datetime import date, datetime
import pytz
import PySimpleGUI as sg
import random
from selenium.webdriver.support import expected_conditions as EC

def end_program():
    global continue_program
    continue_program = False
    return

def start_browser():
    global driver
    # open browser
    browser_options = Options()
    browser_options.add_experimental_option("detach", True)
    s = Service(ChromeDriverManager().install())
    LOGGER.setLevel(logging.WARNING)
    driver = webdriver.Chrome(service=s, options=browser_options)
    driver.get('https://www.mwave.me/en/signin?retUrl=https://mama.mwave.me/en/main')
    driver.maximize_window()

def auth_twitch(account):
    # click the login using twitch button
    elem = driver.find_element(By.XPATH, '//span[contains(@class, "twitch")]')
    elem.click()
    
    # fill in username and password
    elem = driver.find_element(By.XPATH, '//input[@id="login-username"]')
    elem.send_keys(account['username'])

    elem = driver.find_element(By.XPATH, '//input[@id="password-input"]')
    elem.send_keys(account['password'])

    elem = driver.find_element(By.XPATH, '//button[@data-a-target="passport-login-button"]')
    elem.click()

    sg.popup_timed('Logging into Twitch for ' + account['username'] + ', please finish any bot challenges if any', auto_close_duration=5, keep_on_top=True)

    # wait until returned to mama home page
    try:
        print('Wait until returned to mama home page')
        elem = WebDriverWait(driver, 240).until(EC.presence_of_element_located((By.XPATH, '//i[@class="logo_mwave"]')))
        time.sleep(0.5)
    except TimeoutException:
        sg.popup_error('ERROR: Took too long to return to MAMA home page', auto_close_duration=5, keep_on_top=True)
        return 

    # wait until redirected
    # layout = [  [sg.Text('Click Continue if logged into the MAMA website. Verify that you have completed any bot challenges.')],
           # [sg.Button('Continue'), sg.Button('Cancel')] ]
    # window = sg.Window('Project Scientist', layout)

    #while True:             # Event Loop
    #    event, values = window.Read()
    #    if event == 'Continue':
    #        break
     #   elif event == sg.WIN_CLOSED or event == 'Cancel':
     #       end_program()
   # window.Close()


def vote(account):
    actions = ActionChains(driver)
    driver.get('https://mama.mwave.me/en/vote')
    time.sleep(1)

    # check if there is tutorial
    tutorial_arrow = driver.find_element(By.XPATH, '//div[contains(@class, "swiper-button-next")]')

    if (tutorial_arrow.is_displayed() and tutorial_arrow.is_enabled()):
        # click through the tutorial dialog boxes
        tutorial_arrow.click()

        time.sleep(0.5)
        #elem = driver.find_element(By.XPATH, '//div[contains(@class, "swiper-button-next")]')
        tutorial_arrow.click()

        time.sleep(0.5)
        elem = driver.find_element(By.XPATH, '//i[contains(@class, "daysCheck7Btn")]')
        elem.click()

    # find twice and click
    elem = driver.find_element(By.XPATH, '//div[@data-candidate-name="TWICE"]')
    actions.move_to_element(elem).perform()
    vote_btn = driver.find_element(By.XPATH, '//div[@data-candidate-name="TWICE"]').find_element(By.XPATH, './/button')
    if (not vote_btn.is_displayed() or not vote_btn.is_enabled()):
        sg.popup_error('ERROR: Cant find the vote button. The account may have already voted.', auto_close_duration=5, keep_on_top=True)
        return

    vote_btn.click()
    try:
        pop_up_error = driver.find_element(By.XPATH, '//div[contains(text(), "You have exceeded the votes allowed on the current IP.")]')
        if (pop_up_error.is_displayed()):
            sg.popup_error('ERROR: IP limit reached.', auto_close_duration=5, keep_on_top=True)
            return
    except:
        print('Still within IP limit')

    sg.popup_timed('Please input captcha for MAMA vote', auto_close_duration=5, keep_on_top=True)

    # wait until video is done
    try:
        print('Wait until captcha is done')
        elem = WebDriverWait(driver, 240).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="btnVideoPlay"]')))

        # play the video
        elem = driver.find_element(By.XPATH, '//button[@id="btnVideoPlay"]')
        elem.click()

        print('Wait until video is finished')
        elem = WebDriverWait(driver, 240).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="btnYes"]')))
        print('Video completed')

        # accept consent
        print('Accept consent')
        elem = driver.find_element(By.XPATH, '//button[@id="btnYes"]')
        elem.click()
        time.sleep(3)
        
        # take a screenshot of the successful vote
        #html = driver.find_element_by_tag_name('html')
        #html.send_keys(Keys.HOME)
        driver.execute_script('scrollBy(0, -1080)')
        time.sleep(1)
        datetime_now = datetime.now(tz=pytz.timezone('Asia/Seoul'))
        now_str = datetime_now.strftime('%Y-%m-%d-%H%M')
        print('Take screenshot')
        driver.save_screenshot('screenshots/' +  now_str + '-' + account['username'] + '-' + account['method'] + '.png')
        sg.popup_timed('Successfully voted for ' + account['username'] + '!', auto_close_duration=5, keep_on_top=True)
    except TimeoutException:
        sg.popup_error('ERROR: Video too long or User took too long to input captcha.', auto_close_duration=5, keep_on_top=True)
        return
    finally:
        # when done quit the window
        return

os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_LOG_LEVEL'] = '0'

# load credentials from file
credentials = {}
usernames = []
counter = 0
with open("credentials.csv") as f:
    for line in f:
        (username, password, method) = line.split(',')
        obj = {}
        obj['username'] = username
        obj['password'] = password
        obj['method'] = method
        usernameWithMethod = username + '-' + method 
        credentials[usernameWithMethod] = obj
        usernames.append(usernameWithMethod)
        counter += 1

continue_program = True
driver = None

while continue_program:
    layout = [  [sg.Text('love aint a science, do it for twice', size=(60, 1), justification='left')],
                [sg.Combo(usernames, key='username_select', default_value=usernames[0], readonly=True)],
                [sg.Button('Start'), sg.Button('Exit')] ]
    window = sg.Window('Project Scientist', layout, keep_on_top=True)

    while True:             # Event Loop
        event, values = window.Read()
        if event == 'Start':
            curr = credentials[values['username_select']]
            break
        elif event == sg.WIN_CLOSED or event == 'Exit':
            quit()
    window.Close()

    start_browser()
    if curr['method'] == 'twitch':
        auth_twitch(curr)
        vote(curr)
    
    if (driver is not None):
        driver.quit()
