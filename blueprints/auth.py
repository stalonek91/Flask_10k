from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user
from models import User
from extensions import db
from itsdangerous import URLSafeTimedSerializer
from functions import is_safe_url, create_new_table

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST', 'GET'])
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
                    print(f'URL is safe, redirecting to next {session["next"]}')
                return redirect(session['next'])

            print(f'Redirecting to content content')
            return redirect(url_for('content.content'))

        else:

            return f'User: {form.email.data} does not exist'

    session['next'] = request.args.get('next')
    return render_template('login.html', title=title, form=form)


# FIXME: flash messages using 'flash' module
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Register'
    form = RegistrationForm()
    form.submit_button.label.text = f'{title}'

    if form.validate_on_submit():
        print(f'Submitted {title} form ')

        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

        new_user = User(username=form.username.data, email=form.email.data,
                        session_token=serializer.dumps([form.username.data, form.password.data]))
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.flush()

        create_new_table(user_id=new_user.id)
        db.session.commit()

        flash(f'You have been registered: {new_user.username}')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form, title=title)


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():

    logout_user()
    print(f'User has been logged out')
    return redirect(url_for('content.index'))

