import streamlit as st
import pandas as pd
from src.analyzer import Analyzer
from src.recommender import Recommender
import os

st.set_page_config(page_title="AU Trend Analyzer", layout="wide")

st.title("Autodesk University Trend Analyzer (2025 -> 2026)")

# Sidebar - Controls
st.sidebar.header("Filters")

# Initialize Logic
@st.cache_data
def load_data():
    if not os.path.exists("data/au_2025.json"):
        return None
    return Analyzer("data/au_2025.json")

analyzer = load_data()

if not analyzer or analyzer.df.empty:
    st.error("No data found! Please run the scraper first (or use the sample data provided).")
    st.info("Check data/au_2025.json")
    st.stop()

# Filters
all_topics = analyzer.get_all_topics()
all_industries = analyzer.get_all_industries()
all_products = analyzer.get_all_products()

selected_topics = st.sidebar.multiselect("Filter by Topic", all_topics)
selected_industries = st.sidebar.multiselect("Filter by Industry", all_industries)
selected_products = st.sidebar.multiselect("Filter by Product", all_products)

# Apply Filter
filtered_df = analyzer.filter_classes(selected_topics, selected_industries, selected_products)
st.sidebar.markdown(f"**Classes Found:** {len(filtered_df)}")

# Tabs
tab1, tab2, tab3 = st.tabs(["Class Data", "Trend Analysis", "Future Predictions"])

with tab1:
    st.subheader("2025 Class List")
    # Updated: Show Description, Reset Index to start from 1
    display_df = filtered_df[['title', 'summary', 'topics', 'industries', 'products', 'url']].reset_index(drop=True)
    display_df.index = display_df.index + 1
    
    st.dataframe(display_df, use_container_width=True,
                 column_config={
                     "url": st.column_config.LinkColumn("Link"),
                     "summary": st.column_config.TextColumn("Description", width="medium")
                 })

with tab2:
    st.subheader("Trend Analysis (Based on Selection)")
    trends = analyzer.summarize_trends(filtered_df)
    
    # 1. Topic & Phrase Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top Topics")
        st.write("Most frequent topics covered:")
        topics_df = pd.DataFrame(trends.get('top_topics', []), columns=['Topic', 'Count'])
        if not topics_df.empty:
            st.bar_chart(topics_df.set_index('Topic'), color="#ff4b4b")
        else:
            st.info("No topic data available.")

    with col2:
        st.markdown("### Common Phrases")
        st.write("Recurring themes in descriptions (Bigrams):")
        phrases_df = pd.DataFrame(trends.get('top_phrases', []), columns=['Phrase', 'Count'])
        if not phrases_df.empty:
            st.bar_chart(phrases_df.set_index('Phrase'))
        else:
            st.info("No phrase data available.")
            
    # 2. Automated Theme Extraction
    st.markdown("---")
    st.markdown("### 💡 Key Themes & Insights")
    st.write("Automatically extracted patterns from class descriptions:")
    
    themes = analyzer.get_key_themes(filtered_df)
    if themes:
        for i, theme in enumerate(themes):
            st.info(f"**{i+1}.** {theme}.")
    else:
        st.write("No distinct themes found for this selection.")

with tab3:
    st.subheader("2026 Strategic Research Directions")
    st.markdown("Identified by analyzing the alignment between **AU 2025 Content** and **Global Market Trends**.")
    
    recommender = Recommender(analyzer)
    suggestions = recommender.suggest_future_topics()
    
    if not suggestions:
        st.warning("No trends detected. Try selecting 'All' in filters to see the broader picture.")
    
    for item in suggestions:
        with st.expander(f"✨ {item['trend']} (Relevance Score: {item['score']})", expanded=True):
            st.markdown(f"**Insight:** {item['reason']}")
            st.success(f"**Prediction:** {item['prediction']}")
            
            st.markdown("#### 🔭 Recommended Research Directions:")
            directions = item.get('guide', [])
            # Handle both list (new format) and dict (old format backup)
            if isinstance(directions, list):
                for d in directions:
                    st.markdown(f"- 🎯 {d}")
            elif isinstance(directions, dict):
                 for k, v in directions.items():
                    st.markdown(f"- 🎯 {v}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Data source: Autodesk University 2025 Search")
