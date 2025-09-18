from scripts.gsheets import download_l1_gsheet_to_df
import pandas as pd
import sqlite3
from scripts.firestore import create_question, delete_question

# add new columns in addition to l2, keeping in mind that the live data exists in Firestore

def create_table():
    # connect to l1 SQLite database
    conn = sqlite3.connect("l2.db")
    # create the table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS l2 (
        id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        question_title TEXT NOT NULL,
        chapter_id INTEGER NOT NULL,
        correct_answer TEXT NOT NULL,
        distractor_1 TEXT NOT NULL,
        distractor_2 TEXT NOT NULL,
        distractor_3 TEXT NOT NULL,
        source TEXT,
        author TEXT,
        chapter_id_llm BOOLEAN,
        description_llm TEXT,
        is_correct_llm BOOLEAN,
        quality_score_llm INTEGER,
        is_disabled BOOLEAN,
        topic TEXT

    );
    """
    conn.execute(create_table_query)
    conn.close()

def dump_df_to_db(df : pd.DataFrame):
    conn = sqlite3.connect("l2.db")
    df.to_sql('l2', conn, if_exists='append', index=False)
    conn.close()

def replace_df_in_db(df: pd.DataFrame):
    conn = sqlite3.connect("l2.db")
    df.to_sql('l2', conn, if_exists='replace', index=False)
    conn.close()

def delete_question_by_id(question_id: int) -> None:
    conn = sqlite3.connect("l2.db")
    conn.execute(f"DELETE FROM l2 WHERE id = {question_id}")
    conn.commit()
    conn.close()

def process_new_questions(df: pd.DataFrame):
    # Insert new data into the SQLite database
    if not df.empty:
        dump_df_to_db(df)
    # for each new question, create a new document in Firestore
    # retrieve the ids of the new questions
    new_row_count = len(df)
    try:
        conn = sqlite3.connect("l2.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM l2 ORDER BY id DESC LIMIT {new_row_count}")
        new_question_ids = cursor.fetchall()
        for question_id in new_question_ids:
            create_question(question_id[0])
        conn.close()
    except Exception as e:
        print(e)
        return
    
def correct_source():
    conn = sqlite3.connect("l2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM l2")
    rows = cursor.fetchall()
    # for all rows where the chapter_id is 0, set the source to 'Canvas Practice Quiz'
    for row in rows:
        if row[3] == 0:
            cursor.execute("UPDATE l2 SET source = 'Canvas Practice Quiz' WHERE id = ?", (row[0],))
    conn.commit()
    conn.close()

def correct_chapter_id(id):
    # correct chapter_id for question id 60 to 2
    conn = sqlite3.connect("l2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM l2")
    rows = cursor.fetchall()
    for row in rows:
        if row[0] == id:
            cursor.execute("UPDATE l2 SET chapter_id = 2 WHERE id = ?", (row[0],))
    conn.commit()

    

def load_db_into_df():
    conn = sqlite3.connect("l2.db")
    df = pd.read_sql_query("SELECT * FROM l2", conn)
    conn.close()
    return df

# delete the id column in the database
def delete_id_column():
    conn = sqlite3.connect("l2.db")
    conn.execute("ALTER TABLE l2 DROP COLUMN id")
    conn.close()

def create_disabled_column():
    conn = sqlite3.connect("l2.db")
    conn.execute("ALTER TABLE l2 ADD COLUMN is_disabled BOOLEAN")
    conn.close()

def mark_all_questions_as_enabled():
    conn = sqlite3.connect("l2.db")
    conn.execute("UPDATE l2 SET is_disabled = FALSE")
    conn.commit()
    conn.close()

def recreate_table():
    # Create a new db called l2_new.db, then copy the values from l2.db to l2_new.db
    
    # Connect to the original database
    conn = sqlite3.connect("l2.db")
    cursor = conn.cursor()

    # Create the new table with the same structure
    create_table_query = """
    CREATE TABLE IF NOT EXISTS l2_new (
        id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        question_title TEXT NOT NULL,
        chapter_id INTEGER NOT NULL,
        correct_answer TEXT NOT NULL,
        distractor_1 TEXT NOT NULL,
        distractor_2 TEXT NOT NULL,
        distractor_3 TEXT NOT NULL,
        source TEXT,
        author TEXT,
        chapter_id_llm BOOLEAN,
        description_llm TEXT,
        is_correct_llm BOOLEAN,
        quality_score_llm INTEGER,
        is_disabled BOOLEAN,
        topic TEXT
    );
    """
    cursor.execute(create_table_query)

    # Copy the values from l2 to l2_new
    cursor.execute("INSERT INTO l2_new (timestamp, question_title, chapter_id, correct_answer, distractor_1, distractor_2, distractor_3, source, author, chapter_id_llm, description_llm, is_correct_llm, quality_score_llm, is_disabled, topic) SELECT * FROM l2")
    
    conn.commit()
    conn.close()



def drop_table_and_rename_new_to_old():
    # drop the old table
    conn = sqlite3.connect("l2.db")
    conn.execute("DROP TABLE l2")
    conn.close()

    # rename the new table to the old table
    conn = sqlite3.connect("l2.db")
    conn.execute("ALTER TABLE l2_new RENAME TO l2")
    conn.close()


def select_row_id(rowid):
    # try out selecting a row based on the implicit SQLite rowid
    conn = sqlite3.connect("l2.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM l2 WHERE rowid = {rowid}")
    row = cursor.fetchone()
    conn.close()

def give_attribution():
    # to all questions with chapter_id = 0, set the "author" to 'BRM 1 Lecturers'
    conn = sqlite3.connect("l2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM l2")
    rows = cursor.fetchall()
    for row in rows:
        if row[3] == 0:
            cursor.execute("UPDATE l2 SET author = 'IPT Lecturers' WHERE id = ?", (row[0],))
    conn.commit()
    conn.close()

   

if __name__ == "__main__":
# # try load only db into df
#     # delete_id_column()
#     # print(select_row_id(69))
#     # drop_table_and_rename_new_to_old()
#     # delete_question_by_id(689)
#     # mark_all_questions_as_enabled()
#     # create_disabled_column()
#     # recreate_table()
    give_attribution()    
