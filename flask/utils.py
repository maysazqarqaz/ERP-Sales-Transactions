import re
import pandas as pd
import ollama
import sqlite3
import re

conn = sqlite3.connect('data.db',check_same_thread=False)

def query_df(query):
    return pd.read_sql(query, conn)

tables = query_df("Select name from sqlite_master where type='table';")['name'].tolist()
tables_info = []
for table in tables:
    table_info = {}
    table_info['table_name'] = table
    table_info['columns'] = query_df(f"PRAGMA table_info({table})")['name'].tolist()
    tables_info.append(table_info)

def ask_model(prompt):
    response = ollama.chat(model="llama3.1:8b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

def clean_sql_response(response):
    sql = re.findall(r"(?i)select.+?;", response, re.DOTALL)
    return sql[0].strip() if sql else response.strip()

def get_possible_useful_tables(question,tables_info):
    prompt = f"""
    I have a dataset with the following tables: {tables_info}. 
    Which tables could be useful to write an SQL query to answer the following question:
    "{question}"
    Only output the table names that are exist in the dataset separated by commas.Do not explain anything. 
    Do not include code blocks or any text before or after the table names.
    """
    tables_names = ask_model(prompt)
    return tables_names.split(',')

def get_table_data(tables_names):
    tables_data = {}
    for table in tables_names:
        if table not in tables:
            continue
        table_data = {}
        table_data['columns'] = query_df(f"PRAGMA table_info({table.strip()})")['name'].tolist()
        table_data['data_sample'] = query_df(f"select * from {table} limit 5")
        table_data['caterogical_distinct_values'] = {column:get_distinct_values(column,table) for column in table_data['columns']}
        tables_data[table] = table_data

    tables_data_str = [f"table: {table}, columns: {tables_data[table]['columns']}, data_sample: {tables_data[table]['data_sample']}, caterogical_distinct_values: {tables_data[table]['caterogical_distinct_values']}" for table in tables_data]    
    return tables_data_str

def get_distinct_values(column,table):
    return query_df(f"select distinct {column} from {table}")

def generate_sql_query(question,tables_info):
    tables_names = get_possible_useful_tables(question,tables_info)
    
    tables_data = get_table_data(tables_names)

    prompt = f"""
    I have a dataset with the following tables: {tables_data}. 
    Write an SQL query to answer the following question:
    "{question}"
    Make sure that you're using the correct columns and tables, and the query is valid.
    Also when the question is about filtering, sorting, or grouping, make sure to include the relevant SQL clauses using the correct values.
    Only output the SQL query. Do not explain anything. Do not include code blocks or any text before or after the query.
    """
    query = ask_model(prompt)
    return clean_sql_response(query)

def answer_question_flow(question):
    query = generate_sql_query(question,tables_info)
    response = query_df(query)
    generated_question =  f"""
    Based on this data {response}, answer the following question:
    """
    answer = ask_model(generated_question)
    return query,answer