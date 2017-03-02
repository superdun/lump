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
import pickle
from numpy import *
from scipy import optimize
from RK4 import RK
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
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

    def __func_coke(self, const_cataDeact, x):
        '''焦炭影响因素，参数1  const_cataDeact : 催化剂·失活常数'''
        return math.e ** (-1 * const_cataDeact * self.t_resid * x)

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

    def func_dydx(self, K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact, x):
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
        self.Dydx = K * self.Y.T * self.__func_aro(k_aroAdsorbDeact) * self.__func_nitro(
            k_nitroAdsorbDeact) * self.__func_coke(
            const_cataDeact, x) * self.__func_molmass() * self.p / (self.const_r * self.t * self.__func_airspeed())

        return self.Dydx
    def func_dydx_simple(self,K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact, x):
        self.Dydx = K * self.Y.T * (1 / (1 + k_aroAdsorbDeact * self.w_aro)) * \
                    (1 / (1 + k_nitroAdsorbDeact * self.w_nitro / self.r_oil)) *\
                    (math.e ** (-1 * const_cataDeact * self.t_resid * x)) * \
                    ((1 / (asmatrix(self.Y0) * (1 / self.Molmasses.T)))[0, 0]) * \
                    self.p / (self.const_r * self.t * (1 / (self.r_oil * self.t_resid)))

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

        return self.func_dydx(K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact, x)

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
        Y_cal = rk.explicitRK4ForLump(0, self.Y0, 0.01, 1)
        return Y_cal

    def result_for_forecast(self, x0,stepLength=0.1):
        self.x0 = x0
        rk = RK(self.dydx_for_RK)
        Y_cal = rk.explicitRK4ForLump(0, self.Y0, stepLength, 1)
        return Y_cal


class Tools(object):
    def __init__(self):
        self.bounds = []

    def opt_var_constructor(self, K_init, ka_init, kn_init, const_cata_init,k_bound,kn_bound,ka_bound,const_cata_bound):
        x0 = []
        bounds = []
        # k_bound = [0, 10]
        # kn_bound = [0, 1]
        # ka_bound = [0, 1]
        # const_cata_bound = [0, 5]
        for i in K_init.T.flat:
            if i:
                x0.append(i)
                bounds.append(k_bound)
        self.x0 = x0 + [ka_init, kn_init, const_cata_init]
        self.bounds = bounds + [ka_bound, kn_bound, const_cata_bound]
    def opt_var_constructor_By_List(self,X_init,max_bounds,min_bounds):
        # k_bound = [0, 10]
        # kn_bound = [0, 1]
        # ka_bound = [0, 1]
        # const_cata_bound = [0, 5]
        bounds = []
        for i in range(len(max_bounds)):
            bounds.append([min_bounds[i],max_bounds[i]])
        self.x0 = X_init
        self.bounds = bounds

    def make_result(self, K_model, result, n):
        K = result[:-3].tolist()
        args = result[-3:]
        K_raw_result = []
        for i in K_model.T.flat:
            if i:
                K_raw_result.append(K.pop(0))
            else:
                K_raw_result.append(0)
        K_result = reshape(K_raw_result, (n, n)).T.T.T
        ka_result, kn_result, cata_result = args
        print 'K='
        print K_result
        print 'ka='
        print ka_result
        print 'kn='
        print kn_result
        print 'cata='
        print cata_result
        return {'K_result':K_result,'ka_result':ka_result,'kn_result':kn_result,'cata_result':cata_result}
    def obj_para_constructor(self, Molmasses, K_model, factors):
        self.Molmasses = Molmasses
        self.K_model = K_model
        self.factors = factors
        Y_results = []
        print factors
        for i in factors:
            Y_results.append(i['Y_results'])
        self.Y_results = Y_results

def objForBest(x0,args):
    sum=0
    lump = args['lump']
    targets = args['targets']
    Ka = args['Ka']
    Ea = args['Ea']
    stepLength = args['stepLength']
    lump.t,lump.p,lump.r_oil,lump.t_resid=x0
    X0 = getKByT(Ka, Ea, lump.t, R=8.3145)
    Y_result = lump.result_for_forecast(X0, stepLength)
    for i in targets:
        i=int(i)-1
        sum+=Y_result[0,i]
    print sum
    return -sum


