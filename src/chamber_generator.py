import room_generator
import stairs_generator
import tile_handler

class chamber_generator:
  def __init__(self, top_level):

    tile_h = tile_handler.tile_handler(top_level)

    self.rg = room_generator.room_generator(tile_h) 
    self.sg = stairs_generator.stairs_generator(tile_h)
        
  
  def generate_chamber(self, scene):
    cg = self.rg.create_room(scene, "Floor_Flat")
    # cg = self.sg.create_stairs(scene,"Floor_Flat")
    return cg