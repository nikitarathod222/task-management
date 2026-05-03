
from flask import Flask, render_template, session, redirect, request
from config import Config
from database import mysql
from datetime import date
from flask_socketio import SocketIO
from modules.auth import auth

app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)
socketio = SocketIO(app)

app.register_blueprint(auth)


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

# =============================
# LOGOUT
# =============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    role = session['role']
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    today = date.today()


    if role == 'manager':
        cur.execute("""
            SELECT * FROM tasks 
            WHERE deadline < %s 
            AND status != 'completed'
            AND assigned_by=%s
        """, (today, user_id))
    else:
        cur.execute("""
            SELECT * FROM tasks 
            WHERE deadline < %s 
            AND status != 'completed'
        """, (today,))

    overdue_tasks = cur.fetchall()

  
    cur.execute("""
        SELECT 
            COUNT(*),
            SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status IN ('in_progress','starting') THEN 1 ELSE 0 END),
            SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END)
        FROM tasks
        WHERE assigned_by=%s
    """, (user_id,))

    stats = cur.fetchone()

    task_stats = {
        "total": stats[0] or 0,
        "completed": stats[1] or 0,
        "in_progress": stats[2] or 0,
        "pending": stats[3] or 0
    }

   
    if role == 'manager':

        cur.execute("SELECT id, name FROM users WHERE role='employee'")
        employees = cur.fetchall()


        cur.execute("SELECT * FROM tasks WHERE assigned_by=%s", (user_id,))
        tasks = cur.fetchall()

        
        cur.execute("""
            SELECT u.name,
                   COUNT(t.id),
                   SUM(CASE WHEN t.status='completed' THEN 1 ELSE 0 END),
                   ROUND(
                        (SUM(CASE WHEN t.status='completed' THEN 1 ELSE 0 END) / 
                        NULLIF(COUNT(t.id),0)) * 100, 2
                   )
            FROM users u
            LEFT JOIN tasks t ON u.id = t.assigned_to
            WHERE u.role='employee'
            GROUP BY u.id
        """)

        employee_stats = cur.fetchall()

        return render_template(
            'manager/dashboard.html',
            employees=employees,
            tasks=tasks,
            overdue_tasks=overdue_tasks,
            task_stats=task_stats,
            employee_stats=employee_stats
        )

  
    elif role == 'employee':
        cur.execute("SELECT * FROM tasks WHERE assigned_to=%s", (user_id,))
        tasks = cur.fetchall()

        return render_template(
            'employee/dashboard.html',
            tasks=tasks,
            overdue_tasks=overdue_tasks
        )

  
    else:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()

        return render_template(
            'admin/dashboard.html',
            users=users,
            overdue_tasks=overdue_tasks
        )


@app.route('/assign_task/<int:emp_id>', methods=['POST'])
def assign_task(emp_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO tasks(title, description, assigned_to, assigned_by, deadline, status, progress)
        VALUES(%s,%s,%s,%s,%s,'pending',0)
    """, (
        request.form['title'],
        request.form.get('description', ''),
        emp_id,
        session['user_id'],
        request.form['deadline']
    ))

    mysql.connection.commit()
    return redirect('/dashboard')

# =============================
# UPDATE PROGRESS
# =============================
@app.route('/update_progress/<int:task_id>', methods=['POST'])
def update_progress(task_id):
    progress = int(request.form['progress'])

    if progress == 100:
        status = 'completed'
    elif progress >= 50:
        status = 'in_progress'
    elif progress >= 25:
        status = 'starting'
    else:
        status = 'pending'

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE tasks 
        SET progress=%s, status=%s 
        WHERE id=%s
    """, (progress, status, task_id))

    mysql.connection.commit()
    return redirect('/dashboard')


@app.route('/employee/<int:emp_id>')
def employee_detail(emp_id):
    if session.get('role') != 'manager':
        return "Unauthorized", 403

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM users WHERE id=%s", (emp_id,))
    employee = cur.fetchone()

    cur.execute("SELECT * FROM tasks WHERE assigned_to=%s", (emp_id,))
    tasks = cur.fetchall()

    return render_template(
        'manager/employee_detail.html',
        employee=employee,
        tasks=tasks
    )
if __name__ == '__main__':
    socketio.run(app, debug=True)
