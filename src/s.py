from fastapi import FastAPI, Response

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

import pymongo
from bson.objectid import ObjectId
import requests
import random
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import pprint

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


@app.get("/recomended-product/{name_product}")
async def process_data(name_product: str):

    client = pymongo.MongoClient(
        "mongodb+srv://germys:LWBVI45dp8jAIywv@douvery.0oma0vw.mongodb.net/Production")


# Selecciona la base de datos y la colección
    db = client['Production']
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

    # Inicializa el contador en 1

    # Obtiene todos los documentos de la colección
    documentos = searchProducts.find()

    # Para cada documento, agrega un nuevo campo "codigo" con un código único
    for doc in documentos:
        searchProducts.update_one({"_id": doc["_id"]}, {
            "$set": {"store": ['637f24cc2250d328d6aa0a79']}})

    # code

    # Inicializa el contador en 1
    # contador = 1

    # # Obtiene todos los documentos de la colección
    # documentos = searchProducts.find()

    # # Para cada documento, agrega un nuevo campo "codigo" con un código único
    # for doc in documentos:
    #     searchProducts.update_one({"_id": doc["_id"]}, {
    #         "$set": {"raw":  "1"}})
    # #     contador += 1

    warnings.simplefilter(action='ignore', category=FutureWarning)

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
        writer.writerow(['index', 'dc', 'name', 'category',
                        '_id', 'slug', 'marca', 'dui', 'keywords', 'sub-category', 'raw'])
        for documento in dataProduct:
            writer.writerow(
                [documento['index'], documento['dc'], documento['name'], documento['category'], documento['_id'],  documento['slug'],  documento['marca'],  documento['dui'], documento['keywords'], documento['sub-category'], documento['raw']])

    products_data = pd.read_csv('product_array_a_csv.csv',
                                encoding='iso-8859-1')

    # printing the first 5 rows of the dataframe
    products_data.head()

    # number of rows and columns in the data frame

    products_data.shape

    # selecting the relevant features for recommendation

    selected_features = ['sub-category',
                         'raw', 'keywords', 'name', 'category', 'marca', ]

    # replacing the null valuess with null string

    for feature in selected_features:
        products_data[feature] = products_data[feature].fillna('')

    combined_features = products_data['sub-category']+' '+products_data['name']+' ' + \
        products_data['raw']+' '+products_data['category'] + \
        ' '+products_data['marca']

    print(combined_features)
    # converting the text data to feature vectors
    vectorizer = TfidfVectorizer()
    feature_vectors = vectorizer.fit_transform(combined_features)

    # getting the similarity scores using cosine similarity

    similarity = cosine_similarity(feature_vectors)

    product_name = name_product
    # creating a list with all the product names given in the dataset

    list_of_all_titles = products_data['name'].tolist()

    # finding the close match for the product name given by the user

    find_close_match = difflib.get_close_matches(
        product_name, list_of_all_titles)

    close_match = find_close_match[0]

    # finding the index of the product with title

    index_of_the_product = products_data[products_data.name ==
                                         close_match]['index'].values[0]

    # getting a list of similar products

    similarity_score = list(enumerate(similarity[index_of_the_product]))

    len(similarity_score)

    # sorting the products based on their similarity score

    sorted_similar_product = sorted(
        similarity_score, key=lambda x: x[1], reverse=True)

    i = 0

    # for product in sorted_similar_product:
    #     index = product[0]
    #     title_from_index = products_data[products_data.index ==
    #                                      index]['name'].values[0]
    #     if (i < 30):
    #         print(i, '.', title_from_index)
    # i += 1

    def convert_to_serializable(value):
        if isinstance(value, ObjectId):
            # Convert ObjectId to str
            return str(value)
        # Return other values as is
        return value

    def products_to_json(products):
        # Convert each product to a serializable dict
        serializable_products = [
            {key: convert_to_serializable(value) if key == "_id" else value for key, value in product.items(
            ) if key in ["_id", "name", "price", "images", "slug", "category", "marca", "dui", "dc"]}
            for product in products
        ]
        # Serialize the list to JSON
        return serializable_products

    product_ids = []
    for product in sorted_similar_product:
        index = product[0]
        product_id = products_data[products_data.index ==
                                   index]['_id'].values[0]
        if i < 30:
            product_ids.append(product_id)
            i += 1

    product_ids = [ObjectId(pid) for pid in product_ids]

    # Busca los productos con los IDs especificados y los ordena según el índice de cada ID en la lista de IDs
    # Crea un diccionario de productos con sus respectivos IDs como clave
    products_dict = {product["_id"]: product for product in searchProducts.find(
        {'_id': {'$in': product_ids}})}

    # Crea una lista de productos ordenados según el orden de los IDs en la lista
    products_sorted = [products_dict[product_id]
                       for product_id in product_ids]

    # Convert ObjectId to str in the "_id" field of each product
    for product in products_sorted:
        product['_id'] = str(product['_id'])

    products_json = products_to_json(products_sorted)

    return products_json
