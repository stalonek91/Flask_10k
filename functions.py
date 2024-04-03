from urllib.parse import urlparse, urljoin
from flask import request, current_app
from flask_login import current_user
from extensions import db
from models import Lesson, TimeLeft, User
from sqlalchemy.exc import SQLAlchemyError


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def create_new_table(user_id, timeleft=10000):

    try:
        new_table = TimeLeft(time_left=timeleft, user_id=user_id)
        db.session.add(new_table)
        db.session.commit()

    except Exception as e:
        print(f'{e}')


def update_time():
    with current_app.app_context():

        hours_values = Lesson.query.filter(Lesson.table_id == current_user.id).with_entities(Lesson.time).all()
        spent_hours = sum(hour[0] for hour in hours_values)
        print(f'Total time: {spent_hours}')

        print(f'Type of user.id is: {type(current_user.id)}')
        time_record = TimeLeft.query.filter_by(user_id=current_user.id).first()

        print(f'Time record: {time_record}')
        remaining_hours = 10000 - spent_hours
        time_record.time_left = remaining_hours
        db.session.commit()

        return remaining_hours


def create_tables():
    with current_app.app_context():
        db.create_all()


def add_lesson_funct(time, content, table_id):
    print('triggering add_lesson_funct')
    with current_app.app_context():
        try:
            #FIXME: dodac brakujaca kolumne
            new_lesson = Lesson(time=time, content=content, table_id=table_id)
            db.session.add(new_lesson)
            db.session.commit()
            print(f'Time: {time} topic: {content}')

        except SQLAlchemyError as e:
            return f'There has been some problem -> {e}'


def init_login_manager(login_manager):
    @login_manager.user_loader
    def load_user(session_token):
        # serializer.loads(session_token, max_age=3600)
        return User.query.filter_by(session_token=session_token).first()
