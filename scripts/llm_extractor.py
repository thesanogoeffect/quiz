import langchain
import dotenv
import pytz
import pandas as pd
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# timestamp	question_title	chapter_id	correct_answer	distractor_1	distractor_2	distractor_3	source	author	student_id

dotenv.load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()


# for the first function, we want to create a df of questions in the following format
def extract_dict_from_question_text(text: str) -> dict:
    system_template = """
        Extract the following details from the input Psychology question text:
        - Question title
        - Correct answer
        - Three distractors

        Similar to the following example:
        {{
            "question_title": "________ is most well-known for proposing his hierarchy of needs.",
            "correct_answer": "Abraham Maslow",
            "distractor_1": "Carl Rogers",
            "distractor_2": "B.F. Skinner",
            "distractor_3": "Ivan Pavlov"
        }}
        
        Input text: "{text}"
        
        Output format: {{
            "question_title": "<question_title>",
            "correct_answer": "<correct_answer>",
            "distractor_1": "<distractor_1>",
            "distractor_2": "<distractor_2>",
            "distractor_3": "<distractor_3>"
        }}
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    chain = prompt_template | model | parser

    input_dict = {"text": text}

    # Get the string output
    question_str = chain.invoke(input_dict)

    # Attempt to parse the string output to a dictionary
    try:
        question_dict = json.loads(question_str)
    except json.JSONDecodeError:
        # Handle JSON parsing error
        question_dict = {}

    return question_dict


# print(extract_dict_from_question_text("""Based on your reading, which theorist would have been most likely to agree with this statement: Perceptual
# phenomena are best understood as a combination of their components.
# a. William James
# b. Max Wertheimer
# c. Carl Rogers
# d. Noam Chomsky"""))



def llm_get_description(question_title: str, answers: str, correct_answer: str) -> str:
    # we can use the model to get the description of the question
    system_template = """
        Prompt:
        Using the question and answers provided from the Social & Environmental Psychology textbook:

        Write a concise explanation in basic HTML. Use <p> tags for paragraphs and <b> tags for emphasizing key points.
        In your explanation:
        Clearly state whether the correct answer is correct and explain why.
        Explain why each distractor (incorrect answer) is incorrect.
        The explanation should be informative, readable, and tailored for freshmen Psychology students. Provide context where necessary to help students understand the concepts. Make the explanation flow naturally and be easy to read.
        
        Input:
        Question title: "{question_title}"
        Answers: "{answers}"
        Correct answer: "{correct_answer}"

        Output format (valid HTML):
        <div> DESCRIPTION </div>
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("user", "{question_title}\n{answers}\n{correct_answer}"),
        ]
    )
    chain = prompt_template | model | parser

    input_dict = {
        "question_title": question_title,
        "answers": answers,
        "correct_answer": correct_answer,
    }

    # Get the string output
    description_str = chain.invoke(input_dict)

    return description_str


