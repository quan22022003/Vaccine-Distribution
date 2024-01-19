# Project Vaccine Distribution
This repository provides a basic structure for collaborating with your teammates on project Vaccine Distribution. Read the following content carefully to understand the file structure as well as how to work with git and PostgreSQL. 


## File structure
This section explains the recommended file structure for the project

    .project-vaccine-distribution
    ├── code                              # code base (python & sql files)
    │   ├── requirements.txt              
    │   ├── test_postgresql_conn.py       # Example code to test connection with postgres server
    │   ├── ....py                       
    ├── data                              # contain the sample data for Vaccine Distribution projects
    │   ├── sampleData.xls                # sample data as an excel file
    ├── database                          
    │   ├── database.db                   # final version of the project database
    ├── venv                              
    │   ├── bin
    │   │   ├── activate
    │   │   ├── ....
    │   ├── ....
    ├── .gitignore
    └── README.md

## Overview
The main objective of the project is to build a database to keep track of the different vaccine 
types, transportation of vaccine batches, treatment plans, staff schedules of vaccinations 
events, and patient data for Corona vaccine distribution and treatment in Finland.

## Purpose of the database
The purpose of the database is to model and manage the distribution of vaccines. The 
database is designed to track information about vaccine manufacturers, vaccine batches, 
vaccination events, patients, and symptoms.
