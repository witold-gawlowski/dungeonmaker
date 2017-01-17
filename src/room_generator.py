

import math
import time
# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory
import random

import tile_handler
import tile_util


class room_generator:
  def __init__(self, tile_handler):  
    self.tile_handler = tile_handler
    random.seed(time.time())
    self.room_params = {}
    with open("room_params.txt", "r") as ins:
      for line in ins:
        key_val_pair = line.split(':')
        self.room_params[key_val_pair[0]] = int(key_val_pair[1])

  def create_room(self, doors, bounds):
    start_time = time.time()
    print("Creating room ... ")

    tile_size = self.tile_handler.tile_size

    door_mask = self.makeDoorMask(doors)

    bounds = self.tile_handler.snap_room_center(bounds, tile_size)

    shape = self.make_room_dimentions(bounds, doors)
    shape = self.tile_handler.snap_room_center(shape, tile_size)

    pillars = self.make_pillars(shape)
    pillars = self.tile_handler.snap_room_center(pillars, tile_size)

    # Check that the input parameters have been succsefully converted to usable room values.
    if( not doors ):
      raise ValueError("Failure to create room, received ", len(doors)," doors. Room requires at minimum 1 door.")
    if( not shape ):
      raise ValueError("Failure to create a room shape from the given bounds: ", bounds)

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
    self.tile_handler.makeCeiling(edges, nodes, shape, None)
    

    # WALLS BASE =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_4x4x4", False) 

    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, door_mask, None, "Floor_Door_Way_4x4x4", False) 

    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Flat"], "Floor_2x2")
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_L_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_L_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_T_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_X_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, door_mask, "Floor_Wall_End_4x4x4", False)


    # WALL FILL
    heightA = shape[len(shape)-1][1][2]
    #heightB = shape[0][1][2]
    for i in range(heightA-2):
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, None, "Mid_Wall_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, None, "Mid_Wall_L_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_T_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, None, "Mid_Wall_T_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_X_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, None, "Mid_Wall_X_4x4x4", False)
      todo = self.tile_handler.create_todo(edges, nodes, ["Wall_End_Bottom"])
      nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, None, "Mid_Wall_End_4x4x4", False)

    # CEILING WALL TOP =================================================
    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape, "Ceiling_Wall_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"], "Ceiling_Floor_2x2")
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape, "Ceiling_Wall_L_4x4x4", False)
    todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Wall_End"])
    nodes = self.tile_handler.complete_todo(todo, edges, nodes, None, shape, "Ceiling_Wall_L_4x4x4", False)


    #todo = self.tile_handler.create_todo(edges, nodes, ["Wall_St_Bottom"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_4x4x4", False)
    #todo = self.tile_handler.create_todo(edges, nodes, ["Wall_L_Bottom"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_L_4x4x4", False)
    #todo = self.tile_handler.create_todo(edges, nodes, ["Wall_T_Bottom"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_T_4x4x4", False)
    #todo = self.tile_handler.create_todo(edges, nodes, ["Wall_X_Bottom"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_X_4x4x4", False)
    #todo = self.tile_handler.create_todo(edges, nodes, ["Wall_End_Bottom"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, bounds, None, "Mid_Wall_End_4x4x4", False)
    #ceiling_wall_edges = {}
    #todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, None, "Floor_Wall_4x4x4", False)
    #todo = self.tile_handler.create_todo(edges, nodes, ["Ceiling_Flat"], "Ceiling_Floor_2x2")
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, None, "Floor_Wall_L_4x4x4", False)
    #todo = self.tile_handler.create_todo(edges, nodes, ["Floor_Wall_End"])
    #nodes = self.tile_handler.complete_todo(todo, edges, nodes, shape, None, "Floor_Wall_L_4x4x4", False)


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

  def split_square(self, square, size_bounds):
    tile_size = self.tile_handler.tile_size
    (center, size) = square
    anchor = (center[0]-size[0]*tile_size*0.5,center[1]-size[1]*tile_size*0.5)
    randAxis = random.randrange(0, size[0]+size[1])
    axis = (0 if randAxis<size[0]  else 1)
    other = (0 if axis else 1)

    breakpoint = random.randrange(1, size[axis])

    sizeA = sizeB = centerA = centerB = (0,0,0)
    if axis:
      sizeA = (size[0], breakpoint,  random.randrange(2, size_bounds[2]+1, 2))
      sizeB = (size[0], size[1]-breakpoint, random.randrange(2, size_bounds[2]+1, 2))
      centerA = (center[0], anchor[1]+sizeA[1]*tile_size*0.5, center[2])
      centerB = (center[0], anchor[1]+(breakpoint*tile_size)+(sizeB[1]*tile_size*0.5), center[2])
    else:
      sizeA = (breakpoint, size[1], random.randrange(2, size_bounds[2]+1, 2))
      sizeB = (size[0]-breakpoint, size[1], random.randrange(2, size_bounds[2]+1, 2))
      centerA = (anchor[0]+sizeA[0]*tile_size*0.5, center[1], center[2])
      centerB = (anchor[0]+(breakpoint*tile_size)+(sizeB[0]*tile_size*0.5), center[1], center[2])
    squareA = (centerA, sizeA)
    squareB = (centerB, sizeB)
    
    room_grandness = (self.room_params["s-square-area"] if size_bounds[0]*size_bounds[1] < self.room_params["l-bounds-area"] else self.room_params["l-square-area"])

    child_squares = []
    if (squareA[1][0]*squareA[1][1] > room_grandness and squareA[1][0] >= 2 and squareA[1][1] >= 2):
      child_squares += self.split_square(squareA,size_bounds)
    else:
      child_squares.append(squareA)
    if (squareB[1][0]*squareB[1][1] > room_grandness and squareB[1][0] >= 2 and squareB[1][1] >= 2):
      child_squares += self.split_square(squareB,size_bounds)
    else:
      child_squares.append(squareB)
    
    return child_squares
  # END ============ split_square

  def make_room_dimentions(self, bounds, doors):  
    tile_size = self.tile_handler.tile_size
    (center, size) = bounds[0]
    floorspace = (center, (size[0]-2, size[1]-2, size[2]))
    (floorcenter, floorsize) = floorspace

    way_tiles = [] # Tiles directly infront of doors. (These tiles must be floor and must connect to eachother with a floor path)
    # Find the closest tile in the floor space to the door. 
    for door in doors:
      closestTile = (1,1)
      bestDist = 5000
      for x in range(int(floorcenter[0]-(tile_size*floorsize[0]*0.5)+(tile_size*0.5)), int(floorcenter[0]+(tile_size*floorsize[0]*0.5)+(tile_size*0.5)), tile_size):
        for y in range(int(floorcenter[1]-(tile_size*floorsize[1]*0.5)+(tile_size*0.5)), int(floorcenter[1]+(tile_size*floorsize[1]*0.5)+(tile_size*0.5)), tile_size):
          dx = x-door[0]
          dy = y-door[1]
          dist = math.sqrt(dx*dx + dy*dy)
          if dist < bestDist:
            bestDist = dist
            closestTile = (x,y)

      way_tiles.append(((closestTile[0],closestTile[1],floorcenter[2]),(1,1,1)))
    
    divfloor = [floorspace]
    # Divide the room into small squares
    if (floorspace[1][0] >= 2 and floorspace[1][1] >= 2):
      divfloor = self.split_square(floorspace, bounds[0][1])

    output = []
    for divide in divfloor:
      for doorway in way_tiles:
        if self.tile_handler.in_shape_range([divide], doorway[0], tile_size):
          output.append(divide)

    # get vector between doors.
    # Move along vector by 1 until shape reached
    # Every move get the shape that the point along the vector is. 
    # Is the shape in the outgoing
    # If not add it.
    for i in range(0,(len(way_tiles)-1),1):
      startpoint = way_tiles[i][0]
      endpoint = way_tiles[i+1][0]
      pos = (startpoint[0], startpoint[1], startpoint[2])
      vec = (endpoint[0] - startpoint[0], endpoint[1] - startpoint[1])
      length = math.sqrt(vec[0]*vec[0]+vec[1]*vec[1])
      if length == 0:
        newpath = self.tile_handler.get_shape_at_pos(divfloor, pos, tile_size)
        if newpath is not None:
          output.append(newpath)
          continue
        else:
          raise ValueError("Room does not allow a tile at location, ", pos)

      vec = (vec[0]/length, vec[1]/length) # normalise the vector
      

      while not self.tile_handler.in_shape_range([way_tiles[i+1]], pos, tile_size):
        pos = (pos[0] + vec[0], pos[1] + vec[1], startpoint[2])
        if(self.tile_handler.in_shape_range(output, pos, tile_size)):
          continue
        newpath = self.tile_handler.get_shape_at_pos(divfloor, pos, tile_size)
        if newpath is not None:
          output.append(newpath)

    # Set the heights of the squares
    #heightA = heightB = bounds[0][1][2]
    #if bounds[0][1][2] >= 4:
    #  heightA = int(bounds[0][1][2]*0.5)
    for i in range(len(output)):
      (center, size) = output[i]
      output[i] = (center, (size[0], size[1], bounds[0][1][2]))
      #if(heightA < size[2]):
      #  output[i] = (center, (size[0], size[1], heightB))
      #else:
      #  output[i] = (center, (size[0], size[1], heightA))
      

    #output += random.sample(divfloor, 3)
    return output
  # END ============ make_room_dimentions

  def make_pillars(self, shape):
    pillars = []
    for square in shape:
      (center, size) = square
      if size[2] > 4:
        if size[0] <= 1 or size[1] <= 1:
          break;
        pillars.append((center, (1,1,size[2])))
    return pillars
  # END ============ make_pillars

  def makeDoorMask(self, doors):
    mask = []
    for door in doors:
      mask.append(((door[0],door[1],door[2]),(1,1,1)))

    mask = self.tile_handler.snap_room_center(mask, self.tile_handler.tile_size)
    return mask
  # END ============ makeDoorMask