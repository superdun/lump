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
        return self.Molmasses * (1 / self.Y0.T)

    def func_dydx(self, K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact):
        """
        微分方程组求取，参数4,即为集总模型的四个未知模型参数
        K:矩阵，反应速率常数矩阵，k_aroAdsorbDeact：芳烃吸附失活系数
        k_nitroAdsorbDeaoptimize.minimizect：氮吸附失活系数，const_cataDeact : 催化剂失活常数
        """
        self.Dydx = K * self.Y.T * self.__func_aro(k_aroAdsorbDeact) * self.__func_nitro(k_nitroAdsorbDeact) * self.__func_coke(
            const_cataDeact) * self.__func_molmass() * self.p / (self.const_r * self.t * self.__func_airspeed())
        return self.Dydx

    def dydx_for_RK(self, x, Y):
        """
        func_dydx为优化（optimize）的封装
        由于scipy的优化方法局限，函数的参数只能有一个，无法直接对多个参数进行优化
        故以x0封装func_dydx方法中的K,k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact四个参数
        x0为1维数组，结构[K(按行展开平铺),k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact]
        最后一行不足补齐0
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
        print K
        # 最后一行前三个元素分别对应k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact
        k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact = x0[-n:][:3]
        return self.func_dydx(K, k_aroAdsorbDeact, k_nitroAdsorbDeact, const_cataDeact)

    def func_object(self, x0):
        self.x0 = x0
        rk = RK(self.dydx_for_RK)
        rk.explicitRK4(0, self.Y0, 0.1, 1)


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

#    def opt_para_constructor(self , K , ):


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


def init():

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
    Y_result = mat([1.02, 2, 1.9, 25.87, 46.97, 15.57, 6.67])
    t.opt_var_constructor(K_init, ka_init, kn_init, const_cata_init)
    # print 'x0=%r' % t.x0
    lump = LumpModel(Molmasses=Molmasses, K_model=K_model, t_resid=4.01, p=263, Y0=mat([66.43, 22.38, 11.19, 0, 0, 0, 0]), const_r=8.3145, w_aro=22.38, w_nitro=0.175, t=520, r_oil=6.47, n=7)
    # optimize.minimize(lump.dydx_for_optimize, x0=t.x0, bounds=t.bounds, method='L-BFGS-B')
    lump.func_object(array(t.x0))
init()
