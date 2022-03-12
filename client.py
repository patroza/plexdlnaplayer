#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from xml.dom.minidom import parseString

minidlna = 'http://192.168.178.55:32469'
headers = {  'Content-type': 'text/xml'
          , 'SOAPACTION': '"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"',
                      'charset': 'utf-8',
            'User-Agent': '{}/{}'.format(__file__, '1.0')
          }

def get_object_id(index):
    return '''
<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">
      <ObjectID>%s</ObjectID>
      <BrowseFlag>BrowseDirectChildren</BrowseFlag>
      <Filter></Filter>
      <StartingIndex>0</StartingIndex>
      <RequestedCount>0</RequestedCount>
      <SortCriteria></SortCriteria>
    </u:Browse>
  </s:Body>
</s:Envelope>
    ''' % index

def parse_service(service):
    name = service.getElementsByTagName('serviceType')[0].firstChild.nodeValue
    url = service.getElementsByTagName('controlURL')[0].firstChild.nodeValue
    return { 'name': name
           , 'url': url
           }

def parse_container(container):
    index = container.getAttribute('id')
    title = container.getElementsByTagName('dc:title')[0].firstChild.nodeValue
    return { 'index': index
           , 'title': title
           }

def parse_item(item):
    index = item.getAttribute('id')
    title = item.getElementsByTagName('dc:title')[0].firstChild.nodeValue
    result = item.getElementsByTagName('res')[0]
    return { 'index': index
           , 'title': title
           , 'size': result.getAttribute('size')
           , 'duration': result.getAttribute('duration')
           , 'bitrate': result.getAttribute('bitrate')
           , 'sampling': result.getAttribute('sampleFrequency')
           , 'channels': result.getAttribute('nrAudioChannels')
           , 'resolution': result.getAttribute('resolution')
           , 'url': result.firstChild.nodeValue
           }

result = requests.get('%s%s' % (minidlna, '/DeviceDescription.xml'))
#print("hello" + str(result))
root = parseString(result.content)

services = list(map(lambda service: parse_service(service), root.getElementsByTagName('service')))
#print("hello")
#print(str(services))
content = [ service for service in services if service['name'] == 'urn:schemas-upnp-org:service:ContentDirectory:1' ][0]
#print(str(content))
request = '%s%s' % (minidlna, content['url'])
#print(str(request))

#print(str(get_object_id('0')))

result = requests.post(request, data=get_object_id('0'), headers=headers);
#print(str(result.status_code))
#print(str(result.content))
root = parseString(result.content)
body = parseString(root.getElementsByTagName('Result')[0].firstChild.nodeValue)

containers = list(map(lambda container: parse_container(container), body.getElementsByTagName('container')))
for container in containers:
    # print(container['index'], container['title'])

    result = requests.post(request, data=get_object_id(container['index']), headers=headers);
    root = parseString(result.content)
    body = parseString(root.getElementsByTagName('Result')[0].firstChild.nodeValue)
    # pretty = body.toprettyxml()
    # print(pretty)

    interesting_folders = ["Movies", "Raw"]

    folders = list(map(lambda container: parse_container(container), body.getElementsByTagName('container')))
    for folder in folders:
        if not folder['title'] in interesting_folders:
            continue
        print(folder['index'], folder['title'])

        result = requests.post(request, data=get_object_id(folder['index']), headers=headers);


#        print("result: " + str(result.content))
        root = parseString(result.content)
        body = parseString(root.getElementsByTagName('Result')[0].firstChild.nodeValue)

        sub_folders = list(map(lambda container: parse_container(container), body.getElementsByTagName('container')))

        for sf in sub_folders:
            if not sf['title'].startswith("All"):
                 continue
            print(sf['index'], sf['title'])

            result = requests.post(request, data=get_object_id(sf['index']), headers=headers);
            #print("result: " + str(result.content))
            root = parseString(result.content)
            body = parseString(root.getElementsByTagName('Result')[0].firstChild.nodeValue)


            # pretty = body.toprettyxml()
            # print(pretty)

            items = list(map(lambda item: parse_item(item), body.getElementsByTagName('item')))
            for item in items:
                print('Index', item['index'])
                print('Title', item['title'])
                print('Size', item['size'])
                print('Duration', item['duration'])
                print('Bitrate', item['bitrate'])
                print('Sampling', item['sampling'])
                print('Channels', item['channels'])
                print('Resolution', item['resolution'])
                print('Url', item['url'])
                print('----')

            print('----')