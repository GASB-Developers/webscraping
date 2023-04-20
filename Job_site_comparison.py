import csv
import os
import pickle
import requests
import bs4
from datetime import date, timedelta
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from sklearn.feature_extraction.text import TfidfVectorizer
import seaborn as sns
import matplotlib.pylab as plt

from Offer_validation import JobOffer, job_types_dict, is_synbio_job, is_GASB_job

"""
This script is work in progress.
After starting the script the cookies need to be manually accepted.
In addition, the scroll bar needs to be manually scrolled down immediately after the page has loaded,
in order to scrape all results. After 15 seconds the script starts scraping.

The script generates an output csv file which the number of synbio jobs found on each web site.
"""

# TODO: Generation of .csv file of running times/dates and number of added/removed job offers for analysis

# TODO: Automated text-formatting possible?

# TODO: Remove job offers that are filled/expired (e.g. follow URL, search for date or expiry notification)

# TODO: Add jobs in other countries (neighbor countries, or most relevant),
#  e.g. modification of job page to display Germany as default

# TODO: Add Bachelor- and Master-theses offers (additional searches)

# TODO: Extend search terms (e.g. biotechnology, ...-engineering, ...)

# TODO: Connection to Slack channel to include jobs manually found by other active members

# TODO: "Quality ranking" so that in case of (not exact) duplicates the "best" offer can be kept

# TODO: Optimize duplicate identification: It can happen that jobs with the same/similar description are distinct offers

# TODO: Speed-up search so that the script only waits if necessary


# Determines whether to filter results for synbio jobs
do_filtering = True


# url of google search results for synbio jobs
#google_jobs_url = "https://www.google.com/search?q=job+offers+synthetic+biology&oq=job+offers+synthetic+biology&ibp=htl;jobs&sa=X"
google_jobs_url = "https://www.google.com/search?q=synthetic+biology+job+offers&sxsrf=APwXEde-lygOz7othEIDZQdJAq1U6lhppA:1682009949210&ei=XW9BZMevDJeHxc8PpOWsmAE&oq=synth&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAxgAMgQIIxAnMgoIABCKBRCxAxBDMggIABCABBCxAzIICAAQgAQQsQMyCAgAEIAEELEDMggIABCABBCxAzIICAAQgAQQsQMyCAgAEIAEELEDMggIABCABBCxAzIICAAQgAQQsQM6CggAEEcQ1gQQsAM6BwgAEIoFEEM6BQgAEIAEOgsIABCABBCxAxCDAToLCC4QgAQQsQMQgwE6FAguEIAEELEDEIMBEMcBENEDENQCOhEILhCABBCxAxCDARDHARDRAzoICC4QgAQQsQM6DgguEIAEELEDEMcBENEDSgQIQRgAUIMVWJQcYLIsaARwAXgAgAFmiAGYA5IBAzQuMZgBAKABAcgBCMABAQ&sclient=gws-wiz-serp&ibp=htl;jobs&sa=X&ved=2ahUKEwiNmIO297j-AhXEQvEDHbJUD9IQutcGKAF6BAg_EBU#htivrt=jobs&htidocid=DXEjpnrYNgYAAAAAAAAAAA%3D%3D&fpstate=tldetail"

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


def get_title():
    title_elements = browser.find_elements(by=By.CLASS_NAME, value="KLsYvd")
    offer_title = ""
    for i in range(0, len(title_elements)):
        if title_elements[i].is_displayed():
            offer_title = title_elements[i].text
            break
    return offer_title


def get_description():
    description_elements = browser.find_elements(by=By.CLASS_NAME, value="HBvzbc")
    offer_description = ""
    for i in range(0, len(description_elements)):
        if description_elements[i].is_displayed():
            offer_description = description_elements[i].text
    return offer_description


def get_job_types():
    jobtype_info_elem = browser.find_elements(by=By.CSS_SELECTOR,
                                              value="#gws-plugins-horizon-jobs__job_details_page > div > "
                                                    "div.ocResc > div:nth-child(2) > span.LL4CDc")
    jobtype_info = []
    for i in range(0, len(jobtype_info_elem)):
        if jobtype_info_elem[i].is_displayed():
            jobtype_info.append(jobtype_info_elem[i].text)
    offer_jobtypes_found = []
    for job_type in job_types_dict.values():
        for term in job_type:
            if term in jobtype_info or title.find(term) > -1:
                offer_jobtypes_found.append(job_type[0])
                break
    return offer_jobtypes_found


