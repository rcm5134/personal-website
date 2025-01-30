import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:
    
    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = []
        

        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        
    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")

        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)
            # Import the initial data
            try:
                params = []

                with open(data_path + f"initial_data/{table}.csv") as read_file:

                    scsv = read_file.read()

                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
                # Insert the data
                cols = params[0]; params = params[1:]
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                pass

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:

                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']

        return insert_id

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password'):
        # Check if account exists
        authentication = self.authenticate(email, password)
        # account already exists
        if authentication['success'] == 1:
            return {'success': 2}
        # account doesn't exist already
        if authentication['success'] == 0:
            # encrypt password
            password = self.onewayEncrypt(password)
            self.insertRows('users', ['email', 'password'], [email, password])
            return {'success': 1}
        # unknown auth
        return {'success': 0}

    def authenticate(self, email='me@email.com', password='password'):
        print("")
        print("                Authenticating: " + email)
        # Gather all user data
        query = f"""SELECT * FROM users"""
        result = self.query(query)
        # Encrypt password input to check with stored ecrypted password
        password = self.onewayEncrypt(password)
        # For each user in database
        for row in result:
            # If there is a matching password and email combo then return 1
            if email == row['email'] and password == row['password']:
                print("                Authentication successful.")

                return {'success': 1}
        # No matching auth found
        print("                Authentication unsuccessful.")
        return {'success': 0}
    
    def getUserCurrentBoard(self, email):
        query = f"""SELECT email, board_id FROM users"""
        data = self.query(query)

        for user in data:
            if user['email'] == email:
                print('Curr ID: ', user['board_id'])
                return user['board_id']

        return None
    
    def getCurrentBoardName(self, email):
        boardId = self.getUserCurrentBoard(email)

        if (not boardId):
            return None
        
        query = f"""SELECT board_id, name FROM boards"""
        result = self.query(query)

        for board in result:
            if board['board_id'] == boardId:
                return board['name']
            
        return None
    
    def accountExists(self, email = ''):
        query = f"""SELECT email FROM users"""
        data = self.query(query)
        # Chech each email to find a matching email
        for row in data:
            if row['email'] == email:
                return True
        # No match found
        return False

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


