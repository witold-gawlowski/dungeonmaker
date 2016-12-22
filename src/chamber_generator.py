import dungeon_generator
import stairs_generator
import componentsIO
import tile_handler

import fbx

class chamber_generator:
  def create_chamber(self):

    cIO = componentsIO.componentsIO()
    topLevel = cIO.read_components()

    tileH = tile_handler.tile_handler(topLevel)
    
    # Test generation
    tile_meshes = tileH.tile_meshes = {}
    for name in tileH.tiles:
      tile = tileH.tiles[name]
      tile_mesh = tile.GetNodeAttribute()
      tile_meshes[name] = tile_mesh.Clone(fbx.FbxObject.eDeepClone, None)
      tile_meshes[name].SetName(name)

    tile_size = 4;
    shape = [((2,-8,0), (4,4)),
             ((2,28,0), (20,15)),
             ((2,70,0), (8,8)),
             ((2,28,0), (24,6))]

    #shape = [((2,0,0), (20,1)),
    #         ((2,20,0), (20,1)),
    #         ((2,40,0), (20,1)),
    #         ((38,8,0), (2,4)),
    #         ((-34,28,0), (2,4))]

    #shape = [((0,0,0), (4,3))]
    shape = tileH.snap_room_center(shape, tile_size)

    pos = (0,-2,0)
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, "Flat_Floor", False)]
    num_tiles = 0

    nodes = []

    print("Making floor...")

    nodes = tileH.complete_todo(cIO.new_scene, todo, edges, nodes, shape, "Floor_2x2", True)

    print("Floor Complete!")

    
    for node in ceilingNodes:
      nodes.append(node)

    print("Total Nodes: ", len(nodes))
    # This takes all the nodes and sends them to the FXB output.
    for node in nodes:
      (tile_name, tile_pos, new_angle) = node
      tileH.make_node(new_scene, tile_name, tile_pos, new_angle)





    #rg = dungeon_generator.dungeon_generator(tileH)
    #rg.read_components()
    #rg.write_result()
    