def get_company():
    # TODO: Fix problem that location and/or company is sometimes not found, even when displayed
    company_elements = browser.find_elements(by=By.CLASS_NAME, value="nJlQNd")
    offer_company = ""
    for i in range(0, len(company_elements)):
        if company_elements[i].is_displayed():
            offer_company = company_elements[i].text
            break
    return offer_company


def get_location():
    location_elements = browser.find_elements(by=By.CLASS_NAME, value="sMzDkb")
    offer_location = ""
    for i in range(0, len(location_elements)):
        if location_elements[i].is_displayed():
            offer_location = location_elements[i].text
            # Cut string if additional locations are mentioned; for uniformity
            if offer_location.find("weitere Standorte") != -1:
                offer_location = offer_location[:offer_location.find("(") - 1]
    return offer_location


def get_post_date():
    post_time_elements = browser.find_elements(by=By.CSS_SELECTOR,
                                               value="#gws-plugins-horizon-jobs__job_details_page > div > "
                                                     "div.ocResc > div:nth-child(1) > span.LL4CDc > span")
    offer_post_date = str(date.today())
    for i in range(0, len(post_time_elements)):
        if post_time_elements[i].is_displayed():
            post_time = post_time_elements[i].text
            post_time = post_time.split(" ")[1]
            try:
                offer_post_date = str(date.today() - timedelta(days=float(post_time)))
            except Exception as e:
                offer_post_date = str(date.today())
    return offer_post_date


# returns list of names of providers of the displayed job offer
def get_providers():
    providers = browser.find_elements(by=By.CLASS_NAME, value="va9cAf")
    offer_providers = []
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
            # Store each provider of current job
            offer_providers.append(key)
    return offer_providers


# TODO: check whether a job offer is already expired
# TODO: When expanding of description scrolls page down, links to providers are not "displayed" anymore!
# TODO: Currently the script crashes/ends when requests.get(url) is called...
def is_expired():
    provider_url_elements = browser.find_elements(by=By.CLASS_NAME, value="pMhGee")
    job_urls = []
    for elem in provider_url_elements:
        if elem.is_displayed():
            job_urls.append(elem.get_attribute("href"))
    for url in job_urls:
        pass
        #page = requests.get(url)
        # print(page.text)
        #BS_elem = bs4.BeautifulSoup(page.text, 'html.parser')
        #print(BS_elem.get_Text().find("has expired"))
        # page.raise_for_status()
        # print(page.text.find("has expired"))
    # print("")


def show_full_description():
    # click 'show full description' button
    # otherwise some part of the description might be missing
    expand_button_elements = browser.find_elements(by=By.CLASS_NAME, value="OSrXXb")
    for button in expand_button_elements:
        if button.is_displayed():
            button.click()
            break


def accept_cookies():
    cookie_button_elements = browser.find_elements(by=By.CSS_SELECTOR, value="#yDmH0d > c-wiz > div > div > div > "
                                                                             "div.NIoIEf > div.G4njw > div.AIC7ge > "
                                                                             "div.CxJub > div.VtwTSb > "
                                                                             "form:nth-child(2) > div > div > button "
                                                                             "> span")
    for elem in cookie_button_elements:
        if elem.is_displayed():
            elem.click()
            break


browser = webdriver.Firefox()

browser.get(google_jobs_url)

# Dictionary to count occurrences of each provider of job offers
offer_count = {}

# Counter for number of found synbio jobs
synbio_job_count = 0

# List for JobOffer objects generated for found synbio jobs, is stored to hard drive
synbio_job_list = []


