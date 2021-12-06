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
import os
import time
from datetime import date, datetime
import pytz
import PySimpleGUI as sg
import random
from selenium.webdriver.support import expected_conditions as EC
import threading
from notifypy import Notify
import sys
from collections import OrderedDict
from pathlib import Path
import platform

def notify(type, title, message):
    if platform.system() == 'Windows':
        notification = Notify()
        notification.title = title
        notification.message = message
        #notification.audio = "assets/audio/comeon.wav"
        notification.send()

# def end_program():
#     global continue_program
#     continue_program = False
#     return

def start_browser():
    # open browser
    browser_options = Options()
    browser_options.add_experimental_option("detach", True)
    s = Service(ChromeDriverManager().install())
    # s = Service('./webdriver/chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=browser_options)
    driver.get('https://www.mwave.me/en/signin')
    driver.maximize_window()
    return driver

def auth_twitch(driver, account):
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

    notify('notif', 'Logging In - ' + account['username'], 'Logging into Twitch for ' + account['username'] + ', please finish any bot challenges if any.')

    # sg.popup_timed('Logging into Twitch for ' + account['username'] + ', please finish any bot challenges if any', auto_close_duration=5, keep_on_top=True)

    # wait until returned to mama home page
    try:
        #print('Wait until returned to mama home page')
        elem = WebDriverWait(driver, 60).until(EC.title_contains('Mwave'))
        #elem = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//i[contains(@class, "logo_mwave")]')))
        time.sleep(0.5)
        return True
    except:
        print('[' + account['username'] + '] ' + 'ERROR:Login error.', text_color='red')
        return False

def auth_kakao(driver, account):
    # click the login using twitch button
    elem = driver.find_element(By.XPATH, '//span[contains(@class, "kakao")]')
    elem.click()
    
    # fill in username and password
    elem = driver.find_element(By.XPATH, '//input[@name="email"]')
    elem.send_keys(account['username'])

    elem = driver.find_element(By.XPATH, '//input[@name="password"]')
    elem.send_keys(account['password'])

    elem = driver.find_element(By.XPATH, '//button[contains(@class, "btn_confirm")]')
    elem.click()

    #sg.popup_timed('Logging into Kakao for ' + account['username'] + ', please finish any bot challenges if any', auto_close_duration=5, keep_on_top=True)

    # wait until returned to mama home page
    try:
        elem = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//i[contains(@class, "logo_mwave")]')))
        time.sleep(0.5)
        return True
    except:
        print('[' + account['username'] + '] ' + 'ERROR:Login error.', text_color='red')
        #sg.popup_error('ERROR: Took too long to return to MAMA home page. User may have been unable to login.', auto_close_duration=5, keep_on_top=True)
        return False

def auth_google(driver, account):
    # click the login using twitch button
    elem = driver.find_element(By.XPATH, '//span[contains(@class, "google")]')
    elem.click()
    
    # fill in username and password
    elem = driver.find_element(By.XPATH, '//input[@id="identifierId"]')
    elem.send_keys(account['username'])

    print('Click next')
    elem = driver.find_element(By.XPATH, '//div[@id="identifierNext"]')
    elem.click()

    print('Password time')

    elem = driver.find_element(By.XPATH, '//*[@id ="password"]/div[1]/div / div[1]/input')
    elem.send_keys(account['password'])

    elem = driver.find_element(By.XPATH, '//input[@id="passwordNext"]')
    elem.click()

    # sg.popup_timed('Logging into Google for ' + account['username'] + ', please finish any bot challenges if any', auto_close_duration=5, keep_on_top=True)

    # wait until returned to mama home page
    try:
        elem = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//i[contains(@class, "logo_mwave")]')))
        time.sleep(0.5)
        return True
    except:
        print('[' + account['username'] + '] ' + 'ERROR:Login error.', text_color='red')
        return False

