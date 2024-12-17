import sqlite3
from datetime import datetime

DB_NAME = "doc_chatbot_app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''create table if not exists application_logs
                    (id integer primary key autoincrement,
                     session_id text,
                     user_query text,
                     gpt_response text,
                     model text,
                     created_at timestamp default current_timestamp)''')
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('insert into application_logs (session_id, user_query,gpt_response, model) values (?,?,?,?)', (session_id, user_query, gpt_response,model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('Select user_query,gpt_response from application_logs where session_id= ? order by created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row["user_query"]},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages

def create_document_store():
    conn = get_db_connection()
    conn.execute('''create table if not exists document_store
                    (id integer primary key autoincrement,
                     filename text,
                     upload_timestamp timestamp default current_timestamp)''')
    conn.close()

def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('Insert into document_store (filename) values(?)', (filename,))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def delete_document_record(file_id):
    conn = get_db_connection()
    conn.execute('Delete from document_store where id=?', (file_id,))
    conn.commit()
    conn.close()
    return True

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('Select id, filename, upload_timestamp from document_store order by upload_timestamp DESC')
    documents = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in documents]

# initialize Database Tables
create_application_logs()
create_document_store()
