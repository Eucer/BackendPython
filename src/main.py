
import json
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import csv
from fastapi import FastAPI, HTTPException
import pymongo
from bson.objectid import ObjectId
import requests
import random
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.exception_handler(Exception)
def handle_exception(request, exc):
    return {"message": str(exc)}


@app.get("/recomended-product/{dc_product}")
async def process_data(dc_product: str):

    warnings.simplefilter(action='ignore', category=FutureWarning)
    client = pymongo.MongoClient(
        "mongodb+srv://germys:5eucerYw0z7Z@cluster0.ga2lq.mongodb.net/test")

    # Selecciona la base de datos y la colección
    db = client['test']
    searchViews = db['views']
    searchProducts = db['products']

    # # Obtiene todos los documentos de la colección
    # documentos = searchProducts.find()

    # for doc in documentos:
    #     dc = -1
    #     while True:
    #         # Genera un código aleatorio de 8 dígitos
    #         dc = random.randint(10000000, 99999999)

    #         # Comprueba si el código ya existe en la base de datos
    #         existe = searchProducts.find_one({"ped": dc})
    #         if not existe:
    #             # Si el código no existe, termina el bucle y utiliza el código
    #             break
    #     # Utiliza la función update_one() para agregar el código al documento
    #     searchProducts.update_one({"_id": doc["_id"]}, {
    #         "$set": {"ped": dc}})

    # code

    viewsUser = searchViews.find({})
    productUser = searchProducts.find({})

    # Array que quieres convertir a CSV
    dataViews = [documento for documento in viewsUser]

    # Abre el archivo en modo escritura
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

    n_ratings = len(views)
    n_products = len(views['productID'].unique())
    n_users = len(views['userId'].unique())

    user_freq = views[['userId', 'productID']].groupby(
        'userId').count().reset_index()
    user_freq.columns = ['userId', 'n_ratings']
    user_freq.head()

    # Find Lowest and Highest rated movies:
    mean_views = views.groupby('productID')[['views']].mean()

    # Lowest rated movies
    lowest_rated = mean_views['views'].idxmin()

    products.loc[products['dc'] == lowest_rated]
    # Highest rated movies
    highest_rated = mean_views['views'].idxmax()
    products.loc[products['dc'] == highest_rated]
    # show number of people who rated movies rated movie highest
    views[views['productID'] == highest_rated]
    # show number of people who rated movies rated movie lowest
    views[views['productID'] == lowest_rated]

    # the above movies has very low dataset. We will use bayesian average
    product_stats = views.groupby(
        'productID')[['views']].agg(['count', 'mean'])
    product_stats.columns = product_stats.columns.droplevel()

    # Now, we create user-item matrix using scipy csr matrix

    def create_matrix(df):
        N = len(df['userId'].unique())
        M = len(df['productID'].unique())

        # Map Ids to indices
        user_mapper = dict(zip(np.unique(df["userId"]), list(range(N))))
        product_mapper = dict(
            zip(np.unique(df["productID"]), list(range(M))))

        # Map indices to IDs
        user_inv_mapper = dict(
            zip(list(range(N)), np.unique(df["userId"])))
        product_inv_mapper = dict(
            zip(list(range(M)), np.unique(df["productID"])))

        user_index = [user_mapper[i] for i in df['userId']]
        product_index = [product_mapper[i] for i in df['productID']]

        X = csr_matrix(
            (df["views"], (product_index, user_index)), shape=(M, N))

        return X, user_mapper, product_mapper, user_inv_mapper, product_inv_mapper

    X, user_mapper, product_mapper, user_inv_mapper, product_inv_mapper = create_matrix(
        views)

    def find_similar_products(product_id, X, k, metric='cosine', show_distance=False):

        neighbour_ids = []

        if product_id in product_mapper:
            product_ind = product_mapper[product_id]
        else:
            product_ind = product_mapper[72016263]

        product_vec = X[product_ind]
        k += 1
        kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
        kNN.fit(X)

        product_vec = product_vec.reshape(1, -1)
        neighbour = kNN.kneighbors(product_vec, return_distance=show_distance)

        for i in range(0, k):
            n = neighbour.item(i)
            neighbour_ids.append(product_inv_mapper[n])
        neighbour_ids.pop(0)
        return neighbour_ids

    product_name = dict(zip(products['dc'], products['_id']))

    product_id = int(dc_product)

    similar_ids = find_similar_products(product_id, X, k=5)
    product_nameT = product_name[product_id]

    product_ids = []
    for i in similar_ids:

        product_ids.append(ObjectId(product_name[i]))

    def buscar_productos():
        productos = []
        for producto in searchProducts.find({"_id": {"$in": product_ids}}):
            # Convert the ObjectId to a string before appending it to the list
            producto["_id"] = str(producto["_id"])

            productos.append(producto)
        return productos

    productos = buscar_productos()

   # Convertir el objeto ObjectId a una cadena
    productos = [{'_id': str(producto['_id']), 'name': producto['name'], 'marca': producto['marca'], 'description': producto['description'], 'images': producto['images'], 'quantity': producto['quantity'], 'price': producto['price'], 'category': producto['category'],   'discount': producto['discount'], 'slug':producto['slug'], 'uploaded_by': producto['uploaded_by'], 'dui': producto['dui'],  'productDetails': producto['productDetails'], 'raw': producto['raw'], 'store': producto['store'], 'dc': producto['dc'], }
                 for producto in productos]

    return productos
