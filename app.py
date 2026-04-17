from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import session
import pytz
import os

app = Flask(__name__)
app.secret_key = "a8f9d3k2l9x7q1w5z6m4n2p8r0t3y7u"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://sql12823381:aA2AKsb7ip@sql12.freesqldatabase.com:3306/sql12823381'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


def ist_time():
    return datetime.now(pytz.timezone("Asia/Kolkata"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=ist_time)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def hello_world():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        todo = Todo(title=title, description=desc, user_id=session['user_id'])
        db.session.add(todo)
        db.session.commit()

        return redirect('/')

    all_todos = Todo.query.filter_by(user_id=session['user_id']).all()
    user = User.query.get(session['user_id'])
    return render_template('index.html', all_todos=all_todos, user=user)

@app.route('/show')
def products():
    all_todos = Todo.query.all()
    print(all_todos)
    return 'this is products page'

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):

    if 'user_id' not in session:
        return redirect('/login')

    todo = Todo.query.filter_by(sno=sno, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['desc']
        db.session.commit()
        return redirect('/')

    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):

    if 'user_id' not in session:
        return redirect('/login')
    
    todo = Todo.query.filter_by(sno=sno, user_id=session['user_id']).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/complete/<int:sno>')
def complete(sno):

    if 'user_id' not in session:
        return redirect('/login')

    todo = Todo.query.filter_by(sno=sno, user_id=session['user_id']).first_or_404()
    todo.completed = True
    db.session.commit()
    return redirect('/')

@app.route('/search')
def search():
    query = request.args.get('query')

    if query:
        all_todos = Todo.query.filter(Todo.title.contains(query)).all()
    else:
        all_todos = Todo.query.all()

    return render_template('index.html', all_todos=all_todos, query=query)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, port=8000)