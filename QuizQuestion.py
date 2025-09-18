import scripts.db_operations as dbo
import pandas as pd
import pytz


class QuizQuestion:
    """Serves for generating and saving questions"""

    def __init__(
        self,
        question_title,
        chapter_id,
        correct_answer,
        distractor_1,
        distractor_2,
        distractor_3,
        source="JW+AI Iterative v1",
        author=None,
        description_llm=None,
        topic=None,
    ):
        self.question_title = question_title
        self.chapter_id = chapter_id
        self.correct_answer = correct_answer
        self.distractor_1 = distractor_1
        self.distractor_2 = distractor_2
        self.distractor_3 = distractor_3
        self.source = source
        self.author = author
        self.description_llm = description_llm
        self.topic = topic

    def get_dict(self):
        return {
            "question_title": self.question_title,
            "chapter_id": self.chapter_id,
            "correct_answer": self.correct_answer,
            "distractor_1": self.distractor_1,
            "distractor_2": self.distractor_2,
            "distractor_3": self.distractor_3,
            "source": self.source,
            "author": self.author,
            "description_llm": self.description_llm,
            "topic": self.topic,
        }

    # def generate_explanation(self):
    #     # generate an explanation for the question
    #     self.description_llm = llm.llm_get_description(
    #         self.question_title,
    #         str(
    #             [
    #                 self.correct_answer,
    #                 self.distractor_1,
    #                 self.distractor_2,
    #                 self.distractor_3,
    #             ]
    #         ),
    #         self.correct_answer,
    #     )

    def save_question(self):
        # convert the question to a dict

        question_dict = self.get_dict()
        # make a df from the question
        df = pd.DataFrame([question_dict])
        df["timestamp"] = pd.Timestamp.now(
            tz=pytz.timezone("Europe/Amsterdam")
        ).strftime("%m/%d/%Y %H:%M:%S")
        # save the question to the db
        dbo.process_new_questions(df)
        print("Question saved successfully")
