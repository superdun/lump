from RK4 import RK
def func(x,y):
	return -y
rk = RK(func)
print rk.implicitRK4(0,1,0.1,1,0.00000000000001)