from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain import hub
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from typing_extensions import List, TypedDict
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain import hub
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
import dotenv
import time
import os
from QuizQuestion import QuizQuestion as qq
import streamlit as st

ENV_LECTURES_TO_CHAPTERS = {
    1: [1],
    5: [6],
    7: [2],
    9: [3],
    11: [8],
    13: [5],
}
SOC_LECTURES_TO_CHAPTERS = {
    1: [1, 4],
    2: [6, 7],
    4: [14],
    6: [10, 11],
    8: [13, 16, 17],
    10: [20],
    14: [18, 19],
}
dotenv.load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

llm = ChatOpenAI(model="gpt-4o-mini")
llm_advanced = ChatOpenAI(model="gpt-4o")
llm_google = ChatGoogleGenerativeAI(
    model="gemini-exp-1206",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
index_soc = pc.Index(f"sep-quiz-soc")
vector_store_soc = PineconeVectorStore(embedding=embeddings, index=index_soc)
index_env = pc.Index(f"sep-quiz-env")
vector_store_env = PineconeVectorStore(embedding=embeddings, index=index_env)

# Possible values for instruction template:
# generate, regen
PROMPT_TEMPLATES = {
    "generate": """
        Given the following prompt and hand-selected relevant passages (so that you have more context) from a {subject} psychology textbook, create multiple-choice exam question/s intended for university students that properly tests their abilities.
        - They should have a relatively basic format, but still be challenging.
        - Use the provided textbook passages (prioritize important information).
        - Include one correct answer and three distractors. They should all be plausible and challenging! (no trivial or stupid distractors!).
        - Do not refer to the passages or the textbook in the question title, trust that the students know where it's from.
        Follow the exact output format shown below (object in a list with "question_title", "correct_answer", "distractor_1", "distractor_2", and "distractor_3"):
        Do not use text formatting like bold, cursive, nor ```json or ```python. Just plain text.
        Examples of a good question (but try to improve on it!):
        [{{
            "question_title": "An ad on TV shows that electrical cars consume less energy and might help mitigate climate
change. Is this ad likely to be effective?",
            "correct_answer":"Yes, because if influences efficiency behavior, and does not threaten the driver's freedom",
            "distractor_1":"Yes, because it influences maintenance behavior and does not threaten the driver's freedom"
            "distractor_2":"No, because it does not influence the driver's perceived control",
            "distractor_3":"Yes, because it influences curtailment behavior, although it might also threaten the driver's freedom"
        }},
        {{
            "question_title": "Which of the following is an example of a territorial marker?",
            "correct_answer":"A book left on a library table",
            "distractor_1":"A public sign indicating directions",
            "distractor_2":"A bench in a public park",
            "distractor_3":"A lamp post on a street"
        }}, 
        {{
            "question_title": "Consider a space where voice-activated doors are installed for blind users. Which model of therapeutic environments would correspond to this intervention according to Canter & Canter (1970)?",
            "correct_answer": "The prosthetic model",
            "distractor_1": "The custodial model",
            "distractor_2": "The enhancement model",
            "distractor_3": "The medical model"
        }}]
        
        Now, produce {number} question STRICTLY based on the following question/answer prompt (make the question relate to it as much as possible,
        the prompt's content is more important than the passages, which are just for context. You can even use the prompt itself!
        
        Prompt:

        {instruction}
        
        Relevant passages from the textbook:

        {context}

        Output format:
            
        [{{
            "question_title": "<question_title>",
            "correct_answer": "<correct_answer>",
            "distractor_1": "<distractor_1>",
            "distractor_2": "<distractor_2>",
            "distractor_3": "<distractor_3>"
        }}, {{...}}]
        """,
    #     "regen": """
    #         Given the following question, instructions and hand-selected relevant passages (so that you have more context) from a {subject} psychology textbook, regenerate a multiple-choice exam question intended for university students that properly tests their abilities.
    #         - Use the provided textbook passages (prioritize important information).
    #         - IMPORTANT: Keep everything the same - except for what you're asked to regenerate in the instruction!
    #         - Include one correct answer and three distractors. They should all be plausible (no trivial or stupid distractors!).
    #         - Do not refer to the passages or the textbook in the question title, trust that the students know where it's from.
    #         Follow the exact output format shown below (object in a list with "question_title", "correct_answer", "distractor_1", "distractor_2", and "distractor_3"):
    #         Do not use text formatting like bold, cursive, nor ```json or ```python. Just plain text.
    #         Examples of a good question (but try to improve on it!):
    #         [{{
    #             "question_title": "An ad on TV shows that electrical cars consume less energy and might help mitigate climate
    # change. Is this ad likely to be effective?",
    #             "correct_answer":"Yes, because if influences efficiency behavior, and does not threaten the driver's freedom",
    #             "distractor_1":"Yes, because it influences maintenance behavior and does not threaten the driver's freedom"
    #             "distractor_2":"No, because it does not influence the driver's perceived control",
    #             "distractor_3":"Yes, because it influences curtailment behavior, although it might also threaten the driver's freedom"
    #         }},
    #         {{
    #             "question_title": "Which of the following is an example of a territorial marker?",
    #             "correct_answer":"A book left on a library table",
    #             "distractor_1":"A public sign indicating directions",
    #             "distractor_2":"A bench in a public park",
    #             "distractor_3":"A lamp post on a street"
    #         }},
    #         {{
    #             "question_title": "Consider a space where voice-activated doors are installed for blind users. Which model of therapeutic environments would correspond to this intervention according to Canter & Canter (1970)?",
    #             "correct_answer": "The prosthetic model",
    #             "distractor_1": "The custodial model",
    #             "distractor_2": "The enhancement model",
    #             "distractor_3": "The medical model"
    #         }}]
    #         Now, regenerate a question STRICTLY based on the following description:
    #         {instruction}
    #         Question to regenerate:
    #         {question_dict}
    #         Relevant passages from the textbook:
    #         {context}
    #         Output format:
    #         [{{
    #             "question_title": "<question_title>",
    #             "correct_answer": "<correct_answer>",
    #             "distractor_1": "<distractor_1>",
    #             "distractor_2": "<distractor_2>",
    #             "distractor_3": "<distractor_3>"
    #         }}]
    #     """,
}

# INSTRUCTION_PARAMS = {
#     "question_title": "question_title",
#     "correct_answer": "correct_answer",
#     "distractor_1": "distractor_1",
#     "distractor_2": "distractor_2",
#     "distractor_3": "distractor_3",
#     "all_answers": "All answers - the correct answer and the three distractors",
#     "all_distractors": "All of the three distractors, keeping the correct answer the same",
# }


def get_new_question_dict(
    instruction: str,
    manual_instruction: str,
    lecture_id: int,
    subject="soc",
    no_generated_questions: int = 1,
    llm: str = "gemini",
    current_question_dict: dict = None,
) -> dict:

    # Get the relevant chapters for the lecture
    if subject == "soc":
        chapters = SOC_LECTURES_TO_CHAPTERS[lecture_id]
        vector_store = vector_store_soc
    elif subject == "env":
        chapters = ENV_LECTURES_TO_CHAPTERS[lecture_id]
        vector_store = vector_store_env
    else:
        raise ValueError("Invalid subject. Choose either 'soc' or 'env'.")

    # retrieval
    question = (
        f"{manual_instruction}"
        if not current_question_dict
        else f"current_question_dict['question_title']"
    )
    retrieved_docs = vector_store.similarity_search(
        question, filter={"chapter_number": {"$in": [int(x) for x in chapters]}}
    )
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
    formatted_docs = [
        paragraph.strip()
        for paragraph in docs_content.split("\n\n")
        if paragraph.strip()
    ]

    if not retrieved_docs:
        print("No relevant passages found.")
        return None
    if instruction == "generate":
        system_template = PROMPT_TEMPLATES["generate"]
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("user", "{subject}\n{number}\n{instruction}\n{context}"),
            ],
        )
        model = llm_google if llm == "gemini" else llm_advanced
        chain = prompt_template | model | StrOutputParser()
        input_dict = {
            "subject": "Environmental" if subject == "env" else "Social",
            "number": no_generated_questions,
            "context": str(formatted_docs),
            "instruction": manual_instruction,
        }

        # Get the string output
        questions_str = chain.invoke(input_dict)

        print(questions_str)

        # Attempt to parse the string output to a list of dictionaries
        try:
            questions_str = (
                questions_str.strip()
                .replace("```python", "")
                .replace("```json", "")
                .replace("```", "")
                .replace("```json", "")
                .replace("```python", "")
                .replace("```", "")
                .strip()
            )
            questions_list = eval(questions_str)
        except Exception as e:
            # Handle error
            print(e)
            questions_list = []

        return questions_list


