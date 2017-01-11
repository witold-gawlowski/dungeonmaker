
import math

# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory


import tile_handler


class stairs_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler


  def create_stairs(self, new_scene, feature_name):
    print("Creating room ... ")

    tile_size = 4;
   
    shape = []

    #shape = self.tile_handler.snap_room_center(shape, tile_size)

    grid_size = (4,4,1)

    door_A_pos = (0,0,0)
    door_A_pos = self.tile_handler.snap_to_edge(door_A_pos, grid_size)
    door_B_pos = (0,30,0)
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
      self.tile_handler.get_surrounding_pos(open, current_pos, grid_size, start_pos[0], end_pos[0]) 
   
      
      # Sorts by F_cost then by H_cost
      open = sorted(open, key=lambda L: (L[1][2],L[1][1]))



      current_pos = open[0]
      open.pop(0)
      closed.append(current_pos)
    
      
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


    

