import room_generator
import stairs_generator
import tile_handler

infty = 9999


def are_bottom_lvl( doors_list, chamber_min_z):
  for doors in doors_list:
    if doors[2] == chamber_min_z:
      return False
  return True

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


  def doors_to_world_position(self, door_list , chamber_position):
    for doors in door_list:
      new_doors = [ i + j for i, j in zip( doors, chamber_position ) ]
      doors = new_doors

  def generate_chamber(self, chamber):
    chamber_specs = [ chamber.position, [ i+j for i, j in zip( chamber.position, chamber.size) ] ]
    self.doors_to_world_position( chamber.doors, chamber.position )
    if are_bottom_lvl( chamber.doors, chamber.position[0] ):
      self.rg.create_room( chamber.doors, chamber_specs )
    elif len( chamber.doors ) > 1:
      self.sg.create_stairs( chamber.doors, chamber_specs )