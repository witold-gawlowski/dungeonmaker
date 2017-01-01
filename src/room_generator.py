

import math

# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory


import tile_handler
import tile_util


class room_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler


  def create_room(self, new_scene, feature_name):
    print("Creating room ... ")

    tile_size = self.tile_handler.tile_size
    shape = [((0,0,0), (6,  10,  9)),
             ((0,0,0), (10, 6, 9))]

    #shape = [((0,  0,  0), (16,  40,  3)),
    #         ((0,  8,  0), (10,  36,  8)),
    #         ((0,  72,  0), (30,  8,  3)),
    #         ((0,  72,  0), (24,  4,  8)),
    #         ((0,  72,  0), (6,  4,  10)),
    #         ((0,  104,  0), (10,  8,  3)),
    #         ((0,  96,  0), (6,  8,  8))]

    #shape = [((2,0,0), (20,1)),
    #         ((2,20,0), (20,1)),
    #         ((2,40,0), (20,1)),
    #         ((38,8,0), (2,4)),
    #         ((-34,28,0), (2,4))]

    #shape = [((0,0,0), (4,3))]
    shape = self.tile_handler.snap_room_center(shape, tile_size)

    incoming = self.tile_handler.incoming["Ceiling_Flat"]
    
    nodes = []

    pos = self.tile_handler.start_position_in_shape(shape, tile_size)
    pos = (pos[0], pos[1]-tile_size*0.5, 0)
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    
    # FLOOR =================================================
    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, shape, None, "Floor_2x2", True)
    
    # CEILING ==============================================
    # Sort the shape in order of tallest square to shortest square
    shape = sorted(shape, key = lambda tup: tup[1][2], reverse = True)
    self.makeCeiling(new_scene, edges, nodes, shape)
    

    # WALLS =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"])
    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Floor_Wall_4x4x4", False) 

    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Floor_Wall_L_4x4x4", False)

    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"])
    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Ceiling_Wall_4x4x4", False)

    shape = sorted(shape, key = lambda tup: tup[1][2], reverse = False)
    for i in range(shape[0][1][2]-2):
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
      nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Mid_Wall_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])
      nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Mid_Wall_L_4x4x4", False)


    print("Room Generation complete with ", len(nodes), " tiles")

    return nodes



  def makeCeiling(self, new_scene, edges, nodes, shape):
    tile_size = self.tile_handler.tile_size
    mask = []
    last_height = 0;
    
    for i in range(len(shape)):
      ceilingNodes = []
      square = shape[i]

      if last_height > square[1][2]: 
        (roomCenter, size) = mask[len(mask)-1]
        size = (size[0]+2,size[1]+2,size[2]) # Make space for walls
        mask[len(mask)-1] = ((roomCenter, size))

      pos = self.tile_handler.start_position_in_shape([square], tile_size)
      pos = (pos[0], pos[1] - tile_size * 0.5, tile_size * square[1][2])
      angle = 0
      todo = [(pos, angle, "Ceiling_Flat", False)]

      ceilingNodes = self.tile_handler.complete_todo(new_scene, todo, edges, ceilingNodes, [square], mask, "Ceiling_Floor_2x2", True)
      
      mask.append(square)
      last_height = square[1][2]

      nodes += ceilingNodes