def obj(x0, args):
    sum = 0
    Molmasses = args.Molmasses
    # mat([0.8,1.1,1.8,0.2,0.11,0.058,0.012])
    K_model = args.K_model
    #     mat([
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 1, 0, 0],
    #     [1, 1, 1, 1, 1, 0, 0]
    # ])

    factors = args.factors
    Y_results = args.Y_results
    #     [
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 8.59},
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.4181, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.72}]
    # Y_results = [mat([0.01766, 0.04415, 0.02649, 0.1564, 0.4054, 0.2884, 0.0615]),
    #              mat([0.01604, 0.0401, 0.02406, 0.1466, 0.4167, 0.2907, 0.0659])]

    # factors = [
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
        #         [0.481,0.472,0.047,0,0,0,0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 7.92},
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481,0.472,0.047,0,0,0,0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 8.6}]
    # Y_results = [mat([0.01852,0.0463,0.02788,0.1471,0.4468,0.252,0.0615]),
    #              mat([0.01752,0.0438,0.02628,0.1421,0.4533,0.2533,0.0637])]
    # factors = [
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481,0.472,0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.16},
    #     {'t_resid': 3, 'p': 175, 'Y0': mat(
    #         [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.36}]
    # Y_results = [mat([0.02174, 0.05435, 0.03261, 0.1489, 0.4017, 0.2796, 0.0611]),
    #              mat([0.02112, 0.0528, 0.03168, 0.1405, 0.3966, 0.2947, 0.0626])]


    for i in range(len(factors)):
        factor = factors[i]
        lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=factor['t_resid'], p=factor['p'], Y0=factor[
            'Y0'], const_r=8.3145, w_aro=factor['w_aro'], w_nitro=factor['w_nitro'], t=factor['t'],
                         r_oil=factor['r_oil'], n=K_model.shape[0])
        deviation = lump.result_for_opt(x0) - Y_results[i]
        sqa_deviation = (deviation * (deviation).T)[0, 0]
        sum += sqa_deviation
    print sum
    return sum


