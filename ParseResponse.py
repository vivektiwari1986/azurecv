class ParseResponse:
  def polish(self, data):
    dataObj = self.clean(data)
    return {
      'caption': self.getCaption(dataObj),
      'tags': self.getTags(dataObj),
      'objects': self.getObjects(dataObj)
      # 'rawResponse': dataObj
    }

  def clean(self, rawData):
    if 'requestId' in rawData:
      del rawData['requestId']
    return rawData

  def getTags(self, dataObj):
    if 'tags' in dataObj:
      tags = dataObj['tags']
      tagNames = list(map(lambda x: x['name'], tags))
      return ",".join(tagNames)
    if 'description' in dataObj:
      if 'tags' in dataObj['description']:
        return ",".join(dataObj['description']['tags'])
    return ""
  
  def getObjects(self, dataObj):
    if 'objects' in dataObj:
      return ",".join(list(map(lambda x: x['object'], dataObj['objects'])))
    return ""

  def getCaption(self, dataObj):
    if 'description' in dataObj:
      if 'captions' in dataObj['description']:
        return dataObj['description']['captions'][0]
    return ""

# data = {"categories":[{"name":"abstract_","score":0.00390625},{"name":"others_","score":0.0078125}],"tags":[{"name":"floor","confidence":0.9992407560348511},{"name":"indoor","confidence":0.9955368041992188},{"name":"footwear","confidence":0.9339431524276733},{"name":"clothing","confidence":0.8632873296737671},{"name":"person","confidence":0.7471531629562378},{"name":"trousers","confidence":0.5809088349342346}],"description":{"tags":["floor","indoor"],"captions":[{"text":"a dog on a leash in a room with a person standing in the background","confidence":0.4347965717315674}]},"faces":[],"objects":[{"rectangle":{"x":318,"y":21,"w":269,"h":596},"object":"person","confidence":0.67}],"requestId":"7d2dad86-3c48-4198-ab9a-3e790e505c51","metadata":{"height":1080,"width":1920,"format":"Jpeg"}}

# P = ParseResponse()
# c =  P.clean(data)
# d = P.getTags(c)
# e = P.getCaption(c)
# f = P.getObjects(c)
# print(d)
# print(e)
# print(f)
