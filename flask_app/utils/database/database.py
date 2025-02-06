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
        self.tables         = ['projects', 'skills']
        

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
# PROJECT RELATED
#######################################################################################
    
    def createProject(self, name, image, description, link, skills):
        """
        Author: Riley Moorman, rileycmoorman@gmail.com

        Creates a project row in the Projects table
        Params: 
            name (string): name of the project
            image (string): link to the project thumbnail
            description (string): description of the project
            link: (string): external link to the project
            skills (list of string): names of skills used in project (ex: ['C++', 'Python', 'JavaScript'])

        Returns: 
            None
        """
        # Insert Project into database
        self.insertRows(
            'projects', 
            ['name', 'image', 'description', 'link'],
            [name, image, description, link]
        )
        # Get the created project id
        proj_id = self.getProjectID(name)
        
        if proj_id == -1:
            print("Project name not found!")
            return
        
        # insert each skill into the skill db
        for skill in skills:
            self.insertRows(
                'skills',
                ['proj_id', 'name'],
                [proj_id, skill]
            )
        

    def getProjectID(self, proj_name):
        """
        Author: Riley Moorman, rileycmoorman@gmail.com

        Gets the ID of the project row containing the project name as an integer
        Params: 
            proj_name (string): name of the project
            
        Returns: 
            Int representing the project ID
            Returns -1 if there is not project of that name in the table
        """

        query = f"""SELECT proj_id FROM projects WHERE name = '{proj_name}'"""

        result = self.query(query)

        if not result:
            return -1
        
        return result[0]['proj_id']
    




#######################################################################################
# SKILLS RELATED
#######################################################################################