class drawLine(object):
    def __init__(self, varName, lump, resultId, factors,stepLength):
        self.varName = varName
        self.lump = lump
        self.resultId = resultId
        self.factors = factors
        self.stepLength=stepLength

    def drawFunc(self, x):
        y = []
        a= self.factors
        if self.factors.withTemp:
            for i in x:
                if self.varName == 'p':
                    self.lump.p = i
                    X0 = getKByT(self.factors.Ka, self.factors.Ea, self.lump.t, R=8.3145)
                    result = self.lump.result_for_forecast(X0, self.stepLength)[0, self.resultId]

                elif self.varName == 'time':
                    self.lump.t_resid = i
                    X0 = getKByT(self.factors.Ka, self.factors.Ea, self.lump.t, R=8.3145)
                    result = self.lump.result_for_forecast(X0, self.stepLength)[0, self.resultId]

                elif self.varName == 't':
                    self.lump.t = i
                    X0 = getKByT(self.factors.Ka, self.factors.Ea, i, R=8.3145)
                    result = self.lump.result_for_forecast(X0, self.stepLength)[0, self.resultId]

                elif self.varName == 'r':
                    self.lump.r_oil = i
                    X0 = getKByT(self.factors.Ka, self.factors.Ea, self.lump.t, R=8.3145)
                    result = self.lump.result_for_forecast(X0, self.stepLength)[0, self.resultId]

                else:
                    print 'error'
                    result = 0
                y.append(result)
        else:
            for i in x:
                if self.varName == 'p':
                    self.lump.p = i
                    result = self.lump.result_for_forecast(self.factors.X0_result, self.stepLength)[0, self.resultId]

                elif self.varName == 'time':
                    self.lump.t_resid = i

                    result = self.lump.result_for_forecast(self.factors.X0_result, self.stepLength)[0, self.resultId]

                elif self.varName == 't':
                    self.lump.t = i
                    result = self.lump.result_for_forecast(self.factors.X0_result, self.stepLength)[0, self.resultId]

                elif self.varName == 'r':
                    self.lump.r_oil = i
                    result = self.lump.result_for_forecast(self.factors.X0_result, self.stepLength)[0, self.resultId]

                else:
                    print 'error'
                    result = 0
                y.append(result)

        print y
        return array(y)

    def draw3DFunc(self, X,Y):
        result = ones(X.shape)


        if self.varName == ['t', 'p']:
            for x, y in ndindex(result.shape):
                self.lump.t = X[x, y]
                self.lump.p = Y[x, y]
                X0 = getKByT(self.factors.Ka, self.factors.Ea, self.lump.t, R=8.3145)
                sum=0
                for i in self.resultId:
                    sum += self.lump.result_for_forecast(X0, self.stepLength)[0, i]
                result[x, y] =sum
        elif self.varName == ['t', 'r']:
            for x, y in ndindex(result.shape):
                self.lump.t = X[x, y]
                self.lump.r_oil = Y[x, y]
                X0 = getKByT(self.factors.Ka, self.factors.Ea, self.lump.t, R=8.3145)
                sum=0
                for i in self.resultId:
                    sum += self.lump.result_for_forecast(X0, self.stepLength)[0, i]
                result[x, y] = sum
        elif self.varName == ['r', 'p']:
            for x, y in ndindex(result.shape):
                self.lump.r_oil = X[x, y]
                self.lump.p = Y[x, y]
                X0 = getKByT(self.factors.Ka, self.factors.Ea, self.lump.t, R=8.3145)
                sum=0
                for i in self.resultId:
                    sum += self.lump.result_for_forecast(X0, self.stepLength)[0, i]
                result[x, y] = sum
        print result
        return result
    def getXLable(self, varName):
        if varName == 'p':
            return 'pressure (kPa)'

        elif varName == 'time':
            return ' residence time (s)'
        elif varName == 't':
            return 'temperature (K)'

        elif varName == 'r':

            return 'solvent to oil ratio'
        else:
            return 'error!'

    def onpick(self,event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = self.lined[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        self.fig.canvas.draw()

def run():
    K_init = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0]
    ])
    K_model = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0]
    ])
    Molmasses = mat([0.8, 1.1, 1.8, 0.2, 0.11, 0.058, 0.012])
    factors = [{'t_resid': 3, 'p': 175, 'Y0': mat(
        [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 8.59},
               {'t_resid': 3, 'p': 175, 'Y0': mat(
                   [0.4181, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.72}]
    Y_results = [mat([0.01766, 0.04415, 0.02649, 0.1564, 0.4054, 0.2884, 0.0615]),
                 mat([0.01604, 0.0401, 0.02406, 0.1466, 0.4167, 0.2907, 0.0659])]

    ka_init = 1
    kn_init = 1
    const_cata_init = 1
    t = Tools()
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init)
    t.obj_para_constructor(Molmasses=Molmasses, K_model=K_model, factors=factors)
    for i in range(1):
        filename = raw_input('file name>>>>')
        if filename == '':
            X0_result = optimize.minimize(
                obj, x0=array(t.x0), args=(t,), bounds=t.bounds, method='L-BFGS-B', tol=1e-7).x
            print X0_result
        else:
            X0_result = array(open('%s.txt' % filename, 'r+').read().split(',')).astype(float)
        K_model = mat([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 0, 0]
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


def run2():
    K_init = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0]
    ])

    ka_init = 1
    kn_init = 1
    const_cata_init = 1
    t = Tools()
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init)
    for i in range(1):
        filename = raw_input('file name>>>>')
        if filename == '':
            X0_result = optimize.minimize(
                obj, x0=array(t.x0), bounds=t.bounds, method='L-BFGS-B', tol=1e-7).x
            print X0_result
        else:
            X0_result = array(open('%s.txt' % filename, 'r+').read().split(',')).astype(float)
        Molmasses = mat([0.8, 1.1, 1.8, 0.2, 0.11, 0.058, 0.012])
        K_model = mat([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 0, 0]
        ])

        lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=3, p=175, Y0=mat(
            [0.481,0.472,0.047,0,0,0,0]), const_r=8.3145, w_aro=0.472, w_nitro=0, t=685, r_oil=10.36, n=7)

        set_printoptions(precision=4, suppress=False)
        t.make_result(K_model, X0_result, 7)
        print 'pre_result='
        print lump.result_for_forecast(X0_result)
        t.x0 = X0_result
        # lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=3, p=175, Y0=mat(
        #     [0.481, 0.472, 0.047, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.472, w_nitro=0, t=685, r_oil=8.79, n=7)
        # lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=3, p=175, Y0=mat(
        #     [0.481, 0.472, 0.047, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.472, w_nitro=0, t=685, r_oil=9.96, n=7)



        # set_printoptions(precision=4,suppress=False)
        # t.make_result(K_model,X0_result,7)
        # print 'pre_result='
        # print lump.result_for_forecast(X0_result)
        # t.x0 = X0_result


