import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
from .ParseResponse import ParseResponse
class AzureCV:
  apiKey = None
  apiUrl = None
  parser = None

  def __init__(self, apiKey, apiUrl):
    self.apiKey = apiKey
    self.apiUrl = apiUrl
    self.parser = ParseResponse()

  def callWithPath(self, filePath, endpoint, errorHandler):
    headers = {
      'Content-Type': 'application/octet-stream',
      'Ocp-Apim-Subscription-Key': self.apiKey
    }

    try:
      f = open(filePath, "rb")
      binary = f.read()
      conn = http.client.HTTPSConnection(self.apiUrl)
      conn.request("POST", "/vision/v3.1/"+endpoint, binary, headers)
      response = conn.getresponse()
      data = response.read()
      conn.close()
      return json.loads(data)
    except Exception as e:
      errorHandler(e)
  
  def describe(self, params, haContext):
    data = self.callWithPath(params['filePath'], 'describe', params['errorHandler'])
    response = self.parser.polish(data)
    response.update({
      'method': 'describe',
      'haContext': haContext,
      'filePath': params['filePath']
    })
    return response

  def analyze(self, params, haContext, detect):
    data = self.callWithPath(params['filePath'], 'analyze?visualFeatures=Description,Objects,Faces,Tags', params['errorHandler'])
    response = self.parser.polish(data)
    if detect is not None:
      response.update({
        'detection': self.detectInObj(detect, data)
      })
    response.update({
      'method': 'describe',
      'haContext': haContext,
      'filePath': params['filePath']
    })
    return response
  
  def detectInObj(self, detect, data):
    toDetect = list(map(lambda x: x.strip(), detect.split(",")))
    detects = {}
    for x in toDetect:
      detects[x] = False
      if 'tags' in data:
        for tag in data['tags']:
          if tag['name'].find(x) != -1:
            detects[x] = True
      if 'description' in data and 'captions' in data['description']:
        captions = data['description']['captions']
        for caption in captions:
          if caption['text'].find(x) != -1:
            detects[x] = True
      if 'objects' in data:
        for obj in data['objects']:
          if obj['object'].find(x) != -1:
            detects[x] = True
    return detects
