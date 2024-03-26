from urllib.parse import urlparse, urljoin
from flask import request, current_app
from extensions import db
from models import Lesson, TimeLeft, User
from sqlalchemy.exc import SQLAlchemyError


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def update_time():
    with current_app.app_context():

        hours_values = Lesson.query.with_entities(Lesson.time).all()
        spent_hours = sum(hour[0] for hour in hours_values)
        print(f'Total time: {spent_hours}')

        time_record = TimeLeft.query.filter_by(id=1).first()
        remaining_hours = 10000 - spent_hours
        time_record.time_left = remaining_hours
        db.session.commit()

        return remaining_hours


def create_tables():
    with current_app.app_context():
        db.create_all()


def add_lesson_funct(time, content):
    with current_app.app_context():
        try:
            new_lesson = Lesson(time=time, content=content)
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
