import mysql.connector
import re

HTML_TAG_REGEX = re.compile(r'<[^>]+>')

mydb = mysql.connector.connect(
    host="34.71.75.170",
    user="master",
    passwd="password",
    database="gator_bank"
)
mycursor = mydb.cursor()

def get_transactions(username):
    query = 'SELECT * from transactions WHERE username="{}"'.format(username)
    transactions = {
        "transactions" : []
    }
    try:
        mycursor.execute(query)
    except:
        #Transactions could not be pulled, return empty
        return transactions
    for x in mycursor:
        obj = {
            "username": x[1],
            "description": x[2],
            "price": x[3]
        }
        transactions['transactions'].append(obj)
    return transactions

def search_trans_description_unsafe(username, term):
    query = 'SELECT * FROM transactions WHERE username="{}" AND description="{}";'.format(username, term)
    print(query)
    transactions = {
        "transactions" : []
    }
    try:
        mycursor.execute(query)
    except:
        #Transactions could not be pulled, return empty.
        return transactions
    for x in mycursor:
        obj = {
            "username": x[1],
            "description": x[2],
            "price": x[3]
        }
        transactions['transactions'].append(obj)
    return transactions

def search_trans_description_safe(username, term):
    #filter out any bad characters
    term = term.replace('"', '')
    term = term.replace(';', '')
    term = term.replace('#', '')
    query = 'SELECT * FROM transactions WHERE username="{}" AND description="{}";'.format(username, term)
    transactions = {
        "transactions" : []
    }
    print(query)
    try:
        mycursor.execute(query)
    except:
        #Transactions could not be pulled, return empty.
        return transactions
    for x in mycursor:
        obj = {
            "username": x[1],
            "description": x[2],
            "price": x[3]
        }
        transactions['transactions'].append(obj)
    return transactions

def remove_html_tags(term):
    return HTML_TAG_REGEX.sub('', term)
