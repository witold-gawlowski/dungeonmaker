import fbx

def node_iterator( root ):
  print ( "yield : " + root.GetName() )
  yield root
  children = [ root.GetChild(i) for i in range( root.GetChildCount() ) ]
  for c in children:
    print ( "node_iterator child: " + c.GetName() )
    yield from node_iterator( c )

def snap_to_parent_grid( node ):
  # node.LclTranslation.Set( fbx.FbxDouble3( 0, 0, 0 ) )
  1

def scene_to_list( scene ):
  root = scene.GetRootNode()
  return [ root.GetChild( i ) for i in range( root.GetChildCount() ) ]