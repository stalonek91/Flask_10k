# Virtual env is called -> flask_10k/bin/activate /// deactivate after finished work

# Use TODO and FIXME
#TODO: generic -> add error handling to databases or basiaclly in forms, try except
#TODO: add functionality which connects tracker with user ID
#TODO: add dissapearing effect in CSS for flash messages
#TODO: add 2 flash messages when deleting 2 entries fast

from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm, AddLessonForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, UserMixin, current_user, logout_user, login_user
from urllib.parse import urlparse, urljoin
from itsdangerous import URLSafeSerializer
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
serializer = URLSafeSerializer(app.config['SECRET_KEY'])
migrate = Migrate(app, db)

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

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(254),unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    session_token = db.Column(db.String(100), unique=True, nullable=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)



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

        try:
            lesson_to_delete = Lesson.query.get(lesson_id)
            print(lesson_to_delete)
            if lesson_to_delete:
                db.session.delete(lesson_to_delete)
                db.session.commit()
                flash('Lesson successfully deleted!', 'success')
            else:
                flash('No lesson in DB to delete!', 'error')
        except Exception as e:
            print(e)
            flash('An error occurred while deleting the lesson.', 'error')
    else:
        flash('Invalid lesson ID.', 'error')
        
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




@app.route('/login', methods=['POST', 'GET'])
def login():
    title = 'Login'
    form = LoginForm()

    if form.validate_on_submit():

        print(f'jestem w validate on submit')
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        

        #TODO: error handling try specific errrors for users
        if user and user.check_password(password):


            login_user(user)
            print(f'Is user authenticated function {current_user.is_authenticated}')
            flash_login = f'Welcome: {current_user.username}'

            if 'next' in session and session['next']:
                if is_safe_url(session['next']):
                    print('URL is safe, redirecting to next')
                return redirect(session['next'])
            
            return redirect(url_for('index'))
        
        else:
            
            return f'User: {form.email.data} does not exist'
        

    session['next'] = request.args.get('next')
    return render_template('login.html', title=title, form = form)


#FIXME: flash messages using 'flash' module
@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Register'
    form = RegistrationForm()
    form.submit_button.label.text = f'{title}'

    if form.validate_on_submit():
        print(f'Submitted {title} form ')

        new_user = User(username=form.username.data, email=form.email.data, session_token=serializer.dumps([form.username.data, form.password.data]))
        new_user.set_password(form.password.data)
        
        db.session.add(new_user)
        db.session.commit()

        flash(f'You have been registered: {new_user.username}')
        return redirect(url_for('login'))
       
        
    return render_template('register.html', form = form, title = title)

@app.route('/logout', methods=['POST', 'GET'])
def logout():

    logout_user()
    print(f'User has been logged out')
    return redirect(url_for('index'))
    


@app.route('/add_lesson', methods=['POST', 'GET'])
def add_lesson():

    if request.method == 'POST':
        
        try:
            time = float(request.form.get('time', 0))
            content = request.form.get('content')
            new_lesson = add_Lesson(time=time, content=content)
            flash('Lesson successfully addded!', 'success')
        
        except ValueError:
            print(f'ERROR!!!!')
            
    return redirect(url_for('content'))
    

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

    