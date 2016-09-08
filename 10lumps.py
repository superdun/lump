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


import math
from numpy import *


class LumpModel(object):
    '''
    集总模型
    '''

    def __init__(self, t_resid, P, y, R, T, w_aro, w_nitro, r_oil):
        '''
        初始化，参数8，为集总模型中8个已知模型参数，故在实例化的时候就传入
        分别为：
        t_resid : 催化剂停留时间
        P : 压力
        y ：矩阵，组分的质量百分含量
        R ：气体常数，8.3145J·mo1-1·k-1
        T : 反应温度
        w_aro : 原料中芳烃的质量百分含量
        w_nitro ； 原料中芳烃的质量百分含量
        r_oil : 剂油比
        '''
        self.t_resid = t_resid
        self.P = P
        self.y = y
        self.R = R
        self.w_aro = w_aro
        self.w_nitro = w_nitro
        self.r_oil = r_oil

    def __func_coke(self,const_cataDeact ):
        '''焦炭影响因素，参数1  const_cataDeact : 催化剂失活常数'''
        return math.e**(-1 * const_cataDeact * self.t_resid)

    def __func_aro(self, k_aroAdsorbDeact):
        '''芳烃影响因素，参数2  k_aroAdsorbDeact ：芳烃吸附失活系数，w_aro :  芳烃百分含量'''
        return 1 / (1 + k_aroAdsorbDeact *self.w_aro)

    def __func_nitro(self, k_nitroAdsorbDeact):
        '''    
        氮中毒影响因素计算函数，参数4  k_nitroAdsorbDeact：氮吸附失活系数，w_nitro ：氮百分含量，
        t_resid : 催化剂停留时间，r_oil : 剂油比
        '''
        return 1 / (1 + k_nitroAdsorbDeact * self.w_nitro / self.r_oil)

    def __func_airspeed(self):
        '''
        空速求取，工业数据中一般不会含有空速，此为一个近似计算公式,单位： s-1
        参数2, r_oil : 剂油比，t_resid : 催化剂停留时间
        '''
        return 1 / (self.r_oil * self.t_resid)

    def __func_molmass(self, y, molmasses):
        """
        摩尔质量求取，参数2 ,y：矩阵，molmasses:矩阵，组分摩尔质量的集合
        """
        return molmasses * (1 / y.T)

    def func_dydx(self):
