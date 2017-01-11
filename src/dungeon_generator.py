import fbx_io
import chamber_generator
import utils
import fbx

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance, fbx_manager, scene, worldfile_name, mock_version = True ):
    self.mock_version = mock_version
    self.fbx_manager = fbx_manager
    self.chamber_generator_instance = chamber_generator_instance
    self.scene = scene
    self.worldfile_obj = fbx_manager.import_file( worldfile_name )
    self.components = []

  def copy_node_with_children( self, source , node_processor = lambda x: x):
    dest_node = fbx.FbxNode.Create( self.scene, source.GetName() )
    self.components.append( source.GetNodeAttribute().Clone(fbx.FbxObject.eDeepClone, None) )
    dest_node.SetNodeAttribute( self.components[-1] )
    dest_node.LclTranslation.Set(source.LclTranslation.Get())
    dest_node.LclRotation.Set(source.LclRotation.Get())

    node_processor( dest_node )

    for child in [source.GetChild(i) for i in range(source.GetChildCount())]:
      copied_child = self.copy_node_with_children( child, node_processor )
      dest_node.AddChild( copied_child )
    return dest_node

  def generate( self ):
    root = self.scene.GetRootNode()
    for node in self.worldfile_obj:
      if node.GetName().startswith ( "PrecreatedRoom" ):
        copied_node = self.copy_node_with_children ( node, utils.snap_to_parent_grid)
        root.AddChild(copied_node)

    if( self.mock_version ):
      return self.chamber_generator_instance.generate_chamber( self.scene , [], [])
    
    result_nodes = []        
    return result_nodes
