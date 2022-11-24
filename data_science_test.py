import csv
import nltk
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

import_file = "export_files/export_22-11-24.csv"


def calculate_similarity(column, file=import_file):
    dat = pd.read_csv(file, delimiter=';')
    data_list = dat[column].to_list()
    tfidf = TfidfVectorizer().fit_transform(data_list)
    pairwise_similarity = tfidf * tfidf.T
    similarity_array = pairwise_similarity.toarray()
    return similarity_array


combined_similarity_array = calculate_similarity("title")
combined_similarity_array += calculate_similarity("description")
combined_similarity_array += calculate_similarity("company")

mean_similarity = combined_similarity_array/3

ax = sns.heatmap(mean_similarity, linewidth=0.5)
ax.set_title('combined')
plt.show()

threshold = 0.3

x_flat = mean_similarity.flatten()
x_flat.sort()
plt.plot(x_flat)
plt.axhline(y=threshold, color='r', linestyle='-')
plt.show()
