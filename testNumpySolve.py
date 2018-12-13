import numpy as np 
from numpy.linalg import solve

import numpy as np

"""
Circonferenza alfa : (x-2)^2 + (y-4)^2 = 4
Circonferenza beta : x^2 + (y-2)^2 =4
Circonferenza gamma : (x-3)^2 + (y-3)^2 = 4
"""

alfa = np.array([-2,-4,16])
beta = np.array([0,-2,0])
gamma = np.array([-3,-1,16])

eq=np.subtract(alfa,beta)
eq1=np.subtract(beta,gamma)

A = np.array([eq[0:2], eq1[0:2]])
b = np.array([eq[2], eq1[2]])

print A
print b
x = np.linalg.solve(A,b)
