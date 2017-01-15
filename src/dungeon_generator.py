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
room_chance  = 0.5
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
  return Chamber( position = tuple( position ), size = size, is_room = is_room, doors = [])


def are_colliding( chamber_A , chamber_B ):
  a = chamber_A.position
  A = map( sum , zip( a, chamber_A.size ) ) 
  b = chamber_B.position
  B = map( sum , zip( b, chamber_B.size ) ) 
  overlap = lambda x, y : x[0] <= y[1] and x[1] >= y[0]
  blend = zip( zip( a, A ), zip( b, B ) ) 
  os = lambda x: overlap( *x )
  return all( map( os, blend ) )


def tokyo_distance( chamber_A, chamber_B ):
  return sum( [ i - j for i, j in zip ( chamber_A.position, chamber_B.position ) ] )

def get_chambers_from_world_file():
  return "todo"

def grow( chamber, direction ):
  if direction < (0, 0, 0):
    chamber.position = tuple( map( sum, zip( chamber.position, direction ) ) )
  d =  zip( direction, direction ) 
  direction2 = tuple( map( lambda x: x*x, direction ) )
  s = chamber.size
  tt = list( zip( chamber.size, direction2 ) )
  chamber.size = tuple( map( sum, tt ) )
  return chamber

class dungeon_generator(object):
  def __init__( self, chamber_generator_instance ):
    self.chamber_generator_instance = chamber_generator_instance
    self.map = {}
    self.chambers = []
    self.door_slots = {}
    self.chamber_connections = []

  # room in format [[pos_x, pos_y, pos_z], [size_x, size_y, size_z]]
  # all dimensions in tile units

  def get_door_slots( self, chamber ):
    size = chamber.size
    pos = chamber.position
    rangeX = ( pos[0] + 1, pos[0] + size[0] - 1 )
    rangeY = ( pos[1] + 1, pos[1] + size[1] - 1 )
    rangeZ = ( pos[2], pos[2] + size[2] - 1 )
    wallX1 = [ ( i, pos[1], j ) for i in range( * rangeX ) for j in range( *rangeZ )  ]
    wallX2 =[ ( i, pos[1] + size[1] - 1, j ) for i in range( * rangeX ) for j in range( *rangeZ ) ]
    wallY1 =[ ( pos[0], i, j ) for i in range( * rangeY ) for j in range( *rangeZ )  ]
    wallY2 = [ ( pos[0] + size[0] - 1, i, j ) for i in range( * rangeY ) for j in range( *rangeZ ) ]
    return wallX1 +  wallX2 + wallY1 + wallY2    

  def grow_chambers( self ):
    grown_last_iteration = True
    while grown_last_iteration:
      grown_last_iteration = False
      for chamber in self.chambers:
        for direction in -1, 1:
          for axis in 0, 1, 2:
            ''' don't grow up! '''
            if axis == 2 and direction == 1:
              break
            dir = [0, 0, 0]
            dir[axis] = direction
            grown = grow( chamber, tuple( dir ) )
            if not self.collides( grown ):
              chamber = grown
              grown_last_iteration = True
      

  def collides( self, chamber ):
    for other in self.chambers:
      if are_colliding( chamber, other ):
        return True
    return False

  def pull_down( self, pos, new_pos ):
    ''' move the door as low as possible 
    but within the rooms they are currently in '''
    return ( pos, new_pos )

  def add_doors( self ):
    for chamber in self.chambers:
      slots = self.get_door_slots ( chamber )
      pairs = itertools.product( slots, [chamber] )
      self.door_slots.update( pairs )
     
    for pos, chamber in self.door_slots.items():
      for d in [(-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0)]:
        new_pos = map( sum, zip( d, pos ) )
        neighbour = self.door_slots.get( new_pos )
        if neighbour and neighbour is not chamber:
          if ( neighbour, chamber ) not in self.chamber_connections:
            ( pos, new_pos ) = self.pull_down( pos, new_pos )
            chamber.doors.append( pos )
            neighbour.doors.append( new_pos )
            self.chamber_connections.append( ( chamber, neighbour ) )
            self.chamber_connections.append( ( neighbour, chamber ) )

  def generate_world_data( self ):
    for i in range( room_attempts ):
      candidate = random_chamber( True if random.random() < room_chance else False )
      if ( self.collides ( candidate ) ):
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
