# connect to Firestore when we need to touch the live data

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

COLLECTION_NAME = "questions"
client = firestore.client()

new_question = {
    "times_asked": 0,
    "times_answered_correct": 0,
    "times_skipped": 0,
    "times_flagged": 0,
    "times_answered": 0,
    "times_upvoted": 0,
    "times_downvoted": 0,
}


# get a question by id
def get_question_by_id(question_id: int) -> dict:
    doc_ref = client.collection(COLLECTION_NAME).document(str(question_id))
    return doc_ref.get().to_dict()


def create_question(question_id: int) -> None:
    doc_ref = client.collection(COLLECTION_NAME).document(str(question_id))
    question_contents = new_question.copy()
    question_contents["question_id"] = question_id
    doc_ref.set(question_contents)
    # set question_id as the document id
    # also set the question_id in the document


def delete_question(question_id: int) -> None:
    doc_ref = client.collection(COLLECTION_NAME).document(str(question_id))
    doc_ref.delete()


def delete_all_questions():
    questions = client.collection(COLLECTION_NAME).stream()
    for question in questions:
        question.reference.delete()

def get_firestore_stats_df() -> pd.DataFrame:
    # get id - times_flagged - times_asked - times_answered_correct - times_skipped - times_answered - times_upvoted - times_downvoted - flagged_percentage - correct_percentage - skipped_percentage - answered_percentage - upvoted_percentage - downvoted_percentage
    # get all questions
    # get all the stats
    # calculate the percentages
    # return the dataframe
    questions = client.collection(COLLECTION_NAME).stream()
    question_stats = []
    for question in questions:
        question_dict = question.to_dict()
        question_stats.append(question_dict)
    df = pd.DataFrame(question_stats)
    df["flagged_percentage"] = df["times_flagged"] / df["times_asked"]
    df["correct_percentage"] = df["times_answered_correct"] / df["times_asked"]
    df["skipped_percentage"] = df["times_skipped"] / df["times_asked"]
    df["answered_percentage"] = df["times_answered"] / df["times_asked"]
    df["upvoted_percentage"] = df["times_upvoted"] / df["times_asked"]
    df["downvoted_percentage"] = df["times_downvoted"] / df["times_asked"]
    return df 

def reset_all_firestore_stats():
    questions = client.collection(COLLECTION_NAME).stream()
    for question in questions:
        question.reference.update({
            "times_asked": 0,
            "times_answered_correct": 0,
            "times_skipped": 0,
            "times_flagged": 0,
            "times_answered": 0,
            "times_upvoted": 0,
            "times_downvoted": 0,
        })

def reset_firestore_stats_after_fix(question_id: int):
    # reset flagged, upvoted and downvoted after fixing a question
    question = get_question_by_id(question_id)
    question["times_flagged"] = 0
    question["times_upvoted"] = 0
    question["times_downvoted"] = 0
    doc_ref = client.collection(COLLECTION_NAME).document(str(question_id))
    doc_ref.set(question)
    

def create_all_questions(from_index: int, to_index: int) -> None:
    # create all questions from from_index to to_index
    for question_id in range(from_index, to_index):
        create_question(question_id)


if __name__ == "__main__":
    create_all_questions(0, 1000)
