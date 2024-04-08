# Expense Tracker 

#TODO add budget limits
#TODO fix graphing issues

from flask import Flask, request, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
import json 
from bson import json_util
import matplotlib.pyplot as plt


client = MongoClient("localhost", 27017)
app = Flask(__name__)

DB = client['expense-tracker']
USERS = DB.users
EXPENSES = DB.expenses
INCOMES = DB.incomes

@app.route('/', methods=['GET'])
def index():
    return "<p>This is an expense tracker application</p>"

@app.route('/signup', methods=['POST'])
def signup():
    error = None
    user = dict(username = request.headers["username"], password = request.headers["password"])
    if USERS.find_one(user):
        return "User already exists, please login"         
    USERS.insert_one(user)
    return "User created successfully"

@app.route('/addexpense', methods=['POST'])
def addexpense():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    expense = EXPENSES.insert_one(dict(userid=user["_id"], amount=headers["amount"],category= headers["category"],description= headers["description"], date=headers["date"]))
    return str(expense.inserted_id)

@app.route('/addincome', methods=['POST'])
def addincome():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    income = INCOMES.insert_one(dict(userid=user["_id"], amount=headers["amount"],category= headers["category"],description= headers["description"], date=headers["date"]))
    return str(income.inserted_id)

@app.route('/list', methods=['GET'])
def listexpenses(): 
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    expenses = list(EXPENSES.find({"userid":user["_id"]}))
    incomes = list(INCOMES.find({"userid":user["_id"]}))
    accounts = dict(incomes = incomes, expenses = expenses)
    return json.loads(json_util.dumps(accounts))

@app.route('/delete', methods=['DELETE'])
def delete():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    expense = EXPENSES.find_one_and_delete({"_id":ObjectId(headers["id"])})
    if expense:
        return "Expense deleted successfully!"
    else:
        income = INCOMES.find_one_and_delete({"_id":ObjectId(headers["id"])})
        if income: return "Income deleted successfully!" 
        else : return "id not found"
    
@app.route('/update', methods=['PUT'])
def update():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    updatedaccount = dict()
    updatedaccount["$set"] = dict(userid=user["_id"], amount=headers["amount"],category= headers["category"],description= headers["description"], date=headers["date"])
    expense = EXPENSES.find_one_and_update({"_id":ObjectId(headers["id"])}, updatedaccount)

    if expense:
        return "Expense updated successfully!"
    else:
        income = INCOMES.find_one_and_update({"_id":ObjectId(headers["id"])}, updatedaccount)
        if income: return "Income updated successfully"
        else: "id not found"

@app.route('/totalexpense', methods=['GET'])
def totalexpense():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    
    pipeline = [
    {
        '$match': {
            'userid': ObjectId(user["_id"]),
        }
    }  
]
    expenses = list(map(lambda y:float(y),list(map(lambda x: x["amount"],list(EXPENSES.aggregate(pipeline))))))
    totalexpenses = sum(expenses)
    return str(totalexpenses)

@app.route('/totalincome', methods=['GET'])
def totalincome():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    
    pipeline = [
    {
        '$match': {
            'userid': ObjectId(user["_id"]),
        }
    }  
]
    incomes = list(map(lambda y:float(y),list(map(lambda x: x["amount"],list(INCOMES.aggregate(pipeline))))))
    totalincomes = sum(incomes)
    return str(totalincomes)

@app.route('/total', methods=['GET'])
def total():
    headers = request.headers
    user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
    if not user:
        return "User does not exist, please signup"
    pipeline = [
    {
        '$match': {
            'userid': ObjectId(user["_id"]),
        }
    }  
]
    incomes = list(map(lambda y:float(y),list(map(lambda x: x["amount"],list(INCOMES.aggregate(pipeline))))))
    totalincomes = sum(incomes)

    expenses = list(map(lambda y:float(y),list(map(lambda x: x["amount"],list(EXPENSES.aggregate(pipeline))))))
    totalexpenses = sum(expenses)

    total = totalincomes - totalexpenses
    return str(total)


# @app.route('/barplot', methods=['GET'])
# def barplot():
#     headers = request.headers
#     user = USERS.find_one(dict(username = headers["username"], password = headers["password"]))
#     if not user:
#         return "User does not exist, please signup"  
#     expenses = EXPENSES.find({"userid":ObjectId(user["_id"])})
#     categories = list(map(lambda x: x["category"],expenses))
#     amounts = list(map(lambda x: x["amount"],expenses))
#     plt.bar(categories,amounts, color='r', align = 'edge', width = 0.9, edgecolor = 'black', lw=2)
#     plt.savefig('/static/images/barplot.png')
#     return render_template('plot.html', name = 'barplot')





    
    