def vote(driver, account, screenshots_folder):
    write_event_update(account['username'], 'Start Voting')
    actions = ActionChains(driver)
    driver.get('https://mama.mwave.me/en/vote')
    time.sleep(1)

    # check if there is tutorial
    tutorial_arrow = driver.find_element(By.XPATH, '//div[contains(@class, "swiper-button-next")]')

    if (tutorial_arrow.is_displayed() and tutorial_arrow.is_enabled()):
        # click through the tutorial dialog boxes
        tutorial_arrow.click()

        time.sleep(0.5)
        tutorial_arrow.click()

        time.sleep(0.5)
        elem = driver.find_element(By.XPATH, '//i[contains(@class, "daysCheck7Btn")]')
        elem.click()

    # find twice and click
    time.sleep(0.5)
    elem = driver.find_element(By.XPATH, '//div[@data-candidate-name="TWICE"]')
    actions.move_to_element(elem).perform()
    time.sleep(0.5)
    vote_btn = driver.find_element(By.XPATH, '//div[@data-candidate-name="TWICE"]').find_element(By.XPATH, './/button')
    if (not vote_btn.is_displayed() or not vote_btn.is_enabled()):
        print('[' + account['username'] + '] ' + 'ERROR: Cant find the vote button. The account may have already voted.', text_color='red')
        return

    vote_btn.click()
    try:
        pop_up_error = driver.find_element(By.XPATH, '//div[contains(text(), "You have exceeded the votes allowed on the current IP.")]')
        if (pop_up_error.is_displayed()):
            print('[' + account['username'] + '] ' + 'ERROR: IP Limit reached.', text_color='red')
            return
    except:
        pass
    
    notify('notif', 'Input CAPTCHA - ' + account['username'] , 'Please input CAPTCHA for MAMA vote.')
    write_event_update(account['username'], 'Input CAPTCHA')
    # sg.popup_timed('Please input captcha for MAMA vote', auto_close_duration=5, keep_on_top=True)

    # wait until video is done
    try:
        # print('Wait until captcha is done')
        elem = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="btnVideoPlay"]')))
        time.sleep(0.5)
        write_event_update(account['username'], 'Watching Video')
        # play the video
        elem = driver.find_element(By.XPATH, '//button[@id="btnVideoPlay"]')
        elem.click()

        #print('Wait until video is finished')

        # wait until button submit appears and is clickacble
        elem = WebDriverWait(driver, 240).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="btnPlayerSubmit"]')))
        time.sleep(0.5)
        elem = driver.find_element(By.XPATH, '//button[@id="btnPlayerSubmit"]')
        elem.click()
        # print('Submit video, dont watch the rest if can submit already')
        write_event_update(account['username'], 'Video Finished')

        elem = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="btnYes"]')))
        time.sleep(0.5)
        # accept consent
        # print('Accept consent')
        elem = driver.find_element(By.XPATH, '//button[@id="btnYes"]')
        elem.click()
        time.sleep(1)

        # wait for vote confirmation screen
        elem = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//span[@id="step3Date"]')))
        # print('Scroll up for better view')
        driver.execute_script('scrollBy(0, -1080)')
        time.sleep(0.5)
        
        # take a screenshot of the successful vote
        datetime_now = datetime.now(tz=pytz.timezone('Asia/Seoul'))
        now_str = datetime_now.strftime('%Y-%m-%d-%H%M')
        driver.save_screenshot(screenshots_folder +  now_str + '-' + account['username'] + '-' + account['method'] + '.png')
        print('[' + account['username'] + '] ' + 'Successfuly voted for TWICE! Screenshot saved.', text_color='green')   
    except:
        print('[' + account['username'] + '] ' + 'ERROR: Video eror or user took too long to input captcha.', text_color='red')
        return
    finally:
        # when done quit the window
        return

def load_accounts_file(filename):
    if not Path(filename).is_file() or not Path(filename).suffix == '.csv':
        raise Exception('File input error')
    usernames = []
    credentials = {}
    counter = 0
    with open(filename) as f:
        for line in f:
            (username, password, method) = line.strip().split(',')
            obj = {}
            obj['username'] = username
            obj['password'] = password
            obj['method'] = method
            usernameWithMethod = username + '-' + method 
            credentials[usernameWithMethod] = obj
            usernames.append(usernameWithMethod)
            counter += 1
    print('[Scientist] Loaded accounts file.')
    return { 'usernames': usernames, 'credentials': credentials }

def write_event_update(username, status):
    update = {}
    update['username'] = username
    update['status'] = status
    window.write_event_value('Update Running List', update)

def autoVote(account, screenshots_folder):
    write_event_update(account['username'], 'Logging In')
    driver = start_browser()
    auth = None
    running[account['username']] = 'Logging In'
    if account['method'] == 'twitch':
        auth = auth_twitch(driver, account)
    elif account['method'] == 'gmail':
        auth = auth_google(driver, account)
    elif curr['method'] == 'kakao':
        auth = auth_kakao(driver, account)
    
    if (auth is not None):
        vote(driver, account, screenshots_folder)
    else:
        write_event_update(account['username'], 'Quit')
        
    # if done voting
    if (driver is not None):
        write_event_update(account['username'], 'Quit')
        driver.quit()

