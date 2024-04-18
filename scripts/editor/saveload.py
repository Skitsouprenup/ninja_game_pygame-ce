import json

class SaveLoad:

  def save(self, path, data):
    f = open(path, 'w')
    json.dump(data, f)
    f.close()

  def load(self, path):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    return data