import room_generator
import stairs_generator
import tile_handler

infty = 9999


def are_bottom_lvl( doors_list, chamber_min_z):
  for doors in doors_list:
    if doors[2] == chamber_min_z:
      return False
  return True

''' converting doors from relative tile to absolute tile coordinates. only integral values. '''
def convert_door_specs( door_list , chamber_position , tile_size ):
  result = []
  for door in door_list:
    x = chamber_position[0] * tile_size + tile_size * 0.5 + door[0] * tile_size
    y = chamber_position[1] * tile_size + tile_size * 0.5 + door[1] * tile_size
    new_door = (x, y, door[2])
    #new_door = tuple ( [ i * tile_size + (j * tile_size)+(tile_size*0.5) for i, j in zip( door, chamber_position ) ] 
    result.append( new_door )
  return result

def print_chamber_specs( specs ):
  print ( "position: {}, size: {}".format( specs[0], specs[1] ) )

def print_doors_specs( spec_list ):
  print ( "doors: " )
  for doors in spec_list:
    print ( doors )

''' converting to room/stairs coordinates '''
def convert_chamber_specs ( specs , tile_size ):
  new_position = (specs[0][0] * tile_size + specs[1][0] * tile_size * 0.5, specs[0][1] * tile_size + specs[1][1] * tile_size * 0.5, specs[0][2] * tile_size )
  return [ ( new_position, specs[1] ) ]

class chamber_generator:
  def __init__( self, top_level ):

    self.tile_h = tile_handler.tile_handler(top_level)

    self.rg = room_generator.room_generator(self.tile_h) 
    self.sg = stairs_generator.stairs_generator(self.tile_h)
  # dungeon_generator coordinates:
  # each chamber is in format of ( ( pos_x, pos_y, pos_z ) , ( size_x, size_y, size_z ) )
  # pos_xyz specify xyz tile coordinates of the corner of a chamber wih smallest coordinates.
  # size is given in tiles
  # doors are given in tile space

  # chamber_generator coordinates:
  # door list is just a list of xyz coordinates of doors
  # Example formats:   
  #  doors = [(40, 0, 0), (-10, 40, 0), (-40, 16, 0)]
  #  bounds = [((0,0,0), (21,21, 10))]
  #
  # generate_chamber is called by dungeon_generator in function "generate"

  def generate_chamber(self, chamber):
    # position as tile space position of smallest corner
    chamber_specs =  ( ( chamber.position , chamber.size ) )

    print (chamber_specs)
    print (chamber.doors)

    # converting from dungeon_generator specs to chamber_generator specs
    chamber_specs = convert_chamber_specs ( chamber_specs, self.tile_h.tile_size ) 
    doors_specs = convert_door_specs( chamber.doors, chamber.position , self.tile_h.tile_size )



    print_chamber_specs( *chamber_specs )
    print_doors_specs ( doors_specs )
    
    if are_bottom_lvl( doors_specs, chamber.position[0] ):
      result = self.rg.create_room( doors_specs, chamber_specs )
    elif len( doors_specs ) > 1:
      result = self.sg.create_stairwell( doors_specs, chamber_specs )
    
      ### Robs testing
    #doors = [(4,-16,0), (-4,20,8)]
    #bounds = [((0,0,0),(10,10,5))]
    #result = self.sg.create_stairwell(doors, bounds)

    return result


