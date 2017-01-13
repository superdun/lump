# -*- coding: utf-8 -*

# 变量前缀含义：
#    const：常量，k：系数，t：时间，r:比例，w:百分含量,s:速度
# 其余词根注释：
#    aro：芳烃，nitro：氮，adsorb：吸收，resid：停留，deact:失活,cata:催化剂
# 变量注释：
#   k_aroAdsorbDeact ：芳烃吸附失活系数，k_nitroAdsorbDeact：氮吸附失活系数，
#   w_aro :  芳烃百分含量，w_nitro ：氮百分含量
#   t_resid : 催化剂停留时间
#   r_oil : 剂油比  ， const_cataDeact : 催化剂失活常数
#   Y

import math
import ConfigParser
import json

from numpy import *
from scipy import optimize
from RK4 import RK

import matplotlib.pyplot as plts



config = ConfigParser.ConfigParser()


class LumpModel(object):
    '''
    集总模型
    '''

    def __init__(self, t_resid, p, Y0, const_r, t, w_aro, w_nitro, r_oil, Molmasses, n, K_model):
        '''
        初始化，参数9，为集总模型中9个已知模型参数，故在实例化的时候就传入
        分别为：
        t_resid : 催化剂停留时间
        p : 压力
        Y ：矩阵，组分的质量百分含量
        const_r ：气体常数，8.3145J·mo1-1·k-1
        t : 反应温度
        w_aro : 原料中芳烃的质量百分含量
        w_nitro ； 原料中芳烃的质量百分含量
        r_oil : 剂油比
        Molmasses:相对分子质量矩阵
        n : 集总数
        K_model : k矩阵模型，如存在反应途径，则相应位置为1
        '''
        self.t_resid = t_resid
        self.p = p
        self.Y0 = Y0
        self.const_r = const_r
        self.w_aro = w_aro
        self.w_nitro = w_nitro
        self.r_oil = r_oil
        self.Molmasses = Molmasses
        self.t = t
        self.n = n
        self.K_model = K_model

    def __func_coke(self, const_cataDeact):
        '''焦炭影响因素，参数1  const_cataDeact : 催化剂·失活常数'''
        return math.e**(-1 * const_cataDeact * self.t_resid)

    def __func_aro(self, k_aroAdsorbDeact):
        '''芳烃影响因素，参数1  k_aroAdsorbDeact ：芳烃吸附失活系数，w_aro :  芳烃百分含量'''
        return 1 / (1 + k_aroAdsorbDeact * self.w_aro)

    def __func_nitro(self, k_nitroAdsorbDeact):
        '''
        氮中毒影响因素计算函数，参数1  k_nitroAdsorbDeact：氮吸附失活系数，w_nitro ：氮百分含量，
        t_resid : 催化剂停留时间，r_oil : 剂油比
        '''
        return 1 / (1 + k_nitroAdsorbDeact * self.w_nitro / self.r_oil)

    def __func_airspeed(self):
        '''
        空速求取，工业数据中一般不会含有空速，此为一个近似计算公式,单位： s-1
        参数2, r_oil : 剂油比，t_resid : 催化剂停留时间
        '''
        return 1 / (self.r_oil * self.t_resid)

    def __func_molmass(self):
        """
        摩尔质量求取
        """
        # 返回常数，不是矩阵，numpy矩阵相乘后得到的数在矩阵里
        return (1 / (asmatrix(self.Y0) * (1 / self.Molmasses.T)))[0, 0]

    def func_dydx(self, K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact):
        """
        微分方程组求取，参数4,即为集总模型的四个未知模型参数
        K:矩阵，反应速率常数矩阵，k_aroAdsorbDeact：芳烃吸附失活系数
        k_nitroAdsorbDeaoptimize.minimizect：氮吸附失活系数，const_cataDeact : 催化剂失活常数
        """
        # print self.__func_molmass() * self.p / (self.const_r * self.t *
        # self.__func_airspeed())
        # print self.__func_nitro(k_nitroAdsorbDeact)
        # print self.__func_aro(k_aroAdsorbDeact)
        # print self.__func_coke(const_cataDeact)
        # print self.__func_molmass() * self.p / (self.const_r * self.t * self.__func_airspeed())
        # print '!!!!!!!!!!!'
        self.Dydx = K * self.Y.T * self.__func_aro(k_aroAdsorbDeact) * self.__func_nitro(k_nitroAdsorbDeact) * self.__func_coke(
            const_cataDeact) * self.__func_molmass() * self.p / (self.const_r * self.t * self.__func_airspeed())
        return self.Dydx

    def dydx_for_RK(self, x, Y):
        """
        dydx_for_RK 为func_dydx的封装，以便使用龙哥库塔法计算
        """
        n = self.n
        K = asmatrix(zeros((n, n)))
        self.Y = Y
        x0 = self.x0.tolist()
        for i in range(n):  # 将x0中的k按照K_model复原为K矩阵
            sumCol = 0  # 每一列k的和
            for j in range(n):
                if self.K_model.T[i, j]:
                    k = x0.pop(0)
                    K.T[i, j] = k
                    sumCol -= k  # 反应动态平衡
            K.T[i, i] = sumCol
        # print K
        # 最后一行前三个元素分别对应k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact
        k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact = x0[-n:][:3]
        return self.func_dydx(K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact)

    def result_for_opt(self, x0):
        """
        result_for_opt为j计算结果为优化（optimize）的dydx_for_RK封装
        由于scipy的优化方法局限，函数的参数只能有一个，无法直接对多个参数进行优化
        故以x0封装func_dydx方法中的K,k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact四个参数
        x0为1维数组，结构[K(按行展开平铺),k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact]
        最后一行不足补齐0
        """

        self.x0 = x0
        rk = RK(self.dydx_for_RK)
        Y_cal = rk.explicitRK4(0, self.Y0, 0.1, 1)
        return Y_cal

    def result_for_forecast(self, x0):
        return self.result_for_opt(x0)


