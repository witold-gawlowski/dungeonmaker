import fbx_io
import chamber_generator
import utils
import fbx
import random

room_widths = [3, 3, 3, 5, 5, 5, 7, 7, 11]
room_heights = [2, 3, 3, 4, 4]
stair_widths = [5, 5, 7, 13]
stair_heights = [3, 7, 11, 13, 17]
level_bounds = [50, 50, 50]
room_number = 5

class Chamber ( object ):
  def __init__(self, **kwargs):
    self.__dict__.update( kwargs )

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance ):
    self.chamber_generator_instance = chamber_generator_instance
    self.map = {}
    self.chambers = []
   
  def are_colliding( self, chaber_A , chamber_B ):
    return "todo"

  # room in format [[pos_x, pos_y, pos_z], [size_x, size_y, size_z]]
  # all dimensions in tile units


  def make_random_chamber( self, is_room = True ):
    if is_room:
      dimensions = [room_widths, room_widths, room_heights]
    else:
      dimensions = [stair_widths, stair_widths, stair_heights]
    size = list (map( random.choice, dimensions ) )
    bounds = [ i - j for i, j in zip( level_bounds, size ) ]
    position = map ( lambda x: random.randint(*x), [[0, bounds[0]], [0, bounds[1]], [0, bounds[2]]] )
    return Chamber( position = list( position ), size = size, is_room = is_room )

  ''' inflates all the chambers, adds 
  the encountered chambers to the pairs of rooms candidating for door addition '''
  def grow_chambers( self ):
    return "todo"

  ''''''
  def create_and_link_chamber_to( self, chamber, is_room = True ):
    return "todo"

  def build_from_world_file():
    return "todo"

  def build_doors_between( room_A, room_B ):
    return "todo"

  def generate_world_data( self ):
    room = self.make_random_chamber()
    stairs = self.make_random_chamber( False )
    room.doors = [ (0, 1, 0) ]
    stairs.doors = [ (1, 1, 0), (1, stairs.size[1] - 1, 2) ]
    self.chambers.append( room )
    self.chambers.append( stairs )
    # add_random_doors( room )
    # self.rooms.append( starting_room )
    # previous_room = starting_room
    # for i in range( room_number ):
    #  new_room = make_random_room_at( doors )


  def build( self ):
    nodes = []
    for chamber_data in self.chambers:
      nodes.extend( self.chamber_generator_instance.generate_chamber( chamber_data ) )
    return nodes

  def generate( self ):
    # build_from_world_file()
    self.generate_world_data ()
    nodes = self.build()
    return nodes

    

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
