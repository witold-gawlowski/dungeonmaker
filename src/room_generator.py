

import math
import time
# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory


import tile_handler
import tile_util


class room_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler


  def create_room(self, new_scene, feature_name):
    start_time = time.time()
    print("Creating room ... ")
    tile_size = self.tile_handler.tile_size
    bounds = [((0,0,0), (14,  14,  14))]
    shape = [((0,0,0), (13,  13,  9)),
             ((0,0,0), (7, 7, 14))]

    #bounds = [((0,52,0), (60,  60,  10))]
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


    doors = [(28, 0, 0),
             (-28, 0, 0)]
    door_mask = self.makeDoorMask(doors)

    pillars = [((16,0,0),(1,1,9)),
               ((-16,0,0),(1,1,9)),
               ((0,16,0),(1,1,9)),
               ((0,-16,0),(1,1,9))]
    pillars = self.tile_handler.snap_room_center(pillars, tile_size)

    incoming = self.tile_handler.incoming["Wall_St_Top"]
    
    nodes = []

    pos = self.tile_handler.start_position_in_shape(shape, tile_size)
    pos = tile_util.xyz_round((pos[0], pos[1]-tile_size*0.5, 0))
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    
    # FLOOR =================================================
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, pillars, "Floor_2x2", True)
    
    # CEILING ==============================================
    # Sort the shape in order of tallest square to shortest square
    shape = sorted(shape, key = lambda tup: tup[1][2], reverse = True)
    self.makeCeiling(new_scene, edges, nodes, shape, pillars)
    

    # WALLS BASE =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_4x4x4", False) 

    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_L_4x4x4", False)

    # CEILING WALL TOP =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape, "Ceiling_Wall_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape + door_mask, "Ceiling_Wall_L_4x4x4", False)

    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, None, "Floor_Wall_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, door_mask, "Floor_Wall_L_4x4x4", False)


    # WALL FILL
    todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
    while len(todo):
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
      

    todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])
    while len(todo):
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_L_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])

    todo = self.tile_handler.create_todo(edges, nodes, ["Mid_Wall_End_1x4"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, door_mask, "Mid_Wall_4x4x4", True)

    # PILLAR BASE + TOP =================================================
    pillar_edges = {}
    pillar_nodes = []
    todo = []
    for pillar in pillars:
      (coords, size) = pillar
      todo.append(((coords[0],coords[1]-tile_size*0.5,coords[2]), 0, "Floor_Flat", False))

    tmp_todo = []
    tmp_todo += todo
    pillar_nodes = self.tile_handler.complete_todo(todo, pillar_edges, pillar_nodes, pillars, None, "Floor_Column_large_4x4x2", False) 
    pillar_nodes = self.tile_handler.complete_todo(tmp_todo, {}, pillar_nodes, pillars, None, "Floor_2x2", False) 

    for pillar in pillars:
      (coords, size) = pillar
      todo.append(((coords[0],coords[1]-tile_size*0.5,coords[2]+size[2]*tile_size), 0, "Ceiling_Flat", False))

    tmp_todo = []
    tmp_todo += todo
    pillar_nodes = self.tile_handler.complete_todo(todo, pillar_edges, pillar_nodes, pillars, None, "Ceiling_Column_large_4x4x2", False)

    # PILLAR FILL =================================================
    todo = self.tile_handler.create_todo(pillar_edges, pillar_nodes, ["Mid_Column_Large_Top"])
    pillar_nodes = self.tile_handler.complete_todo(todo, pillar_edges, pillar_nodes, pillars, None, "Mid_Column_large_4x4x4", True)

    nodes += pillar_nodes

    print("Room Generation complete with ", len(nodes), " tiles and took ", (time.time() - start_time), " seconds")

    return nodes



  def makeCeiling(self, new_scene, edges, nodes, shape, w_mask):
    tile_size = self.tile_handler.tile_size
    mask = [] + w_mask
    last_height = 0;
    
    for i in range(len(shape)):
      ceilingNodes = []
      square = shape[i]

      if last_height > square[1][2]: 
        (roomCenter, size) = mask[len(mask)-1]
        size = (size[0]+2,size[1]+2,size[2]) # Make space for walls
        mask[len(mask)-1] = ((roomCenter, size))

      pos = (0,0,0)
      angle = 0
      todo = []
      point = [0, 0]
      # Calculate for x then y
      for i in range(2):
        if square[1][i] % 2 == 0:
          point[i] = (square[0][i] - tile_size*0.5) - ((square[1][i]*0.5-1)*tile_size)
        else:
          point[i] = square[0][i]  - ((square[1][i]-1) * 0.5 * tile_size)

      # This loops over every cell in the shape and creates an unsatisfied edge to add to the todo list if the cell is not in mask range.
      # equivalent to  for(int x = point[0]; x < point[0]+square[1][0]*tile_size; x += tile_size)
      for x in range(int(point[0]), int(point[0]+square[1][0]*tile_size), int(tile_size)):
        for y in range(int(point[1]), int(point[1]+square[1][1]*tile_size), int(tile_size)):
          if not self.tile_handler.in_shape_range(mask, (x, y, square[1][2]), tile_size):
            pos = tile_util.xyz_round((x, y - tile_size * 0.5, tile_size * square[1][2]))
            todo.append((pos, angle, "Ceiling_Flat", False))


      ceilingNodes = self.tile_handler.complete_todo(todo, edges, ceilingNodes, [square], mask, "Ceiling_Floor_2x2", False)
      
      mask.append(square)
      last_height = square[1][2]

      nodes += ceilingNodes



  def makeDoorMask(self, doors):
    mask = []
    for door in doors:
      mask.append(((door[0],door[1],door[2]),(1,3,1)))

    mask = self.tile_handler.snap_room_center(mask, self.tile_handler.tile_size)
    return mask