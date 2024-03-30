from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import AddLessonForm
from models import Lesson
from functions import update_time, add_lesson_funct
from extensions import db

content_bp = Blueprint('content', __name__, url_prefix='/content')


@content_bp.route('/content', methods = ['GET', 'POST'])
@login_required
def content():

    form = AddLessonForm()
    print(f' {current_user.id}')
    if form.validate_on_submit():
        print('I am in content POST')
        try:
            new_lesson = add_lesson_funct(time=form.time_field.data, content=form.content.data)
            flash('Lesson successfully added!', 'success')

        except ValueError:
            flash('Fail to add lesson', 'error')
            print(f'ERROR!!!!')

    lessons = Lesson.query.order_by(Lesson.id.desc()).limit(5).all()
    time_left = update_time()

    time_to_display = int(time_left) if time_left % 1 == 0 else time_left
    print(f'Time to display: {time_to_display}')

    return render_template('content.html', lessons=lessons, time_to_display=time_to_display, form=form)


@content_bp.route('/delete_lesson', methods=['POST', 'GET'])
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

    return redirect(url_for('content.content'))


@content_bp.route('/')
def index():
    return render_template('index.html')