class Tools(object):

    def __init__(self):
        self.bounds = []

    def opt_var_constructor(self, K_init, ka_init, kn_init, const_cata_init):
        x0 = []
        bounds = []
        config.read('config.ini')
        k_bound = json.loads(config.get('bounds', 'k'))
        kn_bound = json.loads(config.get('bounds', 'kn'))
        ka_bound = json.loads(config.get('bounds', 'ka'))
        const_cata_bound = json.loads(config.get('bounds', 'const_cata'))
        for i in K_init.T.flat:
            if i:

                x0.append(i)
                bounds.append(k_bound)
        self.x0 = x0 + [ka_init, kn_init, const_cata_init]
        self.bounds = bounds + [ka_bound, kn_bound, const_cata_bound]
    def make_result(self,K_model,result,n):
        K=result[:-3].tolist()
        args = result[-3:]
        K_raw_result=[]
        for i in K_model.T.flat:
            if i:
                K_raw_result.append(K.pop(0))
            else:
                K_raw_result.append(0)
        K_result=reshape(K_raw_result,(n,n)).T.T.T
        ka_result,kn_result,cata_result=args
        print 'K='
        print K_result
        print 'ka='
        print ka_result
        print 'kn='
        print kn_result
        print 'cata='
        print cata_result

def obj(x0):
    sum = 0
    Molmasses = mat([0.8, 1.1, 1.8, 0.2, 0.11, 0.058, 0.012])
    K_model = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 0]
    ])

    factors = [
        {'t_resid': 3, 'p': 175, 'Y0': mat(
            [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 8.59},
        {'t_resid': 3, 'p': 175, 'Y0': mat(
            [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.72}]
    Y_results = [mat([0.01766, 0.04415, 0.02649, 0.1564, 0.4054, 0.2884, 0.0615]),
                 mat([0.01604, 0.0401, 0.02406, 0.1466, 0.4167, 0.2907, 0.0659])]

    # factors = [
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 7.92},
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 8.6}]
    # Y_results = [mat([0.01852, 0.0463, 0.02788, 0.1471, 0.4468, 0.252, 0.0615]),
    #              mat([0.01752, 0.0438, 0.02628, 0.1421, 0.4533, 0.2533, 0.0637])]
    # factors = [
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.16},
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.36}]
    # Y_results = [mat([0.02174, 0.05435, 0.03261, 0.1489, 0.4017, 0.2796, 0.0611]),
    #              mat([0.02112, 0.0528, 0.03168, 0.1405, 0.3966, 0.2947, 0.0626])]


    for i in range(len(factors)):
        factor = factors[i]
        lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=factor['t_resid'], p=factor['p'], Y0=factor[
                         'Y0'], const_r=8.3145, w_aro=factor['w_aro'], w_nitro=factor['w_nitro'], t=factor['t'], r_oil=factor['r_oil'], n=7)
        deviation = lump.result_for_opt(x0) - Y_results[i]
        sqa_deviation = (deviation * (deviation).T)[0, 0]
        sum += sqa_deviation
    return sum

