import os
import sqlite3
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DATA_DIR = os.path.join(BASE_DIR, "data")

DB_PATH = os.path.join(DB_DIR, "corpus.db")
CSV_PATH = os.path.join(DATA_DIR, "conversations.csv")

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id  TEXT PRIMARY KEY,
            topic            TEXT,
            human_message    TEXT NOT NULL,
            ai_response      TEXT NOT NULL,
            timestamp        TEXT NOT NULL,
            human_word_count INTEGER NOT NULL,
            ai_word_count    INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def count_conversations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def generate_conversation_id():
    total = count_conversations()
    return f"CONV_{total + 1:04d}"

def conversation_id_exists(conv_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM conversations WHERE conversation_id = ?", (conv_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def add_conversation(topic, human_msg, ai_resp, sync_csv_backup=True):
    topic = topic.strip() if topic else "General"
    human_msg = human_msg.strip() if human_msg else ""
    ai_resp = ai_resp.strip() if ai_resp else ""
    
    if not human_msg or not ai_resp:
        raise ValueError("Both the human message and AI response are required.")
    
    conv_id = generate_conversation_id()
    if conversation_id_exists(conv_id):
        raise ValueError(f"Conversation ID '{conv_id}' already exists.")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    human_words = len(human_msg.split())
    ai_words = len(ai_resp.split())
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (conv_id, topic, human_msg, ai_resp, timestamp, human_words, ai_words))
    conn.commit()
    conn.close()
    
    if sync_csv_backup:
        sync_csv()

def get_all_conversations():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM conversations ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_conversation_by_id(conv_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM conversations WHERE conversation_id = ?", conn, params=(conv_id,))
    conn.close()
    if df.empty:
        return None
    return df.iloc[0].to_dict()

def delete_conversation(conv_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE conversation_id = ?", (conv_id,))
    conn.commit()
    conn.close()
    sync_csv()

def delete_all_conversations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()
    sync_csv()

def sync_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    df = get_all_conversations()
    df.to_csv(CSV_PATH, index=False)

SAMPLES = [
    ("Climate Change", "Can you explain why climate change is happening and what causes it?",
     "Climate change is primarily driven by the increased concentration of greenhouse gases such as carbon dioxide and methane in the atmosphere. These gases trap heat from the sun, a process known as the greenhouse effect. Human activities like burning fossil fuels, deforestation, and industrial processes have significantly accelerated this natural process over the last two centuries, leading to rising global temperatures, melting ice caps, and more extreme weather events."),
    ("Python Programming", "What is the difference between a list and a tuple in Python?",
     "In Python, a list is a mutable ordered collection, meaning you can add, remove, or change its elements after it is created. A tuple, on the other hand, is immutable, so once it is created its contents cannot be changed. Lists are defined using square brackets, while tuples use parentheses. Because tuples are immutable, they are generally faster and are often used to represent fixed collections of items such as coordinates."),
    ("Healthy Living", "What are some simple tips to stay healthy every day?",
     "Staying healthy every day can be achieved through a few consistent habits. Drink plenty of water throughout the day, eat a balanced diet rich in fruits and vegetables, and try to get at least thirty minutes of physical activity. Aim for seven to eight hours of quality sleep each night, manage stress through relaxation techniques such as meditation, and avoid excessive consumption of sugar and processed foods. Regular health checkups are also important for early detection of potential issues."),
    ("Travel Planning", "I am planning a trip to Japan. What should I know before I go?",
     "Japan is a wonderful destination with a rich mix of tradition and modern culture. Before you go, it helps to learn a few basic Japanese phrases, since English is not always widely spoken outside major cities. Consider purchasing a Japan Rail Pass if you plan to travel between cities, as it can save money on train fares. Cash is still commonly used, so carry some yen with you. Also, be mindful of local etiquette, such as removing your shoes before entering someone's home and avoiding loud conversations on public transportation."),
    ("Artificial Intelligence", "How do large language models generate human-like text?",
     "Large language models generate text by predicting the most likely next word or token based on patterns learned from massive amounts of training data. They use a neural network architecture called a transformer, which allows the model to weigh the relevance of different words in a sentence through a mechanism called attention. During training, the model adjusts millions or billions of internal parameters to minimize prediction errors, allowing it to produce coherent and contextually relevant responses at inference time."),
    ("Cooking", "Can you give me a simple recipe for homemade pasta?",
     "Making homemade pasta is simpler than many people expect. Start by mounding two cups of flour on a clean surface and creating a well in the center. Crack three eggs into the well and gradually mix the flour into the eggs using a fork until a dough forms. Knead the dough for about ten minutes until it becomes smooth and elastic, then let it rest for thirty minutes covered in plastic wrap. Roll it out thinly and cut it into your preferred pasta shape before cooking it in boiling salted water for two to three minutes.")
]

def load_sample_data():
    if count_conversations() == 0:
        for topic, h_msg, ai_resp in SAMPLES:
            add_conversation(topic, h_msg, ai_resp, sync_csv_backup=False)
        sync_csv()
