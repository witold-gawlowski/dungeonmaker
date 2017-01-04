import fbx_io
import chamber_generator
import utils
import fbx

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance, fbx_manager, scene, worldfile_name, mock_version = False ):
    self.mock_version = mock_version
    self.fbx_manager = fbx_manager
    self.chamber_generator_instance = chamber_generator_instance
    self.scene = scene
    self.worldfile_obj = fbx_manager.import_file( worldfile_name , False)

  def make_node(self, node_name, pos, angle):
    dest_node = fbx.FbxNode.Create( scene, node_name )
    dest_node.SetNodeAttribute(self.fbx_manager.tile_meshes[node_name])
    dest_node.LclTranslation.Set(fbx.FbxDouble3(pos[0], pos[1], pos[2]))
    dest_node.LclRotation.Set(fbx.FbxDouble3(angle[0], angle[1], angle[2]))
    root = scene.GetRootNode()
    root.AddChild(dest_node)

  def generate( self ):
    if( self.mock_version ):
      return self.chamber_generator_instance.generate_chamber( scene )
    result_nodes = []
    for node in self.worldfile_obj:
      if node.GetName().startswith ( "Doors" ) or node.GetName().startswith ( "PrecreatedRoom" ):
        print (node.GetName())
        # utils.snap_to_parent_grid ( node )
        dest_node =  fbx.FbxNode.Create( self.scene, node.GetName() )
        self.component  = node.GetNodeAttribute().Clone(fbx.FbxObject.eDeepClone, None)
        
        dest_node.SetNodeAttribute(self.component)
        dest_node.LclTranslation.Set(node.LclTranslation.Get())
        dest_node.LclRotation.Set(node.LclRotation.Get())
        root = self.scene.GetRootNode()
        root.AddChild(dest_node)
            
    return result_nodes