class drawLine(object):
    def __init__(self,varName,lump,resultId,factors):
        self.varName=varName
        self.lump = lump
        self.resultId = resultId
        self.factors=factors

    def drawFunc(self,x):
        y=[]
        print self.lump.result_for_forecast(self.factors)[0,1]
        for i in x:
            if self.varName == 'p':
                self.lump.p = i
                result = self.lump.result_for_forecast(self.factors)[0, self.resultId]

            elif self.varName == 'time':
                self.lump.t_resid = i
                result = self.lump.result_for_forecast(self.factors)[0, self.resultId]

            elif self.varName == 't':
                self.lump.t = i
                result = self.lump.result_for_forecast(self.factors)[0, self.resultId]

            elif self.varName == 'r':
                self.lump.r_oil = i
                result = self.lump.result_for_forecast(self.factors)[0, self.resultId]

            else:
                print 'error'
                result = 0
            y.append(result)
        print y
        return array(y)
def run():
    K_init = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 0]
    ])

    ka_init = 1
    kn_init = 1
    const_cata_init = 1
    t = Tools()
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init)
    for i in range(1):
        filename=raw_input('file name>>>>')
        if filename=='':
            X0_result = optimize.minimize(
                obj, x0=array(t.x0), bounds=t.bounds, method='L-BFGS-B', tol=1e-7).x
            print X0_result
        else:
            X0_result=array(open('%s.txt'%filename,'r+').read().split(',')).astype(float)
        Molmasses = mat([0.8, 1.1, 1.8, 0.2, 0.11, 0.058, 0.012])
        K_model = mat([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 0]
        ])

        lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=3, p=175, Y0=mat(
            [0.481, 0.472, 0.047, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.472, w_nitro=0, t=685, r_oil=10.36, n=7)
        while 1:
            print X0_result
            varName = raw_input('input the var:p/time/t/r')
            varMin = float(raw_input('input min '))
            varMax = float(raw_input('input max '))
            stepNum = int(raw_input('how many steps?'))
            varRange = linspace(varMin, varMax, num=stepNum)
            resultId = (raw_input('input result Id,cut by comma')).split(',')
            for i in range(len(resultId)):
                draw = drawLine(varName=varName, lump=lump, resultId=int(resultId[i]), factors=X0_result)
                plts.subplot(int('%d1%d' % (len(resultId), i + 1)))
                plts.subplot(int('%d1%d' % (len(resultId), i + 1)))
                plts.plot(varRange, draw.drawFunc(varRange), linewidth=2)
                plts.ylabel("%d(%%)" % i)
            plts.xlabel(varName)
            plts.show()


            # lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=3, p=175, Y0=mat(
        #     [0.481, 0.472, 0.047, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.472, w_nitro=0, t=685, r_oil=8.79, n=7)
        # lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=3, p=175, Y0=mat(
        #     [0.481, 0.472, 0.047, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.472, w_nitro=0, t=685, r_oil=9.96, n=7)



        # set_printoptions(precision=4,suppress=False)
        # t.make_result(K_model,X0_result,7)
        # print 'pre_result='
        # print lump.result_for_forecast(X0_result)
        # t.x0 = X0_result
run()