import sys 
sys.path.insert(1,"./")
from pyaces import *



pm = PreModulus(32,10,50000000)
print(pm.polyatom_num)
print(pm.sigma)
print(pm.sigma_fibers)


crs = CoprimeRootSystem(cardinal = len(pm.sigma_fibers[0]),
                        degree = 9,
                        rootrange = 0,
                        negative = True)

print(crs.rootrange,crs.negative,crs.allroots)
for root in crs.root_system:
  print(root)

poly_system = polynomial_system(crs.root_system)
for poly in poly_system:
  print(poly)

a = pm.cancel_out(poly_system)
b = np.array(poly_system)
print(a @ b)