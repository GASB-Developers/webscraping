from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

browser = webdriver.Firefox()

#browser.get('https://inventwithpython.com')
#browser.get('https://login.metafilter.com')


# try:
#     elem = browser.find_element(by=By.CLASS_NAME, value='card-img-top.cover-thumb')
#     print('Found <%s> element with that class name!' % (elem.tag_name))
#     elem.click()
#     linkElem = browser.find_element(by=By.LINK_TEXT, value='Read Online for Free')
#     linkElem.click()
# except:
#     print('Was not able to find an element with that name.')


# try:
#     userElem = browser.find_element(by=By.ID, value='user_name')
#     userElem.send_keys('your_real_username_here')
#     passwordElem = browser.find_element(by=By.ID, value='user_pass')
#     passwordElem.send_keys('your_real_password_here')
#     passwordElem.submit()
# except:
#     print("Element not found")

browser.get('https://gabrielecirulli.github.io/2048/')


def accept_cookies():
    try:
        cookie_accept = browser.find_element(by=By.ID, value='ez-accept-all')
        if cookie_accept.is_displayed():
            cookie_accept.click()
    except Exception as exc:
        pass  # nothing to do when there are no cookies to accept


def play():
    game_ended = False
    while not game_ended:
        try:
            retry_Elem = browser.find_element(by=By.CLASS_NAME, value='retry-button')
            # print(retry_Elem.is_displayed())
            game_ended = retry_Elem.is_displayed()
            htmlElem = browser.find_element(by=By.TAG_NAME, value='html')
            htmlElem.send_keys(Keys.UP)
            htmlElem.send_keys(Keys.RIGHT)
            htmlElem.send_keys(Keys.DOWN)
            htmlElem.send_keys(Keys.LEFT)
            sleep(0.05)
        except Exception as exc:
            print('There was a problem: %s' % (exc))
            game_ended = True
    accept_cookies()
    retry_Elem.click()

for i in range(5):
    play()

try:
    best_score = browser.find_element(by=By.CLASS_NAME, value='best-container')
    print("The best score was: " + best_score.text)
except Exception as exc:
    print('There was a problem: %s' % (exc))
