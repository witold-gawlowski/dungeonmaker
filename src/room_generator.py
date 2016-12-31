

import math
import random

# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory
import fbx

import tile_util
import tile_handler


class room_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler


  def create_room(self, new_scene, feature_name):
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
    shape = self.tile_handler.snap_room_center(shape, tile_size)

    pos = (0,-2,0)
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    num_tiles = 0

    nodes = []

    print("Making floor...")

    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, shape, "Floor_2x2", True)

    print("Floor Complete!")


    print("Making walls...")
    todo = self.tile_handler.create_todo(edges, nodes)
    print("Todo length: ", len(todo))

    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, "Floor_Wall_4x4x4", False)      
    print("Walls Complete!")

    print("Making Corners...")
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    print("Todo length: ", len(todo))
    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, "Floor_Wall_L_4x4x4", False)
    print("Corners Complete!")
    
    print("Making Ceiling...")
    pos = (0,-2,8)
    edges = {}
    angle = 0
    todo = [(pos, angle, "Ceiling_Flat", False)]
    num_tiles = 0
    ceilingNodes = []

    ceilingNodes = self.tile_handler.complete_todo(new_scene, todo, edges, ceilingNodes, shape, "Ceiling_Floor_2x2", True)
    
    #todo = self.tile_handler.create_todo(edges, ceilingNodes)
          
    print("Todo length: ", len(todo))

    #ceilingNodes = self.tile_handler.complete_todo(new_scene, todo, edges, ceilingNodes, None, "Ceiling_Wall_4x4x4", False)
    
    print("Ceiling Complete!")

    
    for node in ceilingNodes:
      nodes.append(node)

    return nodes


    





