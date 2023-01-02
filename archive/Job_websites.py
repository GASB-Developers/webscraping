import requests, bs4, validators
from time import sleep
from Offer_validation import JobOffer, job_types_dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

job_offers_combined = []

browser = webdriver.Firefox()


### Web-Scraping of job websites ###

# JobVector
def jobvector_accept_privacy():
    try:
        accept = browser.find_element(by=By.CSS_SELECTOR,
                                      value='div.ddt-container:nth-child(3) > span:nth-child(1) > button:nth-child(1)')
        if accept.is_displayed():
            accept.click()
    except Exception as exc:
        pass  # nothing to do when there are no cookies to accept


def jobvector_decline_newsletter():
    try:
        decline = browser.find_element(by=By.CSS_SELECTOR,
                                       value='#__layout > div > div > div.navbar-background.no-print.no-print > '
                                             'div:nth-child(2) > div > svg')
        if decline.is_displayed():
            decline.click()
    except Exception as exc:
        #print('There is a problem with declining the newsletter: %s' % (exc))
        pass  # nothing to do when there is no newsletter-overlay


def jobvector_parse_offer(jobvector_offer):
    try:
        sleep(1)
        jobvector_accept_privacy()
        jobvector_decline_newsletter()
        jobvector_offer.click()
        sleep(0.5)
        jobvector_decline_newsletter()
        # parsing of information
        title = browser.find_element(by=By.CSS_SELECTOR, value="#__layout > div > div > div.paneview > "
                                                               "div.columns.is-gapless.paneview-main > "
                                                               "div.column.is-hidden-mobile.content-view.print-page > "
                                                               "div > "
                                                               "div.wrapper.bg-white.border > div > div > div > h2 > "
                                                               "span").text
        description = browser.find_element(by=By.CSS_SELECTOR, value="#__layout > div > div > div.paneview > "
                                                                     "div.columns.is-gapless.paneview-main > "
                                                                     "div.column.is-hidden-mobile.content-view.print"
                                                                     "-page > div > div:nth-child(4) > "
                                                                     "div.job-view.print.print-detail > div > "
                                                                     "div.job-description > div:nth-child(1)").text
        company = browser.find_element(by=By.CSS_SELECTOR, value="#__layout > div > div > div.paneview > "
                                                                 "div.columns.is-gapless.paneview-main > "
                                                                 "div.column.is-hidden-mobile.content-view.print-page "
                                                                 "> div > div.wrapper.bg-white.border > div > div > "
                                                                 "div > div.company > span").text
        jobtype_info = browser.find_element(by=By.CLASS_NAME, value="vacancy-info.columns").text
        jobtypes_found = []
        for job_type in job_types_dict.values():
            for term in job_type:
                if jobtype_info.find(term) > -1 or title.find(term) > -1:
                    jobtypes_found.append(job_type[0])
                    break
        current_url = browser.current_url
        job_id = current_url[(current_url.find("jobId") + 6):]
        application_url = "https://www.jobvector.de/jobs-stellenangebote/bewerben.html?id=" + job_id
        print(title)
        print(jobtypes_found)
        # print(description)
        print(application_url)
        print(company)
        browser.back()
        try:
            return JobOffer(title, jobtypes_found, description, application_url, company)
        except Exception:
            return None
    except Exception as exc:
        print('There was a problem with one job offer on JobVector: %s' % (exc))


url_jobvector = "https://www.jobvector.de/stellensuche/?keyword=synthetic%20biology&sort=score&pn=1"

browser.get(url_jobvector)

try:
    offers = browser.find_elements(by=By.CLASS_NAME, value="list-item")
    for offer in offers:
        offer_obj = jobvector_parse_offer(offer)
        if offer_obj is not None:
            job_offers_combined.append(offer_obj)
except Exception as exc:
    print('No matching job offers found on JobVector: %s' % (exc))





browser.quit()

print(str(len(job_offers_combined)) + " synbio job offers were found:")
for job_offer in job_offers_combined:
    print(job_offer.title + " (" + job_offer.company + ")")

