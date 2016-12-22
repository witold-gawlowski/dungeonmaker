import fbx

class componentsIO(object):
  def __init__(self):
    self.sdk_manager = fbx.FbxManager.Create()
    if not self.sdk_manager:
      sys.exit(1)

    self.io_settings = fbx.FbxIOSettings.Create(self.sdk_manager, fbx.IOSROOT)
    
    self.sdk_manager.SetIOSettings(self.io_settings)
    
    self.new_scene =  fbx.FbxScene.Create(self.sdk_manager, "result");
  
    
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

    return top_level

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



