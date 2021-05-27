# -*- coding: utf-8 -*-
from app import app
from flask import render_template, request, jsonify
import pickle
import json

# 8 значений для прогноза
# [0.038378100, 0.097786738, -0.037833062, 0.007891115, 0.008181598, -0.009838156, 0.049799581, -0.000319685]


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET'])
def predict():
    with open("D:/Projects/2021/practice/app/model.pkl", "rb") as f:
        model = pickle.load(f)
    data = request.args['values'].split(',')
    array = []
    for i in data:
        array.append(float(i))

    x = model.predict([array])
    print(x[0])

    return jsonify({"data": x[0]})
