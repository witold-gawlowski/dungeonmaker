import room_generator
import stairs_generator
import tile_handler

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
  def generate_chamber(self, doors_list, chamber_list):
    cg = self.rg.create_room(doors_list, chamber_list)
    #cg = self.sg.create_stairs(doors_list, chamber_list)
    return cg