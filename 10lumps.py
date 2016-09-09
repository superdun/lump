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

from numpy import *
from scipy import optimize
import pylab as plt


config = ConfigParser.ConfigParser() 

class LumpModel(object):
    '''
    集总模型
    '''

    def __init__(self, t_resid, p, Y, const_r, t, w_aro, w_nitro, r_oil,Molmasses,n):
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
        n : 集总数
        '''
        self.t_resid = t_resid
        self.p = p
        self.Y = Y
        self.const_R = const_R
        self.w_aro = w_aro
        self.w_nitro = w_nitro
        self.r_oil = r_oil
        self.Molmasses=Molmasses
        self.t=t
        self.n=n

    def __func_coke(self,const_cataDeact ):
        '''焦炭影响因素，参数1  const_cataDeact : 催化剂失活常数'''
        return math.e**(-1 * const_cataDeact * self.t_resid)

    def __func_aro(self, k_aroAdsorbDeact):
        '''芳烃影响因素，参数1  k_aroAdsorbDeact ：芳烃吸附失活系数，w_aro :  芳烃百分含量'''
        return 1 / (1 + k_aroAdsorbDeact *self.w_aro)

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
        return self.Molmasses * (1 / self.Y.T)

    def func_dydx(self,K,k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact):
        """
        微分方程组求取，参数4,即为集总模型的四个未知模型参数
        K:矩阵，反应速率常数矩阵，k_aroAdsorbDeact：芳烃吸附失活系数
        k_nitroAdsorbDeaoptimize.minimizect：氮吸附失活系数，const_cataDeact : 催化剂失活常数
        """
        self.Dydx=K*self.Y.T*self.__func_aro(k_aroAdsorbDeact)*self.__func_nitro(k_nitroAdsorbDeact)*self.__func_coke(const_cataDeact)*self.__func_molmass()*self.p/(self.const_r*self.t*__func_airspeed())
        return self.Dydx
        
        
    def dydx_for_optimize(self,x0):
        """
        func_dydx为优化（optimize）的封装
        由于scipy的优化方法局限，函数的参数只能有一个，无法直接对多个参数进行优化
        故以x0封装func_dydx方法中的K,k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact四个参数
        x0为1维数组，结构[K(按行展开平铺),k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact]
        最后一行不足补齐0
        """
        K=[]
        n=self.n
        # 前n行构成K
        for i in xrange(0,len(x0),n):
            K.append(x0[i:i+n])
        K=mat(K[:-1]) 
        
        #最后一行前三个元素分别对应k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact
        k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact = x0[-n:][:3]
        return self.func_dydx(K,k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact)
            
    def func_object(self,x0):
            
        
class Tools(object):
    def __init__(self):
        return
    def opt_var_constructor(self,K,k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact):
        x0=[]
        bounds=
        config.read('config.ini')
        k_bound=config.get('bounds','k')
        kn_bound=config.get('bounds','kn')
        ka_bound=config.get('bounds','ka')
        for i in K:
            x0.append(i)
        self.x0=x0+[k_aroAdsorbDeact,k_nitroAdsorbDeact,const_cataDeact]
        self.bounds=
        
#    def opt_para_constructor(self , K , ):
    
    
#def test(x):
#    return x[0]**2 + 10*sin(x[1])
#x = arange(-10, 10, 0.1)
#plt.plot(x, test(x))
#plt.show()
#print optimize.minimize(test,[-5.0,2],method='L-BFGS-B')
config.read('config.ini')
print config.get('bounds','k')     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
