import fbx

class fbx_io:
  def __init__(self):  
    self.sdk_manager = fbx.FbxManager.Create()
    if not self.sdk_manager:
      sys.exit(1)
    
    self.io_settings = fbx.FbxIOSettings.Create(self.sdk_manager, fbx.IOSROOT)
    self.sdk_manager.SetIOSettings(self.io_settings)



  def import_file(self, file_name):
    importer = fbx.FbxImporter.Create(self.sdk_manager, "")    
    result = importer.Initialize("scenes/"+file_name+".fbx", -1, self.io_settings)
    if not result:
      raise BaseException("could not find components file")
    self.components = fbx.FbxScene.Create(self.sdk_manager, "")
    result = importer.Import(self.components)
    importer.Destroy()

    root = self.components.GetRootNode()
    top_level = [root.GetChild(i) for i in range(root.GetChildCount())]

    
    tiles = self.tiles = {}
    for node in top_level:
      if node.GetChildCount():
        # for each tile, check the names of the connectors
        tiles[node.GetName()] = node;

    return top_level

  def get_format(self, name):
    reg = self.sdk_manager.GetIOPluginRegistry()
    for idx in range(reg.GetWriterFormatCount()):
      desc = reg.GetWriterFormatDescription(idx)
      #print(desc)
      if name in desc:
        return idx
    return -1

  # file_type can be either "FBX binary" or "FBX ascii"
  # Output name is default "result"
  def create_scene(self, file_type, output_name = "result"):
    self.format = self.get_format(file_type)
    new_scene = fbx.FbxScene.Create(self.sdk_manager, output_name);

        # clone the tile meshes and name them after their original nodes.
    tile_meshes = self.tile_meshes = {}
    for name in self.tiles:
      tile = self.tiles[name]
      tile_mesh = tile.GetNodeAttribute()
      tile_meshes[name] = tile_mesh.Clone(fbx.FbxObject.eDeepClone, None)
      tile_meshes[name].SetName(name)

    return new_scene


  def export_scene(self, scene, output_name = "result"):
    exporter = fbx.FbxExporter.Create(self.sdk_manager, "")
    
    if exporter.Initialize("scenes/"+output_name+".fbx", self.format, self.io_settings):
      exporter.Export(scene)

    exporter.Destroy()


  def make_node(self, scene, node_name, pos, angle):
    dest_node = fbx.FbxNode.Create( scene, node_name )
    dest_node.SetNodeAttribute(self.tile_meshes[node_name])
    dest_node.LclTranslation.Set(fbx.FbxDouble3(pos[0], pos[1], pos[2]))
    dest_node.LclRotation.Set(fbx.FbxDouble3(0, 0, angle))
    root = scene.GetRootNode()
    root.AddChild(dest_node)