import fbx

def print_node(root):
  print( root.GetName() )
  children = [root.GetChild(i) for i in range(root.GetChildCount())]
  for c in children:
    print_node(c)