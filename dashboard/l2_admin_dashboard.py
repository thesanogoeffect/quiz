import streamlit as st
import pandas as pd
import sqlite3
from scripts.update_l2_metadata import adjust_question
from scripts.db_operations import load_db_into_df
from scripts.firestore import reset_firestore_stats_after_fix


# Streamlit app
st.title('Adjust Question Metadata')

# Load the question data
df = load_db_into_df()

# Form to select a question and adjust its metadata
question_id = st.selectbox("Select Question ID", df['id'].unique())

# Prefill the fields with the current data for the selected question
question_data = df[df['id'] == question_id].iloc[0]

with st.form(key='question_form'):
    question_title = st.text_input("Question Title (Optional)", value=question_data['question_title'])
    correct_answer = st.text_input("Correct Answer (Optional)", value=question_data['correct_answer'])
    distractor_1 = st.text_input("Distractor 1 (Optional)", value=question_data['distractor_1'])
    distractor_2 = st.text_input("Distractor 2 (Optional)", value=question_data['distractor_2'])
    distractor_3 = st.text_input("Distractor 3 (Optional)", value=question_data['distractor_3'])
    chapter_id = st.number_input("Chapter ID (Optional)", min_value=1, step=1, value=int(question_data['chapter_id']))
    description_llm = st.text_area("Description LLM (Optional)", value=question_data['description_llm'])

    # Ensure is_disabled is a valid boolean
    is_disabled_value = bool(question_data['is_disabled']) if not pd.isnull(question_data['is_disabled']) else False
    is_disabled = st.checkbox("Is Disabled", value=is_disabled_value)

    # Submit button
    submit_button = st.form_submit_button(label='Update Question')

# Reset Firestore stats button
reset_stats_button = st.button('Reset Firestore Stats')

if reset_stats_button:
    reset_firestore_stats_after_fix(question_id)
    st.success(f"Firestore stats reset successfully for question {question_id}")

# Call the function with the inputs after the form submission
if submit_button:
    adjust_question(
        question_id=question_id,
        question_title=question_title if question_title else None,
        correct_answer=correct_answer if correct_answer else None,
        distractor_1=distractor_1 if distractor_1 else None,
        distractor_2=distractor_2 if distractor_2 else None,
        distractor_3=distractor_3 if distractor_3 else None,
        chapter_id=chapter_id if chapter_id > 0 else None,
        description_llm=description_llm if description_llm else None,
        is_disabled=is_disabled
    )
    st.success("Question metadata updated successfully!")