#
# run()


class catObj(object):
    def __init__(self, n, K_model, K_init, ka_init, kn_init, const_cata_init, tool, tol, optMethod, X0_result,withTemp,Ea,Ka,t):
        self.K_init = K_init
        self.ka_init = ka_init
        self.kn_init = kn_init
        self.const_cata_init = const_cata_init
        self.tool = tool
        self.tol = tol
        self.optMethod = optMethod
        self.X0_result = X0_result
        self.n = n
        self.K_model = K_model
        self.withTemp=withTemp
        self.Ea=Ea
        self.Ka =Ka
        self.t=t


def saveCat(filename, n, lump, K_init, ka_init, kn_init, const_cata_init, tool, tol, optMethod, X0_result,withTemp,Ea,Ka,t):
    if filename[-4:]=='.cat':
        fileObject = open(filename, 'wb')
    else:
        fileObject = open('%s.cat' % filename, 'wb')
    #          n, K_model, K_init, ka_init, kn_init, const_cata_init, tool, tol, optMethod, X0_result,withTemp,Ea,Ka,t
    a = catObj(n, lump, K_init, ka_init, kn_init, const_cata_init, tool, tol, optMethod, X0_result,withTemp,Ea,Ka,t)
    pickle.dump(a, fileObject)
    fileObject.close()


def loadCat(filename):

    fileObject = open('/home/dun/opt/htdocs/lump/%s.cat' % filename, 'r')
    return pickle.load(fileObject)

def getEa(K1,K2,t1,t2,R=8.3145):
    Ea = (R*t1*t2/(t1-t2))*log(K1/K2)
    Ea[-2]=0
    return [Ea,multiply(K1,(math.e**(Ea/(t1*R))))]
def getKByT(Ka,Ea,t,R=8.3145):
    return multiply(Ka,(math.e**(-1*Ea/(t*R))))
def newBest(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n,stepLength,target):
    result={}
    lump = LumpModel(Molmasses=catObj.tool.Molmasses, K_model=catObj.K_model, t_resid=t_resid, p=p, Y0=Y0,
                     const_r=const_r, w_aro=w_aro, w_nitro=w_nitro, t=t, r_oil=r_oil, n=catObj.n)
    set_printoptions(precision=4, suppress=False)
    # catObj.tool.make_result(catObj.K_model, catObj.X0_result, 7)
    #TODO:noWithTemp
    args = {'lump':lump,'targets':target,'Ka':catObj.Ka,'Ea':catObj.Ea,'stepLength':stepLength}
    bounds = array([t,p,r_oil,t_resid])
    if not catObj.withTemp:
        pass
    else:
        X0_result = optimize.minimize(
            objForBest, x0=array([(t[0]+t[1])/2,(p[0]+p[1])/2,(r_oil[0]+r_oil[1])/2,(t_resid[0]+t_resid[1])/2]), args=(args,), bounds=bounds, method=catObj.optMethod, tol=catObj.tol).x
        lump.t, lump.p, lump.r_oil,lump.t_resid =X0_result
        X0=getKByT(catObj.Ka, catObj.Ea, lump.t, R=8.3145)
        Y_result = lump.result_for_forecast(X0,stepLength)[0]
        sum=0
        for i in target:
            i = int(i) - 1
            sum += Y_result[0, i]
        result={'bestT':lump.t,'bestP':lump.p,'bestR':lump.r_oil,'bestTime':lump.t_resid,'sum':sum,'Y':Y_result[0]}

    return result

