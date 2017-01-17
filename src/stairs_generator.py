
import math
import time
# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory
import random

import tile_handler
import tile_util

class stairs_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler

  def create_stairwell(self, doors, bounds):
    nodes = []
    start_time = time.time()
    print("Creating Stairwell ... ")

    tile_size = self.tile_handler.tile_size

    door_mask = self.makeDoorMask(doors)

    bounds = self.tile_handler.snap_room_center(bounds, tile_size)

    shape = self.make_room_dimentions(bounds, doors)
    shape = self.tile_handler.snap_room_center(shape, tile_size)

    nodes = []

    pos = self.tile_handler.start_position_in_shape(shape, tile_size)
    pos = tile_util.xyz_round((pos[0], pos[1]-tile_size*0.5, bounds[0][0][2]))
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, "Floor_Flat", False)]
    
    # FLOOR =================================================
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, None, "Floor_2x2", True)
    
    # CEILING ==============================================
    # Sort the shape in order of tallest square to shortest square
    shape = sorted(shape, key = lambda tup: tup[1][2], reverse = True)
    self.makeCeiling(edges, nodes, shape, None)
    
    # WALLS BASE =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_4x4x4", False) 

    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_L_4x4x4", False)

    # CREATE DOORS ==================================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, door_mask, None, "Floor_Door_Way_4x4x4", False) 

 

    # FILL SPACE ABOVE DOOR ==========================================================
    x_length = (shape[0][1][0]*2)-1
    y_length = (shape[0][1][1]*2)-1

    for door in doors:  
      if not door [2] == bounds[0][0][2]:
        rotation = 0
        if door[0] >= (bounds[0][0][0] + x_length):
          rotation = 270
        elif door[0] <= (bounds[0][0][0] - x_length):
          rotation = 90
        elif door[1] >= (bounds[0][0][1] + y_length):
          rotation = 0 
        elif door[1] <= (bounds[0][0][1] - y_length):
          rotation = 180
        
        nodes.append(("Floor_Door_Way_4x4x4",(door[0],door[1],door[2]),rotation))
        print(("Floor_Door_Way_4x4x4",(door[0],door[1],door[2]),rotation))
        relative_door = (door[2] - bounds[0][0][2])
        space_above_door = (bounds[0][1][2]-3) - (relative_door*0.25)
        for i in range(int(space_above_door)+1):
          nodes.append(("Mid_Wall_4x4x4",(door[0],door[1],door[2]+((i+1)*4)),rotation+90))
    

    # WALL FILL FROM BOTTOM
    heightA = shape[len(shape)-1][1][2]
    for i in range(heightA-2):
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, door_mask, "Mid_Wall_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, door_mask, "Mid_Wall_L_4x4x4", False)
    
    # CEILING WALL TOP =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape, "Ceiling_Wall_4x4x4", False)

    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape, "Ceiling_Wall_L_4x4x4", False)


    print("Stairs Shell complete with ", len(nodes), " tiles and took ", (time.time() - start_time), " seconds")

    self.create_stairs(nodes, doors, shape)

    print("Stairwell Generation complete with ", len(nodes), " tiles and took ", (time.time() - start_time), " seconds")
    return nodes

  def makeDoorMask(self, doors):
    mask = []
    for door in doors:
      mask.append(((door[0],door[1],door[2]),(1,1,0.25)))

    mask = self.tile_handler.snap_room_center(mask, self.tile_handler.tile_size)
    return mask
  # END ============ makeDoorMask

  def makeCeiling(self, edges, nodes, shape, w_mask):
    tile_size = self.tile_handler.tile_size
    mask = [] + ([] if w_mask is None else w_mask)
    last_height = 0;
    
    for i in range(len(shape)):
      ceilingNodes = []
      square = shape[i]

      if last_height > square[1][2]: 
        for j in range(len(mask)):
          (roomCenter, size) = mask[j]
          size = (size[0]+2,size[1]+2,size[2]) # Make space for walls
          mask[j] = ((roomCenter, size))

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
            pos = tile_util.xyz_round((x, y - tile_size * 0.5, square[0][2] + tile_size * square[1][2]))
            todo.append((pos, angle, "Ceiling_Flat", False))
             

      ceilingNodes = self.tile_handler.complete_todo(todo, edges, ceilingNodes, [square], mask, "Ceiling_Floor_2x2", False)
      
      mask.append(square)
      last_height = square[1][2]

      nodes += ceilingNodes
  # END ============ makeCeiling

  def make_room_dimentions(self, bounds, doors):  
    (center, size) = bounds[0]
    output = []
    output.append((center, (size[0]-2, size[1]-2, size[2])))
    return output
  # END ============ make_room_dimentions


  def create_stairs(self,nodes, doors, shape):
 
    print("Searching for the fastest path ... ")
    start_time = time.time()
    tile_size = 4;
   
    off_limits_shapes = [((0,0,0),(4,4,50))]

    in_limits_shapes = [((shape[0][0]),(shape[0][1][0]+4,shape[0][1][1]+4,shape[0][1][2]+4))]

    grid_size = (4,4,1)

    #oors[0] = self.tile_handler.grid_to_tile_space(doors[0],grid_size)
    #doors[1] = self.tile_handler.grid_to_tile_space(doors[1],grid_size)

    #doors[1] = self.tile_handler.snap_to_edge(doors[1],grid_size)

    #start_pos = (self.tile_handler.snap_grid_center(door_A_pos,grid_size), (0,0,0),(0,0,0))
    start_pos = ((doors[0][0],doors[0][1],doors[0][2]),(0,0,0),(0,0,0))
    #end_pos = (self.tile_handler.snap_grid_center(door_B_pos,grid_size), (0,0,0),(0,0,0))
    end_pos = ((doors[1][0],doors[1][1],doors[1][2]),(0,0,0),(0,0,0))
    
    half_tile = tile_size*0.5
    x_length = (shape[0][1][0]*half_tile)-half_tile
    y_length = (shape[0][1][1]*half_tile)-half_tile
    xy_wps = [(shape[0][0][0]-x_length,shape[0][0][1]+y_length),
              (shape[0][0][0]+x_length,shape[0][0][1]+y_length),
              (shape[0][0][0]+x_length,shape[0][0][1]-y_length),
              (shape[0][0][0]-x_length,shape[0][0][1]-y_length)]

    path_wps = []
    doors = sorted(doors, key=lambda L: (L[2]))

    for index in range(len(doors)-1): 
      path_wps.append((doors[index],(0,0,0),(0,0,0)))

      currentZ_counter = doors[index][2]
      wp_counter = 1
      isStairs = False
      while currentZ_counter+4 < doors[index+1][2]:

        if isStairs == True:
          currentZ_counter += 4
          wp_counter +=1
          isStairs = False
        elif isStairs == False:
          wp_counter += 2
          isStairs = True

      path_wps.append(((xy_wps[wp_counter%4][0],xy_wps[wp_counter%4][1],currentZ_counter),(0,0,0),(0,0,0)))
      #print(((xy_wps[wp_counter%4][0],xy_wps[wp_counter%4][1],currentZ_counter),(0,0,0),(0,0,0)))  
          
    path_wps.append((doors[len(doors)-1],(0,0,0),(0,0,0)))



    
    #path_wps.append(start_pos)
    


 
    #print(end_pos)

    #path_wps = sorted(path_wps, key=lambda L: (L[0][2]))
    

    collected_journey = []
    for index in range(len(path_wps)-1):
      collected_journey += self.create_path(path_wps[index],path_wps[index+1], grid_size,in_limits_shapes,off_limits_shapes)
      
    print("finished Collecting Journey")
    
    collected_journey.reverse()
    print("reversed Path")

    pre_pos = collected_journey[0]
    rotation = 0
    for index, cp in enumerate(collected_journey):
      # On Top
      if cp[0] < pre_pos[0]:
        rotation = 0
      # On Bottom
      if cp[0] > pre_pos[0]:
        rotation = 180
      # At Left
      if cp[1] > pre_pos[1]:
        rotation = 270
      # At Right
      if cp[1] < pre_pos[1]:
        rotation = 90

      if cp[2] - pre_pos[2] == 0:
        nodes.append(("Floor_2x2", cp, rotation))
      else:
        nodes.append(("Steps_01",(cp[0],cp[1],cp[2]-1), rotation)) 
      pre_pos = cp
       
        
    # Add doors To nodes
    #nodes.append(("Floor_Door_Way_4x4x4", doors[0], 0))
    #nodes.append(("Floor_Door_Way_4x4x4", (doors[1][0]-4,doors[1][1],doors[1][2]), 180))


    print("Doors Connected with", len(collected_journey), " tiles in a time of ", time.time() - start_time )
    return nodes

  #------- End Create Stairs ---------------------


  def create_path(self, start, end, grid_size, in_bounds, off_bounds):
    
    open = []
    closed = []

    current_pos = start
    closed.append(current_pos)

  

    # get lowest f_cost 
    #current_pos = min(open, key=lambda L: L[1][2])
    allow_upper_pos = True
    
    print("looking for path") 
    #while current_pos is not end_pos:
    while not (current_pos[0][0] == end[0][0] and current_pos[0][1] == end[0][1] and current_pos[0][2] == end[0][2]):
      print(current_pos[0],"current ", end[0], "end ") 
      #print = current_pos[0] +end_pos[
      self.tile_handler.get_surrounding_pos(open, closed, current_pos, grid_size, start[0], end[0],in_bounds,off_bounds,allow_upper_pos) 
   
      
      # Sorts by F_cost then by H_cost
      # open = sorted(open, key=lambda L: (L[1][2],L[1][1]))

      open = sorted(open, key=lambda L: (L[1][1],L[1][2]))

      if (current_pos[0][2] - open[0][0][2]) == 0:
        allow_upper_pos = True
      else:
        allow_upper_pos = False

      current_pos = open[0]
      
      open.pop(0)
      closed.append(current_pos)
      #print (current_pos)
    
      
    print("Path Found ... Building In Progress")

    choosen_path = []

    while not (current_pos[0][0] == start[0][0] and current_pos[0][1] == start[0][1] and current_pos[0][2] == start[0][2]):
      for j in closed:
        if current_pos[2] == j[0]:
          #print("Appending CP: ", j[0])
          choosen_path.append(j[0])
          current_pos = j     

    return choosen_path