

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
import pymongo
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://germys:072704gg@course.zifpblx.mongodb.net/Prev'
mongo = PyMongo(app)
# Access the users collection in the database
db = mongo.db.users
dbProduct = mongo.db.products

CORS(app)


@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

# * Create User


@app.route('/users', methods=['POST'])
def createUser():
    id = db.insert_one({
        'name': request.json['name'],
        'email': request.json['email'],
        'password': request.json['password']
    })
    return jsonify()

# * Search ALL Users


@app.route('/users', methods=['GET'])
def getUsers():
    users = []
    for doc in db.find():
        users.append({
            'id': str(doc['_id']),
            'name': doc['name'],
            'email': doc['email'],
            'password': doc['password']
        })
    return jsonify(users)

# * Search ONE User


@app.route('/user/<id>', methods=['GET'])
def getUser(id):
    user = db.find_one({'_id': ObjectId(id)})
    return jsonify({
        'id': str(ObjectId(user['_id'])),
        'name': user['name'],
        'email': user['email'],
        'password': user['password']
    })


# * Delete User
@ app.route('/user/<id>', methods=['DELETE'])
def deleteUser(id):
    db.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'User Deleted'})

# * Update User


@ app.route('/user/<id>', methods=['PUT'])
def updateUser(id):
    db.update_one({'_id': ObjectId(id)}, {'$set': {
                  'name': request.json['name'], 'email': request.json['email'], 'password': request.json['password']}})
    return 'User Updated'


# / Products


@ app.route('/product', methods=['POST'])
def createProduct():
    id = dbProduct.insert_one({
        'name': request.json['name'],
        'category': request.json['category'],
        'price': request.json['price']
    })
    return 'Okay! Product created'


if __name__ == '__main__':
    app.run(debug=True)
