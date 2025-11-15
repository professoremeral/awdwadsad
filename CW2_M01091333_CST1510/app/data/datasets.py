import pandas as pd
from app.data.db import connect_database

#Function to create a dataset
def insert_dataset(name, category, source, last_updated, record_count, file_size_mb):
    conn = connect_database()
    cursor = conn.cursor()
    dataset_id = None
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    dataset_id = cursor.lastrowid
    print(f"✅ Inserted dataset '{name}' with ID: {dataset_id}")
    return dataset_id

#Function to read a dataset
def get_all_datasets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", conn)
    return df

#Function to update a dataset
def update_dataset_record_count(dataset_id, new_record_count):
    conn = connect_database()
    cursor = conn.cursor()
    rows_affected = 0
    cursor.execute(
        "UPDATE datasets_metadata SET record_count = ? WHERE id = ?",
        (new_record_count, dataset_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    if rows_affected > 0:
        print(f"✅ Updated record count for dataset ID: {dataset_id}")
    return rows_affected

#Functions to delete a dataset
def delete_dataset(dataset_id):
    conn = connect_database()
    cursor = conn.cursor()
    rows_affected = 0
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    if rows_affected > 0:
        print(f"✅ Deleted dataset with ID: {dataset_id}")
    return rows_affected