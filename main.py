from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
import datetime
import sqlite3
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Initialize Flask application
webpage = Flask(__name__)
webpage.secret_key = 'your_secret_key'

# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('mydatabase.db')
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                session_start TEXT,
                session_end TEXT
            )
        ''')
        conn.commit()
    return conn

# Route for the home page
@webpage.route("/")
def home():
    return render_template('index.html')

# Route for signup
@webpage.route("/signup")
def signup():
    return render_template('signup.html')

# Route for handling signup form submission
@webpage.route("/submit_signup", methods=["POST"])
def submit_signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        create_username = request.form.get('create_username')
        create_password = request.form.get('create_password')

        # Validation
        if not first_name or not last_name or not create_username or not create_password:
            flash("All fields are required.", 'error')
            return redirect(url_for('signup'))

        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', create_username):
            flash("Username must be a valid Gmail address.", 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(create_password)

        with get_db_connection() as conn:
            existing_user = conn.execute(
                'SELECT * FROM users WHERE username = ?', 
                (create_username,)
            ).fetchone()

            if existing_user:
                flash("Username already exists.", 'error')
                return redirect(url_for('signup'))

            conn.execute(
                'INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)',
                (first_name, last_name, create_username, hashed_password)
            )
            conn.commit()
            flash("Account created successfully! Please log in.", 'success')
            return redirect(url_for('login'))
    return redirect(url_for('signup'))

# Route for login
@webpage.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', 
                (username,)
            ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with get_db_connection() as conn:
                conn.execute(
                    'UPDATE users SET session_start = ? WHERE username = ?',
                    (session['start_time'], username)
                )
                conn.commit()

            return redirect(url_for('homepage'))
        else:
            flash("Invalid username or password.", 'error')
            return render_template('login.html')
    return render_template('login.html')

# Route for homepage
@webpage.route("/home")
def homepage():
    if 'username' not in session:
        return redirect(url_for('login'))

    csv_file_path = 'C:/Pavan/VS/JYPNB/WebPage/NYC_Collisions.csv'
    try:
        df = pd.read_csv(csv_file_path)

        search_query = request.args.get('search', '')
        sort_column = request.args.get('sort', None)
        sort_order = request.args.get('order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = 250

        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        if sort_column:
            df = df.sort_values(by=sort_column, ascending=(sort_order == 'asc'))

        total_records = len(df)
        total_pages = max(1, (total_records - 1) // per_page + 1)
        current_page = max(1, min(page, total_pages))
        start = (current_page - 1) * per_page
        end = start + per_page

        data_rows = df.iloc[start:end].to_dict(orient='records')
        column_names = df.columns.tolist()

    except FileNotFoundError:
        column_names = []
        data_rows = []
        total_pages = 1
        current_page = 1

    username = session.get('username')
    return render_template(
        'home.html',
        username=username,
        columns=column_names,
        rows=data_rows,
        current_page=current_page,
        total_pages=total_pages,
        search_query=search_query,
        sort_column=sort_column,
        sort_order=sort_order,
        max=max,
        min=min
    )

# Dash app for dashboard
dash_app = dash.Dash(
    __name__,
    server=webpage,
    url_base_pathname='/dashboard/'
)

# Load and preprocess dataset
CSV_FILE_PATH = "C:/Pavan/VS/JYPNB/WebPage/NYC_Collisions.csv"
data = pd.read_csv(CSV_FILE_PATH, parse_dates=[['Date', 'Time']])
data.columns = data.columns.str.strip().str.upper()
data.fillna({"BOROUGH": "Unknown", "PERSONS INJURED": 0, "PERSONS KILLED": 0}, inplace=True)
data['HOUR'] = data['DATE_TIME'].dt.hour

# GeeksforGeeks-inspired style for Dash layout
dash_app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'background-color': '#f4f4f4', 'padding': '20px'}, children=[
    html.H1("NYC Collisions Dashboard", style={'textAlign': 'center', 'color': '#0f9d58'}),
    dcc.Tabs([
        dcc.Tab(label='Persons Injured by Borough', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('BOROUGH')['PERSONS INJURED'].sum().reset_index(),
                    x='BOROUGH', y='PERSONS INJURED',
                    color='BOROUGH',
                    title="Persons Injured by Borough"
                )
            )
        ]),
        dcc.Tab(label='Persons Injured by Vehicle Type', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('VEHICLE TYPE')['PERSONS INJURED'].sum().nlargest(10).reset_index(),
                    x='VEHICLE TYPE', y='PERSONS INJURED',
                    color='VEHICLE TYPE',
                    title="Top 10 Vehicle Types: Persons Injured"
                )
            )
        ]),
        dcc.Tab(label='Pedestrians Killed by Vehicle Type', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('VEHICLE TYPE')['PEDESTRIANS KILLED'].sum().nlargest(10).reset_index(),
                    x='VEHICLE TYPE', y='PEDESTRIANS KILLED',
                    color='VEHICLE TYPE',
                    title="Top 10 Vehicle Types: Pedestrians Killed"
                )
            )
        ]),
        dcc.Tab(label='Persons Injured by Time of Day', children=[
            dcc.Graph(
                figure=px.line(
                    data.groupby('HOUR')['PERSONS INJURED'].sum().reset_index(),
                    x='HOUR', y='PERSONS INJURED',
                    markers=True,
                    title="Persons Injured by Hour of Day"
                )
            )
        ]),
        dcc.Tab(label='Persons Injured by Contributing Factor', children=[
            dcc.Graph(
                figure=px.bar(
                    data.groupby('CONTRIBUTING FACTOR')['PERSONS INJURED'].sum().nlargest(10).reset_index(),
                    x='CONTRIBUTING FACTOR', y='PERSONS INJURED',
                    color='CONTRIBUTING FACTOR',
                    title="Top 10 Contributing Factors: Persons Injured"
                )
            )
        ])
    ])
])

# Route to redirect to the dashboard
@webpage.route('/dashboard/')
def dashboard():
    return redirect('/dashboard/')

# Logout route
@webpage.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", 'success')
    return redirect(url_for('home'))

# Run Flask app
if __name__ == '__main__':
    webpage.run(host='0.0.0.0', port=5000, debug=True)
