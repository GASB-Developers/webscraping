import os
import csv
import nltk
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

import_file = "export_files/export_22-11-24.csv"
import_files = os.listdir("export_files/")


print(import_files)
title_list = []
description_list = []
company_list = []
for file in import_files:
    dat = pd.read_csv("export_files/" + file, delimiter=';')
    title_list.extend(dat["title"].to_list())
    description_list.extend(dat["description"].to_list())
    company_list.extend(dat["company"].to_list())


def calculate_similarity(data_list):
    tfidf = TfidfVectorizer().fit_transform(data_list)
    pairwise_similarity = tfidf * tfidf.T
    similarity_array = pairwise_similarity.toarray()
    return similarity_array


combined_similarity_array = calculate_similarity(title_list)
combined_similarity_array += calculate_similarity(description_list)
# When using all export files: companies have to be removed from analysis as the column is missing in older files
#combined_similarity_array += calculate_similarity(company_list)

#mean_similarity = combined_similarity_array/3
mean_similarity = combined_similarity_array/2

# When using all export files: Heatmap is not very meaningful
#print(mean_similarity)

#ax = sns.heatmap(mean_similarity)
#ax.set_title('combined')
#plt.show()

threshold = 0.3

x_flat = mean_similarity.flatten()
x_flat.sort()
plt.plot(x_flat)
plt.axhline(y=threshold, color='r', linestyle='-')
plt.show()
