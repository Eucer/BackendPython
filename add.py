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
from pydantic import BaseModel
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
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


@app.get("/suggestions")
async def get_suggestions(q: str):
    client = pymongo.MongoClient(
        "mongodb+srv://germys:LWBVI45dp8jAIywv@douvery.0oma0vw.mongodb.net/Production")

    db = client['Production']

    products = db['products']
    products = list(products.find(
        {'$or': [
            {'name': {'$regex': q, '$options': 'i'}},
            {'keywords': {'$regex': q, '$options': 'i'}},
            {'category': {'$regex': q, '$options': 'i'}},

        ]}
    ))

    product_names = [product["name"].lower() for product in products]
    suggestions = [(products["name"], fuzz.token_set_ratio(
        q, product_name)) for product_name in product_names]
    suggestions.sort(key=lambda x: x[1], reverse=True)
    suggestions = suggestions[:13]
    return [suggestion[0] for suggestion in suggestions]


@app.get("/edit-data")
async def process_data():

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

    # # Inicializa el contador en 1
    # contador = 1

    # # Obtiene todos los documentos de la colección
    documentos = searchProducts.find()

    # Para cada documento, agrega un nuevo campo "codigo" con un código único
    for doc in documentos:
        searchProducts.update_one({"_id": doc["_id"]}, {
            "$set": {"item_condition": 'Nuevo'}})

    return ()
