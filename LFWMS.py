import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Food data Entry",layout="wide")

# --- DB connection ---
def create_connection():
    return mysql.connector.connect(
            host="127.0.0.1",
            user="systemmanage",       
            password="System123",     
            database="food_wastage"    
        )

# --- Fetch tables ---
def get_tables():
    conn = create_connection()   # changed
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

# --- Load data ---
def load_data(table_name):
    conn = create_connection()   # changed
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# --- Add record ---
def add_record(table_name, values):
    conn = create_connection()   # changed
    cursor = conn.cursor()
    placeholders = ", ".join(["%s"] * len(values))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# --- Get record by ID ---
def get_record_by_id(table_name, pk_column, pk_value):
    conn = create_connection() 
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name} WHERE {pk_column}=%s", (pk_value,))
    record = cursor.fetchone()
    conn.close()
    return record

# --- Update record ---
def update_record(table_name, pk_column, pk_value, updates):
    old_record = get_record_by_id(table_name, pk_column, pk_value)
    if not old_record:
        return False

    # Keep old values if blank
    for col in updates:
        if updates[col] == "" or updates[col] is None:
            updates[col] = old_record[col]

    set_clause = ", ".join([f"{col}=%s" for col in updates.keys()])
    values = list(updates.values()) + [pk_value]

    conn = create_connection()   
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {pk_column}=%s", values)
    conn.commit()
    conn.close()
    return True

# --- Delete record ---
def delete_record(table_name, pk_column, pk_value):
    conn = create_connection()   
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE {pk_column}=%s", (pk_value,))
    conn.commit()
    conn.close()

# --- Streamlit UI ---
st.title("Food wast Data management ")
tables = ["claims_data", "food_listings_data","providers_data", "receivers_data"] 

tables = get_tables()
selected_table = st.sidebar.selectbox("Select Table", tables)
menu = ["View", "Add", "Update", "Delete"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "View":
    st.subheader(f"All Records from {selected_table}")
    df = load_data(selected_table)
    st.dataframe(df)

elif choice == "Add":
    st.subheader(f"Add Record to {selected_table}")
    df = load_data(selected_table)
    cols = df.columns.tolist()

    inputs = []
    for col in cols:
        val = st.text_input(f"{col}")
        inputs.append(val)

    if st.button("Add"):
        add_record(selected_table, inputs)
        st.success("Record added successfully!")

elif choice == "Update":
    st.subheader(f"Update Record in {selected_table}")
    df = load_data(selected_table)
    st.dataframe(df)

    pk_column = df.columns[0]   # assume first column is primary key
    pk_value = st.text_input(f"Enter {pk_column} of record to update")

    updates = {}
    for col in df.columns[1:]:
        updates[col] = st.text_input(f"{col} (leave blank to keep old)")

    if st.button("Update"):
        if update_record(selected_table, pk_column, pk_value, updates):
            st.success("Record updated successfully!")
        else:
            st.error("Record not found!")

elif choice == "Delete":
    st.subheader(f"Delete Record from {selected_table}")
    df = load_data(selected_table)
    st.dataframe(df)

    pk_column = df.columns[0]   # assume first column is primary key
    pk_value = st.text_input(f"Enter {pk_column} of record to delete")

    if st.button("Delete"):
        delete_record(selected_table, pk_column, pk_value)
        st.warning("Record deleted successfully!")
