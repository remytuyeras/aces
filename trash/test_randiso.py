import sys 
sys.path.insert(1,"./")
import pyaces as pyc
import numpy as np

intmod = 100
ri = pyc.RandIso(intmod,5)
u, invu = ri.generate(60)

print(u)
print(invu)

print(u @ invu % intmod) 
assert (u @ invu % intmod == np.identity(5)).all()

print(invu @ u % intmod) 
assert (invu @ u % intmod == np.identity(5)).all()
