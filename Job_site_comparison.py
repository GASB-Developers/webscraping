import os
import csv
import pickle
from time import sleep
from datetime import date, timedelta
from selenium import webdriver
from Offer_validation import JobOffer, buzzwords, job_types, job_types_dict, is_synbio_job
from selenium.webdriver.common.by import By

"""
This script is work in progress.
After starting the script the cookies need to be manually accepted.
In addition, the scroll bar needs to be manually scrolled down immediately after the page has loaded,
in order to scrape all results. After 15 seconds the script starts scraping.

The script generates an output csv file which the number of synbio jobs found on each web site.
"""

# TODO: Automatic cookie-acceptance and scrolling

# TODO: Generation of .csv file of running times/dates and number of added/removed job offers for analysis

# TODO: Automated text-formatting possible?

# TODO: Fix upload of location (Google API needed?)

# Determines whether to filter results for synbio jobs
do_filtering = True


# url of google search results for synbio jobs
google_jobs_url = "https://www.google.com/search?q=job+offers+synthetic+biology&oq=job+offers+synthetic+biology&ibp=htl;jobs&sa=X"


# Name of output file to store JobOffer objects
job_offers_file_name = "Job_offers_last_run.list"


# changes output file name if it already exists
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path


browser = webdriver.Firefox()

browser.get(google_jobs_url)

# Dictionary to count occurrences of each provider of job offers
offer_count = {}

# Counter for number of found synbio jobs
synbio_job_count = 0

# List for JobOffer objects generated for found synbio jobs, is stored to hard drive
synbio_job_list = []


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

            # click 'show full description' button
            # otherwise some part of the description might be missing
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

            jobtype_info_elem = browser.find_elements(by=By.CSS_SELECTOR,
                                                      value="#gws-plugins-horizon-jobs__job_details_page > div > "
                                                            "div.ocResc > div:nth-child(2) > span.LL4CDc")
            jobtype_info = []
            for i in range(0, len(jobtype_info_elem)):
                if jobtype_info_elem[i].is_displayed():
                    jobtype_info.append(jobtype_info_elem[i].text)
            jobtypes_found = []
            for job_type in job_types_dict.values():
                for term in job_type:
                    if term in jobtype_info or title.find(term) > -1:
                        jobtypes_found.append(job_type[0])
                        break

            # TODO: Fix problem that location and/or company is sometimes not found, even when displayed
            company_elements = browser.find_elements(by=By.CLASS_NAME, value="nJlQNd")
            company = ""
            for i in range(0, len(company_elements)):
                if company_elements[i].is_displayed():
                    company = company_elements[i].text
                    break

            location_elements = browser.find_elements(by=By.CLASS_NAME, value="sMzDkb")
            location = ""
            for i in range(0, len(location_elements)):
                if location_elements[i].is_displayed():
                    location = location_elements[i].text
                    # Cut string if additional locations are mentioned; for uniformity
                    if location.find("weitere Standorte") != -1:
                        location = location[:location.find("(")-1]

            post_time_elements = browser.find_elements(by=By.CSS_SELECTOR,
                                                       value="#gws-plugins-horizon-jobs__job_details_page > div > "
                                                             "div.ocResc > div:nth-child(1) > span.LL4CDc > span")
            post_date = str(date.today())
            for i in range(0, len(post_time_elements)):
                if post_time_elements[i].is_displayed():
                    post_time = post_time_elements[i].text
                    post_time = post_time.split(" ")[1]
                    try:
                        post_date = str(date.today() - timedelta(days=float(post_time)))
                    except Exception as e:
                        post_date = str(date.today())

            if not do_filtering or is_synbio_job(title, description):
                synbio_job_count += 1
                providers = browser.find_elements(by=By.CLASS_NAME, value="va9cAf")
                for provider in providers:
                    if provider.is_displayed():
                        key = provider.text[15:]
                        # A-New-Career job website has a number in its name which would make counting difficult
                        if key.find("Live Jobs At A-New-Career") > -1:
                            key = "A-New-Career"
                        if key in offer_count.keys():
                            offer_count[key] += 1
                        else:
                            offer_count[key] = 1

            if is_synbio_job(title, description):
                try:
                    offer = JobOffer(title, jobtypes_found, description, browser.current_url,
                                     company, location, post_date)
                    synbio_job_list.append(offer)
                except Exception as exc:
                    print(exc)

        except Exception as exc:
            print('No providers found for job offer: %s' % (exc))

except Exception as exc:
    print('No matching job offers found with Google: %s' % (exc))


browser.quit()

# Remove duplicates
not_duplicated = [synbio_job_list[0]]
for i in range(1, len(synbio_job_list)):
    duplicated = False
    for j in range(0, len(not_duplicated)):
        if synbio_job_list[i].is_duplicate(not_duplicated[j]):
            duplicated = True
            break
    if not duplicated:
        not_duplicated.append(synbio_job_list[i])
# Report which offers where removed as duplicates for check by user
removed_duplicates = [item for item in synbio_job_list if item not in not_duplicated]
if len(removed_duplicates) != 0:
    print("\n--- REMOVED DUPLICATES ({}) ---\n".format(len(removed_duplicates)))
    for offer in removed_duplicates:
        print(offer)
else:
    print("\n--- No duplicates were removed ---\n")
synbio_job_list = not_duplicated


if do_filtering:
    print(str(synbio_job_count), " SynBio jobs have been found.")
else:
    print(str(synbio_job_count), " jobs have been found.")

if do_filtering:
    stats_file_name = uniquify("Job_site_comparison_" + date.today().strftime("%y-%m-%d") + "_synbio.csv")
else:
    stats_file_name = uniquify("Job_site_comparison_" + date.today().strftime("%y-%m-%d") + "_all.csv")

# Read last file of saved JobOffers
if os.path.exists(job_offers_file_name):
    with open(job_offers_file_name, "rb") as job_offers_file:
        synbio_job_list_old = pickle.load(job_offers_file)

    # Compare old and new JobOffers to find Offers that were published or removed since the last run,
    # report these changes
    removed_offers = [item for item in synbio_job_list_old if item not in synbio_job_list]
    new_offers = [item for item in synbio_job_list if item not in synbio_job_list_old]
    if len(removed_offers) != 0:
        print("\n--- REMOVED JOB OFFERS SINCE LAST SEARCH ({}) ---\n".format(len(removed_offers)))
        for offer in removed_offers:
            print(offer)
    else:
        print("\n--- No job offer was removed since last search ---\n")
    if len(new_offers) != 0:
        print("\n--- NEW JOB OFFERS SINCE LAST SEARCH ({}) ---\n".format(len(new_offers)))
        for offer in new_offers:
            print(offer)
    else:
        print("\n--- No job offer was added since last search ---\n")

# Save all JobOffer objects to file
with open(job_offers_file_name, "wb") as job_offers_file:
    pickle.dump(synbio_job_list, job_offers_file)

# Generate csv file for upload to website
with open("export.csv", "w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=";")
    csv_writer.writerow(["title", "description", "company", "job-type", "application-url",
                         "post-date", "expiry-date", "location"])
    for offer in synbio_job_list:
        csv_writer.writerow(offer.csv_line())

# write generated statistics in csv file
with open(stats_file_name, "w", encoding="utf-8") as out_file:
    dict_keys = list(offer_count.keys())
    dict_keys.sort()
    writer = csv.DictWriter(out_file, dict_keys)
    writer.writeheader()
    writer.writerow(offer_count)
