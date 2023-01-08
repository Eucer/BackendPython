# code
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import pymongo
import warnings
import csv

warnings.simplefilter(action='ignore', category=FutureWarning)
client = pymongo.MongoClient(
    "mongodb+srv://germys:5eucerYw0z7Z@cluster0.ga2lq.mongodb.net/test")

# Selecciona la base de datos y la colección
db = client['test']
searchViews = db['views']
searchProducts = db['products']


# code

viewsUser = searchViews.find({})
productUser = searchProducts.find({})

# Array que quieres convertir a CSV
dataViews = [documento for documento in viewsUser]

with open('views_array_a_csv.csv', 'w', newline='') as csvfile:
    # Crea un objeto writer
    writer = csv.writer(csvfile)
    writer.writerow(['userId', 'productID', 'views'])
    # Itera sobre el array y escribe cada fila en el archivo CSV
    for documento in dataViews:
        writer.writerow(
            [documento['userId'], documento['productID'], documento['views']])

# Array que quieres convertir a CSV
dataProduct = [documento for documento in productUser]

# Abre el archivo en modo escritura
with open('product_array_a_csv.csv', 'w', newline='') as csvfile:
    # Crea un objeto writer
    writer = csv.writer(csvfile)
    # Itera sobre el array y escribe cada fila en el archivo CSV
    writer.writerow(['dc', 'name', 'category', '_id'])
    for documento in dataProduct:
        writer.writerow(
            [documento['dc'], documento['name'], documento['category'], documento['_id']])

views = pd.read_csv("views_array_a_csv.csv")
views.head()

products = pd.read_csv('product_array_a_csv.csv', encoding='iso-8859-1')
products.head()

n_views = len(views)
n_products = len(views['productID'].unique())
n_users = len(views['userId'].unique())

print(f"Number of views: {n_views}")
print(f"Number of unique productID's: {n_products}")
print(f"Number of unique users: {n_users}")
print(f"Average views per user: {round(n_views/n_users, 2)}")
print(f"Average views per movie: {round(n_views/n_products, 2)}")

user_freq = views[['userId', 'productID']].groupby(
    'userId').count().reset_index()
user_freq.columns = ['userId', 'n_views']
user_freq.head()


# Find Lowest and Highest rated products:
mean_views = views.groupby('productID')[['views']].mean()
# Lowest rated products
lowest_rated = mean_views['views'].idxmin()
products.loc[products['dc'] == lowest_rated]
# Highest rated products
highest_rated = mean_views['views'].idxmax()
products.loc[products['dc'] == highest_rated]
# show number of people who rated products rated movie highest
views[views['productID'] == highest_rated]
# show number of people who rated products rated movie lowest
views[views['productID'] == lowest_rated]

# the above products has very low dataset. We will use bayesian average
movie_stats = views.groupby('productID')[['views']].agg(['count', 'mean'])
movie_stats.columns = movie_stats.columns.droplevel()

# Now, we create user-item matrix using scipy csr matrix


def create_matrix(df):

    N = len(df['userId'].unique())
    M = len(df['productID'].unique())

    # Map Ids to indices
    user_mapper = dict(zip(np.unique(df["userId"]), list(range(N))))
    movie_mapper = dict(zip(np.unique(df["productID"]), list(range(M))))

    # Map indices to IDs
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["userId"])))
    movie_inv_mapper = dict(zip(list(range(M)), np.unique(df["productID"])))

    user_index = [user_mapper[i] for i in df['userId']]
    movie_index = [movie_mapper[i] for i in df['productID']]

    X = csr_matrix((df["views"], (movie_index, user_index)), shape=(M, N))

    return X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper


X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper = create_matrix(
    views)

"""
Find similar products using KNN
"""


def find_similar_products(movie_id, X, k, metric='cosine', show_distance=False):

    neighbour_ids = []

    movie_ind = movie_mapper[movie_id]

    if movie_ind in movie_mapper:
        movie_ind = movie_mapper[movie_id]
    else:
        movie_ind = movie_mapper[72016263]

    movie_vec = X[movie_ind]
    k += 1
    kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
    kNN.fit(X)
    movie_vec = movie_vec.reshape(1, -1)
    neighbour = kNN.kneighbors(movie_vec, return_distance=show_distance)
    for i in range(0, k):
        n = neighbour.item(i)
        neighbour_ids.append(movie_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids


product_name = dict(zip(products['dc'], products['name']))


movie_id = 52349818

similar_ids = find_similar_products(movie_id, X, k=10)
movie_title = product_name[movie_id]

print(f"Since you watched {movie_title}")
for i in similar_ids:
    print(product_name[i])