def mprint(*args, **kwargs):
    window['log'].print(*args, **kwargs)

print = mprint
        

# main

# os.environ['WDM_LOCAL'] = '1'
# os.environ['WDM_LOG_LEVEL'] = '0'

#load user settings
#sg.user_settings_filename(path='.')
settings = sg.UserSettings('scientist_config.ini', use_config_file=True, convert_bools_and_none=True)

credentials = {}
usernames = []

running = OrderedDict()
running_accounts = []

continue_program = True
driver = None
layout = [  
            [sg.Text('love aint a science, do it for twice', size=(30, 1), font=('Any', 15, 'bold'), justification='left')],
            [sg.Text('Select accounts file (.csv) to load and folder for screenshots output:', size=(60, 1), justification='left')],
            [sg.Text('Accounts', size=(10, 1)), sg.Input(settings['Settings']['prev_accounts_file'], key='accounts_file_browse', enable_events=True), sg.FileBrowse()],
            [sg.Text('Screenshots', size=(10, 1)), sg.Input(settings['Settings']['prev_screenshots_folder'], key='screenshots_folder_browse', enable_events=True), sg.FolderBrowse()],
            [sg.Text('Select account:', size=(30, 1), justification='left'), sg.Text('Currently running:', size=(30, 1), justification='left'),],
            [sg.Listbox(usernames, key='username_select', size=(30,10)), sg.Listbox(running_accounts, key='running_list', highlight_text_color=sg.theme_input_text_color(), highlight_background_color=sg.theme_input_background_color(), size=(30,10), pad=((20, 0), (10, 10)))],
            [sg.Column([ [sg.Button('Vote'), sg.Button('Refresh Accounts'), sg.Button('Exit')] ], vertical_alignment='center', justification='left')],
            [sg.Text('Log:', size=(10, 1), justification='left')],
            [sg.Multiline(size=(66, 5), reroute_cprint=True, key='log', reroute_stdout=True, disabled=True, auto_refresh=True, write_only=True, pad=((5, 0), (0, 20)))]
            #[sg.Combo(usernames, key='username_select', default_value=usernames[0], readonly=True)],
        ]
if platform.system() == 'Windows':
    icon = 'assets/icons/potion.ico'  
else:
    icon = 'assets/icons/potion.icns'  
window = sg.Window('Project Scientist', layout, icon=icon, keep_on_top=True).finalize()

if (settings['Settings']['prev_accounts_file']):
    try:
        accounts = load_accounts_file(settings['Settings']['prev_accounts_file'])
        usernames = accounts['usernames']
        credentials = accounts['credentials']
        window['username_select'].Update(values=usernames)
    except:
        sg.popup_error('Error reading file. Please make sure that the file is a .csv and follows the "username,password,method" format.', keep_on_top=True)

while True:
    event, values = window.Read()
    if event == 'Vote':
        if len(values['username_select']) > 0:
            curr = credentials[values['username_select'][0]]
            screenshots_folder = values['screenshots_folder_browse']
            if screenshots_folder and Path(screenshots_folder).is_dir():
                screenshots_folder += '/'
                voter = threading.Thread(target=autoVote, args=(curr, screenshots_folder))
                voter.daemon = True
                voter.start()
            else:
                sg.popup_error('Error reading screenshots folder.', keep_on_top=True)  
        # curr = credentials[values['username_select']]
    elif event == 'accounts_file_browse' or event == 'Refresh Accounts':
        usernames = []
        credentials = {}
        try:
            accounts = load_accounts_file(values['accounts_file_browse'])
            usernames = accounts['usernames']
            credentials = accounts['credentials']
            settings['Settings']['prev_accounts_file'] = values['accounts_file_browse']
        except Exception as e:
            window['accounts_file_browse'].Update(value='')
            sg.popup_error('Error reading file. Please make sure that the file is a .csv and follows the "username,password,method" format.', keep_on_top=True)   
        window['username_select'].Update(values=usernames)
    elif event == 'screenshots_folder_browse':
        settings['Settings']['prev_screenshots_folder'] = values['screenshots_folder_browse']
    elif event == 'Update Running List':
        update = values[event]
        if update['status'] == 'Quit':
            if update['username'] in running:
                del running[update['username']]
        else:
            running[update['username']] = update['status']
        running_list = []
        ctr = 0
        for key, value in running.items():
            running_list.append(str(key) + ' - ' + value)

        window['running_list'].Update(values=running_list)
    elif event == sg.WIN_CLOSED or event == 'Exit':
        sys.exit()

    
