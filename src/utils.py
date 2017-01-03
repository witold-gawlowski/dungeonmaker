import fbx

def print_node( root ):
  print( root.GetName() )
  children = [ root.GetChild(i) for i in range( root.GetChildCount() ) ]
  for c in children:
    print_node( c )

def snap_to_parent_grid( node ):
  node.LclTranslation.Set( fbx.FbxDouble3( 0, 0, 0 ) )

def scene_to_list( scene ):
  root = scene.GetRootNode()
  return [ root.GetChild( i ) for i in range( root.GetChildCount() ) ]