# -*- coding: utf-8 -*
from flask import Flask, render_template, request
import numpy
import lumps
import json

app = Flask(__name__)


def makeFactors(rawData):
    data = json.loads(rawData)
    result = {}
    result['t_resid'] = float(data['t_resid'])
    result['p'] = float(data['p'])
    result['Y0'] = numpy.mat(data['Y0_values']).astype(numpy.float)
    result['w_aro'] = float(data['aro'])
    result['w_nitro'] = float(data['nitro'])
    result['t'] = float(data['T'])
    result['r_oil'] = float(data['OR'])

    return result


def makeY_result(rawData):
    data = json.loads(rawData)
    result = numpy.mat(data['Y_values']).astype(numpy.float)
    return result


def makeK_model(rawK_model, n):
    result = []
    for i in range(n):
        result.append(rawK_model[i * n:(i + 1) * n])
    return numpy.mat(result).astype(numpy.int).T


def makePreDatas(rawPreDatas):
    result = {}
    data = json.loads(rawPreDatas)
    result['t_resid'] = float(data['t_resid'])
    result['p'] = float(data['p'])
    result['Y0'] = numpy.mat(data['Y0_values']).astype(numpy.float)
    result['w_aro'] = float(data['aro'])
    result['w_nitro'] = float(data['nitro'])
    result['t'] = float(data['T'])
    result['r_oil'] = float(data['OR'])
    return result

@app.route('/')
def ui():
    return render_template('ui.html')


@app.route('/getK', methods=['POST'])
def returnK():
    rawK_model = request.form['K_model'].split(',')
    n = int(request.form['n'])
    rawDatas = request.form['data']
    rawMol_mass = request.form['mol_mass'].split(',')

    K_init = K_model = makeK_model(rawK_model, n)
    factors = map(makeFactors, rawDatas.split(', '))
    Y_result = map(makeY_result, rawDatas.split(', '))
    Molmasses = numpy.mat(rawMol_mass).astype(numpy.float)
    ka_init = kn_init = const_cata_init = 1
    const_r = float(json.loads(rawDatas.split(', ')[0])['R'])
    K = lumps.getK(factors, Y_result, K_init, K_model, n, Molmasses,
                   const_r, ka_init, kn_init, const_cata_init)
    print factors
    print Y_result
    print [K_init, K_model, n, Molmasses,
                   const_r, ka_init, kn_init, const_cata_init]




    return K


@app.route('/getResult', methods=['POST'])
def returnResult():
    rawK_model = request.form['K_model'].split(',')
    n = int(request.form['n'])
    rawDatas = request.form['data']
    rawMol_mass = request.form['mol_mass'].split(',')
    rawPre_data = request.form['preData']
    K_init = K_model = makeK_model(rawK_model, n)
    factors = map(makeFactors, rawDatas.split(', '))
    Y_result = map(makeY_result, rawDatas.split(', '))
    Molmasses = numpy.mat(rawMol_mass).astype(numpy.float)
    const_r = float(json.loads(rawDatas.split(', ')[0])['R'])
    ka_init = kn_init = const_cata_init = 1
    preDatas = makePreDatas(rawPre_data)
    pre_t_resid = preDatas['t_resid']
    pre_t = preDatas['t']
    pre_p = preDatas['p']
    pre_Y0 = preDatas['Y0']
    pre_r_oil = preDatas['r_oil']
    pre_w_aro = preDatas['w_aro']
    pre_w_nitro = preDatas['w_nitro']
    print '@@@@@@@@@@@@@@@@@@'
    X0 = lumps.getK(factors, Y_result, K_init, K_model, n, Molmasses,
                         const_r, ka_init, kn_init, const_cata_init)

    print X0
    print [X0, K_model, n, Molmasses, pre_t_resid, pre_t, pre_p, pre_Y0, pre_r_oil, pre_w_aro,
                             pre_w_nitro, const_r]

    result = lumps.getResult(X0, K_model, n, Molmasses, pre_t_resid, pre_t, pre_p, pre_Y0, pre_r_oil, pre_w_aro,
                             pre_w_nitro, const_r)
    print result
    return 'result  '


if __name__ == '__main__':
    app.run()
