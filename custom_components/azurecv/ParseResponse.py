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
