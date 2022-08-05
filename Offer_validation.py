import re
import validators
import textwrap as tr
from datetime import date, timedelta

buzzwords = ["synthetic biology", "synthetic biologist", "strain engineering", "protein engineering"]
job_types = ["Part-time", "Industry", "Internship", "PhD", "PostDoc", "StartUp"]
job_types_dict = dict(Full_Time=["Part-time", "Part time", "part time", "part-time", "Teilzeit"],
                      Industry=["Industry", "Industrie"],
                      Internship=["Internship", "Praktikum"],
                      PhD=["PhD", "Promotion"],
                      PostDoc=["PostDoc", "Post-Doc", "Post Doc", "Postdoctoral", "post-doc", "postdoc",
                               "postdoctoral"],
                      StartUp=["StartUp", "Startup"])

### Definition of data-type to store job offers ###
class JobOffer:
    def __init__(self, title, job_type, description, application_address_url, company, location, post_date):
        # verify title
        if not is_synbio_job(title, description):
            raise Exception("Seems not to be a SynBio job! It has to contain one of the pre-defined buzzwords.")

        # verify job type
        if is_job_type_valid(job_type):
            self.job_type = job_type
        else:
            raise Exception("Invalid job type! It has to be a list and to contain only pre-defined job-types.")

        # verify application url
        if is_appl_url_valid(application_address_url):
            self.application_address_url = application_address_url
        else:
            raise Exception("Invalid application URL/eMail-Address!")

        self.title = title
        self.description = description
        self.company = company
        self.location = location
        self.post_date = post_date

    def __str__(self):
        return "Title: {}\nDescription: {}\nCompany: {}\nLocation: {}\nJob-Type: {}\nApplication-URL: {}\n"\
            .format(self.title, tr.shorten(self.description, width=100, placeholder=" [...]"),
                    self.company, self.location, ", ".join(self.job_type), self.application_address_url, self.post_date)

    # comparison of objects
    def __eq__(self, other):
        return self.title == other.title and self.description == other.description and self.company == other.company \
               and self.job_type == other.job_type and self.application_address_url == other.application_address_url \
               and self.location == other.location and self.post_date == other.post_date

    # decide whether two offers are duplicates of each other TODO: make duplicate identification more precise
    def is_duplicate(self, other):
        return self.description == other.description \
               or self.has_same_title(other) and self.location == other.location

    def comparable_title(self):
        title1 = self.title.lower()
        title1 = re.sub(" \(.{3,7}\)", "", title1)
        title1 = title1.replace(" mfd", "")
        title1 = title1.replace(",", "")
        title1 = title1.replace(" -", "")
        title1 = title1.replace("-", " ")
        title1 = title1.replace(" –", "")
        title1 = title1.replace("...", "")
        title1 = title1.replace("\"", "")
        title1 = title1.replace("“", "")
        return title1

    def has_same_title(self, other):
        #print(self.title)
        #print(other.title)
        title1 = self.comparable_title().split(" ")
        title2 = other.comparable_title().split(" ")
        one_in_two = True
        for term in title1:
            if term not in title2:
                one_in_two = False
                break
        two_in_one = True
        for term in title2:
            if term not in title1:
                two_in_one = False
                break
        #print(one_in_two or two_in_one)
        #print("\n")
        return one_in_two or two_in_one

    # generate string for .csv file, representing object
    def csv_line(self):
        # job offer expires after one week (planned frequency for actualization of website)
        expiry_date = str(date.today() + timedelta(days=7))
        return [self.title, self.description, self.company, ", ".join(self.job_type), self.application_address_url,
                self.post_date, expiry_date, self.location]


def is_synbio_job(title, description):
    is_valid = False
    # convert to lower case for case-insensitive comparison
    title = title.lower()
    for term in buzzwords:
        if title.find(term) > -1 or description.find(term) > -1:
            is_valid = True
            break
    return is_valid


def is_job_type_valid(job_type):
    is_valid = True
    if type(job_type) is list:
        for t in job_type:
            if t not in job_types:
                is_valid = False
                break
    else:
        is_valid = False
    return is_valid


def is_appl_url_valid(appl_url):
    return validators.url(appl_url) or validators.email(appl_url)