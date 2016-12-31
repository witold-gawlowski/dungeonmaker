import room_generator
import stairs_generator

class chamber_generator:
  def create_chamber(self):
    rg = room_generator.room_generator()
    rg.read_components()
    rg.write_result()

    sg = stairs_generator.stairs_generator()
    sg.read_components()
    #sg.write_result()
    