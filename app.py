from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///todo.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def ist_time():
    return datetime.now(pytz.timezone("Asia/Kolkata"))

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=ist_time)
    completed = db.Column(db.Boolean, default=False)
                             

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':

        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title, description=desc)
        db.session.add(todo)
        db.session.commit()


        return redirect('/')
    all_todos = Todo.query.all()
    return render_template('index.html', all_todos=all_todos)

@app.route('/show')
def products():
    all_todos = Todo.query.all()
    print(all_todos)
    return 'this is products page'

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.get(sno)

    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['desc']

        db.session.commit()
        return redirect('/')
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.get(sno)
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/complete/<int:sno>')
def complete(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
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


if __name__ == '__main__':
    app.run(debug=True, port=8000)