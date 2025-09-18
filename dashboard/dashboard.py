import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Intro to P&T Quiz Questions",
    page_icon="📊",
    layout="wide"
)

# CSS for custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .stat-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-number {
        font-size: 3rem;
        font-weight: bold;
        color: #2563EB;
    }
    .stat-label {
        font-size: 1.2rem;
        color: #4B5563;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1F2937;
    }
    .question-card {
        background-color: white;
        border-left: 5px solid #3B82F6;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .question-title {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .answer-correct {
        color: #059669;
        font-weight: bold;
    }
    .answer-distractor {
        color: #DC2626;
    }
</style>
""", unsafe_allow_html=True)

# Function to load and process data
def load_data():
    try:
        df = pd.read_csv('data/l3.csv')
        return df
    except FileNotFoundError:
        data = {
        }
        return pd.DataFrame(data)

# Main function
def main():
    st.markdown('<div class="main-header">Intro to P&T Questions</div>', unsafe_allow_html=True)
    st.markdown('[🔗 Back to Quiz](https://quiz.jakubwerner.com/ipt)', unsafe_allow_html=True)


    chapter_map = {
      1: "Introduction to Psychology",
      2: "Psychological Research",
      3: "Biopsychology",
      4: "States of Consciousness",
      5: "Sensation and Perception",
      6: "Learning",
      7: "Thinking and Intelligence",
      8: "Memory",
      9: "Lifespan Development",
      10: "Motivation and Emotion",
      12: "Social Psychology",
      14: "Stress, Lifestyle, and Health",
    }

    df = load_data()

    total_questions = len(df)
    chapters_present = df['chapter_id'].nunique()
    chapters_distribution = df['chapter_id'].value_counts().sort_index()

    # Create a list of formatted chapter names with IDs
    # formatted_chapter_names = [f"Chapters {id}: {chapter_map.get(id, f'Chapters {id}')}" for id in chapters_distribution.index]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_questions}</div>
            <div class="stat-label">Total Questions</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{chapters_present-1}</div>
            <div class="stat-label">Chapters Covered</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_questions = total_questions / chapters_present if chapters_present > 0 else 0
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{avg_questions:.1f}</div>
            <div class="stat-label">Avg Questions per Chapters</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown('<br>', unsafe_allow_html=True)
    # Create Altair chart
    chart_data = chapters_distribution.reset_index()
    chart_data.columns = ['chapter_id', 'Number of Questions']
    # Map chapter_id to the formatted chapter names
    chart_data['Chapters'] = chart_data['chapter_id'].map(lambda x: f"Chapters {x}: {chapter_map.get(x, f'Chapters {x}')}")

    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Chapters', sort=None, axis=alt.Axis(labelAngle=45)), # Increased label angle for better readability
        y='Number of Questions',
        color=alt.Color('Chapters:N', scale=alt.Scale(scheme='category10')),
        tooltip=['Chapters', 'Number of Questions']
    )
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5  # Nudges text above top of bar
    ).encode(
        text='Number of Questions'
    )

    final_chart = (chart + text).interactive()


    source_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('source:N', title='Source'),
    y=alt.Y('count():Q', title='Number of Questions'),
    color=alt.Color('source:N', scale=alt.Scale(scheme='set2'))  # Another discrete color palette
)
    

    col1, col2 = st.columns(2)

    with col1:
        st.altair_chart(final_chart, use_container_width=True)

    with col2:
        st.altair_chart(source_chart, use_container_width=True)


if __name__ == "__main__":
    main()