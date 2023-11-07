import psycopg2
from psycopg2 import Error
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.exc import IntegrityError


def run_sql_from_file(sql_file, psql_conn):
    '''
   read a SQL file with multiple stmts and process it
   adapted from an idea by JF Santos
   Note: not really needed when using dataframes.
   '''
    sql_command = ''
    for line in sql_file:
        # if line.startswith('VALUES'):
        # Ignore commented lines
        if not line.startswith('--') and line.strip('\n'):
            # Append line to the command string, prefix with space
            sql_command += ' ' + line.strip('\n')
            # sql_command = ' ' + sql_command + line.strip('\n')
        # If the command string ends with ';', it is a full statement
        if sql_command.endswith(';'):
            # Try to execute statement and commit it
            try:
                # print("running " + sql_command+".")
                psql_conn.execute(text(sql_command))
                print("Success")
                psql_conn.commit()
            # Assert in case of error
            except:
                print('Error at command:' + sql_command + ".")
                ret_ = False
            # Finally, clear command string
            finally:
                sql_command = ''
                ret_ = True
    return ret_


def main():
    DATADIR = str(Path(__file__).parent.parent)  # for relative path
    print(DATADIR)
    database = 'grp20db_2023'
    user = 'grp20_2023'
    password = 'Q6JXVTt5'
    host = 'dbcourse.cs.aalto.fi'
    try:
        # Connect the postgres database from your local machine using psycopg2
        connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port='5432'
        )
        connection.autocommit = True

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        cursor.execute("SELECT version();")
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        # -------------- Start Example -----------------#

        # THE TUTORIAL WILL USE SQLAlchemy to create connection, execute queries and fill table
        #####################################################################################################
        # Create and fill table from sql file using run_sql_from_file function (Not needed if using pandas df)
        #####################################################################################################
        # Step 1: Connect to db using SQLAlchemy create_engine
        DIALECT = 'postgresql+psycopg2://'
        db_uri = "%s:%s@%s/%s" % (user, password, host, database)
        print(DIALECT + db_uri)
        engine = create_engine(DIALECT + db_uri)
        sql_file1 = open(DATADIR + '/database/Script-2.sql')
        psql_conn = engine.connect()

        # Step 2 (Option 1): Read SQL files for CREATE TABLE and INSERT queries to Student table

        # run statements to create tables
        run_sql_from_file(sql_file1, psql_conn)

        #####################################################################################################
        # Create and file table from sql file using run_sql_from_file function (Not needed if using pandas df)
        #####################################################################################################
        # Step 1: Connect to db using SQLAlchemy create_engine
        xl = pd.ExcelFile(DATADIR + '/data/vaccine-distribution-data.xlsx')

        # %%
        # Define the mapping between sheet names and table names and the order in which they need to be inserted
        sheet_to_table_mapping = [
            ('VaccineType', 'vaccinetype'),
            ('Manufacturer', 'manufacturer'),
            ('VaccineBatch', 'vaccinebatch'),
            ('VaccinationStations', 'vaccinationstation'),
            ('Transportation log', 'transportlog'),
            ('StaffMembers', 'staffmembers'),
            ('Shifts', 'shifts'),
            ('Patients', 'patients'),
            ('Vaccinations', 'vaccinations'),
            ('VaccinePatients', 'vaccinepatients'),
            ('Symptoms', 'symptoms'),
            ('Diagnosis', 'diagnosis')
        ]

        # %%
        for sheet_name, table_name in sheet_to_table_mapping:
            # Read an Excel table into DataFrame
            df = xl.parse(sheet_name)
            print(sheet_name)

            #Rename the columns of the DataFrame if the sheet name is 'StaffMember'
            if sheet_name == 'StaffMembers':
                df = df.rename(columns={"social security number": "ssNo", "date of birth": "dob",
                                        "vaccination status": "vaccStatus", "hospital": "hospital"})

            #Rename the columns of the DataFrame if the sheet name is 'Patients'
            if sheet_name == 'Patients':
                df = df.rename(columns={"date of birth": "dob"})

            #Filter out the non-exist date '2021-02-29' and corrupted data '44237'
            if sheet_name == 'Diagnosis':
                df = df[df['date'] != '2021-02-29' & df['date'] != 44237]

            try:
                #Convert all columns to lowercase
                df.columns = df.columns.str.lower()
                #Strip all blank space in the columns' names
                df.columns = df.columns.str.strip()
                #Remove all quotation marks
                df.columns = df.columns.str.replace('"', '')
                df.to_sql(table_name, psql_conn, if_exists='append', index=False)
            except IntegrityError as e:
                print(f"Error inserting data into table {table_name}: {str(e)}")



        # if we have an excel file
        # df = pd.read_excel(DATADIR + '/data/vaccine-distribution-data.xlsx')



        # queryfile = open(DATADIR + '/database/test.sql')
        # run_query_from_file(queryfile, psql_conn)



    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            psql_conn.close()
            # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


main()