try:
    accept_cookies()

    sleep(1)
    offers = browser.find_elements(by=By.CLASS_NAME, value="gws-plugins-horizon-jobs__tl-lif")
    print(len(offers))
    len_offers = len(offers)
    browser.execute_script("arguments[0].scrollIntoView();", offers[len(offers)-1])
    sleep(1)
    offers = browser.find_elements(by=By.CLASS_NAME, value="gws-plugins-horizon-jobs__tl-lif")
    while len_offers < len(offers):
        print(len(offers))
        len_offers = len(offers)
        browser.execute_script("arguments[0].scrollIntoView();", offers[len(offers) - 1])
        sleep(5)
        offers = browser.find_elements(by=By.CLASS_NAME, value="gws-plugins-horizon-jobs__tl-lif")


    print(str(len(offers)) + " overall job offers have been found.")
    for offer in offers:
        try:
            browser.execute_script("arguments[0].scrollIntoView();", offer)

            offer.click()

            # wait for all providers of a job to load
            sleep(0.1)

            # Collect information about job offer
            title = get_title()
            jobtypes_found = get_job_types()
            company = get_company()
            location = get_location()
            post_date = get_post_date()
            providers_for_offer = get_providers()
            is_expired()
            # Expanding of description might cause problems with job providers when is scrolls the page down
            show_full_description()
            description = get_description()
            is_synbio = is_synbio_job(title, description)

            if not do_filtering or is_synbio:
                synbio_job_count += 1

            # Create JobOffer object and store in list
            if is_synbio and not is_GASB_job(providers_for_offer):
                try:
                    offer = JobOffer(title, jobtypes_found, description, browser.current_url,
                                     company, location, post_date)
                    synbio_job_list.append(offer)
                except Exception as exc:
                    print(exc)

        except Exception as exc:
            print('ERROR:' % (exc))

except Exception as exc:
    print('No matching job offers found with Google: %s' % (exc))


browser.quit()

### Remove duplicates (code modified taken from Jonathan Funk) ###

# Get data out of the objects
titles = []
descriptions = []
companies = []

for job in synbio_job_list:
    titles.append(job.title)
    descriptions.append(job.description)
    companies.append(job.company)


# Apply natural language processing to calculate pairwise similarities between offers
def calculate_similarity(data_list):
    tfidf = TfidfVectorizer().fit_transform(data_list)
    pairwise_similarity = tfidf * tfidf.T
    similarity_array = pairwise_similarity.toarray()
    return similarity_array


combined_similarity_array = calculate_similarity(titles)
combined_similarity_array += calculate_similarity(descriptions)
combined_similarity_array += calculate_similarity(companies)

# Calculate mean similarity over three data columns
mean_similarity = combined_similarity_array/3

# Visualize similarity to check if threshold is chosen correctly
ax = sns.heatmap(mean_similarity, linewidth=0.5)
ax.set_title('combined')
plt.show()

# Set threshold below which two job offers are considered to be duplicates
threshold = 0.3


# Keep only one of each duplicated job offer
not_duplicated = []
# Iterate through all job offers
for i in range(0, len(synbio_job_list)):
    duplicated = False
    # Compare each with all others further back in the list (of duplicates only the last one is kept)
    for j in range(i + 1, len(synbio_job_list)):
        if mean_similarity[i][j] > threshold:
            duplicated = True
            break
    # A job offer is kept when no duplicate is found further back in the list
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
    stats_file_name = uniquify("output_files/Job_site_comparison_" + date.today().strftime("%y-%m-%d") + "_synbio.csv")
else:
    stats_file_name = uniquify("output_files/Job_site_comparison_" + date.today().strftime("%y-%m-%d") + "_all.csv")

# Read last file of saved JobOffers
if os.path.exists(job_offers_file_name):
    with open(job_offers_file_name, "rb") as job_offers_file:
        synbio_job_list_old = pickle.load(job_offers_file)


    ### Code to print changes since last search. Does not work well because details might change. ###

    # Compare old and new JobOffers to find Offers that were published or removed since the last run,
    # report these changes
    # removed_offers = [item for item in synbio_job_list_old if item not in synbio_job_list]
    # new_offers = [item for item in synbio_job_list if item not in synbio_job_list_old]
    # if len(removed_offers) != 0:
    #     print("\n--- REMOVED JOB OFFERS SINCE LAST SEARCH ({}) ---\n".format(len(removed_offers)))
    #     for offer in removed_offers:
    #         print(offer)
    # else:
    #     print("\n--- No job offer was removed since last search ---\n")
    # if len(new_offers) != 0:
    #     print("\n--- NEW JOB OFFERS SINCE LAST SEARCH ({}) ---\n".format(len(new_offers)))
    #     for offer in new_offers:
    #         print(offer)
    # else:
    #     print("\n--- No job offer was added since last search ---\n")

# Save all JobOffer objects to file
with open(job_offers_file_name, "wb") as job_offers_file:
    pickle.dump(synbio_job_list, job_offers_file)

# Generate csv file for upload to website
export_file_name = uniquify("export_files/export_" + date.today().strftime("%y-%m-%d") + ".csv")
with open(export_file_name, "w", newline="", encoding="utf-8") as csv_file:
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
