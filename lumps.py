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
        return math.e ** (-1 * const_cataDeact * self.t_resid)

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
        self.Dydx = K * self.Y.T * self.__func_aro(k_aroAdsorbDeact) * self.__func_nitro(
            k_nitroAdsorbDeact) * self.__func_coke(
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


# def opt_para_constructor(self , K , ):


# def test(x):const_cataDeact
#    return x[0]**2 + 10*sin(x[1])Deact
# x = arange(-10, 10, 0.1)
# plt.plot(x, test(x))
# plt.show()
# print optimize.minimize(test,[-5.0,2],method='L-BFGS-B')

# x0 = []
# K_model = mat([[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0]])
# K_init = mat([[0, 0, 0, 0], [2, 0, 0, 0], [0, 1, 0, 0], [3, 2, 4, 0]])
# for i in K_init.T.fl__func_airspeedat:
#     if i:
#         x0.append(i)
# print x0
# n = 4
# K = asmatrix(zeros((n, n)))
# # 前n行构成K
# for i in range(n):  # 将x0中的k按照K_model复原为K矩阵
#     sumCol = 0  # 每一列k的和json转列表
#     for j in range(n):
#         if K_model.T[i, j]:
#             k = x0.pop(0)
#             K.T[i, j] = k
#             sumCol -= k  # 反应动态平衡
#     K.T[i, i] = sumCol
# print K

class factorsFactory(object):
    def __init__(self, factors, Y_result, K_init, K_model, n,  Molmasses,
                 const_r=8.3145, ka_init=1, kn_init=1, const_cata_init=1):
        self.K_model = K_model
        self.K_init = K_init
        self.n = n
        self.factors = factors
        self.Y_result = Y_result
        self.Molmasses = Molmasses
        self.const_r = const_r
        self.ka_init = ka_init
        self.kn_init = kn_init
        self.const_cata_init = const_cata_init
        self.Y0 = []
        self.pre_t_resid = 0
        self.pre_p = 0
        self.pre_w_aro = 0
        self.pre_w_nitro = 0
        self.pre_r_oil = 1

    def addFactorsForResult(self, pre_factor,Y0, pre_t_resid, pre_p, pre_w_aro, pre_w_nitro, pre_r_oil):
        self.Y0 = Y0
        self.pre_t_resid = pre_t_resid
        self.pre_p = pre_p
        self.pre_w_aro = pre_w_aro
        self.pre_w_nitro = pre_w_nitro
        self.pre_r_oil = pre_r_oil
        self.pre_factor =pre_factor


def getK(factors, Y_result, K_init, K_model, n, Molmasses,
         const_r, ka_init, kn_init, const_cata_init):
    factor = factorsFactory(factors, Y_result, K_init, K_model, n, Molmasses,
                   const_r, ka_init, kn_init, const_cata_init)
    ka_init = factor.ka_init
    kn_init = factor.kn_init
    const_cata_init = factor.const_cata_init
    K_init = factor.K_init
    Molmasses = factor.Molmasses
    K_model = factor.K_model
    factors = factor.factors
    Y_result = factor.Y_result
    t = Tools()
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init)
    X0_result = optimize.minimize(
            obj, x0=t.x0, args=(Molmasses,K_model,factors,Y_result),bounds=t.bounds, method='L-BFGS-B', tol=1e-7).x
    return X0_result

def getResult(X0_result, K_model, n, Molmasses,t_resid,t,p,Y0,r_oil,w_aro,w_nitro,const_r):
    lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=t_resid, p=p, Y0=Y0, const_r=const_r, w_aro=w_aro, w_nitro=w_nitro, t=t, r_oil=r_oil,
                     n=n)
    result = lump.result_for_forecast(X0_result)
    return result

