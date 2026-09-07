import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import re
from collections import Counter

import database as db
from nlp.preprocessing import full_preprocess
from nlp.analysis import analyze_text
from nlp.comparison import compare_texts, compare_corpus

st.set_page_config(
    page_title="Human vs AI Conversation Corpus Explorer",
    page_icon="💬",
    layout="wide"
)

db.init_db()
db.load_sample_data()

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.0rem; color: #4B5563; margin-bottom: 1.5rem; }
    .chat-human { background-color: #E0F2FE; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; color: #0369A1; }
    .chat-ai { background-color: #F0FDF4; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; color: #15803D; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💬 Human vs AI Corpus Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced NLP analysis and comparison of Human vs AI conversational responses.</div>', unsafe_allow_html=True)

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", [
    "📊 Corpus Analytics",
    "🔤 Deep NLP Analysis",
    "⚖️ Side-by-Side Comparison",
    "➕ Add Conversation",
    "🔍 Search Corpus",
    "⚙️ Manage Data"
])

df = db.get_all_conversations()

if menu == "📊 Corpus Analytics":
    st.header("Corpus Level Statistics & Metrics")
    if df.empty:
        st.warning("Corpus is empty. Please add conversations.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Conversations", len(df))
        c2.metric("Topics Covered", df['topic'].nunique())
        c3.metric("Avg Human Words", f"{df['human_word_count'].mean():.1f}")
        c4.metric("Avg AI Words", f"{df['ai_word_count'].mean():.1f}")

        st.divider()
        st.subheader("Aggregated NLP Comparison across Corpus")
        comp_df = compare_corpus(df)
        st.dataframe(comp_df, use_container_width=True)

elif menu == "🔤 Deep NLP Analysis":
    st.header("SpaCy & NLTK Text Processing Pipeline")
    sample_text = st.text_area("Enter Text for Pipeline Processing", "Large language models generate text by predicting the most likely next word.")
    if st.button("Run Preprocessing"):
        res = full_preprocess(sample_text)
        st.subheader("Tokens")
        st.write(res["words"])
        st.subheader("POS Tags & Lemmas")
        st.json(res["pos_tags"])
        st.subheader("Stopword Analysis")
        st.json(res["stopwords"])

elif menu == "⚖️ Side-by-Side Comparison":
    st.header("Single Pair Side-by-Side NLP Comparison")
    if df.empty:
        st.warning("Corpus is empty.")
    else:
        conv_ids = df["conversation_id"].tolist()
        selected_id = st.selectbox("Select Conversation ID", conv_ids)
        row = db.get_conversation_by_id(selected_id)
        
        st.markdown(f'<div class="chat-human"><b>Human:</b> {row["human_message"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai"><b>AI:</b> {row["ai_response"]}</div>', unsafe_allow_html=True)
        
        cmp_df, h_ana, a_ana = compare_texts(row["human_message"], row["ai_response"])
        st.subheader("Linguistic Metrics Comparison")
        st.dataframe(cmp_df, use_container_width=True)

elif menu == "➕ Add Conversation":
    st.header("Add Conversation Pair")
    with st.form("add_form", clear_on_submit=True):
        topic = st.text_input("Topic Category")
        human_msg = st.text_area("Human Message")
        ai_resp = st.text_area("AI Response")
        if st.form_submit_button("Save"):
            if human_msg.strip() and ai_resp.strip():
                db.add_conversation(topic, human_msg, ai_resp)
                st.success("Saved!")
                st.rerun()

elif menu == "🔍 Search Corpus":
    st.header("Search & Filter")
    q = st.text_input("Keyword Search")
    if q and not df.empty:
        res = df[df["human_message"].str.contains(q, case=False) | df["ai_response"].str.contains(q, case=False)]
        st.dataframe(res)

elif menu == "⚙️ Manage Data":
    st.header("Manage Corpus")
    if st.button("Reset to Sample Data"):
        db.delete_all_conversations()
        db.load_sample_data()
        st.success("Reset completed!")
        st.rerun()
