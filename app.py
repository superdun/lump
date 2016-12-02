# -*- coding: utf-8 -*
from flask import Flask,render_template,request
import numpy
import lumps
app = Flask(__name__)

@app.route('/')
def ui():
    return render_template('ui.html')

@app.route('/getK', methods=['POST'])
def returnK():
    rawK_model =  request.form['K_model']
    n = int(request.form['n'])
    rawDatas = request.form['data']
    return 'K'

@app.route('/getResult', methods=['POST'])
def returnResult():
    rawK_model =  request.form['K_model']
    n = int(request.form['n'])
    rawDatas = request.form['data']
    return 'result  '

if __name__ == '__main__':
    app.run()