import os, io, sys
import json
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson, MessageToDict

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'gilbreth-token.json'

def ocrUrl():
    client = vision.ImageAnnotatorClient()
    img_url = "https://i.imgur.com/rsRQgEM.jpg"
    image = vision.types.Image()
    image.source.image_uri = img_url

    response = client.document_text_detection(image=image)

    # docText = response.full_text_annotation.pages

    return response

def ocrLocal(name):
    client =vision.ImageAnnotatorClient()
    
    file_name = name
    path = file_name

    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.types.Image(content = content)
    response = client.document_text_detection(image=image)

    # return response
    # return json.dumps(response), 200, {'Content-Type': 'application/json'}
    return response

# annotations = ocrLocal(sys.argv[1]).text_annotations
# # print(annotations[-1])
# for annotation in annotations:
#     print("NEW ANNOTATION")
#     print(annotation)
# print(ocrLocal(sys.argv[1]))