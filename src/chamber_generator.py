import room_generator
import stairs_generator
import tile_handler

class chamber_generator:
  def __init__(self, top_level):

    tile_h = tile_handler.tile_handler(top_level)

    self.rg = room_generator.room_generator(tile_h) 
    self.sg = stairs_generator.stairs_generator(tile_h)
        
  # each chamber is in format of [ [pos_x, pos_y, pos_z] , [size_x, size_y, size_z] ]
  # pos_xyz specify xyz coordinates of the corner of a chamber wih smallest coordinates.
  # size is given in unites of tiles: 4x4x4
  # door list is just a list of xyz coordinates of doors
  def generate_chamber(self, scene, doors_list, chamber_list):
    #cg = self.rg.create_room("Floor_Flat", [])
    temp_doors = [(0,-7,0),(5,7,10)]
    bounds = [((0,0,0),(14,14,14))]
    shape = [((0,0,0), (13,  13,  9))]
    cg = self.sg.create_stairs("Floor_Flat",temp_doors,bounds,shape)
    return cg