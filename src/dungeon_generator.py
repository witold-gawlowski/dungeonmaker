import fbx_io
import chamber_generator
import utils
import fbx
import random
import itertools

room_widths = [3, 3, 3, 5, 5, 5, 7, 7, 11]
room_heights = [2, 3, 3, 4, 4]
stair_widths = [5, 5, 7, 13]
stair_heights = [3, 7, 11, 13, 17]
level_bounds = [50, 50, 50]
room_number = 5
room_chance  = [0.5]
room_attempts = 10

class Chamber ( object ):
  def __init__(self, **kwargs):
    self.__dict__.update( kwargs )

    
def random_chamber_size( is_room ):
  if is_room:
    dimensions = [room_widths, room_widths, room_heights]
  else:
    dimensions = [stair_widths, stair_widths, stair_heights]
  size = tuple (map( random.choice, dimensions ) )
  return size

def random_chamber( is_room = True ):
  size = random_chamber_size( is_room )
  bounds = [ i - j for i, j in zip( level_bounds, size ) ]
  position = map ( lambda x: random.randint( *x ), [[0, bounds[0]], [0, bounds[1]], [0, bounds[2]]] )
  return Chamber( position = tuple( position ), size = size, is_room = is_room )

def are_colliding( chamber_A , chamber_B ):
  if chamber_A.position > chamber_B.position:
    ( chamber_A, chamber_B ) = ( chamber_B, chamber_A )
  for i in 0, 1, 2:
    if chamber_B.position[ i ] > chamber_A.position[ i ] + chamber_A.size[ i ]:
      return False
  return True



def distance( chamber_A, chamber_B ):
  return sum( [ i - j for i, j in zip ( chamber_A.position, chamber_B.position ) ] )

def get_chambers_from_world_file():
  return "todo"

def doors_between( chamber_A, chaber_B ):
  return "todo"

def grow( chamber, direction ):
  return "todo"

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance ):
    self.chamber_generator_instance = chamber_generator_instance
    self.map = {}
    self.chambers = []

  # room in format [[pos_x, pos_y, pos_z], [size_x, size_y, size_z]]
  # all dimensions in tile units

  ''' inflates all the chambers, adds 
  the encountered chambers to the pairs of rooms candidating for door addition '''

  def generate_doors( self ):
    for position in itertools.product( [ range( level_bound[ i ] - 1 ) for i in range( 2 ) ] ):
      '''
      add a dictionary of chambers
      go over all level
      and check if two neighboring tiles 
      are not from different chambers but
      chambers shifted by 1 smalle by 2
      then add doors to those chambers
      '''

  def grow_chambers( self ):
    grown_last_iteration = True
    while grown_last_iteration:
      grown_last_iteration = False
      for chamber in self.chambers:
        for direction in -1, 1:
          for axis in 0, 1, 2:
            dir = (0, 0, 0)
            dir[axis] = direction
            grown = grow( chamber, dir )
            if not collides( grown ):
              chamber = grown
              grown_last_iteration = True
      

  def collides( chamber ):
    for other in self.chambers:
      if are_colliding( chamber, other ):
        return True
    return False

  def generate_world_data( self ):
    for i in range( room_attempts ):
      candidate = random_chamber( True if random.random() < room_chance else False )
      if ( collides ( candidate ) ):
        continue
      self.chambers.append( candidate ) 
      
      self.grow_chambers()

      self.add_doors()
  
  def build_from_world_file( self ):
    '''
    read csv and add chambers snapped from grid.
    also artists can add blocking boxes
    ez pz
    '''
    return "todo"
        
  def build( self ):
    nodes = []
    for chamber in self.chambers:
      nodes.extend( self.chamber_generator_instance.generate_chamber( chamber ) )
    return nodes

  def generate( self ):
    # self.build_from_world_file()
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