def llm_get_description(question_title, answers, correct_answer, context=None):
    system_template = """
    Using the following question and answers the Environmental Psychology textbook, along with relevant context passages, 
    write a very short, concise explanation in basic HTML. Use <p> tags for paragraphs and <b> tags for emphasizing key points.
    Where possible, prefer the provided context in your explanation.
    In your explanation:
    Make it flow naturally, as if you were a good teacher explaining it to a student.
    The explanation should be structured, readable, and tailored for undergraduate Psychology students, but condensed and very short! Provide some nuance where necessary to help students understand the concepts. 
    
    Input:
    Question title: "{question_title}"
    Answers: "{answers}"
    Correct answer: "{correct_answer}"
    Context: "{context}"

    Output format (valid HTML):
    <div> DESCRIPTION </div>
    
    """

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("user", "{question_title}\n{answers}\n{correct_answer}\n{context}"),
        ]
    )

    chain = prompt_template | llm_google | StrOutputParser()

    input_dict = {
        "question_title": question_title,
        "answers": answers,
        "correct_answer": correct_answer,
        "context": context,
    }

    # Get the string output
    description_str = chain.invoke(input_dict)

    # clean ```html and similar
    description_str = description_str.replace("```html", "").replace("```", "").strip()

    print(description_str)

    return description_str


