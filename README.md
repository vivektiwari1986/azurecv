# Home Assistant - Azure Computer Vision API Component
Custom Component for Home assistant to get image data from Azure Computer Vision Cognitive Service.

TLDR; You can easily integrate azure computer vision services and detect objects in an image. I personally use this for human detection when nobody is in the home and motionEye detects motion in an image.

# Setup
## Azure Cognitive Developer Account Setup (Free)
This component will need access to Azure Cognitive Services Developer account. You can follow the steps below to set it up.
1. Visit [Azure Cognitive Services Page](https://azure.microsoft.com/en-us/services/cognitive-services/) and click 'Free account' or 'Try Cognitive Services Free' to create an Azure Account.
2. After Account setup above, visit [Azure Portal Page](https://portal.azure.com/#home)
3. Click 'Create a Resource' and search for 'Cognitive Services'. Click on Create.
4. For Resource Group field, click 'Create New' and give any name for resource group.
5. Select the closest region, give a name for instance and select the free tier for pricing.
6. You may give any random some tag names in the next screen. 
7. Once you have created the cognitive services resource, Go back to the home page of your portal and select the Cognitive Service resource you just created.
8. Select 'Keys and Endpoint' in the left rail. Click Show Keys.
9.  Note down any one of the key.
10. Note down the endpoint. Lets call this url.
11. The above two values will be needed in the config for custom component.

## Installation (HACS) - Work in progress
1. Have [HACS](https://github.com/custom-components/hacs) installed, this will allow you to easily update
2. Add `https://github.com/vivektiwari1986/azurecv` as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) as Type: Integration
3. Click install under "TBA", restart your instance.

## Installation (Manual)
1. Download this repository as a ZIP (green button, top right) and unzip the archive
2. Copy `/custom_components/azurecv` to your `<config_dir>/custom_components/` directory
   * You will need to create the `custom_components` folder if it does not exist
   * On Hassio the final location will be `/config/custom_components/azurecv`
   * On Hassbian the final location will be `/home/homeassistant/.homeassistant/custom_components/azurecv`

## Configuration
Add the following to your configuration file and restart Home Assistant to load the configuration

```yaml
azurecv:
  api_key: !secret azurecv_key
  url: !secret azurecv_url
```

# Usage
The component can be used to detect any objects and to describe an image. This component exposes two services that can be given an image path.

## Service: azurecv.analyze
This calls the underlyzing azure image analyze REST method
Example Call to service.
```yaml
- service: azurecv.analyze
  data_template:
    filepath: '/share/motioneye/Camera2/2021-01-30/20-13-23.jpg'
    haContext: 'Camera Name'
    detect: 'dog,person'
```
Parameters:
* filepath: Path to image file
<!-- * fileurl: Alternatively, an internet accessible url for the image -->
* haContext: A context that is returned in the response
* detect (optional) : a comma separated list of objects to look for. Returns easy to parse data indicating if the object was detected or not.

The response is available as event on the home assistant event bus. You can subsribe to the topic name 'azurecv_image_analyzed'. The response contains:
* caption: A caption and confidence for the captioned image
* tags: All tags detected in the image.
* objects: All objects detected in the image
* haContext: The haContext passed in the service call
* method: The azureCV service method called
* filePath: The image file path used
<!-- * fileUrl: the image file url used -->
* detection: A dictionary containing whether each of the asked detection objects were present or not.

 An example event data is shown below.

```json
{
    "event_type": "azurecv_image_analyzed",
    "data": {
        "caption": {
            "text": "a dog sitting on a wood floor in a living room",
            "confidence": 0.49372708797454834
        },
        "tags": "floor,indoor,chair,wall,table,coffee table,living,room,couch,desk,kitchen & dining room table,house,studio couch,flooring,sofa bed,bed,hardwood,furniture,cluttered",
        "objects": "chair,dog,chair,chair",
        "detection": {
            "dog": true,
            "person": false
        },
        "method": "analyze",
        "haContext": "Camera Name",
        "filePath": "/share/motioneye/Camera2/2021-01-30/20-13-23.jpg"
    },
    "origin": "LOCAL",
    "time_fired": "2021-01-31T04:23:57.394243+00:00",
    "context": {
        "id": "dbc796a1c247bc81afa8353632d7fa40",
        "parent_id": null,
        "user_id": null
    }
}
```

Example automation to listen to the event and alert:
```yaml
- alias: Notify when person detected on a cam
  initial_state: true
  trigger:
    platform: event
    event_type: azurecv_image_analyzed
  condition:
    - condition: state
      entity_id: input_boolean.home_armed
      state: 'on'
    - condition: template
      value_template: >
        {{ trigger.event.data.detection.person == True }}
  action:
    - service: script.notify_home_alarm
      data_template:
        message: >
          Person Detected on {{ trigger.event.data.haContext }}
```

## Service: azurecv.describe
This calls the underlyzing azure image describe REST method. this is a more lightweight call and only returns the caption and tags.
Example Call to service.
```yaml
- service: azurecv.describe
  data_template:
    filepath: '/share/motioneye/Camera2/2021-01-30/20-13-23.jpg'
    haContext: 'Camera Name'
```

Event fired:
```json
{
    "event_type": "azurecv_image_analyzed",
    "data": {
        "caption": {
            "text": "a dog sitting on a wood floor in a living room",
            "confidence": 0.49372708797454834
        },
        "tags": "floor,indoor,wall,living,room,furniture,cluttered",
        "objects": "",
        "method": "describe",
        "haContext": "Camera Name",
        "filePath": "/share/motioneye/Camera2/2021-01-30/20-13-23.jpg"
    },
    "origin": "LOCAL",
    "time_fired": "2021-01-31T04:34:25.536038+00:00",
    "context": {
        "id": "12c5f7a25c96ebfb0f55d3916b5fb3fa",
        "parent_id": null,
        "user_id": null
    }
}
```
