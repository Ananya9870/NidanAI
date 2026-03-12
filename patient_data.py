import sqlite3

def init_patient_db():
    """Database aur Table create karne ke liye"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Table structure jo main.py ke indexing se match karta hai
    c.execute('''CREATE TABLE IF NOT EXISTS patient_profiles (
                 username TEXT PRIMARY KEY,
                 full_name TEXT,
                 contact TEXT,
                 age INTEGER,
                 dob TEXT,
                 gender TEXT,
                 blood_group TEXT,
                 medical_history TEXT,
                 current_meds TEXT,
                 lifestyle TEXT,
                 FOREIGN KEY (username) REFERENCES users(username))''')
    conn.commit()
    conn.close()

def save_patient_data(data_tuple):
    """Data save ya update karne ke liye"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # INSERT OR REPLACE ensures ki duplicate username na bane, bas data update ho
    c.execute('''INSERT OR REPLACE INTO patient_profiles 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_tuple)
    conn.commit()
    conn.close()

def fetch_patient_data(username):
    """Particular user ka data nikalne ke liye"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patient_profiles WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    return data