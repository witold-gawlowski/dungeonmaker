
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
    door_B_pos = (15,30,0)
    door_B_pos = self.tile_handler.snap_to_edge(door_B_pos, grid_size)
    
    start_pos = self.tile_handler.snap_grid_center(door_A_pos,grid_size)
    end_pos = self.tile_handler.snap_grid_center(door_B_pos,grid_size)

    open = []
    closed = []
    current_pos = start_pos
    closed.append(current_pos)

    # get lowest f_cost 
    #current_pos = min(open, key=lambda L: L[1][2])
    
    #while current_pos is not end_pos:
    while not (current_pos[0] == end_pos[0] and current_pos[1] == end_pos[1]):
      self.tile_handler.get_surrounding_pos(open, current_pos, grid_size, start_pos, end_pos) 
   
      
      # Sorts by F_cost then by H_cost
      open = sorted(open, key=lambda L: (L[1][2],L[1][1]))

      current_pos = open[0][0]
      open.pop(0)
      closed.append(current_pos)
    
      
      
    #self.tile_handler.get_surrounding_pos(open, current_pos, grid_size, start_pos, end_pos) 

    for i in range(len(closed)):
      shape.append((closed[i],(1,1,0.25)))


    #grid_tiles = []
    #grid_tiles.append(check_tile)


    nodes = []
    pos = self.tile_handler.start_position_in_shape(shape, tile_size)
    pos = (pos[0], pos[1]-tile_size*0.5, 0)
    edges = {}
    angle = 0
    
    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    
    # FLOOR =================================================
    nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, shape, None, "Floor_2x2", True)
    
    
    
    
    
    
    
    
    
    
    
    # create an unsatisfied edge
    #todo = [(pos, angle, feature_name, False)]

    # DOORS ===============================================
    
    #todo = [(door_A_pos, angle,"Floor_Flat", False)]
    #nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, shape, None, "Doorway_narrow_02", False)
    
    #todo = [(door_B_pos, angle,"Floor_Flat", False)]
    #nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, shape, None, "Doorway_narrow_02", False)
    

    #nodes = []
    #pos = self.tile_handler.start_position_in_shape(shape, tile_size)
    #pos = (pos[0], pos[1]-tile_size*0.5, 0)
    #edges = {}
    #angle = 0

    # create an unsatisfied edge
    #todo = [(pos, angle, feature_name, False)]

    #
    
    # FLOOR =================================================
    #nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, shape, None, "Floor_2x2", True)

    # WALLS =================================================
    #todo = self.tile_handler.create_todo(edges, nodes,["Floor_Flat"])
    #nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Floor_Wall_4x4x4", False) 

    #todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    #nodes = self.tile_handler.complete_todo(new_scene, todo, edges, nodes, None, None, "Floor_Wall_L_4x4x4", False)


    print("Room Generation complete with ", len(nodes), " tiles")

    return nodes


    

