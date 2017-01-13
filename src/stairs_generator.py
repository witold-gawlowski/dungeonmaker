
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
    start_time = time.time()
    tile_size = 4;
   
    shape = []

    #shape = self.tile_handler.snap_room_center(shape, tile_size)

    off_limits_shapes = [((6,6,0),(4,10,10))]

    grid_size = (4,4,1)

    door_A_pos = (0,0,0)
    door_A_pos = self.tile_handler.snap_to_edge(door_A_pos, grid_size)
    door_B_pos = (30,30,10)
    door_B_pos = self.tile_handler.snap_to_edge(door_B_pos, grid_size)
    

    #start_pos = (self.tile_handler.snap_grid_center(door_A_pos,grid_size), (0,0,0),(0,0,0))
    start_pos = ((door_A_pos[0],door_A_pos[1]+4,door_A_pos[2]),(0,0,0),(0,0,0))
    #end_pos = (self.tile_handler.snap_grid_center(door_B_pos,grid_size), (0,0,0),(0,0,0))
    end_pos = ((door_B_pos[0],door_B_pos[1]-4,door_B_pos[2]),(0,0,0),(0,0,0))

    open = []
    closed = []
    
    current_pos = start_pos
    closed.append(current_pos)

    # get lowest f_cost 
    #current_pos = min(open, key=lambda L: L[1][2])
    allow_upper_pos = True
    #while current_pos is not end_pos:
    while not (current_pos[0][0] == end_pos[0][0] and current_pos[0][1] == end_pos[0][1] and current_pos[0][2] == end_pos[0][2]):
      #print = current_pos[0] +end_pos[
      self.tile_handler.get_surrounding_pos(open, closed, current_pos, grid_size, start_pos[0], end_pos[0],off_limits_shapes,allow_upper_pos) 
   
      
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
    
      
    print("Path Found ... Drawing now Master")

    choosen_path = []

    while not (current_pos[0][0] == start_pos[0][0] and current_pos[0][1] == start_pos[0][1] and current_pos[0][2] == start_pos[0][2]):
      for j in closed:
        if current_pos[2] == j[0]:
          choosen_path.append(j[0])
          current_pos = j     

    for i in range(len(closed)):
      shape.append((closed[i],(1,1,0.25)))



    # Add the tiles to the list of nodes 
    ######### check the next tile to see if it is higher or same height as current
    choosen_path.reverse()

    nodes = []
    pre_pos = choosen_path[0]
    rotation = 0
    for index, cp in enumerate(choosen_path):
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
    nodes.append(("Floor_Door_Way_4x4x4", door_A_pos, 0))
    nodes.append(("Floor_Door_Way_4x4x4", door_B_pos, 180))


    print("Stairs Generation complete with ", len(nodes), " tiles")
    print(time.time() - start_time)
    return nodes

  #------- End Create Stairs ---------------------