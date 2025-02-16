import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import chardet
from dotenv import load_dotenv
import os

load_dotenv()


st.title("Excel to SQL Chatbot")
st.write("Upload an Excel file and convert it to a SQL database then use NL to generate sql qurey.")

# step0: allow user to upload files 
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls","csv"])

#  step1 : determine file format and encoding then strore in df
if uploaded_file is not None:
    result = chardet.detect(uploaded_file.read())
    uploaded_file.seek(0)   # reset pointer to begining after using read()
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file,encoding = result['encoding'])
    else:
        df = pd.read_excel(uploaded_file)   # excel file doesn`t need encoding`

    columns = df.columns.tolist()

    st.write("Preview of the uploaded data:")
    st.dataframe(df.head())

    # step3: convert the df to SQLit database
    engine = create_engine('sqlite:///:memory:')
    df.to_sql('data', engine, index=False, if_exists='replace')
    
    st.success("Data successfully loaded into SQL database!")

    # step3.5: verify the data insertion
    # query = "SELECT * FROM data LIMIT 5"
    # result = pd.read_sql_query(query, engine)
    
    # st.write("Sample data from the SQL database:")
    # st.dataframe(result)


