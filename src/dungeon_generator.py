import fbx_io
import chamber_generator
import utils

class dungeon_generator(object):
  def __init__(self, chamber_generator_instance, mock_version = False):
    self.mock_version = mock_version
    self.fbx_manager = fbx_io.fbx_io()
    self.input_scene = self.fbx_manager.import_file("worldfile")
    self.chamber_generator_instance = chamber_generator_instance

  def snap_to_parents_grid(node):
    1
  
  def generate(self, scene):
    if(self.mock_version):
      return self.chamber_generator_instance.generate_chamber(scene)
    
    for node in self.input_scene:
      utils.print_node(node)

    return []
