# Virtual env is called -> flask_10k/bin/activate /// deactivate after finished work

# Use TODO and FIXME
# TODO: generic -> add error handling to databases or basically in forms, try except
# TODO: add functionality which connects tracker with user ID
# TODO: add dissapearring effect in CSS for flash messages
# TODO: add 2 flash messages when deleting 2 entries fast
# TODO: add search of lessons by keywords

from flask import Flask, render_template, request, url_for, redirect, session, flash
from forms import LoginForm, RegistrationForm, AddLessonForm
from flask_login import LoginManager, login_required, current_user, logout_user, login_user

from itsdangerous import URLSafeTimedSerializer
from flask_migrate import Migrate
from extensions import db, bcrypt
from models import User, Lesson
from functions import is_safe_url, update_time, create_tables, add_lesson_funct, init_login_manager


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db.init_app(app)
bcrypt.init_app(app)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Log in first to access the tracker!'

init_login_manager(login_manager)


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

    time_to_display = int(time_left) if time_left % 1 == 0 else time_left
    print(f'Time to display: {time_to_display}')

    return render_template('content.html', lessons=lessons, time_to_display=time_to_display)


@app.route('/login', methods=['POST', 'GET'])
def login():
    title = 'Login'
    form = LoginForm()

    if form.validate_on_submit():

        print(f'Im in validate on submit')
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # TODO: error handling try specific errors for users
        if user and user.check_password(password):
            print(f'Is user authenticated function {current_user.is_authenticated}')
            print('Login_user function triggered')
            login_user(user, remember=True)
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
    return render_template('login.html', title=title, form=form)


# FIXME: flash messages using 'flash' module
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

    return render_template('register.html', form=form, title=title)


@app.route('/logout', methods=['POST', 'GET'])
def logout():

    logout_user()
    print(f'User has been logged out')
    return redirect(url_for('index'))
    

# FIXME: fix the validators
@app.route('/add_lesson', methods=['POST', 'GET'])
def add_lesson():

    if request.method == 'POST':
        
        try:
            time = float(request.form.get('time', 0))
            content = request.form.get('content')
            new_lesson = add_lesson_funct(time=time, content=content)
            flash('Lesson successfully added!', 'success')
        
        except ValueError:
            print(f'ERROR!!!!')

    return redirect(url_for('content'))


if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)

    