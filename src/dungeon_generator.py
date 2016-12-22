
import re
import math
import random

# if (when) this doesn't work, copy 64 bit Python 3.3 fbx.pyd and fbxsip.pyd from the Autodesk FBX SDK
# into this directory
import fbx

import tile_filter

# FbxDouble3 unpacker
def tolist(x):
  return [x[i] for i in range(3)]

# FbxDouble3 packer
def tovec3(x):
  return fbx.FbxDouble3(x[0], x[1], x[2], x[3])

def round3(x):
  return (round(x[0]), round(x[1]), round(x[2]))

def add3(x, y):
  return [x[i]+y[i] for i in range(3)]

def sub3(x, y):
  return [x[i]-y[i] for i in range(3)]

def neg3(x):
  return [-x[i] for i in range(3)]

def xy_location(x):
  return (round(x[0]), round(x[1]))

def rotateZ(v, angle):
  sz = math.sin(angle * (3.14159/180))
  cz = math.cos(angle * (3.14159/180))
  return [
    cz * v[0] - sz * v[1],
    sz * v[0] + cz * v[1],
    v[2]
  ]

def lim360(x):
  x = x + 360 if x < 0 else x
  x = x - 360 if x >= 360 else x
  return round(x)
  

class dungeon_generator:
  def __init__(self):  
    self.sdk_manager = fbx.FbxManager.Create()
    if not self.sdk_manager:
      sys.exit(1)
    
    self.io_settings = fbx.FbxIOSettings.Create(self.sdk_manager, fbx.IOSROOT)
    self.sdk_manager.SetIOSettings(self.io_settings)

    self.tile_filter = tile_filter.tile_filter()

  def read_components(self):
    importer = fbx.FbxImporter.Create(self.sdk_manager, "")    
    result = importer.Initialize("scenes/components7.fbx", -1, self.io_settings)
    if not result:
      raise BaseException("could not find components file")
    self.components = fbx.FbxScene.Create(self.sdk_manager, "")
    result = importer.Import(self.components)
    importer.Destroy()

    root = self.components.GetRootNode()
    top_level = [root.GetChild(i) for i in range(root.GetChildCount())]

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

    # at this point incoming and outgoing index connectors
    # tiles indexes the tiles by name.
    #print("self.incoming:", self.incoming)
    #print("\n self.outgoing:", self.outgoing)


  def get_format(self, name):
    reg = self.sdk_manager.GetIOPluginRegistry()
    for idx in range(reg.GetWriterFormatCount()):
      desc = reg.GetWriterFormatDescription(idx)
      #print(desc)
      if name in desc:
        return idx
    return -1

  def write_result(self):
    #format = self.get_format("FBX binary")
    format = self.get_format("FBX ascii")

    new_scene = fbx.FbxScene.Create(self.sdk_manager, "result");
    #self.create_dungeon(new_scene, "flat")
    self.create_room(new_scene, "Floor_Flat")

    exporter = fbx.FbxExporter.Create(self.sdk_manager, "")
    
    if exporter.Initialize("scenes/result.fbx", format, self.io_settings):
      exporter.Export(new_scene)

    exporter.Destroy()

  def make_node(self, new_scene, node_name, pos, angle):
    dest_node = fbx.FbxNode.Create( new_scene, node_name )
    dest_node.SetNodeAttribute(self.tile_meshes[node_name])
    dest_node.LclTranslation.Set(fbx.FbxDouble3(pos[0], pos[1], pos[2]))
    dest_node.LclRotation.Set(fbx.FbxDouble3(0, 0, angle))
    root = new_scene.GetRootNode()
    root.AddChild(dest_node)

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

        #if (out_feature_name == "step_down" and edge_feature_name != "step_up"):
        #  return False
        #elif (out_feature_name == "step_up" and edge_feature_name != "step_down"):
        #  return False
        #elif (out_feature_name == "Ceiling_Flat" and not (edge_feature_name == "Ceiling_Flat" or edge_feature_name == "Floor_Flat")):
        #  return False
        #elif (out_feature_name == "Floor_Flat" and not (edge_feature_name == "Floor_Flat" or edge_feature_name == "Ceiling_Flat")):
        #  return False

        
          
          

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


  def create_dungeon(self, new_scene, feature_name):
    # clone the tile meshes and name them after their original nodes.
    tile_meshes = self.tile_meshes = {}
    for name in self.tiles:
      tile = self.tiles[name]
      tile_mesh = tile.GetNodeAttribute()
      tile_meshes[name] = tile_mesh.Clone(fbx.FbxObject.eDeepClone, None)
      tile_meshes[name].SetName(name)

    edges = {}
    pos = (0, 0, 0)
    angle = 0

    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    num_tiles = 0
    random.seed(1)

    # this loop processes one edge from the todo list.
    while len(todo) and num_tiles < 200:
      pos, angle, out_feature_name, in_feature_name = todo.pop()

      print(xy_location(pos))

      for i in range(4):
        # incoming features are indexed on the feature name
        incoming = self.incoming[out_feature_name]
        in_sel = int(random.randrange(len(incoming)))

        if self.try_tile(new_scene, todo, edges, pos, angle, incoming, in_sel):
          break

      num_tiles += 1


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

  def get_incoming_tile_index(self, incoming, name):
    for i in range(len(incoming)):
      if name == incoming[i][1]:
        return i

    return None

  def in_shape_range(self, shape, pos, scale):
    for square in shape:
      (roomCenter, size) = square
      if ((pos[0] <= roomCenter[0]+(scale*size[0]*0.5) and pos[0] >= roomCenter[0]-(scale*size[0]*0.5)) and (pos[1] <= roomCenter[1]+(scale*size[1]*0.5) and pos[1] >= roomCenter[1]-(scale*size[1]*0.5))):
        return True 
    return False

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

  def create_room(self, new_scene, feature_name):
    # clone the tile meshes and name them after their original nodes.
    tile_meshes = self.tile_meshes = {}
    for name in self.tiles:
      tile = self.tiles[name]
      tile_mesh = tile.GetNodeAttribute()
      tile_meshes[name] = tile_mesh.Clone(fbx.FbxObject.eDeepClone, None)
      tile_meshes[name].SetName(name)

    tile_size = 4;
    shape = [((2,-8,0), (4,4)),
             ((2,28,0), (20,15)),
             ((2,70,0), (8,8)),
             ((2,28,0), (24,6))]

    #shape = [((2,0,0), (20,1)),
    #         ((2,20,0), (20,1)),
    #         ((2,40,0), (20,1)),
    #         ((38,8,0), (2,4)),
    #         ((-34,28,0), (2,4))]

    #shape = [((0,0,0), (4,3))]
    shape = self.snap_room_center(shape, tile_size)

    pos = (0,-2,0)
    edges = {}
    angle = 0
    # create an unsatisfied edge
    todo = [(pos, angle, feature_name, False)]
    num_tiles = 0

    nodes = []

    print("Making floor...")

    nodes = self.complete_todo(new_scene, todo, edges, nodes, shape, "Floor_2x2", True)

    print("Floor Complete!")


    print("Making walls...")
    todo = self.create_todo(edges, nodes)
    print("Todo length: ", len(todo))

    nodes = self.complete_todo(new_scene, todo, edges, nodes, None, "Floor_Wall_4x4x4", False)      
    print("Walls Complete!")

    print("Making Corners...")
    todo = self.create_todo(edges, nodes, ["Floor_Wall_End"])
    print("Todo length: ", len(todo))
    nodes = self.complete_todo(new_scene, todo, edges, nodes, None, "Floor_Wall_L_4x4x4", False)
    print("Corners Complete!")
    
    print("Making Ceiling...")
    pos = (0,-2,8)
    edges = {}
    angle = 0
    todo = [(pos, angle, "Ceiling_Flat", False)]
    num_tiles = 0
    ceilingNodes = []

    ceilingNodes = self.complete_todo(new_scene, todo, edges, ceilingNodes, shape, "Ceiling_Floor_2x2", True)
    
    todo = self.create_todo(edges, ceilingNodes)
          
    print("Todo length: ", len(todo))

    ceilingNodes = self.complete_todo(new_scene, todo, edges, ceilingNodes, None, "Ceiling_Wall_4x4x4", False)

    #while len(unsatisfiedWalls):
    #  pos, angle, out_feature_name, in_feature_name = unsatisfiedWalls.pop()
    #  incoming = self.incoming["Ceiling_Flat"]
    #  in_sel = int(self.get_incoming_tile_index(incoming, "Ceiling_Wall_4x4x4"))

    #  if self.try_tile(new_scene, todo, edges, pos, angle, incoming, in_sel):
    #    in_feature_name, in_tile_name, in_trans, in_rot = incoming[in_sel]
    #    new_angle = lim360(angle - in_rot[2])
    #    tile_pos = round3(add3(pos, rotateZ(neg3(in_trans), new_angle)))
    #    tile_name = in_tile_name
    #    ceilingNodes.append((tile_name, tile_pos, new_angle))

    
    print("Ceiling Complete!")

    
    for node in ceilingNodes:
      nodes.append(node)

    print("Total Nodes: ", len(nodes))
    # This takes all the nodes and sends them to the FXB output.
    for node in nodes:
      (tile_name, tile_pos, new_angle) = node
      self.make_node(new_scene, tile_name, tile_pos, new_angle)


    





