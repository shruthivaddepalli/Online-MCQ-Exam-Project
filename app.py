from flask import Flask, render_template, request, redirect, session, g
import sqlite3


app = Flask(__name__)
app.secret_key = 'somesecretkey'

DATABASE = 'exam.db'


# Utility function to connect to the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Create the database tables
def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct_option INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                exam_id INTEGER,
                score INTEGER
            )
        ''')
        db.commit()


# Home route
@app.route('/')
def home():
    return render_template('login.html')


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        db.commit()
        return redirect('/')
    return render_template('register.html')


# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        return redirect('/dashboard')
    return 'Invalid Credentials'


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    if session['role'] == 'admin':
        return render_template('admin.html')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM exams')
    exams = cursor.fetchall()

    return render_template('dashboard.html', exams=exams)


# Admin route for creating exam
@app.route('/create_exam', methods=['POST'])
def create_exam():
    if session['role'] != 'admin':
        return redirect('/')
    title = request.form['title']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO exams (title) VALUES (?)', (title,))
    db.commit()
    return redirect('/dashboard')


@app.route('/exam/<int:exam_id>')
def exam(exam_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,))
    questions = cursor.fetchall()
    #print(f'Questions for exam ID {exam_id}: {questions}')  # Debugging line

    if not questions:  # Check if questions are empty
        return "No questions found for this exam."

    return render_template('exam.html', questions=questions)


'''@app.route('/submit_exam/<int:exam_id>', methods=['POST'])
def submit_exam(exam_id):
    user_id = session['user_id']  # Get the logged-in user's ID from the session
    db = get_db()
    cursor = db.cursor()

    # Fetch questions for the exam
    cursor.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,))
    questions = cursor.fetchall()

    # Initialize score
    score = 0

    # Check each question's answer
    for question in questions:
        selected_option = request.form.get(f'question_{question[0]}')  # Get user's selected answer
        if selected_option and int(selected_option) == question[6]:  # Compare with correct answer
            score += 1

    # Check if the result already exists for this user and exam
    cursor.execute('SELECT * FROM results WHERE user_id = ? AND exam_id = ?', (user_id, exam_id))
    existing_result = cursor.fetchone()

    if existing_result:
        # If a result exists, update the score
        cursor.execute('UPDATE results SET score = ? WHERE user_id = ? AND exam_id = ?', (score, user_id, exam_id))
    else:
        # If no result exists, insert a new score
        cursor.execute('INSERT INTO results (user_id, exam_id, score) VALUES (?, ?, ?)', (user_id, exam_id, score))

    db.commit()

    # Redirect to the result page to display the score (with exam_id)
    return redirect(f'/result/1')'''


@app.route('/result/<int:exam_id>')
def show_result(exam_id):
    user_id = session['user_id']  # Get the user_id from the session
    db = get_db()
    cursor = db.cursor()

    # Fetch the latest result for the specific exam and user
    cursor.execute('SELECT score FROM results WHERE user_id = ? AND exam_id = ?', (user_id, exam_id))
    result = cursor.fetchone()

    if result:
        score = result[0]
    else:
        score = None  # No result found, handle this case

    # Ensure score is the most recent
    print(f"Score fetched for user {user_id} and exam {exam_id}: {score}")

    # Render the result page and pass the score
    return render_template('result.html', score=score, exam_id=exam_id)
@app.route('/submit_exam/<int:exam_id>', methods=['POST'])
def submit_exam(exam_id):
    user_id = session['user_id']  # Get the logged-in user's ID from the session
    db = get_db()
    cursor = db.cursor()

    # Fetch questions for the exam
    cursor.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,))
    questions = cursor.fetchall()

    # Initialize score
    score = 0

    # Check each question's answer
    for question in questions:
        question_id = question[0]
        correct_option = question[7]  # Assuming index 7 is the correct option
        selected_option = request.form.get(f'question_{question_id}')  # Get user's selected answer

        # Ensure both are integers for accurate comparison
        if selected_option and int(selected_option) == correct_option:
            score += 1

    # Store or update the result in the results table
    cursor.execute('SELECT * FROM results WHERE user_id = ? AND exam_id = ?', (user_id, exam_id))
    existing_result = cursor.fetchone()

    if existing_result:
        # If a result exists, update the score
        cursor.execute('UPDATE results SET score = ? WHERE user_id = ? AND exam_id = ?', (score, user_id, exam_id))
    else:
        # If no result exists, insert a new score
        cursor.execute('INSERT INTO results (user_id, exam_id, score) VALUES (?, ?, ?)', (user_id, exam_id, score))

    db.commit()

    # Redirect to the result page to display the score
    return redirect(f'/result/1')



if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
