import scripts.db_operations as db
import pandas as pd
import scripts.llm_extractor as llm
import os
import scripts.gsheets as gsh
"""provides methods that will be used in pipelines to regularly update the l2 metadata"""


def update_missing_descriptions():
    """Update the l2 metadata with missing descriptions"""
    # get the l2 data
    df = db.load_db_into_df()
    # get the rows with missing descriptions
    missing_descriptions = df[df["description_llm"].isnull()]
    # update the missing descriptions
    for index, row in missing_descriptions.iterrows():
        # get the description
        llm_description = llm.llm_get_description(
            row["question_title"],
            f"A) {row['distractor_1']}\nB) {row['distractor_2']}\nC) {row['distractor_3']}\nD) {row['correct_answer']}",
            row["correct_answer"],
        )
        # update the description
        df.at[index, "description_llm"] = llm_description
    # save the updated data
    db.replace_df_in_db(df)


def update_is_correct():
    """Update the l2 metadata with missing is_correct values"""
    # get the l2 data
    df = db.load_db_into_df()
    # get the rows with missing is_correct values
    missing_is_correct = df[df["is_correct_llm"].isnull()]
    # update the missing is_correct values
    for index, row in missing_is_correct.iterrows():
        # get the is_correct value
        is_correct = llm.llm_get_correct(
            row["question_title"],
            f"A) {row['distractor_1']}\nB) {row['distractor_2']}\nC) {row['distractor_3']}\nD) {row['correct_answer']}",
            row["correct_answer"],
        )
        # update the is_correct value
        df.at[index, "is_correct_llm"] = is_correct
    # save the updated data
    db.replace_df_in_db(df)


def update_missing_chapter_ids():
    """Update the l2 metadata with missing chapter ids"""
    # get the l2 data
    df = db.load_db_into_df()
    # get the rows with missing chapter ids
    missing_chapter_ids = df[df["chapter_id"].isnull() | df["chapter_id"] == 0]
    # update the missing chapter ids
    for index, row in missing_chapter_ids.iterrows():
        # get the chapter id
        chapter_id = llm.llm_get_chapter(row["question_title"], f"A) {row['distractor_1']}\nB) {row['distractor_2']}\nC) {row['distractor_3']}\nD) {row['correct_answer']}")
        # update the chapter id
        df.at[index, "chapter_id"] = chapter_id
    # save the updated data
    db.replace_df_in_db(df)

def make_db_backup():
    """Make a backup of the l2 database"""
    # get the l2 data
    df = db.load_db_into_df()
    # save the data as a csv
    df.to_csv("l2_backup.csv", index=False)


def fix_chapter_id(question_id: int, chapter_id: int):
    """Fix the chapter id of a question"""
    # get the l2 data
    df = db.load_db_into_df()
    # update the chapter id
    df.loc[df["id"] == question_id, "chapter_id"] = chapter_id
    # save the updated data
    db.replace_df_in_db(df)


def get_correct_id_to_chapter_id_pairs():
    # will generate tuples with the modus for the correct answer and the chapter id from the df
    df = gsh.get_chapter_errors_table_as_df()
    # the colu Timestamp	Question ID	Current chapter number	Correct chapter number
    # get the correct chapter number and the modus for the correct chapter number
    # get the errored IDs
    errored_ids = df["Question ID"].tolist()
    id_chapter_pairs = []

    for id in errored_ids:
        filtered_df_by_id = df[df["Question ID"] == id]
        # now get the mode of the correct chapter number
        correct_chapter_number = filtered_df_by_id["Correct chapter number"].mode().values[0]
        id_chapter_pairs.append((id, correct_chapter_number))
    return id_chapter_pairs



# adjust metadata based on what comes into params

def adjust_question(question_id: int, question_title : str = None, correct_answer : str = None, distractor_1: str = None, 
                    distractor_2: str = None, distractor_3: str = None, chapter_id: int = None, description_llm: str = None, is_disabled: bool = None):
    """Adjust the metadata of a question"""
    # get the l2 data
    df = db.load_db_into_df()
    # update the metadata
    if question_title:
        df.loc[df["id"] == question_id, "question_title"] = question_title
    if correct_answer:
        df.loc[df["id"] == question_id, "correct_answer"] = correct_answer
    if distractor_1:
        df.loc[df["id"] == question_id, "distractor_1"] = distractor_1
    if distractor_2:
        df.loc[df["id"] == question_id, "distractor_2"] = distractor_2
    if distractor_3:
        df.loc[df["id"] == question_id, "distractor_3"] = distractor_3
    if chapter_id:
        df.loc[df["id"] == question_id, "chapter_id"] = chapter_id
    if description_llm:
        df.loc[df["id"] == question_id, "description_llm"] = description_llm
    if is_disabled:
        df.loc[df["id"] == question_id, "is_disabled"] = is_disabled
    # save the updated data
    db.replace_df_in_db(df)

        




if __name__ == "__main__":
    # make_db_backup()
    # update_missing_chapter_ids()
    # update_is_correct()
    # update_missing_descriptions()
    for id, chapter in get_correct_id_to_chapter_id_pairs():
        fix_chapter_id(id, chapter)
        # print(id, chapter)