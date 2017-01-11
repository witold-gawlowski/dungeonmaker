
import math
import time
# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory


import tile_handler
import tile_util

class stairs_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler


  def create_stairs(self, new_scene, feature_name):
    print("Finding Path ... ")

    tile_size = 4;
   
    shape = []

    #shape = self.tile_handler.snap_room_center(shape, tile_size)

    grid_size = (4,4,1)

    door_A_pos = (0,0,0)
    door_A_pos = self.tile_handler.snap_to_edge(door_A_pos, grid_size)
    door_B_pos = (6,6,0)
    door_B_pos = self.tile_handler.snap_to_edge(door_B_pos, grid_size)
    

    start_pos = (self.tile_handler.snap_grid_center(door_A_pos,grid_size), (0,0,0),(0,0,0))
    end_pos = (self.tile_handler.snap_grid_center(door_B_pos,grid_size), (0,0,0),(0,0,0))

    open = []
    closed = []
    
    current_pos = start_pos
    closed.append(current_pos)

    # get lowest f_cost 
    #current_pos = min(open, key=lambda L: L[1][2])
    
    #while current_pos is not end_pos:
    while not (current_pos[0][0] == end_pos[0][0] and current_pos[0][1] == end_pos[0][1]):
      #print = current_pos[0] +end_pos[
      self.tile_handler.get_surrounding_pos(open, closed, current_pos, grid_size, start_pos[0], end_pos[0]) 
   
      
      # Sorts by F_cost then by H_cost
      # open = sorted(open, key=lambda L: (L[1][2],L[1][1]))
      print("Before")
      for o in open:
        print(o)
      open = sorted(open, key=lambda L: (L[1][2],L[1][1]))

      print("After")
      for o in open:
        print(o)


      current_pos = open[0]
      open.pop(0)
      closed.append(current_pos)
      #print (start_pos[0] + current_pos[0] + end_pos[0])
    
      
    print("Path Found ... Drawing now Master")

    choosen_path = []

    while not (current_pos[0][0] == start_pos[0][0] and current_pos[0][1] == start_pos[0][1]):
      for j in closed:
        if current_pos[2] == j[0]:
          choosen_path.append(j[0])
          current_pos = j     

    for i in range(len(closed)):
      shape.append((closed[i],(1,1,0.25)))



    # Add the tiles to the list of nodes 
    ######### check the next tile to see if it is higher or same height as current
    nodes = []
    for cp in choosen_path:
      nodes.append(("Floor_2x2", cp, 0))
        
   

    print("Room Generation complete with ", len(nodes), " tiles")

    return nodes

  #------- End Create Stairs ---------------------

  def create_room(self, new_scene, feature_name):
    start_time = time.time()
    print("Creating room ... ")
    tile_size = self.tile_handler.tile_size
    bounds = [((0,0,0), (10,  10, 20))]
   
    shape = [((0,0,0), (9, 9,  19))]

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


    doors = [(20, 0, 0),
             (-20, 0, 0)]
    door_mask = self.makeDoorMask(doors)

 
    incoming = self.tile_handler.incoming["Wall_St_Top"]
    
    nodes = []

    pos = self.tile_handler.start_position_in_shape(shape, tile_size)
    pos = tile_util.xyz_round((pos[0], pos[1]-tile_size*0.5, 0))
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    
    # FLOOR =================================================
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, [], "Floor_2x2", True)
    
    # CEILING ==============================================
    # Sort the shape in order of tallest square to shortest square
    shape = sorted(shape, key = lambda tup: tup[1][2], reverse = True)
    self.makeCeiling(new_scene, edges, nodes, shape, [])
    

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
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, door_mask, "Mid_Wall_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
      

    todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])
    while len(todo):
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, door_mask, "Mid_Wall_L_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])

    todo = self.tile_handler.create_todo(edges, nodes, ["Mid_Wall_End_1x4"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, door_mask, "Mid_Wall_4x4x4", True)

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