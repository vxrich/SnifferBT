import numpy as np 
from numpy.linalg import det
import scipy as sp 


"""
Circonferenza alfa : (x-2)^2 + (y-4)^2 = 4
Circonferenza beta : x^2 + (y-2)^2 =4
Circonferenza gamma : (x-3)^2 + (y-2)^2 = 4
"""

def deter(A):

    return A[0][0]*A[1][1]-A[0][1]*A[1][0]

def cramer(A,b):
    det = deter(A)

    Ax = [b,A[1]]
    x = deter(Ax)/det

    Ay=[A[0],b]
    y = deter(Ay)/det

    return x,y

alfa = np.array([-4,-8,16])
beta = np.array([0,-4,0])
gamma = np.array([-6,-4,16])

eq=np.subtract(alfa,beta)
eq1=np.subtract(beta,gamma)

A = np.array([eq[0:2], eq1[0:2]])
b = np.array([eq[2], eq1[2]])

print A
print b

x=np.linalg.solve(A,b)

x,y = cramer(A,b)
print x,y
