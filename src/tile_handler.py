
import math
import re
# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory
import fbx
import tile_util

class tile_handler:
  def __init__(self, top_level):  
    self.whitelist = {}
    self.whitelist["step_up"] = ["step_down"]
    self.whitelist["step_down"] = ["step_up"]
    self.whitelist["Ceiling_Flat"] = ["Floor_Flat"]
    self.whitelist["Floor_Flat"] = ["Ceiling_Flat"]
    self.whitelist["Wall_St_Bottom"] = ["Wall_St_Top"]
    self.whitelist["Wall_St_Top"] = ["Wall_St_Bottom"]
    self.whitelist["Wall_L_Bottom"] = ["Wall_L_Top"]
    self.whitelist["Wall_L_Top"] = ["Wall_L_Bottom"]
    self.whitelist["Mid_Column_Large_Bottom"] = ["Mid_Column_Large_Top"]
    self.whitelist["Mid_Column_Large_Top"] = ["Mid_Column_Large_Bottom"]

    self.blacklist = {}
    self.blacklist["step_up"] = ["step_up"]
    self.blacklist["step_down"] = ["step_down"]
    #self.blacklist["Wall_St_Bottom"] = ["Wall_St_Bottom"]
    #self.blacklist["Wall_St_Top"] = ["Wall_St_Top"]
    #self.blacklist["Wall_L_Bottom"] = ["Wall_L_Bottom"]
    #self.blacklist["Wall_L_Top"] = ["Wall_L_Top"]

    self.tile_size = 4

    # child nodes matching this pattern are feature markup
    feature_pattern = re.compile('(\<|\>)([^.]+)(\..*)?')

    incoming = self.incoming = {}
    outgoing = self.outgoing = {}
    tiles = self.tiles = {}

    # find the tiles in the file with at least one child (the connectors)
    for node in top_level:
      if node.GetChildCount():
        # for each tile, check the names of the connectors
        tiles[node.GetName()] = node;
        connectors = [node.GetChild(i) for i in range(node.GetChildCount())]
        tile_name = node.GetName()
        #print("%s has %d children" % (tile_name, node.GetChildCount()))
        for c in connectors:
          conn_name = c.GetName();
          # use a regular expression to match the connector name
          # and discard any trailing numbers
          match = feature_pattern.match(conn_name)
          if match:
            direction = match.group(1)
            feature_name = match.group(2)
            #print("  %s %s %s" % (tile_name, direction, feature_name))
            trans = c.LclTranslation.Get()
            rot = c.LclRotation.Get()
            result = (feature_name, tile_name, trans, rot)

            if direction == '>':
              # outgoing tile indexed by tile_name
              idx = tile_name
              dict = outgoing
            else:
              # incoming tile indexed by feature name
              idx = feature_name
              dict = incoming
            if not idx in dict:
              dict[idx] = []
            dict[idx].append(result)


  def is_in_whitelist(self, tile_name_1, tile_name_2):
    if tile_name_1 in self.whitelist:
      good_tiles = self.whitelist[tile_name_1]
      for valid_tile in good_tiles:
        if valid_tile == tile_name_2:
          return True
    return False
  ## ======== END is_in_whitelist

  def is_in_blacklist(self, tile_name_1, tile_name_2):
    if tile_name_1 in self.blacklist:
      bad_tiles = self.blacklist[tile_name_1]
      for invalid_tile in bad_tiles:
        if invalid_tile == tile_name_2:
          return True
    return False
  ## ======== END is_in_blacklist

  def try_tile(self, edges, pos, angle, incoming, in_sel):
    in_feature_name, in_tile_name, in_trans, in_rot = incoming[in_sel]

    # from the feature, set the position and rotation of the new tile
    new_angle = tile_util.lim360(angle - in_rot[2])
    tile_pos = tile_util.add3(pos, tile_util.rotateZ(tile_util.neg3(in_trans), new_angle))
    tile_name = in_tile_name

    # outgoing features are indexed on the tile name
    outgoing = self.outgoing[tile_name]

    # check existing edges to see if this tile fits.
    # although we know that one edge fits, we haven't checked the others.
    for out_sel in range(len(outgoing)):
      out_feature_name, out_tile_name, out_trans, out_rot = outgoing[out_sel]
      new_pos = tile_util.xyz_round(tile_util.add3(tile_pos, tile_util.rotateZ(out_trans, new_angle)))
      if new_pos in edges:
        edge_pos, edge_angle, edge_feature_name, edge_satisfied = edges[new_pos]
        if edge_satisfied:
          return False
        # check the height of the join.
        # note: we should also check that the incoming matches the outgoing.
        if abs(edge_pos[2] - new_pos[2]) > 0.01:
          return False
        
        # Check to see that the feature types match up "flat = flat" also check for the exception where "step_up" must match to "step_down"

        if not self.is_in_whitelist(out_feature_name,edge_feature_name):
          if self.is_in_blacklist(out_feature_name,edge_feature_name):
            return False
          if edge_feature_name != out_feature_name:
            return False

    return True
  ## ======== END try_tile

  def update_edges(self, todo, edges, pos, angle, incoming, in_sel):
    in_feature_name, in_tile_name, in_trans, in_rot = incoming[in_sel]

    # from the feature, set the position and rotation of the new tile
    new_angle = tile_util.lim360(angle - in_rot[2])
    tile_pos = tile_util.add3(pos, tile_util.rotateZ(tile_util.neg3(in_trans), new_angle))
    tile_name = in_tile_name

    # outgoing features are indexed on the tile name
    outgoing = self.outgoing[tile_name]
    # add all outgoing edges to the todo list and mark edges
    # note: if there were multiple outgoing edge choices, we would have to select them.
    for out_sel in range(len(outgoing)):
      out_feature_name, out_tile_name, out_trans, out_rot = outgoing[out_sel]
      new_pos = tile_util.xyz_round(tile_util.add3(tile_pos, tile_util.rotateZ(out_trans, new_angle)))
      if not tile_util.xyz_round(new_pos) in edges:
        # make an unsatisfied edge
        edge = (new_pos, tile_util.lim360(new_angle + out_rot[2]), out_feature_name, None)
        edges[tile_util.xyz_round(new_pos)] = edge
        todo.append(edge)
        #print(edge)
      else:
        edge_pos, edge_angle, edge_feature_name, edge_satisfied = edges[tile_util.xyz_round(new_pos)]
        edges[tile_util.xyz_round(new_pos)] = (edge_pos, edge_angle, edge_feature_name, out_feature_name)


  ## ======== END update_edges
  
  def get_distance(self, pointA, pointB):
    x_dist = pointB[0] - pointA[0]
    y_dist = pointB[1] - pointA[1]
    z_dist = pointB[2] - pointA[2]
    distance = math.sqrt(x_dist*x_dist + y_dist*y_dist + z_dist*z_dist)
    return distance
  ## ======== END get_distance
  
  def grid_to_tile_space(self, pos, gridsize):
    x = pos[0] * gridsize[0]
    y = pos[1] * gridsize[1]
    z = pos[2] * gridsize[2]
    return (x,y,z)
  ## ======== END get_distance

  def snap_grid_center(self, pos, grid_size):
    pos = ((pos[0] + grid_size[0]*0.5), (pos[1] + grid_size[1]*0.5),pos[2])
    return pos
  ## ======== END add_tuple3
  
  def snap_to_edge(self, pos, grid_size):
    if not pos[0] % grid_size[0] == 0:
      pos = (pos[0] - pos[0] % grid_size[0], pos[1], pos[2])
    if not pos[1] % grid_size[1] == 0:
      pos = (pos[0], pos[1] - pos[1] % grid_size[1], pos[2])
    if not pos[2] % grid_size[2] == 0:
      pos = (pos[0], pos[1], pos[2] - pos[2] % grid_size[2])
    return pos
  ## ======== END snap_to_edge
  
  def calc_ghf_cost(self, start, end, current):
    g_cost = self.get_distance(start,current)
    h_cost = self.get_distance(current, end)
    f_cost = g_cost + h_cost
    return (g_cost, h_cost, f_cost)
  ## ======== END calc_ghf_cost

  def in_the_list(self, current, list):
    for l in list:
      if l == current:
        return True

    return False

  def get_surrounding_pos(self, open, closed, current, grid_size, start, end,in_limits, off_limits, allow_upper_positions):
    
    surrounding_pos = []
    # Same grid Level
    surrounding_pos.append((current[0][0], current[0][1]+grid_size[1], current[0][2])) # Forward pos
    surrounding_pos.append((current[0][0], current[0][1]-grid_size[1], current[0][2])) # Backwards pos
    surrounding_pos.append((current[0][0]-grid_size[0], current[0][1], current[0][2])) # Left pos
    surrounding_pos.append((current[0][0]+grid_size[0], current[0][1], current[0][2])) # Right pos
    
    #if allow_upper_positions == True:
      # One grid level higher
    surrounding_pos.append((current[0][0], current[0][1]+grid_size[1], current[0][2]+grid_size[2])) # Forward pos
    surrounding_pos.append((current[0][0], current[0][1]-grid_size[1], current[0][2]+grid_size[2])) # Backwards pos
    surrounding_pos.append((current[0][0]-grid_size[0], current[0][1], current[0][2]+grid_size[2])) # Left pos
    surrounding_pos.append((current[0][0]+grid_size[0], current[0][1], current[0][2]+grid_size[2])) # Right pos

    surrounding_struct = []
    for pos in surrounding_pos:
      surrounding_struct.append((pos, self.calc_ghf_cost(start,end,pos),current[0]))

    for struct in surrounding_struct:
      if self.in_shape_range(in_limits,struct[0],4):
        if not self.in_shape_range(off_limits,struct[0],1):
          if not self.in_the_list(struct[0],closed[0]):
            if len(open) == 0:
              open.append(struct)
            elif not self.in_the_list(struct[0],open[0]):
              open.append(struct)


    return open

  def snap_room_center(self, shape, scale):
    for i in range(len(shape)):
      (roomCenter, size) = shape[i]
      if not roomCenter[0] % scale == 0:
        roomCenter = (roomCenter[0] - (roomCenter[0] % scale), roomCenter[1], roomCenter[2])
      if not roomCenter[1] % scale == 0:
        roomCenter = (roomCenter[0], roomCenter[1] - (roomCenter[1] % scale), roomCenter[2])
      if size[0] % 2 == 0:
        roomCenter = (roomCenter[0]+(scale*0.5), roomCenter[1], roomCenter[2])
      if size[1] % 2 == 0:
        roomCenter = (roomCenter[0], roomCenter[1]+(scale*0.5), roomCenter[2])
      shape[i] = (roomCenter, size)
    return shape
  ## ======== END snap_room_center

  def get_incoming_tile_index(self, incoming, name):
    for i in range(len(incoming)):
      if name == incoming[i][1]:
        return i

    return None
  ## ======== END get_incoming_tile_index

  # Returns an XY position, the Z must be calculated seperately
  # Returns the center of a potential tile, translation is needed to obtain the edge (if you want to add it to a todo list)
  def start_position_in_shape(self, shape, scale):
    for square in shape:
      (roomCenter, size) = square
      pos = (0, 0);
      if size[0] % 2 == 0:
        pos = (roomCenter[0]-scale*0.5, pos[1])
      else:
        pos = (roomCenter[0], pos[1])

      if size[1] % 2 == 0:
        pos = (pos[0], roomCenter[1]-scale*0.5)
      else:
        pos = (pos[0], roomCenter[1])

      return pos
  # ======== END start_position_in_shape

  def in_shape_range(self, shape, pos, scale):
    for square in shape:
      (roomCenter, size) = square
      if ((pos[0] <= roomCenter[0]+(scale*size[0]*0.5) and pos[0] >= roomCenter[0]-(scale*size[0]*0.5)) and (pos[1] <= roomCenter[1]+(scale*size[1]*0.5) and pos[1] >= roomCenter[1]-(scale*size[1]*0.5))):
        if pos[2] <= roomCenter[2] + size[2]*scale and pos[2] >= roomCenter[2]:
          return True 
    return False
  ## ======== END in_shape_range

  def get_shape_at_pos(self, shape, pos, scale):
    for square in shape:
      (roomCenter, size) = square
      if ((pos[0] <= roomCenter[0]+(scale*size[0]*0.5) and pos[0] >= roomCenter[0]-(scale*size[0]*0.5)) and (pos[1] <= roomCenter[1]+(scale*size[1]*0.5) and pos[1] >= roomCenter[1]-(scale*size[1]*0.5))):
        if pos[2] <= roomCenter[2] + size[2]*scale and pos[2] >= roomCenter[2]:
          return square 
    return None
  ## ======== END in_shape_range

  def create_todo(self, edges, nodes, feature_names = None, tile_name_ = None):
    todo = []
    for node in nodes:
      (tile_name, tile_pos, new_angle) = node
      if tile_name_ != None:
        if tile_name_ != tile_name:
          continue
      outgoing = self.outgoing[tile_name]
      for out_sel in range(len(outgoing)):
        out_feature_name, out_tile_name, out_trans, out_rot = outgoing[out_sel]
        new_pos = tile_util.xyz_round(tile_util.add3(tile_pos, tile_util.rotateZ(out_trans, new_angle)))
        if new_pos in edges:
          edge_pos, edge_angle, edge_feature_name, edge_satisfied = edges[new_pos]
          if not edge_satisfied:
            if feature_names is None:
              todo.append(edges[new_pos])
            else:
              for name in feature_names:
                if name == edge_feature_name:
                  todo.append(edges[new_pos])
    return todo
  ## ======== END create_todo

  def complete_todo(self, todo, edges, nodes, boundary = None, mask = None, tile_name = None, flood_fill = False):
    if flood_fill and boundary is None:
      raise ValueError("You can't flood fill without a boundary! boundary is ", boundary, " and flood_fill is ", flood_fill)

    junk_todo = []
    junk_edges = {}
    while len(todo):
      pos, angle, out_feature_name, in_feature_name = todo.pop()
      incoming = self.incoming[out_feature_name]
      in_sel = 0
      if tile_name != None: # Add feature later to decide what to do when the name is None for now default to index 0 of incoming
        if out_feature_name in self.whitelist:
          in_sel = self.get_incoming_tile_index(incoming, tile_name)
          if in_sel == None:
            for feature_name in self.whitelist[out_feature_name]:
              incoming = self.incoming[feature_name]
              in_sel = self.get_incoming_tile_index(incoming, tile_name)
              if in_sel != None:
                break
        else:
          in_sel = self.get_incoming_tile_index(incoming, tile_name)

      in_feature_name, in_tile_name, in_trans, in_rot = incoming[in_sel]
      new_angle = tile_util.lim360(angle - in_rot[2])
      tile_pos = tile_util.xyz_round(tile_util.add3(pos, tile_util.rotateZ(tile_util.neg3(in_trans), new_angle)))
      tile_name = in_tile_name

      if not boundary is None:
        if not self.in_shape_range(boundary, tile_pos, self.tile_size):
          continue

      if not mask is None:
        if self.in_shape_range(mask, tile_pos, self.tile_size):
          continue

      if self.try_tile(edges, pos, angle, incoming, in_sel):
        self.update_edges((todo if flood_fill else junk_todo), edges, pos, angle, incoming, in_sel)
        nodes.append((tile_name, tile_pos, new_angle))

    return nodes
  ## ======== END complete_todo