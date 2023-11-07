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
    database = 'grp20db_2023'  # TO BE REPLACED
    user = 'grp20_2023'  # TO BE REPLACED
    password = 'Q6JXVTt5'  # TO BE REPLACED
    host = 'dbcourse.cs.aalto.fi'
    # database = 'postgres'  # TO BE REPLACED
    # user = 'postgres'  # TO BE REPLACED
    # password = 'password'  # TO BE REPLACED
    # host = 'localhost'
    # use connect function to establish the connection
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
            df = xl.parse(sheet_name)
            print(sheet_name)

            if sheet_name == 'StaffMembers':
                df = df.rename(columns={"social security number": "ssNo", "date of birth": "dob",
                                        "vaccination status": "vaccStatus", "hospital": "hospital"})
            if sheet_name == 'Patients':
                df = df.rename(columns={"date of birth": "dob"})
            if sheet_name == 'Diagnosis':
                df = df[df['date'] != '2021-02-29']
                df = df[df['date'] != 44237]
            try:
                df.columns = df.columns.str.lower()
                df.columns = df.columns.str.strip()
                df.columns = df.columns.str.replace('"', '')
                print(df.dtypes)
                df.to_sql(table_name, psql_conn, if_exists='append', index=False)
            except IntegrityError as e:
                print(f"Error inserting data into table {table_name}: {str(e)}")



        # if we have an excel file
        # df = pd.read_excel(DATADIR + '/data/vaccine-distribution-data.xlsx')


        # Step 2: the dataframe df is written into an SQL table 'student'
        # df.to_sql('Manufacturer', con=psql_conn, if_exists='append', index=False)



        # queryfile = open(DATADIR + '/database/test.sql')
        # run_query_from_file(queryfile, psql_conn)
        sql_query1_ = """
                select s.ssno, s.name, s.phone, s.role, s.vaccstatus, v.location
                    from staffmembers s join shifts s2 on s.ssno = s2.worker
                    join vaccinations v on v.location = s2.station
                    where v.date = '2021-05-10' and trim(lower(to_char(timestamp '2021-05-10','DAY'))) = lower(s2.weekday);
                """
        tt_query1 = pd.read_sql_query(text(sql_query1_), psql_conn)
        print("Query 1 output:")
        print(tt_query1)
        print("")


        sql_query2_ = """
                  select distinct staffmembers.name, staffmembers.ssno, shifts.weekday, staffmembers.role
                    from staffmembers join vaccinationstation on staffmembers.hospital = vaccinationstation.name
					join shifts on shifts.station = vaccinationstation.name
                    where vaccinationstation.address like '%HELSINKI%'
                    and shifts.weekday = 'Wednesday' and staffmembers.role = 'doctor';
                 """
        tt_query2 = pd.read_sql_query(text(sql_query2_), psql_conn)
        print("Query 2 output:")
        print(tt_query2)
        print("")

        sql_query3_1 = """
                  select b1.batchid, b1.location as currentLocation, b2.lastlocation
                    from vaccinebatch as b1 join (select t.batchid, t.arrival as lastlocation, t.datearr
                    from transportlog t inner join (select batchid, max(tlog1.datearr) as latestdatearr
																from transportlog as tlog1
																group by batchid) as t2 on t.datearr = t2.latestdatearr
								where t.batchid = t2.batchid) as b2 on b1.batchid = b2.batchid
								join vaccinationstation as vs on b2.lastlocation = vs.name
                    order by b1.location != b2.lastlocation, b1.batchid;
                """
        tt_query3_1 = pd.read_sql_query(text(sql_query3_1), psql_conn)
        print("Query 3 output:")
        print("All vaccine batches:")
        print(tt_query3_1)
        print("")

        sql_query3_2 = """
                  select b1.batchid, b1.location as currentLocation, b2.lastlocation, vs.phone
                    from vaccinebatch as b1 join (select t.batchid, t.arrival as lastlocation, t.datearr
                    from transportlog t inner join (select batchid, max(tlog1.datearr) as latestdatearr
                                                                from transportlog as tlog1
                                                                group by batchid) as t2 on t.datearr = t2.latestdatearr
                                where t.batchid = t2.batchid) as b2 on b1.batchid = b2.batchid
                                join vaccinationstation as vs on b2.lastlocation = vs.name
                    order by b1.location != b2.lastlocation, b1.batchid;
                    """
        tt_query3_2 = pd.read_sql_query(text(sql_query3_2), psql_conn)
        print("Inconsistent location:")
        print(tt_query3_2)
        print("")

        sql_query4_ = """
                    select p.patientssNo, p.date, p.location, v.batchid, b."type"
                        from vaccinepatients p join diagnosis d on p.patientssNo = d.patient
                        join symptoms s on s.name = d.symptom
                        join vaccinations v on v.date = p.date and v.location = p.location
                        join vaccinebatch b on b.batchid = v.batchid
                        where s.criticality = '1' and d.date > '2021-05-10';
                    """
        tt_query4 = pd.read_sql_query(text(sql_query4_), psql_conn)
        print("Query 4 output:")
        print(tt_query4)
        print("")

        sql_query5_ = """
                create or replace view Patients_vaccStat as
                    select ssno, p.name, dob, gender, 1 as vaccinationStatus from patients p 
                    join vaccinepatients v on p.ssNo = v.patientssno,
                    vaccinations v2, vaccinebatch v3, vaccinetype v4
                    where v."location" = v2."location" and v."date" = v2.date and v2.batchid = v3.batchid and v3.type = v4.id
                    group by ssno, doses
                    having count(ssno) = doses
                    
                    union 
                    
                    (select *, 0 as vaccinationStatus from patients 
                    except 
                    (
                    select ssno, p.name, dob, gender, 0 as vaccinationStatus from patients p 
                    join vaccinepatients v on p.ssNo = v.patientssno,
                    vaccinations v2, vaccinebatch v3, vaccinetype v4
                    where v."location" = v2."location" and v."date" = v2.date and v2.batchid = v3.batchid and v3.type = v4.id
                    group by ssno, doses
                    having count(ssno) = doses)); 
                    """
        psql_conn.execute(text(sql_query5_))
        psql_conn.commit()
        print("Query 5 output:")
        sql_query5_1 = """
                    select *
                    from Patients_vaccStat;
                    """
        tt_query5_1 = pd.read_sql_query(text(sql_query5_1), psql_conn)
        print(tt_query5_1)
        print("")

        sql_query6_ = """
              select v.location, sum(case when v.type = 'V01' then v.amount else 0 end) as type_V01, 
                sum(case when v.type = 'V02' then v.amount else 0 end) as type_V02,
                sum(case when v.type = 'V03' then v.amount else 0 end) as type_V03, sum(v.amount)
                from vaccinebatch v 
                group by v.location
                order by v.location;   
                    """
        tt_query6 = pd.read_sql_query(text(sql_query6_), psql_conn)
        print("Query 6 output:")
        print(tt_query6)
        print("")

        sql_query7_ = """
                select b.type, d.symptom, count(patient) as frequency, round((count(patient):: decimal)/total.sum,3) as average_frequency
                from vaccinepatients p 
                join diagnosis d on p.patientssno = d.patient
                join vaccinations v on p.date = v.date and p.location = v.location
                join vaccinebatch b on b.batchid = v.batchid
                join (select count(patientssno) as sum, b.type
                        from vaccinations v join vaccinebatch b on b.batchid = v.batchid
                        join vaccinepatients p on v.date = p.date and v.location = p.location
                        group by b.type) as total on total.type = b.type
                where d.date >= v.date
                group by b.type, d.symptom, total.sum;
            """
        tt_query7 = pd.read_sql_query(text(sql_query7_), psql_conn)
        print("Query 7 output:")
        print(tt_query7)
        print("")



    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            psql_conn.close()
            # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


main()
