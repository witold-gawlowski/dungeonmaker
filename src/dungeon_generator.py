import fbx_io
import chamber_generator

class dungeon_generator(object):
  def __init__(self, scene):
    fbx_manager = self.fbx_manager = fbx_io.fbx_io()
    input = self.input_scene = fbx_manager.import_file("worldfile")
    output = scene

  def snap_to_grid():
    for node in input:
      print( node.GetName() )