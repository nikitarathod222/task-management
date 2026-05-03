from flask import Blueprint, request, render_template, redirect, session, flash
from database import mysql
import bcrypt

auth = Blueprint('auth', __name__)

# =============================
# 📝 REGISTER
# =============================
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # ❌ Prevent admin self-registration
        if role == 'admin':
            flash("Admin cannot be created from register page")
            return redirect('/register')

        # 🔍 Check existing email
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Email already exists")
            return redirect('/register')

        # 🔐 Hash password (convert to string)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cur.execute("""
            INSERT INTO users(name,email,password,role)
            VALUES(%s,%s,%s,%s)
        """, (name, email, hashed_password, role))

        mysql.connection.commit()

        flash("Registration successful. Please login.")
        return redirect('/login')

    return render_template('register.html')


# =============================
# 🔐 LOGIN
# =============================
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user:
            flash("User not found")
            return redirect('/login')

        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            session['role'] = user[4]

            flash("Login successful")
            return redirect('/dashboard')
        else:
            flash("Invalid password")
            return redirect('/login')

    return render_template('login.html')
