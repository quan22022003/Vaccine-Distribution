import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

database = 'grp20db_2023'
user = 'grp20_2023'
password = 'Q6JXVTt5'
host = 'dbcourse.cs.aalto.fi'

engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
connection = engine.connect()

# Plot 1: Vaccine Distribution Tracking
query1 = text("""
    SELECT manufdate, SUM(amount) as vaccines_distributed
    FROM vaccinebatch
    GROUP BY manufdate
    ORDER BY manufdate;
""")
df1 = pd.read_sql_query(query1, connection)

fig = plt.figure(figsize=(18, 8))
plt.plot(df1['manufdate'], df1['vaccines_distributed'])
plt.title('Vaccine Distribution Over Time')
plt.xlabel('Date')
plt.ylabel('Vaccines Distributed')
plt.show()

# Plot 2: Vaccination Event Management
query2 = text("""
    SELECT location, COUNT(*) as vaccination_events
    FROM vaccinations
    GROUP BY location;
""")
df2 = pd.read_sql_query(query2, connection)

fig = plt.figure(figsize=(18, 8))
plt.bar(df2['location'], df2['vaccination_events'])
plt.title('Number of Vaccination Events by Location')
plt.xlabel('Location')
plt.ylabel('Number of Vaccination Events')
plt.show()

# Plot 3: Patient Tracking
query3 = text("""
    SELECT date, COUNT(patientssno) as patients_vaccinated
    FROM vaccinepatients
    GROUP BY date
    ORDER BY date;
""")
df3 = pd.read_sql_query(query3, connection)

fig = plt.figure(figsize=(18, 8))
plt.plot(df3['date'], df3['patients_vaccinated'])
plt.title('Number of Patients Vaccinated Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Patients Vaccinated')
plt.show()

# Plot 4: Vaccine Batch Tracking
query4 = text("""
    SELECT location, COUNT(batchid) as batches
    FROM vaccinebatch
    GROUP BY location;
""")
df4 = pd.read_sql_query(query4, connection)

fig = plt.figure(figsize=(18, 8))
plt.bar(df4['location'], df4['batches'])
plt.title('Distribution of Vaccine Batches Across Locations')
plt.ylabel('Number of Batches')
plt.xlabel('Location')
plt.show()

# Plot 5: Symptom Analysis
query5 = text("""
    SELECT symptom, COUNT(patient) as frequency
    FROM diagnosis
    GROUP BY symptom;
""")
df5 = pd.read_sql_query(query5, connection)
df5 = df5.sort_values(by=['frequency'], ascending=False)
df5 = df5.head(10)

fig = plt.figure(figsize=(18, 8))
plt.bar(df5['symptom'], df5['frequency'])
plt.title('Frequency of Symptoms (top 10) in Vaccinated Patients')
plt.xlabel('Symptom')
plt.ylabel('Frequency')
plt.show()
