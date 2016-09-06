#龙格库塔法
##1. 参考资料：
http://wenku.baidu.com/view/7f62170d4a7302768e993990.html
https://zh.wikipedia.org/wiki/%E9%BE%99%E6%A0%BC%EF%BC%8D%E5%BA%93%E5%A1%94%E6%B3%95

##2.  作用
求微分方程解dy/dx=f(x,y)
##3.  方法：
####3.1 step，龙格库塔法的每一步计算方法
|参数名|解释|
|---------|-----------|---------|
|x0|初始x|
|y0|初始y|
|stepLength|初始步长|

####3.2 explicitRK4，显式龙格库塔，即固定步长：
###参数：
|参数名|解释|
|---------|-----------|---------|
|x0|初始x|
|y0|初始y|
|stepLength|初始步长|
|targetX|目标的x|


####3.3 implicitRK4 可变步长，隐式
###参数：
|参数名|解释|
|---------|-----------|---------|
|x0|初始x|
|y0|初始y|
|stepLength|初始步长|
|targetX|目标的x|
|accuracy|变步长的精确度|

##4. example:
``` python
from RK4 import RK
def func(x,y):
	return -y
rk = RK(func)
print rk.implicitRK4(0,1,0.1,1,0.00000000000001)
```