def obj(x0,Molmasses,K_model,factors,Y_results):
    sum = 0
    # Molmasses = factorsFactory.Molmasses
    # K_model = factorsFactory.K_model
    # factors = factorsFactory.factors
    # Y_results = factorsFactory.Y_results

    # Molmasses = mat([0.8, 1.1, 1.8, 0.2, 0.11, 0.058, 0.012])
    # K_model = mat([
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 1, 0, 0],
    #     [1, 1, 1, 1, 1, 0, 0]
    # ])

    # 't_resid': 4.01, 'p': 263, 'Y0': mat(
    #         [0.6643, 0.2238, 0.1119, 0, 0, 0, 0]), 'const_r': 8.3145, 'w_aro': 0.2238, 'w_nitro': 0.00175, 't': 520, 'r_oil': 6.47, 'n': 7},
    # factors = [
    #     {'t_resid': 3.04, 'p': 164, 'Y0': mat(
    #         [0.6938, 0.1895, 0.1167, 0, 0, 0, 0]), 'w_aro': 0.1895, 'w_nitro': 0.00134, 't': 793.15, 'r_oil': 8.2},
    #     {'t_resid': 3.22, 'p': 163, 'Y0': mat(
    #         [0.7014, 0.161, 0.1376, 0, 0, 0, 0]), 'w_aro': 0.161, 'w_nitro': 0.001703, 't': 793.15, 'r_oil': 8},
    #     {'t_resid': 3.22, 'p': 163, 'Y0': mat(
    #         [0.6605, 0.2525, 0.087, 0, 0, 0, 0]), 'w_aro': 0.2525, 'w_nitro': 0.00175, 't': 793.15, 'r_oil': 8.1}]
    # Y_results = [mat([0.0096, 0.0253, 0.0132, 0.2632, 0.3954, 0.1668, 0.1265]),
    #              mat([0.0067, 0.0185, 0.0079, 0.2685, 0.4089, 0.1652, 0.1273]),
    #              mat([0.0109, 0.0294, 0.0089, 0.2745, 0.3929, 0.1533, 0.1301])]
    for i in range(len(factors)):
        factor = factors[i]
        lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=factor['t_resid'], p=factor['p'], Y0=factor[
            'Y0'], const_r=8.3145, w_aro=factor['w_aro'], w_nitro=factor['w_nitro'], t=factor['t'],
                         r_oil=factor['r_oil'], n=K_model.shape[0])
        deviation = lump.result_for_opt(x0) - Y_results[i]
        sqa_deviation = (deviation * (deviation).T)[0, 0]
        sum += sqa_deviation
    return sum
    # print 'x0=%r' % t.x0
    # lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=4.01, p=263, Y0=mat(
    #     [0.6643, 0.2238, 0.1119, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.2238, w_nitro=0.00175, t=520, r_oil=6.47, n=7)
    # lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=4.19, p=263, Y0=mat(
    #     [0.6366, 0.2368, 0.1266, 0, 0, 0, 0]), const_r=8.3145, w_aro=0.2368, w_nitro=0.001703, t=520, r_oil=6.29, n=7)

    # lump.func_object(array(t.x0))


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
    # K_init = mat([
    #     [0,     0,     0,       0,       0,      0, 0],
    #     [0,     0,     0,       0,       0,      0, 0],
    #     [0,     0,     0,       0,       0,      0, 0],
    #     [1.59,  1.419, 0.47738, 0,       0,      0, 0],
    #     [2.24,  1.410, 1.40121, 0.64871, 0,      0, 0],
    #     [0.4877, 0.4584, 1.31941, 0.03473, 0.40114, 0, 0],
    #     [0.092, 0.1069, 0.63123, 0.3566,  0.04694, 0, 0]
    # ])

    # K_init = mat([2.07745367e+00,   1.77375607e+00,   2.44926962e-01,
    #               4.44831362e-02,   8.23186706e-01,   8.86057071e-01,
    #               1.04978809e-01,   5.95094499e-01,   6.33720879e-01,
    #               6.60040783e-01,   3.65101313e-01,   1.10248296e-01,
    #               6.44659134e-01,   4.26872169e-02,   1.29619541e-02,
    #               2.39223407e-01,   1.09750865e-04,   1.94931725e+00,
    #               1.95221608e+00,   4.08913128e+00])

    ka_init = 1
    kn_init = 1
    const_cata_init = 1
    t = Tools()
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init)
    for i in range(1):
        X0_result = optimize.minimize(
            obj, x0=t.x0, bounds=t.bounds, method='L-BFGS-B', tol=1e-7).x

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

        lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=2.91, p=160, Y0=mat(
            [0.5123,0.3696,0.1181,0,0,0,0]), const_r=8.3145, w_aro=0.3696, w_nitro=0.001011, t=793.15, r_oil=7.1,
                         n=7)

        print 'K='
        print X0_result
        print 'result='
        print lump.result_for_forecast(X0_result)
        t.x0 = X0_result

# run()
