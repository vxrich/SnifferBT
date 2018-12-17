import numpy as np 
from numpy.linalg import det
import scipy as sp 


"""
Circonferenza alfa : (x-2)^2 + (y-4)^2 = 4
[1 0 -2]
[0 1 -4]
[-2 -4 16]
Circonferenza beta : x^2 + (y-2)^2 =4
[1 0 0]
[0 1 -2]
[0 -2 0]
Circonferenza gamma : (x-3)^2 + (y-2)^2 = 4
[1 0 -3]
[0 1 -2]
[-3 -2 9]
"""

alfa = np.array([-4,-8,16])
beta = np.array([0,-4,0])
gamma = np.array([-6,-4,9])

eq=np.subtract(alfa,beta)
eq1=np.subtract(beta,gamma)

A = np.array([eq[0:2], eq1[0:2]])
b = np.array([eq[2], eq1[2]])

print A
print b

x=np.linalg.solve(A,b)

#x,y = cramer(A,b)
print x
