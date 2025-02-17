import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import chardet
import ollama

client = ollama.Client(host='http://localhost:11434')


st.title("Excel to SQL")
st.write("Upload an Excel file and upload it to a SQLite database then use NL to generate sql qurey and print results.")

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
    nl_query = st.text_input("Enter your natural language query:")

    if nl_query:
        # Step4: generate SQL using Ollama
        prompt = f"""
        You are a SQL expert. Convert this natural language query to SQL:
        QUERY: "{nl_query}"
        
        SCHEMA: {columns}
        TABLE NAME: "data"
        
        Return ONLY the SQL query, no explanations.
        """

        try:
            response = client.generate(
                model='llama3.2:3b',  
                prompt=prompt,
                options={'temperature': 0.1}  
            )
            
            sql_query = response['response'].strip()
            st.write("Generated SQL:")
            st.code(sql_query)

            result = pd.read_sql_query(sql_query, engine)
            st.write("Query Results:")
            st.dataframe(result)

        except Exception as e:
            st.error(f"Error generating SQL: {str(e)}")