def newCatNoKa(filename, K_init, ka_init, kn_init, const_cata_init, K_model, Molmasses, factors, optMethod, tol,
           n):
    t = Tools()
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init,[0,10],[0,1],[0,1],[0,1])
    t.obj_para_constructor(Molmasses=Molmasses, K_model=K_model, factors=factors)
    X0_result = optimize.minimize(
        obj, x0=array(t.x0), args=(t,), bounds=t.bounds, method=optMethod, tol=tol).x
    withTemp=0
    saveCat(filename, n, K_model, K_init, ka_init, kn_init, const_cata_init,t, tol, optMethod, X0_result,withTemp,mat([]),mat([]),factors[0]['t'])
def newCatWithKa(filename, K_init, ka_init, kn_init, const_cata_init, K_model, Molmasses, factors, optMethod, tol,
           n):
    X0_results = []
    temps = []
    t=Tools()

    for i in factors:
        if len(temps)==0:
            t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init, [0, 10], [0, 1], [0, 1], [0, 1])
            t.obj_para_constructor(Molmasses=Molmasses, K_model=K_model, factors=factors[i])
            X0_result = optimize.minimize(obj, x0=array(t.x0), args=(t,), bounds=t.bounds, method=optMethod, tol=tol).x
        else:
            temp = factors[i][0]['t']
            maxTIndex = temps.index(max(temps))
            minTIndex = temps.index(min(temps))
            init_bounds=[[],[]]
            for k in X0_results[0]:
                init_bounds[0].append(0)
                init_bounds[1].append(10)

            upTIndex = 0
            downTIndex = 0
            for j in range(len(temps)):
                if temp >= temps[j] and temps[j] >= temps[downTIndex]:
                    downTIndex = j
                elif temp < temps[j] and temps[j] < temps[upTIndex]:
                    upTIndex = j

            if upTIndex==downTIndex and downTIndex == maxTIndex and temp>temps[maxTIndex]:
                X_init = X0_results[maxTIndex]
                max_bounds = init_bounds[1]
                min_bounds = X0_results[maxTIndex]
                kn_bound = [X0_results[maxTIndex][-2],X0_results[maxTIndex][-2]]
                ka_bound = [X0_results[maxTIndex][-3],X0_results[maxTIndex][-3]]
                const_cata_bound = [X0_results[maxTIndex][-1],X0_results[maxTIndex][-1]]

            elif upTIndex==downTIndex and downTIndex == minTIndex and temp<temps[minTIndex]:
                X_init = X0_results[minTIndex]
                max_bounds = X0_results[minTIndex]
                min_bounds = init_bounds[0]

            else:
                X_init = (X0_results[minTIndex]+X0_results[maxTIndex])/2
                max_bounds = X0_results[maxTIndex]
                min_bounds = X0_results[minTIndex]

            print [X_init,max_bounds]
            t.opt_var_constructor_By_List(X_init,max_bounds,min_bounds)
            t.obj_para_constructor(Molmasses=Molmasses, K_model=K_model, factors=factors[i])
            X0_result = optimize.minimize(obj, x0=array(t.x0), args=(t,), bounds=t.bounds, method=optMethod, tol=tol).x
            X0_result[-3]=X0_results[0][-3]
            X0_result[-2] = X0_results[0][-2]
            X0_result[-1] = X0_results[0][-1]
        X0_results.append(X0_result)
        temps.append(factors[i][0]['t'])
        print X0_results[0]
        # print t.make_result(K_init, X0_results[0], 12)
    Ea,Ka=getEa(X0_results[0],X0_results[1],temps[0],temps[1],8.3145)
    withTemp = 1
    saveCat(filename, n, K_model, K_init, ka_init, kn_init, const_cata_init,t, tol, optMethod, X0_results,withTemp,Ea,Ka,temps)

