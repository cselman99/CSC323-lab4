class Output:
  def __init__(self, values: list, keys: list):
    if len(values) != len(keys):
      raise Exception("Number of keys does not match number of values in Output object creation.")
    self.num_parties = len(values)
    self.values = values
    self.keys = keys 
    self.active = [True]*self.num_parties

  def __repr__(self):
    final = ""
    for i in range(len(self.keys) - 1):
      final += str(self.keys[i]) + ":" str(self.values[i]) + ", "
    final += str(self.keys[len(self.keys) - 1])  + ":" + str(self.values[len(self.values) - 1])
    return final

  def get_value(self, key):
    for i in range(self.num_parties):
      if key == self.keys[i]:
        if self.active[i] == True:
          self.active[i] = False
          return self.value
        else:
          raise Exception("Inactive block for user.")
    raise Exception("Invalid key for block.")
 