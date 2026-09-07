# Human vs AI Conversation Corpus Project

A complete, production-ready machine learning dataset explorer and analytical dashboard built to collect, process, and analyze **Human vs AI Conversation Corpus** pairings.

---

## 📌 Project Overview
This project provides an end-to-end infrastructure for building a domain-specific corpus comparing human inputs with AI responses. It includes:
1. **Database Tier**: Embedded SQLite database (`corpus.db`) managed via `database.py`.
2. **Data Backup**: Automatic synchronization to `data/conversations.csv`.
3. **Interactive UI**: A multi-page Streamlit web dashboard (`app.py`) featuring comparative word count analysis, topic breakdowns, and keyword search.

---

## 🛠️ Installation & Setup

1. **Clone or extract the project directory**:
   ```bash
   cd human_ai_corpus
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit Web Application**:
   ```bash
   streamlit run app.py
   ```

---

## 📁 Directory Structure
```
human_ai_corpus/
│
├── app.py                   # Streamlit Web Application Dashboard
├── database.py              # SQLite Database Handler & Helper Methods
├── requirements.txt         # Project Dependencies
├── README.md                # Project Documentation
├── database/
│   └── corpus.db            # SQLite Corpus Database (Generated automatically)
└── data/
    └── conversations.csv    # CSV Backup of Corpus (Generated automatically)
```

---

## 💡 Key Features
- **Dataset Overview**: Interactive metrics, word count ratio charts, and topic distributions using Altair.
- **Data Collection**: Integrated UI form to register new human-AI conversation pairs into the database.
- **Search & Filter**: Real-time text filtering across topics and conversation text.
- **Text Analysis**: Frequency distributions comparing vocabulary across human prompts and AI answers.
- **Export Capabilities**: One-click dataset downloads in `.csv` and `.json` formats.
