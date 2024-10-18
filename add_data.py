import sqlite3

DATABASE = 'exam.db'

def add_sample_data():
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Add sample exam
    cursor.execute('INSERT INTO exams (title) VALUES (?)', ('Sample Exam',))
    exam_id = cursor.lastrowid

    # Add sample questions for the exam
    questions = [
        ('What is the capital of France?', 'Paris', 'Berlin', 'Madrid', 'Rome', 1),
        ('Which planet is known as the Red Planet?', 'Earth', 'Mars', 'Jupiter', 'Venus', 2),
        ('What is 2 + 2?', '3', '4', '5', '6', 2)
    ]

    cursor.executemany('''
        INSERT INTO questions (exam_id, question, option1, option2, option3, option4, correct_option) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [(exam_id, *q) for q in questions])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_sample_data()
