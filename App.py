import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import re
from collections import Counter
import database as db

st.set_page_config(
    page_title="Human vs AI Conversation Corpus Explorer",
    page_icon="💬",
    layout="wide"
)

# Initialize DB
db.init_db()
db.load_sample_data()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #2563EB;
    }
    .chat-human {
        background-color: #E0F2FE;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: #0369A1;
    }
    .chat-ai {
        background-color: #F0FDF4;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: #15803D;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💬 Human vs AI Corpus Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">A comprehensive dashboard for collecting, analyzing, and exploring Human-AI conversation pairings.</div>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", [
    "📊 Dataset Overview & Analytics",
    "➕ Add New Conversation",
    "🔍 Search & Filter Corpus",
    "🔤 Comparative Text Analysis",
    "⚙️ Manage Corpus"
])

df = db.get_all_conversations()

def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', str(text).lower())

def get_word_freq(text_series, top_n=10):
    words = []
    stopwords = set(["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "it", "you", "i", "can", "what", "how", "this", "that", "be", "as", "from", "have", "has", "do", "does", "not", "your", "my", "we", "they"])
    for text in text_series:
        cleaned = clean_text(text)
        for w in cleaned.split():
            if w not in stopwords and len(w) > 2:
                words.append(w)
    return pd.DataFrame(Counter(words).most_common(top_n), columns=["Word", "Frequency"])

if menu == "📊 Dataset Overview & Analytics":
    st.header("Corpus Analytics & Summary")
    
    if df.empty:
        st.warning("Corpus is currently empty. Please add conversations or reset sample data.")
    else:
        # Key Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Conversations", len(df))
        col2.metric("Topics Covered", df['topic'].nunique())
        col3.metric("Avg Human Words", f"{df['human_word_count'].mean():.1f}")
        col4.metric("Avg AI Words", f"{df['ai_word_count'].mean():.1f}")
        ratio = df['ai_word_count'].mean() / max(df['human_word_count'].mean(), 1)
        col5.metric("AI/Human Word Ratio", f"{ratio:.2f}x")

        st.divider()

        # Word Count Comparison Plot
        st.subheader("Word Count Comparison per Conversation")
        melted_df = df.melt(id_vars=["conversation_id", "topic"], value_vars=["human_word_count", "ai_word_count"],
                            var_name="Speaker", value_name="Word Count")
        melted_df["Speaker"] = melted_df["Speaker"].map({"human_word_count": "Human Prompt", "ai_word_count": "AI Response"})

        chart = alt.Chart(melted_df).mark_bar().encode(
            x=alt.X('conversation_id:N', title='Conversation ID'),
            y=alt.Y('Word Count:Q', title='Word Count'),
            color=alt.Color('Speaker:N', scale=alt.Scale(domain=['Human Prompt', 'AI Response'], range=['#0284C7', '#16A34A'])),
            tooltip=['conversation_id', 'topic', 'Speaker', 'Word Count']
        ).properties(height=350)
        
        st.altair_chart(chart, use_container_width=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Conversations by Topic")
            topic_counts = df['topic'].value_counts().reset_index()
            topic_counts.columns = ['Topic', 'Count']
            pie = alt.Chart(topic_counts).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Topic", type="nominal"),
                tooltip=['Topic', 'Count']
            ).properties(height=300)
            st.altair_chart(pie, use_container_width=True)

        with col_right:
            st.subheader("Word Length Distribution")
            hist = alt.Chart(melted_df).mark_area(opacity=0.5).encode(
                x=alt.X("Word Count:Q", bin=alt.Bin(maxbins=20)),
                y=alt.Y("count():Q", stack=None),
                color=alt.Color("Speaker:N")
            ).properties(height=300)
            st.altair_chart(hist, use_container_width=True)

elif menu == "➕ Add New Conversation":
    st.header("Add New Conversation Pair")
    
    with st.form("add_form", clear_on_submit=True):
        topic = st.text_input("Topic Category", placeholder="e.g., Data Science, Philosophy, Customer Support")
        human_msg = st.text_area("Human Message / Prompt", height=120, placeholder="Enter the user's prompt or question here...")
        ai_resp = st.text_area("AI Response", height=180, placeholder="Enter the AI's response here...")
        
        submitted = st.form_submit_button("Save Conversation to Corpus")
        if submitted:
            if not human_msg.strip() or not ai_resp.strip():
                st.error("Error: Both Human Message and AI Response must be provided.")
            else:
                try:
                    db.add_conversation(topic, human_msg, ai_resp)
                    st.success("✅ Conversation added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add conversation: {e}")

elif menu == "🔍 Search & Filter Corpus":
    st.header("Search & Explore Corpus")
    
    if df.empty:
        st.info("No conversations found in the database.")
    else:
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search Keyword (in Human Prompt or AI Response)", "")
        with col_s2:
            selected_topic = st.selectbox("Filter by Topic", ["All Topics"] + list(df['topic'].unique()))

        filtered_df = df.copy()
        if selected_topic != "All Topics":
            filtered_df = filtered_df[filtered_df['topic'] == selected_topic]
        if search_query.strip():
            query = search_query.lower()
            filtered_df = filtered_df[
                filtered_df['human_message'].str.lower().str.contains(query) |
                filtered_df['ai_response'].str.lower().str.contains(query)
            ]

        st.caption(f"Showing {len(filtered_df)} of {len(df)} records")

        for _, row in filtered_df.iterrows():
            with st.expander(f"📌 {row['conversation_id']} | Topic: {row['topic']} ({row['timestamp']})"):
                st.markdown(f"**Human Word Count:** {row['human_word_count']} | **AI Word Count:** {row['ai_word_count']}")
                st.markdown(f'<div class="chat-human"><b>👤 Human:</b><br>{row["human_message"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-ai"><b>🤖 AI:</b><br>{row["ai_response"]}</div>', unsafe_allow_html=True)

elif menu == "🔤 Comparative Text Analysis":
    st.header("Comparative Text & Vocabulary Analysis")
    
    if df.empty:
        st.warning("Corpus is empty.")
    else:
        st.markdown("Analyze vocabulary differences between Human prompts and AI generated responses.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Top Frequent Words in Human Prompts")
            human_freq = get_word_freq(df['human_message'], top_n=10)
            bar_h = alt.Chart(human_freq).mark_bar(color='#0284C7').encode(
                x='Frequency:Q',
                y=alt.Y('Word:N', sort='-x')
            ).properties(height=300)
            st.altair_chart(bar_h, use_container_width=True)

        with c2:
            st.subheader("Top Frequent Words in AI Responses")
            ai_freq = get_word_freq(df['ai_response'], top_n=10)
            bar_a = alt.Chart(ai_freq).mark_bar(color='#16A34A').encode(
                x='Frequency:Q',
                y=alt.Y('Word:N', sort='-x')
            ).properties(height=300)
            st.altair_chart(bar_a, use_container_width=True)

        st.divider()
        st.subheader("Raw Data Table")
        st.dataframe(df[['conversation_id', 'topic', 'human_word_count', 'ai_word_count', 'timestamp', 'human_message', 'ai_response']], use_container_width=True)

elif menu == "⚙️ Manage Corpus":
    st.header("Corpus Data Management")
    
    st.subheader("Data Export & Download")
    col_e1, col_e2 = st.columns(2)
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    col_e1.download_button(
        label="📥 Download Corpus as CSV",
        data=csv_data,
        file_name="human_ai_conversations_corpus.csv",
        mime="text/csv"
    )
    
    json_data = df.to_json(orient="records", indent=2)
    col_e2.download_button(
        label="📥 Download Corpus as JSON",
        data=json_data,
        file_name="human_ai_conversations_corpus.json",
        mime="application/json"
    )

    st.divider()
    st.subheader("Database Administrative Actions")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if st.button("🔄 Reset Corpus with Sample Data"):
            db.delete_all_conversations()
            db.load_sample_data()
            st.success("Corpus reset with sample data successfully!")
            st.rerun()

    with col_m2:
        if st.button("⚠️ Clear Entire Corpus"):
            db.delete_all_conversations()
            st.warning("All conversations deleted from database!")
            st.rerun()
