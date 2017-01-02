import chamber_generator
import dungeon_generator
import fbx_io

if __name__ == '__main__':

  # Read input
  fbx_file_io = fbx_io.fbx_io()
  top_level = fbx_file_io.import_file("components8")

  # Create a scene for scene objects to be attached to
  scene = fbx_file_io.create_scene("FBX ascii")

  # Initialise rooms and stairs generators (to be used in the algorythm bellow)
  chamber_generator_instance = chamber_generator.chamber_generator(top_level)

  # Initialise the dungeon_generator
  dungeon_generator_instance = dungeon_generator.dungeon_generator(scene)

  # From what i undestand I'd be changing below line of code to:
  # nodes = dungeon_generator_instance.generate()

  # Algorithm to stitch rooms together
  # Each room is returned as an array of "nodes" (tile instances)
  # all these array's of nodes will be needed to write the fbx output
  nodes = chamber_generator_instance.generate_chamber(scene)

  # This takes all the nodes and sends them to the FXB output.
  for node in nodes:
    (tile_name, tile_pos, new_angle) = node
    fbx_file_io.make_node(scene, tile_name, tile_pos, new_angle)

  # Write result
  # Close fbx
  fbx_file_io.export_scene(scene)
  
  
