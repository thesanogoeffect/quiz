import streamlit as st
import json
from QuizQuestion import QuizQuestion
import scripts.db_operations as dbo

st.set_page_config(page_title="Quiz Question Uploader", layout="centered")

st.title("📋 Quiz Question Uploader")
st.markdown("Paste your JSON-formatted questions below:")

json_input = st.text_area("JSON Input", height=400)

if st.button("Validate and Save"):
    try:
        parsed = json.loads(json_input)
        if not isinstance(parsed, list):
            st.error("JSON must be a list of question objects.")
        else:
            saved_count = 0
            for idx, item in enumerate(parsed, 1):
                try:
                    question = QuizQuestion(
                        question_title=item["question_title"],
                        chapter_id=item["chapter_id"],
                        correct_answer=item["correct_answer"],
                        distractor_1=item["distractor_1"],
                        distractor_2=item["distractor_2"],
                        distractor_3=item["distractor_3"],
                        source=item.get("source", "JW+AI Iterative v1"),
                        author=item.get("author"),
                        description_llm=item.get("description_llm"),
                        topic=item.get("topic"),
                    )

                    if not question.description_llm:
                        question.generate_explanation()

                    question.save_question()
                    saved_count += 1
                except Exception as e:
                    st.error(f"❌ Error on question {idx}: {e}")
            st.success(f"✅ {saved_count} questions saved successfully!")
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
