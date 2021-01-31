""" 

azure computer vision integration
v0.0.1

"""

import logging
import json
import subprocess
import homeassistant.helpers.config_validation as cv
from voluptuous import Invalid, Schema, All, Required, ALLOW_EXTRA, Optional
from os import path
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, CONF_API_KEY, CONF_URL
from .AzureCV import AzureCV

DOMAIN = "azurecv"
STORAGE = ".storage/azurecv.json"
ATTR_FILEPATH = "filepath"
ATTR_FILEURL = "fileurl"
ATTR_HACONTEXT = "haContext"
ATTR_DETECT = "detect"


SERVICE_DESCRIBE = 'describe'
SERVICE_ANALYZE = 'analyze'

def file_must_be_given(params):
  if ATTR_FILEPATH not in params and ATTR_FILEURL not in params:
    raise Invalid('No file attribute given')
  return params

SERVICE_DESCRIBE_SCHEMA = Schema(All(
  {
    Optional(ATTR_FILEURL): str,
    Optional(ATTR_FILEPATH): str,
    Optional(ATTR_HACONTEXT): str
  },
  file_must_be_given
))

SERVICE_ANALYZE_SCHEMA = Schema(All(
  {
    Optional(ATTR_FILEURL): str,
    Optional(ATTR_FILEPATH): str,
    Optional(ATTR_HACONTEXT): str,
    Optional(ATTR_DETECT): str
  },
  file_must_be_given
))

CONFIG_SCHEMA = Schema(
  {
    DOMAIN: Schema(
      {
        Required(CONF_API_KEY): cv.string,
        Required(CONF_URL): cv.string
      }
    )
  },
  extra=ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

def getHAContext(call):
  if ATTR_HACONTEXT in call.data:
    return call.data[ATTR_HACONTEXT]
  return ''

def getDetect(call):
  if ATTR_DETECT in call.data:
    return call.data[ATTR_DETECT]
  return None

def getFile(call, errorHandler):
  if ATTR_FILEPATH in call.data:
    return {
      'filePath': call.data.get(ATTR_FILEPATH)
    }
  elif ATTR_FILEURL in call.data:
    return {
      'fileUrl': call.data.get(ATTR_FILEURL).lower()
    }
  else:
    error = "[azurecv] No filepath or fileurl supplied"
    errorHandler(error)
    return {}

def setup(hass, config):
  _LOGGER.debug("AZURECV v0.0.1")
  conf = config[DOMAIN]
  api_secret_key = conf[CONF_API_KEY]
  api_url = conf[CONF_URL]
  azureCV = AzureCV(api_secret_key, api_url)

  # Configure Destructor
  def on_shutdown(event):
    _LOGGER.debug("On shutdown called for azureCV")

  hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, on_shutdown)

  def handleError(e):
    notification = str(e)
    hass.components.persistent_notification.create(notification, DOMAIN)
    _LOGGER.error(notification)

  def onDescribe(call):
    fileObj = getFile(call, handleError)
    if 'filePath' in fileObj:
      response = azureCV.describe(
        {
          'filePath': fileObj['filePath'],
          'errorHandler': handleError
        }, 
        getHAContext(call)
      )
      fireEvent(response)

  def onAnalyze(call):
    fileObj = getFile(call, handleError)
    if 'filePath' in fileObj:
      response = azureCV.analyze(
        {
          'filePath': fileObj['filePath'],
          'errorHandler': handleError
        }, 
        getHAContext(call),
        getDetect(call)
      )
      fireEvent(response)
      
  def fireEvent(data):
    # _LOGGER.debug("AZURECV return response" + str(data))
    hass.bus.fire("azurecv_image_analyzed", data)

  hass.services.register(DOMAIN, SERVICE_DESCRIBE, onDescribe, SERVICE_DESCRIBE_SCHEMA)
  hass.services.register(DOMAIN, SERVICE_ANALYZE, onAnalyze, SERVICE_ANALYZE_SCHEMA)
  return True


  # params = urllib.urlencode({
  #     # Request parameters
  #     'visualFeatures': 'Categories',
  #     'details': '{string}',
  #     'language': 'en',
  # })