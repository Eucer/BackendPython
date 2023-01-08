
import pandas as pd

import ast

from sklearn.feature_extraction.text import CountVectorizer

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity

import seaborn as sns

import numpy as np

import matplotlib.pyplot as plt


df_data = pd.read_csv('movies_metadata.csv', low_memory=False)

df_data = df_data[df_data['vote_count'].notna()]

plt.figure(figsize=(20, 5))

sns.distplot(df_data['vote_count'])

plt.title("Histogram of vote counts")

min_votes = np.percentile(df_data['vote_count'].values, 85)

df = df_data.copy(deep=True).loc[df_data['vote_count'] > min_votes]

df = df[df['overview'].notna()]

df.reset_index(inplace=True)


# processing of overviews

def process_text(text):

    # replace multiple spaces with one

    text = ' '.join(text.split())

    # lowercase

    text = text.lower()

    return text

    df['overview'] = df.apply(lambda x: process_text(x.overview), axis=1)

    tf_idf = TfidfVectorizer(stop_words='english')

    tf_idf_matrix = tf_idf.fit_transform(df['overview'])

    cosine_similarity_matrix = cosine_similarity(tf_idf_matrix, tf_idf_matrix)

    return df[df['original_title'] == title].index.values[0]
