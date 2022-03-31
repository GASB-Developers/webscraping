import os
import csv
from time import sleep
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By

"""
This script is work in progress.
After starting the script the cookies need to be manually accepted.
In addition, the scroll bar needs to be manually scrolled down immediately after the page has loaded,
in order to scrape all results. After 15 seconds the script starts scraping.

The script generates an output csv file which the number of synbio jobs found on each web site.
"""


buzzwords = ["synthetic biology", "synthetic biologist", "strain engineering", "protein engineering"]


# changes output file name if it already exists
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path


# checks for buzzwords to distinguish if it's a synbio job
def is_synbio_job(title, description):
    is_valid = False
    # convert to lower case for case-insensitive comparison
    title = title.lower()
    for term in buzzwords:
        if title.find(term) > -1 or description.find(term) > -1:
            is_valid = True
            break
    return is_valid


browser = webdriver.Firefox()

# url of google search results for synbio jobs
google_jobs_url = "https://www.google.com/search?q=job+offers+synthetic+biology&oq=job+offers+synthetic+biology&ibp=htl;jobs&sa=X"

browser.get(google_jobs_url)

offer_count = {}

synbio_job_count = 0

try:
    # Sleep time for manually accept cookies and scroll down in search results
    sleep(15)
    offers = browser.find_elements(by=By.CLASS_NAME, value="gws-plugins-horizon-jobs__tl-lif")

    for offer in offers:
        try:
            offer.click()

            # wait for all providers of a job to load
            sleep(0.5)

            title_elements = browser.find_elements(by=By.CLASS_NAME, value="KLsYvd")
            title = ""
            for i in range(0, len(title_elements)):
                if title_elements[i].is_displayed():
                    title = title_elements[i].text
                    break

            expand_button_elements = browser.find_elements(by=By.CLASS_NAME, value="OSrXXb")
            for button in expand_button_elements:
                if button.is_displayed():
                    button.click()
                    break

            description_elements = browser.find_elements(by=By.CLASS_NAME, value="HBvzbc")
            description = ""
            for i in range(0, len(description_elements)):
                if description_elements[i].is_displayed():
                    description = description_elements[i].text

            if is_synbio_job(title, description):
                synbio_job_count += 1
                providers = browser.find_elements(by=By.CLASS_NAME, value="va9cAf")
                for provider in providers:
                    if provider.is_displayed():
                        key = provider.text[15:]
                        if key.find("Live Jobs At A-New-Career") > -1:
                            key = "A-New-Career"
                        if key in offer_count.keys():
                            offer_count[key] += 1
                        else:
                            offer_count[key] = 1

        except Exception as exc:
            print('No providers found for job offer: %s' % (exc))

except Exception as exc:
    print('No matching job offers found with Google: %s' % (exc))


browser.quit()

print(str(synbio_job_count), " SynBio jobs have been found.")

file_name = uniquify("Job_site_comparison_" + date.today().strftime("%y-%m-%d") + ".csv")


# write generated statistics in csv file
with open(file_name, "w") as out_file:
    dict_keys = list(offer_count.keys())
    dict_keys.sort()
    writer = csv.DictWriter(out_file, dict_keys)
    writer.writeheader()
    writer.writerow(offer_count)
