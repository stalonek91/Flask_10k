# Virtual env is called -> flask_10k/bin/activate /// deactivate after finished work

# Use TODO and FIXME
#TODO: generic -> add error handling to databases or basiaclly in forms, try except
#TODO: add only 5 last updates on top of page not full list

from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required
from urllib.parse import urlparse, urljoin



app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Log in first to acess the tracker!'


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(254),unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)



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
@login_required
def content():
    lessons = Lesson.query.order_by(Lesson.id.desc()).limit(5).all()
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

    if request.method == 'POST':
        
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username)


        if form.validate_on_submit():
            print(f'Submitted {title} form ')
            return 'kwoka'
    
    session['next'] = request.args.get('next')
    return render_template('login.html', title=title, form = form)


#FIXME: flash messages using 'flash' module
@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Register'
    form = LoginForm()
    form.submit_button.label.text = f'{title}'

    if form.validate_on_submit():
        print(f'Submitted {title} form ')

        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)


        db.session.add(new_user)
        db.session.commit()

        flash(f'You have been registered: {new_user.username}')
        return redirect(url_for('login'))
       
        
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

    