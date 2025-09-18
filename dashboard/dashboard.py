import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path

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
def load_data() -> pd.DataFrame:
    """Load questions CSV from common locations.

    Tries, in order:
    - dashboard/l3.csv (next to this file)
    - data/l3.csv (repo data folder)

    Returns an empty DataFrame with expected columns if not found.
    """
    candidates = [
        Path(__file__).with_name('l3.csv'),
        Path(__file__).resolve().parent.parent / 'data' / 'l3.csv',
    ]

    for path in candidates:
        try:
            if path.exists():
                return pd.read_csv(path)
        except Exception as e:
            st.warning(f"Failed to read data from {path}: {e}")

    # Fallback: empty DataFrame with expected columns to avoid KeyErrors downstream
    st.warning("No quiz data found (looked for l3.csv). Displaying empty dashboard.")
    return pd.DataFrame(columns=["chapter_id", "source"]) 

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
    chapters_present = df['chapter_id'].nunique() if 'chapter_id' in df.columns else 0
    chapters_distribution = (
        df['chapter_id'].value_counts().sort_index() if 'chapter_id' in df.columns else pd.Series(dtype=int)
    )

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
            <div class="stat-number">{chapters_present}</div>
            <div class="stat-label">Chapters Covered</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_questions = total_questions / chapters_present if chapters_present > 0 else 0
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{avg_questions:.1f}</div>
            <div class="stat-label">Avg Questions per Chapter</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown('<br>', unsafe_allow_html=True)
    # Create Altair chart
    chart_data = chapters_distribution.reset_index()
    chart_data.columns = ['chapter_id', 'Number of Questions']
    # Map chapter_id to the formatted chapter names with clean fallback
    chart_data['Chapter'] = chart_data['chapter_id'].map(
        lambda x: f"Chapter {x}: {chapter_map[x]}" if x in chapter_map else f"Chapter {x}"
    )

    # Ensure numerical order and show all tick labels; only present chapters are included
    ordered_chapters = chart_data['chapter_id'].sort_values().tolist()

    if not chart_data.empty:
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X(
                'chapter_id:O',
                title='Chapter',
                scale=alt.Scale(domain=ordered_chapters),
                sort=ordered_chapters,
                axis=alt.Axis(labelAngle=0, labelOverlap=False, values=ordered_chapters)
            ),
            y=alt.Y('Number of Questions:Q', title='Number of Questions'),
            color=alt.Color('Chapter:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Chapter', 'Number of Questions']
        )
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5  # Nudges text above top of bar
        ).encode(
            text='Number of Questions'
        )

        final_chart = (chart + text).interactive()
    else:
        final_chart = None

    # Build source chart only if the 'source' column exists and has data
    source_chart = None
    if 'source' in df.columns and df['source'].notna().any():
        source_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('source:N', title='Source'),
            y=alt.Y('count():Q', title='Number of Questions'),
            color=alt.Color('source:N', scale=alt.Scale(scheme='set2'))  # Another discrete color palette
        )
    

    col1, col2 = st.columns(2)

    with col1:
        if final_chart is not None:
            st.altair_chart(final_chart, use_container_width=True)
        else:
            st.info("No chapter data available to display the chapter distribution.")

    with col2:
        if source_chart is not None:
            st.altair_chart(source_chart, use_container_width=True)
        else:
            st.info("No 'source' data available to display the source distribution.")


if __name__ == "__main__":
    main()