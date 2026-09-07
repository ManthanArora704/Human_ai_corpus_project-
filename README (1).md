# Human vs AI Conversation Corpus Project (with NLP Pipeline)

Full-stack corpus collection, storage, and linguistic analysis toolkit powered by SpaCy, NLTK, SQLite, and Streamlit.

## Modules

- `nlp/preprocessing.py`: Tokenization, lemmatization, POS tagging, and stopword analysis.
- `nlp/analysis.py`: Extracting linguistic metrics (lexical diversity, sentence length, POS counts).
- `nlp/comparison.py`: Comparative tables between Human prompts and AI responses.
- `database.py`: SQLite connection and CSV synchronization.
- `app.py`: Streamlit multi-page web application.

## Quick Start

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run SpaCy model setup:
   ```bash
   python -m spacy download en_core_web_sm
   ```
3. Launch Streamlit:
   ```bash
   streamlit run app.py
   ```
