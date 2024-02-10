# applies algebraic operation (specified on indices) to the array
def read_operations(alg,instruction,array,level=0):
  # print(level,instruction)
  if all([not(a in instruction) for a in ["+","*","(",")"," "] ]):
    # print("cal",array[int(instruction)])
    return array[int(instruction)]
  else:
    output = {}
    parser = level
    inst = instruction.replace(" ","")
    for i,s in enumerate(inst):
      if s == "+":
        output[i] = [s,parser]
      elif s == "(":
        parser +=1
      elif s == ")":
        parser -=1
    pos = [[i,s] for i,[s,p] in output.items() if p == level]
    # print(pos)
    if pos == []:
      output = {}
      parser = level
      inst = instruction.replace(" ","")
      for i,s in enumerate(inst):
        if s == "*":
          output[i] = [s,parser]
        elif s == "(":
          parser +=1
        elif s == ")":
          parser -=1
      pos = [[i,s] for i,[s,p] in output.items() if p == level]
      # print(pos)
      if pos == []:
        return read_operations(alg,inst[1:-1],array,level=level+1)
      else:
        index, symbol = pos[0]
        if symbol == "*":
          return alg.mult(read_operations(alg,inst[:index],array,level=level),read_operations(alg,inst[index+1:],array,level=level))
    else:
      index, symbol = pos[0]
      if symbol == "+":
        return alg.add(read_operations(alg,inst[:index],array,level=level),read_operations(alg,inst[index+1:],array,level=level))


class Algebra(object):

  @staticmethod
  def add(a,b):
    return a+b
  
  @staticmethod
  def mult(a,b):
    return a*b

  def compile(self,instruction):
    return lambda a: read_operations(self,instruction,a) 
