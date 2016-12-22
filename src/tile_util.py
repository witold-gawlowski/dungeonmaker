import math

# FbxDouble3 unpacker
def tolist(x):
  return [x[i] for i in range(3)]

# FbxDouble3 packer
def tovec3(x):
  return fbx.FbxDouble3(x[0], x[1], x[2], x[3])

def add3(x, y):
  return [x[i]+y[i] for i in range(3)]

def sub3(x, y):
  return [x[i]-y[i] for i in range(3)]

def neg3(x):
  return [-x[i] for i in range(3)]

def xy_round(x):
  return (round(x[0]), round(x[1]))

def xyz_round(x):
  return (round(x[0]), round(x[1]), round(x[2]))

def rotateZ(v, angle):
  sz = math.sin(angle * (3.14159/180))
  cz = math.cos(angle * (3.14159/180))
  return [
    cz * v[0] - sz * v[1],
    sz * v[0] + cz * v[1],
    v[2]
  ]

def lim360(x):
  x = x + 360 if x < 0 else x
  x = x - 360 if x >= 360 else x
  return round(x)
  