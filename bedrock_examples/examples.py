import boto3
import json
from requests import request
import os
import mimetypes
import base64

region = 'us-east-1'
os.environ["AWS_REGION"] = region
llm_response = ""

#Cambiar la region y el perfil de AWS
aws = boto3.session.Session(profile_name='genaiday', region_name=region)
client = aws.client('bedrock-runtime')


def read_mime_type(file_path):
    # Este hack es para versiones de python anteriores a 3.13
    # Esta función lee el mime type de un archivo
    mimetypes.add_type('image/webp', '.webp')
    mime_type = mimetypes.guess_type(file_path)
    return mime_type[0]


def call_text(prompt,modelId="anthropic.claude-3-haiku-20240307-v1:0"):
    #esta función es para llamar un modelo de texto
    config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt
                }]
            }
        ]
    }

    body = json.dumps(config)
    modelId = modelId
    accept = "application/json"
    contentType = "application/json"

    response = client.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get("body").read())
    results = response_body.get("content")[0].get("text")
    return results


def call_multimodal(file,caption,modelId="anthropic.claude-3-haiku-20240307-v1:0"):
    #esta funcion es para llamar a un modelo multimodal con una imagen y un texto
    config = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                     "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": read_mime_type(file),
                            "data": base64.b64encode(open(file, "rb").read()).decode("utf-8")
                        }
                },
                {
                    "type": "text",
                    "text": caption
            }]
        }
    ]
    }

    body = json.dumps(config)
    modelId = modelId
    accept = "application/json"
    contentType = "application/json"

    response = client.invoke_model(
    body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get("body").read())
    results = response_body.get("content")[0].get("text")
    return results


# Ejemplos de uso:
# Texto:
#prompt = "Estoy por abrir una cafeteria al paso, recomiendame 5 nombres"
#print("Haiku")
#print(call_text(prompt,"anthropic.claude-3-haiku-20240307-v1:0"))

#print("Sonnet")
#print(call_text(prompt,"anthropic.claude-3-sonnet-20240229-v1:0"))


#Imagen
#pic_path = "./meetup_test_image.jpg"
#caption = "Cuantas personas hay en la imagen? cuantas laptos ves? cuantos usan gorro o sombrero?, de que color es el hoddie de la primer persona a la derecha de la foto?"
#print("Haiku")
#print(call_image(pic_path,caption,"anthropic.claude-3-haiku-20240307-v1:0"))
#print("Sonnet")
#print(call_image(pic_path,caption,"anthropic.claude-3-sonnet-20240229-v1:0"))




