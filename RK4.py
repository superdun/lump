# -*- coding: utf-8 -*
"""
龙格库塔法：
参考资料：http://wenku.baidu.com/view/7f62170d4a7302768e993990.html
      https://zh.wikipedia.org/wiki/%E9%BE%99%E6%A0%BC%EF%BC%8D%E5%BA%93%E5%A1%94%E6%B3%95

求微分方程解dy/dx=f(x,y)
包含3个方法：
1. step，龙格库塔法的每一步计算方法
参数{
    x0,
    y0:初始x,y,
    stepLength:初始步长 ,

}

2. explicitRK4，显式龙格库塔，即固定步长：
参数{
    x0,
    y0:初始x,y,
    stepLength:初始步长 ,
    targetX：目标的x
}
3. implicitRK4 可变步长，隐式
参数{
    x0,
    y0:初始x,y,
    stepLength:初始步长 ,
    targetX：目标的x,
    accuracy: 变步长的精确度
}


example:
from RK4 import RK
def func(x,y):
    return -y
rk = RK(func)
print rk.implicitRK4(0,1,0.1,1,0.00000000000001)


"""
from numpy import *


class RK(object):

    def __init__(self, f):
        self.func = f

    def step(self, func, x, y, stepLength):
        K1 = func(x, y)
        K2 = func(x + stepLength / 2, y + (stepLength * K1 / 2).T)
        K3 = func(x + stepLength / 2, y + (stepLength * K2 / 2).T)
        K4 = func(x + stepLength, y + (stepLength * K3).T)

        return y + (stepLength * (K1 + 2 * K2 + 2 * K3 + K4) / 6).T
    # 显式龙格库塔，即固定步长

    def explicitRK4(self, x0, Y0, stepLength, targetX):
        x = x0
        y = Y0
        func = self.func
        while x + stepLength < targetX:
            y = self.step(func, x, y, stepLength)
            x = x + stepLength
        stepLength = targetX - x
        y = self.step(func, x, y, stepLength)
        print y
        return y
    # 可变步长，隐式

    def implicitRK4(self, x0, Y0, stepLength, targetX, accuracy):
        x = x0
        Y = Y0
        result_y = []
        for i in range(len(self.funcs)):

            y = Y[i]
            func = self.funcs[i]
            while x + stepLength < targetX:
                y2 = self.explicitRK4(
                    x, [y], stepLength / 2, x + stepLength)[0]
                y1 = self.step(func, x, y, stepLength)
                i = 0
                if abs(y1 - y2) > accuracy:
                    while abs(y1 - y2) > accuracy:
                        i += 1
                        para = 2**i
                        y2 = self.explicitRK4(
                            x, [y], stepLength / (2 * para), x + stepLength / para)[0]
                        y1 = self.step(func, x, y, stepLength / para)
                    stepLength = stepLength / para
                    y = y1
                elif abs(y1 - y2) < accuracy:
                    while abs(y1 - y2) < accuracy:
                        i -= 1
                        para = 2**i
                        y2 = self.explicitRK4(
                            x, [y], stepLength / (2 * para), x + stepLength / para)[0]
                        y1 = self.step(func, x, y, stepLength / para)

                    stepLength = stepLength / (para * 2)
                    y = self.step(func, x, y, stepLength)
                else:
                    y = self.step(func, x, y, stepLength)
                x = x + stepLength

            stepLength = targetX - x
            y = self.step(func, x, y, stepLength)
            result_y.append(y)
        return result_y
