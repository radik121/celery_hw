import requests
from celery.result import AsyncResult
from celery_utils import get_celery_app_instance
from flask_mail import Mail, Message
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import atexit

engine = create_engine('postgresql://admin:admin@127.0.0.1:5432/flask_hw')
Base = declarative_base()
Session = sessionmaker(bind=engine)
atexit.register(lambda: engine.dispose())


class Adverts(Base):
    __tablename__ = 'adverts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, server_default=func.now())
    owner_name = Column(Text, nullable=False)
    email = Column(String, nullable=False, unique=True)


Base.metadata.create_all(engine)

app = Flask('adverts')
app.config.from_object('config')
celery = get_celery_app_instance(app)

mail = Mail(app)


@celery.task
def send_mail(data):
    """ Функция отправки эл. писем.
    """
    with app.app_context():
        msg = Message("Ping!",
                      sender="12345@mail.ru",
                      recipients=data)
        msg.body = f"Technical work on the site!"
        mail.send(msg)
        return 'Messages send'


class SendMail(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status,
                        'result': task.result})

    def post(self):
        if request.json['submit'] == 'Send':
            data = [user['email'] for user in requests.get('http://127.0.0.1:5000/advert/0').json()]
            task = send_mail.apply_async(args=[data])
            return jsonify({'task_id': task.id})


class AdvertsView(MethodView):

    def get(self, id: int):
        with Session() as session:
            adverts_all = session.query(Adverts).all()
            advert_one = session.query(Adverts).filter(Adverts.id == id).first()
            if id == 0:
                return jsonify([{'name': advert.name,
                                 'description': advert.description,
                                 'create_time': advert.date,
                                 'owner': advert.owner_name,
                                 'email': advert.email}
                                for advert in adverts_all])
            return jsonify({
                'name': advert_one.name,
                'description': advert_one.description,
                'create_time': advert_one.date,
                'owner': advert_one.owner_name,
                'email': advert_one.email
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            advert = Adverts(name=json_data['name'],
                             description=json_data['description'],
                             owner_name=json_data['owner_name'],
                             email=json_data['email'])
            session.add(advert)
            session.commit()

            return jsonify({
                'id': advert.id,
                'name': advert.name,
                'description': advert.description,
                'time': advert.date.isoformat(),
                'owner': advert.owner_name,
                'email': advert.email
            })

    def put(self, id: int):
        json_data = request.json
        with Session() as session:
            advert_update = session.query(Adverts).filter(Adverts.id == id).first()
            advert = Adverts(name=json_data['name'],
                             description=json_data['description'],
                             owner_name=json_data['owner_name'])
            advert_update.name = advert.name
            advert_update.description = advert.description
            advert_update.owner_name = advert.owner_name
            session.commit()
            return jsonify({
                'name': advert_update.name,
                'description': advert_update.description,
                'create_time': advert_update.date,
                'owner': advert_update.owner_name
            })

    def delete(self, id: int):
        with Session() as session:
            advert_del = session.query(Adverts).filter(Adverts.id == id).first()
            session.delete(advert_del)
            session.commit()
            return jsonify({id: 'delete'})


app.add_url_rule('/advert/', view_func=AdvertsView.as_view('create_advert'), methods=['POST'])
app.add_url_rule('/advert/<int:id>', view_func=AdvertsView.as_view('get_advert'), methods=['GET'])
app.add_url_rule('/advert/<int:id>', view_func=AdvertsView.as_view('put_advert'), methods=['PUT'])
app.add_url_rule('/advert/<int:id>', view_func=AdvertsView.as_view('del_advert'), methods=['DELETE'])

# celery routr
app.add_url_rule('/celery/', view_func=SendMail.as_view('post_celery'), methods=['POST'])
app.add_url_rule('/celery/<string:task_id>', view_func=SendMail.as_view('get_celery'), methods=['GET'])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
