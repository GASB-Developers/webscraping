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
    def __init__(self, title, job_type, description, application_address_url, company):
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

    def __str__(self):
        return "Title: {}\nDescription: {}\nCompany: {}\nJob-Type: {}\nApplication-URL: {}\n"\
            .format(self.title, tr.shorten(self.description, width=100, placeholder=" [...]"),
                    self.company, ", ".join(self.job_type), self.application_address_url)

    # comparison of objects
    def __eq__(self, other):
        return self.title == other.title and self.description == other.description and self.company == other.company \
               and self.job_type == other.job_type and self.application_address_url == other.application_address_url

    # generate string for .csv file, representing object
    def csv_line(self):
        # job offer expires after one week (planned frequency for actualization of website)
        expiry_date = str(date.today() + timedelta(days=14))  # TODO: change back to 7
        return [self.title, self.description, self.company, ", ".join(self.job_type), self.application_address_url,
                expiry_date]


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