def save_question(question: dict, lecture_number: int, formatted_docs: List[str]):
    question = qq(
        question_title=question["question_title"],
        correct_answer=question["correct_answer"],
        distractor_1=question["distractor_1"],
        distractor_2=question["distractor_2"],
        distractor_3=question["distractor_3"],
        chapter_id=lecture_number,  # here, actually put the lecture number
    )
    description = llm_get_description(
        question_title=question.question_title,
        answers=str(
            [
                question.correct_answer,
                question.distractor_1,
                question.distractor_2,
                question.distractor_3,
            ]
        ),
        correct_answer=question.correct_answer,
        context=str(formatted_docs),
    )
    question.description_llm = description
    question.save_question()


# Lecture mappings
lectures = {
    1: "Lewin, B=f(p, E)",
    2: "Attitudes, beliefs, the self",
    3: "Perception, appraisal, preference",
    4: "Emotions and stress",
    5: "Restorative environments",
    6: "Groups",
    7: "Sense of place",
    8: "Social influence",
    9: "Privacy, interaction & space",
    10: "Prosocial behavior",
    11: "Pro-environmental behavior",
    13: "Crime",
    14: "Conflict",
}

# App layout
st.title("Quiz Question Generator")

# Instruction input
instruction = st.text_area("Enter your instruction for the question:")

# Toggle between LLMs
llm_selection = st.selectbox("Select Language Model:", ["Gemini", "OpenAI"])

# Toggle between Soc/Env
subject_selection = st.radio("Select Subject:", ["Soc", "Env"])

# Lecture selection
selected_lecture = st.selectbox(
    "Select a Lecture:", list(lectures.items()), format_func=lambda x: x[1]
)

# Number of questions to generate
num_questions = st.number_input(
    "Number of questions to generate:",
    min_value=1,
    max_value=10,
    value=1,
    step=1,
)

# Generate and Save buttons
if st.button("Generate Questions"):
    lecture_id = selected_lecture[0]
    subject = subject_selection.lower()
    llm = "gemini" if llm_selection == "Gemini" else "openai"

    # Call the question generation function
    questions = get_new_question_dict(
        instruction="generate",
        manual_instruction=instruction,
        lecture_id=lecture_id,
        subject=subject,
        no_generated_questions=num_questions,
        llm=llm,
    )

    if questions:
        st.session_state["current_questions"] = questions
        st.success(f"{len(questions)} question(s) generated successfully!")
    else:
        st.error("No questions generated. Check your inputs and try again.")

if "current_questions" in st.session_state:
    st.write("### Generated Questions:")
    lecture_number = selected_lecture[0]
    for idx, question in enumerate(st.session_state["current_questions"], start=1):
        st.write(f"### Question {idx}:")
        st.json(question)
        
        # Create a unique Save button for each question
        if st.button(f"Save Question {idx}", key=f"save_button_{idx}"):
            save_question(
                question=question,
                lecture_number=lecture_number,
                formatted_docs=[],  # Replace with actual context docs if needed
            )
            st.success(f"Question {idx} saved successfully!")
