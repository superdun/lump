# -*- coding: utf-8 -*
import math
#变量前缀含义：
#    const：常量，k：系数，t：时间，r:比例，w:百分含量,s:速度
#其余词根注释：
#    aro：芳烃，nitro：氮，adsorb：吸收，resid：停留，deact:失活,cata:催化剂
#变量注释：
#   k_aroAdsorbDeact ：芳烃吸附失活系数，k_nitroAdsorbDeact：氮吸附失活系数，
#   w_aro :  芳烃百分含量，w_nitro ：氮百分含量
#   t_resid : 催化剂停留时间
#   r_oil : 剂油比  ， const_cataDeact : 催化剂失活常数
            
class lumpModel(object):

    def __init__(self):
        return
        
    #焦炭影响因素，参数2  const_cataDeact : 催化剂失活常数，t_resid : 催化剂停留时间
    def funcCoke(self ,const_cataDeact,t_resid):
        return math.e**(-1*const_cataDeact*t_resid)
        
    #芳烃影响因素，参数2  k_aroAdsorbDeact ：芳烃吸附失活系数，w_aro :  芳烃百分含量
    def funcAro(self , k_aroAdsorbDeact,w_aro):
        return 1/(1 + k_aroAdsorbDeact*w_aro)
        
    #氮中毒影响因素计算函数，参数4  k_nitroAdsorbDeact：氮吸附失活系数，w_nitro ：氮百分含量，
    #t_resid : 催化剂停留时间，r_oil : 剂油比
    def funcNitro(self, k_nitroAdsorbDeact,w_nitro,t_resid,r_oil):
        return 1/(1+k_nitroAdsorbDeact*w_nitro/r_oil)
     
    #空速求取，工业数据中一般不会含有空速，此为一个近似计算公式
    #参数2, r_oil : 剂油比，t_resid : 催化剂停留时间
    def funcAirspeed(self，r_oil，t_resid):
        return 1/(r_oil*t_resid)
    
    #
    
    
