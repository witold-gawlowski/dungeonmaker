import fbx_io
import chamber_generator
import utils
import fbx
import random

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance ):
    self.chamber_generator_instance = chamber_generator_instance
    self.map = {}
    self.rooms = []
    self.boundar
    self.room_widths = [3, 3, 3, 5, 5, 5, 7, 7, 11]
    self.room_heights = [2, 3, 3, 4, 4]
    self.stair_widths = [5, 5, 7, 13]
    self.stair_heights = [3, 7, 11, 13, 17]
    self.level_bounds = [50, 50, 50]
  
  def are_colliding( chaber_A , chamber_B ):
    return "todo"

  # room in format [[pos_x, pos_y, pos_z], [size_x, size_y, size_z]]
  # all dimensions in tile units

  def make_random_chamber( room = True ):
    if room :
      dimensions = [room_widths, room_widths, room_heights]
    else:
      dimensions = [stair_widths, stair_widths, stair_heights]
    size = map( random.choice, dimensions )
    bounds = [ a_i - b_i for a_i, b_i in zip( level_bounds, size ) ]
    position = map ( lambda x: random.randint(*x), [[0, bounds[0]], [0, bounds[1]], [0, bounds[2]]] )
    return ( position, size )
  
  def make_random_chamber_at( door, room = True ):
    return "todo"

  def add_random_doors( chamber, room = True ):
    chamber.unsatifsied_doors.append( doors )

  def generate( self, room_number ):
    starting_room = get_random_room()
    add_random_doors( room )
    self.rooms.append( starting_room )
    previous_room = starting_room
    for i in range( room_number ):
      new_room = make_random_room_at( doors )

    return result

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