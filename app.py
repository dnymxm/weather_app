import os
import requests

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from pprint import pprint

API_KEY = 'YOURAPIKEY'  # Create an account on https://openweathermap.org/api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(16)

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
    r = requests.get(url).json()
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    # POST SECTION
    err_msg = ''
    if request.method == 'POST':
        new_city = request.form.get('city')
        if new_city:
            existing_city = City.query.filter_by(name=new_city.title()).first()
            if not existing_city:
                new_city_data = get_weather_data(new_city)
                if new_city_data['cod'] == 200:
                    new_city_obj = City(name=new_city.title())
                    db.session.add(new_city_obj)
                    db.session.commit()
                else:
                    err_msg = 'This city does not exist!'
            else:
                err_msg = 'City already exists in the database!'

        if err_msg:
            flash(err_msg, 'error')
        else:
            flash('City added succesfully')

    # GET SECTION
    cities = City.query.all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city': city.name,
            'temperature': r.get('main').get('temp'),
            'description': r.get('weather')[0].get('description'),
            'icon': r.get('weather')[0].get('icon'),
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data[::-1])


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }', 'success')
    return redirect(url_for('index'))