def new3dChart(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n,chartConfig,stepLength):
    lump = LumpModel(Molmasses=catObj.tool.Molmasses, K_model=catObj.K_model, t_resid=t_resid, p=p, Y0=Y0,
                     const_r=const_r, w_aro=w_aro, w_nitro=w_nitro, t=t, r_oil=r_oil, n=catObj.n)
    set_printoptions(precision=4, suppress=False)
    # catObj.tool.make_result(catObj.K_model, catObj.X0_result, 7)
    varName = chartConfig['varName']
    varMin = chartConfig['varMin']
    varMax = chartConfig['varMax']
    stepNum = int(chartConfig['stepNum'])
    varRange = [linspace(float(varMin[0]),float(varMax[0]) , num=stepNum),linspace(float(varMin[1]),float(varMax[1]), num=stepNum)]
    resultId = chartConfig['resultId']
    resultName = chartConfig['resultName']
    #TODO:nowithTemp
    X,Y=meshgrid(varRange[0],varRange[1])
    resultIds = []
    for i in resultId.split(','):
        resultIds.append(int(i)-1)
    draw = drawLine(varName=varName, lump=lump, resultId=resultIds, factors=catObj,
                    stepLength=stepLength)

    Z =draw.draw3DFunc(X,Y)
    fig = plts.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)

    ax.set_xlabel(draw.getXLable(varName[0]),fontsize=20)
    ax.set_ylabel(draw.getXLable(varName[1]),fontsize=20)
    ax.set_zlabel('y',fontsize=20)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    plts.tick_params(which='major', labelsize=15)
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plts.show()
    return 1


def new2dChart(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n,chartConfig,stepLength):
    lump = LumpModel(Molmasses=catObj.tool.Molmasses, K_model=catObj.K_model, t_resid=t_resid, p=p, Y0=Y0,
                     const_r=const_r, w_aro=w_aro, w_nitro=w_nitro, t=t, r_oil=r_oil, n=catObj.n)
    set_printoptions(precision=4, suppress=False)
    # catObj.tool.make_result(catObj.K_model, catObj.X0_result, 7)
    varName = chartConfig['varName']
    varMin = float(chartConfig['varMin'])
    varMax = float(chartConfig['varMax'])
    stepNum = int(chartConfig['stepNum'])
    varRange = linspace(varMin, varMax, num=stepNum)
    resultId = (chartConfig['resultId']).split(',')
    resultName = (chartConfig['resultName']).split(',')
    if not catObj.withTemp:
        fig, ax = plts.subplots()
        lines=[]
        for i in range(len(resultId)):
            draw = drawLine(varName=varName, lump=lump, resultId=int(resultId[i])-1, factors=catObj,stepLength=stepLength)
            line,=ax.plot(varRange, draw.drawFunc(varRange), 'o-', linewidth=2, label=resultName[int(resultId[i]) - 1])
            lines.append(line)
        leg = ax.legend(loc='upper right', fancybox=True, shadow=True)
        lined = dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline
        ax.set_xlabel(draw.getXLable(varName))
        ax.set_ylabel('y')
        draw.lined=lined
        draw.fig=fig
        fig.canvas.mpl_connect('pick_event', draw.onpick)
        plts.tick_params(axis='both', which='major', labelsize=20)
        plts.show()
    else:
        fig, ax = plts.subplots()
        lines = []
        for i in range(len(resultId)):
            draw = drawLine(varName=varName, lump=lump, resultId=int(resultId[i])-1, factors=catObj,stepLength=stepLength)
            line,=ax.plot(varRange, draw.drawFunc(varRange), 'o-', linewidth=2, label=resultName[int(resultId[i]) - 1])
            lines.append(line)

        leg = ax.legend(loc='upper right', fancybox=True, shadow=True)
        lined = dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline
        ax.set_xlabel(draw.getXLable(varName), fontsize=20)
        ax.set_ylabel('y', fontsize=20)
        draw.lined=lined
        draw.fig=fig
        fig.canvas.mpl_connect('pick_event', draw.onpick)
        plts.tick_params(axis='both', which='major', labelsize=20)
        plts.show()
    return 1




