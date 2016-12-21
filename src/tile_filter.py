class tile_filter:
  def __init__(self):  
    self.whitelist = {}
    self.whitelist["step_up"] = ["step_down"]
    self.whitelist["step_down"] = ["step_up"]
    self.whitelist["Ceiling_Flat"] = ["Floor_Flat"]
    self.whitelist["Floor_Flat"] = ["Ceiling_Flat"]

    self.blacklist = {}
    self.blacklist["step_up"] = ["step_up"]
    self.blacklist["step_down"] = ["step_down"]


  def is_in_whitelist(self, tile_name_1, tile_name_2):
    if tile_name_1 in self.whitelist:
      good_tiles = self.whitelist[tile_name_1]
      for valid_tile in good_tiles:
        if valid_tile == tile_name_2:
          return True
    return False

  def is_in_blacklist(self, tile_name_1, tile_name_2):
    if tile_name_1 in self.blacklist:
      bad_tiles = self.blacklist[tile_name_1]
      for invalid_tile in bad_tiles:
        if invalid_tile == tile_name_2:
          return True
    return False