import numpy as np
import pandas as pd
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# loading the data from the csv file to apandas dataframe
products_data = pd.read_csv('product_array_a_csv.csv',
                            encoding='iso-8859-1')

# printing the first 5 rows of the dataframe
products_data.head()

# number of rows and columns in the data frame

products_data.shape


# selecting the relevant features for recommendation

selected_features = ['category', 'slug', 'name', 'dui', 'marca']
print(selected_features)
# replacing the null valuess with null string

for feature in selected_features:
    products_data[feature] = products_data[feature].fillna('')

combined_features = products_data['category']+' '+products_data['slug']+' ' + \
    products_data['name']+' '+products_data['dui']+' '+products_data['marca']

print(combined_features)

# converting the text data to feature vectors
vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
print(feature_vectors)

# getting the similarity scores using cosine similarity

similarity = cosine_similarity(feature_vectors)
print(similarity)

print(similarity.shape)
# getting the product name from the user

product_name = " AirPods Pro"
# creating a list with all the product names given in the dataset

list_of_all_titles = products_data['name'].tolist()
print(list_of_all_titles)
# finding the close match for the product name given by the user

find_close_match = difflib.get_close_matches(product_name, list_of_all_titles)
print(find_close_match)
close_match = find_close_match[0]
print(close_match)

# finding the index of the product with title

index_of_the_product = products_data[products_data.name ==
                                     close_match]['index'].values[0]
print(index_of_the_product)
print(index_of_the_product)

# getting a list of similar products

similarity_score = list(enumerate(similarity[index_of_the_product]))
print(similarity_score)

len(similarity_score)

# sorting the products based on their similarity score

sorted_similar_product = sorted(
    similarity_score, key=lambda x: x[1], reverse=True)
print(sorted_similar_product)
# print the name of similar products based on the index

print('products suggested for you : \n')

i = 1

for product in sorted_similar_product:
    index = product[0]
    title_from_index = products_data[products_data.index ==
                                     index]['_id'].values[0]
    if (i < 30):
        print(i, '.', title_from_index)
        i += 1
