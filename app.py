# Virtual env is called -> flask_10k/bin/activate /// deactivate after finished work

# Use TODO and FIXME
#TODO: generic -> add error handling to databases or basiaclly in forms, try except
#TODO: add only 5 last updates on top of page not full list

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(254),unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)



class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Float, nullable=False)
    content = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Lesson ID: {self.id} time spent:{self.time}, content: {self.content}'

#TODO: add user id linked with timeleft 
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

    return redirect(url_for('content'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/content')
def content():
    lessons = Lesson.query.all()
    time_left = update_time()

    time_to_display = int(time_left) if time_left %1 == 0 else time_left
    print(f'Time to display: {time_to_display}')

    return render_template('content.html', lessons=lessons, time_to_display=time_to_display)

#FIXME: hash pass + flash messages
@app.route('/login', methods=['POST', 'GET'])
def login():
    title = 'Login'
    form = LoginForm()
    form.submit_button.label.text = f'{title}'

    if form.validate_on_submit():
        print(f'Submitted {title} form ')
        return 'kwoka'
    return render_template('login.html', title=title, form = form)


#FIXME: flash messages
@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Register'
    form = LoginForm()
    form.submit_button.label.text = f'{title}'

    if form.validate_on_submit():
        print(f'Submitted {title} form ')

        username = form.username.data
        email = form.email.data
        plain_password = form.password.data

        hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return f'Success! user: {username} has been created!'
       
        
    return render_template('register.html', form = form, title = title)


@app.route('/add_lesson', methods=['POST', 'GET'])
def add_lesson():

    if request.method == 'POST':
        
        try:
            time = float(request.form.get('time', 0))
            content = request.form.get('content')
            new_lesson = add_Lesson(time=time, content=content)
        
        except ValueError:
            print(f'ERROR!!!!')
            
    return redirect(url_for('content'))
    

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

    