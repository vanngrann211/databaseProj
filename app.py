#1 from flask, import flash
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "cat"

def get_students():
    conn = sqlite3.connect('workshop_sample.db')
    conn.row_factory = sqlite3.Row
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return students

#Get classes using function
def get_classes():
    conn = sqlite3.connect('workshop_sample.db')
    conn.row_factory = sqlite3.Row
    classes = conn.execute('SELECT * FROM classes').fetchall()
    conn.close()
    return classes

#Add student functionality
@app.route('/add', methods=['POST'])
def add_student():
    #pull 3 values from your modal pop-up
    name = request.form['name']
    class_id = request.form['class_id']
    grade = request.form['grade']

    #connect to your database and insert the 3 values selected. Once done, commit (this permanently saves)
    conn = sqlite3.connect('workshop_sample.db')
    conn.execute('INSERT INTO students (name, class_id, grade) VALUES (?, ?, ?)', (name, class_id, grade))
    conn.commit()
    conn.close()

    #2 Add a flash message when student added successfully
    #flash(message you want displayed, "success/info/warning/danger(error)")
    flash(f"{name} has been successfully added", "success")

    #redirect the user back to the home page
    return redirect(url_for('index'))

#Delete student functionality
#this goes by each student id
@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = sqlite3.connect('workshop_sample.db')
    conn.row_factory = sqlite3.Row

    #pull student name based on their id (fetchone, not all)
    student = conn.execute('SELECT name FROM students WHERE id = ?', (student_id,)).fetchone()

    #create condition: if a student was found, delete and add message. Else, provide error
    if student:
        conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        flash(f"{student['name']} has been deleted", "success")
    else:
        flash("No student found", "error")
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    #create condition: If seeing data, use GET. If changing data, use POST
    if request.method == 'POST':
        # Extract updated values from the submitted form
        name = request.form['name']
        grade = request.form['grade']
        class_id = request.form['class_id']

        # Update student data in the database
        conn = sqlite3.connect('workshop_sample.db')
        conn.execute('UPDATE students SET name = ?, grade = ?, class_id = ? WHERE id = ?',(name, grade, class_id, id))
        conn.commit()
        conn.close()

        # Redirect back to homepage
        return redirect(url_for('index'))

    # For GET request: fetch student and class list for the form
    conn = sqlite3.connect('workshop_sample.db')
    conn.row_factory = sqlite3.Row

    #fetch only one student, not all
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()

    #condition to check that student exists
    if student is None:
        flash("Student not found", "error")
        return redirect(url_for('index'))
    
    classes = conn.execute('SELECT * FROM classes').fetchall()
    conn.close()

    return render_template('edit.html', student=student, classes=classes)


@app.route('/')
def index():
    min_grade = request.args.get('min_grade')
    class_id = request.args.get('class_id')
    conn = sqlite3.connect('workshop_sample.db')
    conn.row_factory = sqlite3.Row
    query = '''
        SELECT students.id, students.name, students.grade, classes.name as class_name
        FROM students
        JOIN classes ON students.class_id = classes.id
        WHERE 1=1
    '''
    params = []
    if min_grade:
        query += ' AND grade >= ?'
        params.append(min_grade)
    if class_id:
        query += ' AND class_id = ?'
        params.append(class_id)
    students = conn.execute(query, params).fetchall()
    conn.close()
    # Get all classes to populate the dropdown in modal pop-up
    classes = get_classes()
    return render_template('index.html', students=students, classes=classes)

if __name__ == '__main__':
    app.run(debug=True)
