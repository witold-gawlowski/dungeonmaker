
import math

# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory
import fbx

import tile_filter


class tile_handler:
  def __init__(self, top_level):  
    self.whitelist = {}
    self.whitelist["step_up"] = ["step_down"]
    self.whitelist["step_down"] = ["step_up"]
    self.whitelist["Ceiling_Flat"] = ["Floor_Flat"]
    self.whitelist["Floor_Flat"] = ["Ceiling_Flat"]

    self.blacklist = {}
    self.blacklist["step_up"] = ["step_up"]
    self.blacklist["step_down"] = ["step_down"]

    
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

  def try_tile(self, new_scene, todo, edges, pos, angle, incoming, in_sel):

    #print("\n------------\n",incoming)

    in_feature_name, in_tile_name, in_trans, in_rot = incoming[in_sel]
    #print("\nNAME: ", in_tile_name, "\n")

    # from the feature, set the position and rotation of the new tile
    new_angle = lim360(angle - in_rot[2])
    tile_pos = add3(pos, rotateZ(neg3(in_trans), new_angle))
    tile_name = in_tile_name
    #print(tile_pos, new_angle, tile_name)

    # outgoing features are indexed on the tile name
    outgoing = self.outgoing[tile_name]
    #print(outgoing)

    # check existing edges to see if this tile fits.
    # although we know that one edge fits, we haven't checked the others.
    for out_sel in range(len(outgoing)):
      out_feature_name, out_tile_name, out_trans, out_rot = outgoing[out_sel]
      new_pos = add3(tile_pos, rotateZ(out_trans, new_angle))
      if round3(new_pos) in edges:
        edge_pos, edge_angle, edge_feature_name, edge_satisfied = edges[round3(new_pos)]
        #print("check", new_pos, edge_pos, out_feature_name, edge_feature_name, edge_satisfied)
        if edge_satisfied:
          return False
        # check the height of the join.
        # note: we should also check that the incoming matches the outgoing.
        if abs(edge_pos[2] - new_pos[2]) > 0.01:
          #print("fail")
          return False
        
        # Check to see that the feature types match up "flat = flat" also check for the exception where "step_up" must match to "step_down"

        if not self.tile_filter.is_in_whitelist(out_feature_name,edge_feature_name):
          if self.tile_filter.is_in_blacklist(out_feature_name,edge_feature_name):
            return False
          if edge_feature_name != out_feature_name:
            return False


    # add all outgoing edges to the todo list and mark edges
    # note: if there were multiple outgoing edge choices, we would have to select them.
    for out_sel in range(len(outgoing)):
      out_feature_name, out_tile_name, out_trans, out_rot = outgoing[out_sel]
      new_pos = add3(tile_pos, rotateZ(out_trans, new_angle))
      if not round3(new_pos) in edges:
        # make an unsatisfied edge
        edge = (new_pos, lim360(new_angle + out_rot[2]), out_feature_name, None)
        edges[round3(new_pos)] = edge
        todo.append(edge)
        #print(edge)
      else:
        edge_pos, edge_angle, edge_feature_name, edge_satisfied = edges[round3(new_pos)]
        edges[round3(new_pos)] = (edge_pos, edge_angle, edge_feature_name, out_feature_name)

    #self.make_node(new_scene, tile_name, tile_pos, new_angle)
    #print("pass")
    return True
  ## ======== END try_tile

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

  def in_shape_range(self, shape, pos, scale):
    for square in shape:
      (roomCenter, size) = square
      if ((pos[0] <= roomCenter[0]+(scale*size[0]*0.5) and pos[0] >= roomCenter[0]-(scale*size[0]*0.5)) and (pos[1] <= roomCenter[1]+(scale*size[1]*0.5) and pos[1] >= roomCenter[1]-(scale*size[1]*0.5))):
        return True 
    return False
  ## ======== END create_todo

  def create_todo(self, edges, nodes, feature_names = None):
    todo = []
    for node in nodes:
      (tile_name, tile_pos, new_angle) = node
      outgoing = self.outgoing[tile_name]
      for out_sel in range(len(outgoing)):
        out_feature_name, out_tile_name, out_trans, out_rot = outgoing[out_sel]
        new_pos = add3(tile_pos, rotateZ(out_trans, new_angle))
        if round3(new_pos) in edges:
          edge_pos, edge_angle, edge_feature_name, edge_satisfied = edges[round3(new_pos)]
          if not edge_satisfied:
            if feature_names is None:
              todo.append(edges[round3(new_pos)])
            else:
              for name in feature_names:
                if name == edge_feature_name:
                  todo.append(edges[round3(new_pos)])
    return todo
  ## ======== END create_todo

  def complete_todo(self, new_scene, todo, edges, nodes, boundary = None, tile_name = None, flood_fill = False):
    if flood_fill and boundary is None:
      raise ValueError("You can't flood fill without a boundary! boundary is ", boundary, " and flood_fill is ", flood_fill)

    junk = []
    while len(todo):
      pos, angle, out_feature_name, in_feature_name = todo.pop()
      incoming = self.incoming[out_feature_name]
      in_sel = int(self.get_incoming_tile_index(incoming, tile_name))

      in_feature_name, in_tile_name, in_trans, in_rot = incoming[in_sel]
      new_angle = lim360(angle - in_rot[2])
      tile_pos = round3(add3(pos, rotateZ(neg3(in_trans), new_angle)))
      tile_name = in_tile_name

      if not boundary is None:
        if not self.in_shape_range(boundary, xy_location(tile_pos), 4):
          continue

      if self.try_tile(new_scene, (todo if flood_fill else junk), edges, pos, angle, incoming, in_sel):
        nodes.append((tile_name, tile_pos, new_angle))

    return nodes
  ## ======== END complete_todo






