import sqlite3
import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

DATABASE = 'database.db'
CSV_FILE = 'new_data.csv'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # to access columns by name
    print(conn.row_factory)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create users table for signup/login
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Create students table for CSV data
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            StudentID INTEGER PRIMARY KEY,
            CGPA REAL,
            Internships INTEGER,
            Projects INTEGER,
            Workshops_Certifications INTEGER,
            AptitudeTestScore REAL,
            SoftSkillsRating REAL,
            ExtracurricularActivities TEXT,
            PlacementTraining TEXT,
            SSC_Marks INTEGER,
            HSC_Marks INTEGER,
            PlacementStatus TEXT,
            Backlogs INTEGER,
            NoOfAttempts INTEGER,
            CollegeName TEXT,
            University TEXT
            
        )
    ''')
    
    #c.execute("ALTER TABLE students ADD COLUMN Backlogs INTEGER;")
    #c.execute("UPDATE students SET Backlogs = 0 WHERE Backlogs IS NULL;")
    #c.execute("ALTER TABLE students ADD COLUMN NoOfAttempts INTEGER;")
    #c.execute("ALTER TABLE students ADD COLUMN CollegeName TEXT;")
    #c.execute("ALTER TABLE students ADD COLUMN University TEXT;")

    
    # Execute a query to fetch data from the table
    c.execute("SELECT * FROM students")

    # Get column names
    column_names = [description[0] for description in c.description]

    # Print column names
    #print("Column names:", column_names)
    conn.commit()
    conn.close()

def populate_students():
    # Populate the students table from CSV if it is empty
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM students')
    
    column_names = [description[0] for description in c.description]

    # Print column names
    print("Column names:", column_names)
    count = c.fetchone()[0]
    if count == 10000:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    c.execute('INSERT OR REPLACE INTO students (StudentID, CGPA, Internships, Projects, Workshops_Certifications, AptitudeTestScore, SoftSkillsRating,ExtracurricularActivities,PlacementTraining,SSC_Marks,HSC_Marks,PlacementStatus,Backlogs,NoOfAttempts,CollegeName,University) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                              (row['StudentID'], row['CGPA'], row['Internships'],row['Projects'],row['Workshops/Certifications'],row['AptitudeTestScore'],row['SoftSkillsRating'],row['ExtracurricularActivities'],row['PlacementTraining'],row['SSC_Marks'],row['HSC_Marks'],row['PlacementStatus'],row['Backlogs'],
                              row['NoOfAttempts'],row['CollegeName'],row['University']))
            conn.commit()
    conn.close()
    
def check():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a query to fetch all rows
    cursor.execute("SELECT * FROM students")

    # Fetch all rows
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Print column headers
    print("\t".join(column_names))

    # Print each row
    for row in rows[:10]:
        print("\t".join(str(value) for value in row))

    # Close the connection
    conn.close()
    
    return None

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('search'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Signup successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.', 'error')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('search'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    student_data = None
    if request.method == 'POST':
        student_id = request.form['student_id']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM students WHERE StudentID = ?', (student_id,))
        student_data = c.fetchone()
        conn.close()
        if not student_data:
            flash('Student not found.', 'error')
    return render_template('search.html', student=student_data)

if __name__ == '__main__':
    init_db()
    populate_students()
    #check()
    app.run(debug=True)


