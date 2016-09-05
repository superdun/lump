import time
def explicitlyRK4(f,x0,y0,h,e):
	x=x0
	y=y0
	while x+h<e:
		y = step(f,x,y,h)
		x= x+h
	h=e-x
	y = step(f,x,y,h)

		#time.sleep(0.5)
	print  y

def step(f,x,y,h):
	K1 = f(x,y)
	K2 = f(x+h/2,y+h*K1/2)
	K3 = f(x+h/2,y+h*K2/2)
	K4 = f(x+h,y+h*K3)
	return y + h*(K1+2*K2+2*K3+K4) /6
# def implicitRK4():
# class RK4(object):
# 	def __init__(self,):
def func(x,y):
	return -y

