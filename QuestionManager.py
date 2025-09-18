import pandas as pd
import random as rd

class QuestionManager():
    def __init__(self, path):
        self.path = path
        self.df = None
        # load the df from the path
        self.df = pd.read_parquet(path, engine="pyarrow")

    def get_random_question(self, chapters=[1,2,3,4,5,6], seen_questions=[]):
        # get a random question from the df
        # filter the df by the chapters
        filtered_df = self.df[self.df["chapter"].isin(chapters) & ~self.df.index.isin(seen_questions)]
        # get a random row from the filtered df
        return filtered_df.sample().iloc[0]
    

if __name__ == "__main__":
    qm = QuestionManager("Halfway Answers 2021-2_cleaned.parquet")
    print(qm.df.head())
    print(qm.df.info())
    print(qm.df.describe())
    print(qm.df.columns)
    print(qm.df.index)
    print(qm.df.shape)
    print(qm.df.dtypes)
    print(qm.df["question_title"])
    print(qm.df["correct_answer"])
    print(qm.df["distractors"])


        