def newPre(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n,stepLength):
    lump = LumpModel(Molmasses=catObj.tool.Molmasses, K_model=catObj.K_model, t_resid=t_resid, p=p, Y0=Y0,
                     const_r=const_r, w_aro=w_aro, w_nitro=w_nitro, t=t, r_oil=r_oil, n=catObj.n)
    set_printoptions(precision=4, suppress=False)
    # catObj.tool.make_result(catObj.K_model, catObj.X0_result, 7)
    if not catObj.withTemp:
        print 'pre_result='
        result = lump.result_for_forecast(catObj.X0_result,stepLength)
        print result
        return result
    else:

        X0 = getKByT(catObj.Ka,catObj.Ea,t,R=8.3145)
        print X0
        X0[-2]=0
        print 'pre_result='
        result = lump.result_for_forecast(X0,stepLength)
        print result
        return result
lumpObj=mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0]
    ])
Molmasses=mat([0.8,1.1,1.8,0.2,0.11,0.058,0.012])
factors ={797.15: [{'p': 175.0, 'w_nitro': 0.0, 't': 797.15, 'r_oil': 8.9, 'w_aro': 0.472, 'Y0': matrix([[ 0.481,  0.472,  0.047,  0.   ,  0.   ,  0.   ,  0.   ]]), 'Y_results': matrix([[ 0.04  ,  0.032 ,  0.008 ,  0.151 ,  0.453 ,  0.2429,  0.0731]]), 't_resid': 3.0}], 807.15: [{'p': 175.0, 'w_nitro': 0.0, 't': 807.15, 'r_oil': 8.5, 'w_aro': 0.472, 'Y0': matrix([[ 0.481,  0.472,  0.047,  0.   ,  0.   ,  0.   ,  0.   ]]), 'Y_results': matrix([[ 0.0406 ,  0.03248,  0.00812,  0.143  ,  0.4467 ,  0.2557 ,  0.0734 ]]), 't_resid': 3.0}, {'p': 175.0, 'w_nitro': 0.0, 't': 807.15, 'r_oil': 9.2, 'w_aro': 0.472, 'Y0': matrix([[ 0.481,  0.472,  0.047,  0.   ,  0.   ,  0.   ,  0.   ]]), 'Y_results': matrix([[ 0.038 ,  0.0304,  0.0076,  0.142 ,  0.4408,  0.2661,  0.0751]]), 't_resid': 3.0}]}
# newCatWithKa('./4.cat',lumpObj, 1, 0, 1, lumpObj, Molmasses, factors, 'L-BFGS-B', 1e-7,
#                          lumpObj.shape[0])
# f = open('./4.cat', "r")
# aobj = pickle.load(f)
#
# newPre(aobj,3,175,mat([0.481,0.472,0.047,0,0,0,0]),8.3145,0.472,0,900,9.2,7)
def test():
    K_init = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0]
    ])
    K_model = mat([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0]
    ])
    Molmasses = mat([0.8, 1.1, 1.8, 0.2, 0.11, 0.058, 0.012])
    factors = [{'t_resid': 3, 'p': 175, 'Y0': mat(
        [0.481, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 8.59},
               {'t_resid': 3, 'p': 175, 'Y0': mat(
                   [0.4181, 0.472, 0.047, 0, 0, 0, 0]), 'w_aro': 0.472, 'w_nitro': 0, 't': 685, 'r_oil': 9.72}]
    Y_results = [mat([0.01766, 0.04415, 0.02649, 0.1564, 0.4054, 0.2884, 0.0615]),
                 mat([0.01604, 0.0401, 0.02406, 0.1466, 0.4167, 0.2907, 0.0659])]

    ka_init = 1
    kn_init = 1
    const_cata_init = 1
    n = 7
    optMethod = 'L-BFGS-B'
    tol = 1e-7
    newCat('1', K_init, ka_init, kn_init, const_cata_init, K_model, Molmasses, factors, Y_results, optMethod, tol, n)


