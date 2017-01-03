import fbx_io
import chamber_generator
import utils

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance, fbx_manager, mock_version = False ):
    self.mock_version = mock_version
    self.fbx_manager = fbx_manager
    self.chamber_generator_instance = chamber_generator_instance

  def generate( self, scene ):
    if( self.mock_version ):
      return self.chamber_generator_instance.generate_chamber( scene )

    result_nodes = []
    
    print ( "snap and add to result_scene" )
    for node_name, node in self.fbx_manager.tiles.items():
      print ( "node_name: " + node_name )
      if node_name.startswith ( "PrecreatedChamber" ):
        doors = [ node.GetChild ( i ) for i in range ( node.GetChildCount () ) ]
        for d in doors:
          utils.snap_to_parent_grid ( d )
          print ( d.GetName() )
          result_nodes.append ( ( d.GetName(),
                               d.LclTranslation.Get(),
                               d.LclRotation.Get() ) )
        utils.snap_to_parent_grid ( node )
        print ( node.GetName() )
        result_nodes.append ( ( node.GetName(),
                               node.LclTranslation.Get(),
                               node.LclRotation.Get() ) ) 
    return result_nodes
