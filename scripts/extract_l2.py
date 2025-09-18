from scripts.db_operations import load_db_into_df
import os
# running scripts to transform the l2 (sqlite) into a cherrypicked selection (l3) based on heuristic rules (such as sensible, grammatical, relevant chapter, complete, correct, misleading and quality/difficulty scores)


# in L3, we want less features again. the final features are:
# id INTEGER PRIMARY KEY AUTOINCREMENT,
        # id INTEGER PRIMARY KEY AUTOINCREMENT,
        # timestamp TEXT NOT NULL,
        # question_title TEXT NOT NULL,
        # chapter_id INTEGER NOT NULL,
        # correct_answer TEXT NOT NULL,
        # distractor_1 TEXT NOT NULL,
        # distractor_2 TEXT NOT NULL,
        # distractor_3 TEXT NOT NULL,
        # source TEXT,
        # author TEXT,
        # chapter_id_llm BOOLEAN,
        # description_llm TEXT,
        # is_correct_llm BOOLEAN,
        # quality_score_llm INTEGER,

# at first, we just export all questions from L2, later we will add heuristics to filter out the best questions and discard duplicates
# it's ok to have l3 only .csv, .json, no need for a database
def create_l3():
    # get the l2 data
    df = load_db_into_df()
    # load index column as id
    # keep only the columns we want
    df = df[["id", "timestamp", "question_title", "chapter_id", "correct_answer", "distractor_1", "distractor_2", "distractor_3", "source", "author", "description_llm", "is_disabled", "topic"]]
    # filter
    df = filter_l2(df)
    # save the l2 data as l3

    # drop is_disabled and topic columns

    df = df.drop(columns=["is_disabled", "topic"])

    # replace all matches of "According to the passages" with "According to the textbook" in question_title

    # replace all matches of "According to the passages" with "According to the textbook"
    df["question_title"] = df["question_title"].str.replace("According to the passages", "According to the textbook", regex=False)
    
    # replace the lowercase version
    df["question_title"] = df["question_title"].str.replace("according to the passages", "according to the textbook", regex=False)
    df["question_title"] = df["question_title"].str.replace("According to the provided passages", "in the textbook", regex=False)
    df["question_title"] = df["question_title"].str.replace("according to the provided passages", "in the textbook", regex=False)
    df["question_title"] = df["question_title"].str.replace("textbook passages", "textbook", regex=False)
    df["question_title"] = df["question_title"].str.replace("According to the textbook passages", "In the textbook", regex=False)
    df["question_title"] = df["question_title"].str.replace("passages", "textbook", regex=False)





    df.to_csv("l3.csv", index=False)
    # now also save it as json
    df.to_json("l3.json", orient="records")

def filter_l2(df):
    # print the shape of the df
    print("pre-filtering shape: ", df.shape)
    # go through the l2 df and filter questions based on heuristics
    # for now, only exclude questions with is_disabled = True
    # print the values of is_disabled for first 5 rows
    df = df[(df["is_disabled"] == "0") | (df["is_disabled"].isnull())]
    # print the shape of the df
    print("post-filtering shape: ", df.shape)

    return df

def copy_l3_to_public():
    os.system("cp l3.json frontend/public/l3.json")

if __name__ == "__main__":
    create_l3()
    copy_l3_to_public()
