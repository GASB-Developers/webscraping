import csv
import nltk
from sklearn.feature_extraction.text import CountVectorizer
#nltk.download('punkt')

import_file = "export_files/export_22-11-02.csv"

with open(import_file, "r", newline="", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=";")
    for line in csv_reader:
        print(nltk.tokenize.word_tokenize(line[0].lower()))
        #print(line[0])
