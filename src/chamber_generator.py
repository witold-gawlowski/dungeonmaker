import room_generator
import stairs_generator
import tile_handler

infty = 9999


def are_bottom_lvl( doors_list, chamber_min_z):
  for doors in doors_list:
    if doors[2] == chamber_min_z:
      return False
  return True

def doors_to_world_position( door_list , chamber_position ):
  result = []
  for doors in door_list:
    new_doors = tuple ( [ i + j for i, j in zip( doors, chamber_position ) ] )
    result.append( new_doors )
  return result

class chamber_generator:
  def __init__(self, top_level):

    tile_h = tile_handler.tile_handler(top_level)

    self.rg = room_generator.room_generator(tile_h) 
    self.sg = stairs_generator.stairs_generator(tile_h)
        
  # each chamber is in format of ( (pos_x, pos_y, pos_z) , (size_x, size_y, size_z) )
  # pos_xyz specify xyz coordinates of the corner of a chamber wih smallest coordinates.
  # size is given in unites of tiles: 4x4x4
  # door list is just a list of xyz coordinates of doors
  # Example formats:   
  #  doors = [(40, 0, 0), (-10, 40, 0), (-40, 16, 0)]
  #  bounds = [((0,0,0), (21,21, 10))]
  #
  # generate_chamber is called by dungeon_generator in function "generate"

  def generate_chamber(self, chamber):
    chamber_position =  tuple ( [ i + j / 2 for i, j in zip( chamber.position, chamber.size) ] )
    chamber_specs = [ ( chamber_position , tuple (chamber.size ) ) ]
    doors_wrld = doors_to_world_position( chamber.doors, chamber.position )
    print ('doors {} '.format(doors_wrld) )

    if are_bottom_lvl( doors_wrld, chamber.position[0] ):
      return self.rg.create_room( doors_wrld, chamber_specs )
    elif len( doors_wrld ) > 1:
      return self.sg.create_stairs( doors_wrld, chamber_specs )