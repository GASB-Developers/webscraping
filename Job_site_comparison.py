import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By


# def google_accept_cookies():
#     sleep(2)
#     try:
#         accept = browser.find_element(by=By.CLASS_NAME,
#                                       value='VfPpkd-Jh9lGc')
#         #if accept.is_displayed():
#         accept.click()
#     except Exception as exc:
#         print('A problem occurred while searching for button: %s' % (exc))


def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path


browser = webdriver.Firefox()
out_file = open(uniquify("Job_site_comparison.txt"), "w")

google_jobs_url = "https://www.google.com/search?q=job+offers+synthetic+biology&oq=job+offers+synthetic+biology&ibp=htl;jobs&sa=X"

browser.get(google_jobs_url)

try:
    #google_accept_cookies()
    # Sleep time for manually accept cookies and scroll down in search results
    sleep(15)
    offers = browser.find_elements(by=By.CLASS_NAME, value="gws-plugins-horizon-jobs__tl-lif")
    print(str(len(offers)) + " job offers found with Google")
except Exception as exc:
    print('No matching job offers found with Google: %s' % (exc))

browser.quit()
out_file.close()
