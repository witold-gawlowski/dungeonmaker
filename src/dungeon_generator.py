import fbx_io
import chamber_generator
import utils
import fbx
import random

room_widths = [3, 3, 3, 5, 5, 5, 7, 7, 11]
room_heights = [2, 3, 3, 4, 4]
stair_widths = [5, 5, 7, 13]
stair_heights = [3, 7, 11, 13, 17]
level_bounds = [15, 15, 15]
room_number = 5

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance ):
    self.chamber_generator_instance = chamber_generator_instance
    self.map = {}
    self.rooms = []
   
  def are_colliding( self, chaber_A , chamber_B ):
    return "todo"

  # room in format [[pos_x, pos_y, pos_z], [size_x, size_y, size_z]]
  # all dimensions in tile units

  def make_random_chamber( self, room = True ):
    if room:
      dimensions = [room_widths, room_widths, room_heights]
    else:
      dimensions = [stair_widths, stair_widths, stair_heights]
    size = list (map( random.choice, dimensions ) )
    bounds = [ i - j for i, j in zip( level_bounds, size ) ]
    position = map ( lambda x: random.randint(*x), [[0, bounds[0]], [0, bounds[1]], [0, bounds[2]]] )
    return ( position, size )
  
  def make_random_chamber_at(self, doors, room = True ):
    return "todo"

  def add_random_doors(self, chamber, room = True ):
    chamber.unsatifsied_doors.append( doors )

  def generate( self ):
    starting_room = self.make_random_chamber()

    #add_random_doors( room )
    #self.rooms.append( starting_room )
    #previous_room = starting_room
    #for i in range( room_number ):
    #  new_room = make_random_room_at( doors )

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