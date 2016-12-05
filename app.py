# -*- coding: utf-8 -*
from flask import Flask,render_template,request
import numpy
import lumps
import json
app = Flask(__name__)


def makeFactors(rawData):
    data = json.loads(rawData)
    result ={}
    result['t_resid']=float(data['t_resid'])
    result['p']=float(data['p'])
    result['Y0']=numpy.mat(data['Y0_values'])
    result['w_aro']=float(data['aro'])
    result['w_nitro']=float(data['nitro'])
    result['t']=float(data['T'])
    result['r_oil']=float(data['OR'])

    return result

def makeY_result(rawData):
    data = json.loads(rawData)
    result =numpy.mat(data['Y_values'])
    return result
def makeK_model(rawK_model,n):
    result=[]
    for i in range(n):
        result.append(rawK_model[i:i+n])
    return numpy.mat(result)

@app.route('/')
def ui():
    return render_template('ui.html')

@app.route('/getK', methods=['POST'])
def returnK():
    rawK_model =  request.form['K_model'].split(',')
    n = int(request.form['n'])
    rawDatas = request.form['data']
    rawMol_mass = request.form['mol_mass'].split(',')

    K_init=K_model = makeK_model(rawK_model,n)
    factors=map(makeFactors,rawDatas.split(', '))
    Y_result =map(makeY_result,rawDatas.split(', '))
    Molmasses = numpy.mat(rawMol_mass)
    const_r= ka_init=kn_init=const_cata_init=1
    K = lumps.getK(factors,Y_result,K_init,K_model,n,Molmasses,
                   const_r,ka_init,kn_init,const_cata_init)
    return K

@app.route('/getResult', methods=['POST'])
def returnResult():
    rawK_model =  request.form['K_model'].split(',')
    n = int(request.form['n'])
    rawDatas = request.form['data']
    rawMol_mass = request.form['mol_mass']

    return 'result  '

if __name__ == '__main__':
    app.run()