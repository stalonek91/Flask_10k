# Virtual env is called -> flask_10k/bin/activate /// deactivate after finished work

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired



app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Float, nullable=False)
    content = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Lesson ID: {self.id} time spent:{self.time}, content: {self.content}'

class TimeLeft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_left = db.Column(db.Float, nullable=False)

def update_time():
    with app.app_context():

        hours_values = Lesson.query.with_entities(Lesson.time).all()
        spent_hours = sum(hour[0] for hour in hours_values)
        print(f'Total time: {spent_hours}')

        time_record = TimeLeft.query.filter_by(id=1).first()
        remaining_hours = 10000 - spent_hours
        time_record.time_left = remaining_hours
        db.session.commit()

        return remaining_hours
  

def create_tables():
    with app.app_context():
        db.create_all()

def add_Lesson(time, content):
    with app.app_context():
        new_Lesson = Lesson(time=time, content=content)
        db.session.add(new_Lesson)
        db.session.commit()
        print(f'Time: {time} topic: {content}')


@app.route('/delete_lesson', methods=['POST', 'GET'])
def delete_lesson():
    lesson_id = request.form.get('lesson_id')
    print(f'Lesson to delete ID: {lesson_id}')

    if lesson_id and lesson_id.isdigit():
        lesson_id = int(lesson_id)
        lesson_to_delete = Lesson.query.get(lesson_id)
        print(lesson_to_delete)
        db.session.delete(lesson_to_delete)
        db.session.commit()
    else:
        print('L')

    return redirect(url_for('index'))


@app.route('/')
def index():
    lessons = Lesson.query.all()
    time_left = update_time()

    time_to_display = int(time_left) if time_left %2 == 0 else time_left

    return render_template('index.html', lessons=lessons, time_to_display=time_to_display)

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')


@app.route('/add_lesson', methods=['POST', 'GET'])
def add_lesson():

    if request.method == 'POST':
        #TODO moze dotac wtf validatory?
        try:
            time = float(request.form.get('time', 0))
            content = request.form.get('content')
            new_lesson = add_Lesson(time=time, content=content)
        
        except ValueError:
            print(f'ERROR!!!!')
            
    return redirect(url_for('index'))
    

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

    