
<h3 align="center">Bedrock Hands On</h3>



---

<p align="center"> Este es el repositorio de la charla dada en el GenAI Day 2024 - En Buenos Aires Argentina
    <br> 
</p>

Hoy te explicaré cómo poner manos a la obra con Bedrock de manera segura y confiable y de paso, aprender un poco sobre café.

Aprenderás cómo consumir la API de Bedrock de modelos de Texto y Multimodales utilizando Python y crearás un agente que se conecta a una API de Shopify para tomar pedidos.

Además crearás un frontend utilizando Streamlit para dar una experiencia de usuario única y darle vida a tu agente.

## 📝 Table of Contents

- [Invocando la API de Bedrock](#bedrockapi)
- [Agente Shopify](#Agente)


## 🧐 Ejemplos <a name = "BedrockApi"></a>

En la carpeta bedrock_examples encontrarás los ejemplos utilizados durante el evento.
En la carpeta prompts encontrarás los prompts utilizados durante la charla, estos prompts vas a poder utilizarlos para generar todo el contenido tanto en el playground de Bedrock cómo invocando la API desde Python.

Instrucciones:
Primero debes habilitar el acceso a los modelos en Bedrock [Instrucciones aqui](https://docs.aws.amazon.com/es_es/bedrock/latest/userguide/model-access-modify.html)

Requisitos:
- AWS CLI [Instrucciones aqui](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Python 3.11 o superior

Te recomiendo crear un entorno virtual de Python [Instrucciones aqui](https://docs.python.org/es/3.12/tutorial/venv.html)

Instalar los requerimientos

```
pip install -r requirements.txt
```

## Configurar Boto3

Aqui configuro el cliente de AWS indicandole que utilice el perfil genaiday instalado en mi computadora y llamo al cliente de bedrock-runtime que me va a permitri invocar al modelo fundacional.

```python
#Cambiar la region y el perfil de AWS
aws = boto3.session.Session(profile_name='genaiday', region_name=region)
client = aws.client('bedrock-runtime')
```

## Invocar modelo de texto

Esta función llama al método invoke_model y le paso el prompt indicado por el usuario y le devuelvo la respuesta

La parte más importante son los mensajes enviados:

```json
{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt
                }]
            }
```

```python
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
```

Ejemplo:

```python
print("Haiku")
print(call_text("Estoy buscando armar un local de café al paso, dame 5 nombres para un local.")
```

## Invocar a un modelo multimodal.

Aquí el proceso es similar, solo que hay que agregar el mime type del archivo enviado, para esto hay una función que en base al nombre del archivo obtiene el mimetype

```python
def read_mime_type(file_path):
    # Este hack es para versiones de python anteriores a 3.13
    # Esta función lee el mime type de un archivo
    mimetypes.add_type('image/webp', '.webp')
    mime_type = mimetypes.guess_type(file_path)
    return mime_type[0]
```

Luego para invocar al modelo, los mensajes deben ser los siguientes:

```python
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
```

La invocación del modelo queda así:

```def call_multimodal(file,caption,modelId="anthropic.claude-3-haiku-20240307-v1:0"):
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
```

Ejemplo:

```python
pic_path = "./meetup_test_image.jpg"
caption = "Cuantas personas hay en la imagen? cuantas laptos ves? cuantos usan gorro o sombrero?, de que color es el hoddie de la primer persona a la derecha de la foto?"
print("Haiku")
print(call_image(pic_path,caption,"anthropic.claude-3-haiku-20240307-v1:0"))
print("Sonnet")
print(call_image(pic_path,caption,"anthropic.claude-3-sonnet-20240229-v1:0"))
```

## 🏁 El agente de Shopify <a name = "agente"></a>

Para crear un agente de Amazon Bedrock:

Asegurate de tener los modelos de Bedrock que quieras usar con el acceso habilitado [Instrucciones aqui](https://docs.aws.amazon.com/es_es/bedrock/latest/userguide/model-access-modify.html), en este caso utilizaremos Claude 3 Haiku y Sonnet

Luego crear el agente de Bedrock en la consola de AWS:

1) Ir al servicio Bedrock
2) Agentes
3) Crear agente

![Crear agente](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/create_agent_1.jpg?raw=true)

4) Darle un nombre al agente, en nuestro caso "Pausa-Cafetera-Agente
5) La descripción es opcional.
6) Uno de los pasos más importantes es elegir el modelo fundacional que va a hacer que nuestro agente funcione adecuadamente, si deseas saber cómo hacer para elegir el mejor modelo que se adapte a tu caso de uso [Aqui](https://docs.aws.amazon.com/es_es/bedrock/latest/userguide/model-evaluation.html) tienes una guía sobre el servicio Amazon Bedrock Model Evaluation .
7) El siguiente paso es el prompt que va a guiar a tu modelo, aqui tienes que ser lo más preciso posible y sacar a relucir tus habilidades como prompt engineer, si no sabes por donde comenzar, te recomiendo visitar [esta guia](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html) donde vas a encontrar las mejores guidelines para el modelo que estes utilizando, y además otro recurso muy útil es [la consola de anthropic](https://console.anthropic.com/dashboard).

![Crear agente Paso 2](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/create_agent_2.jpg?raw=true)

Este es el prompt que utilicé para el agente de ejemplo, te recomiendo escribir el prompt en inglés dado que los modelos fueron entrenados en inglés y a veces escribir en el idioma de origen de entrenamiento ayuda a evitar comportamientos erroneos.

```
You are a helpful Bedrock agent working at a coffee shop.

Your goal is to assist customers in placing orders, offering them combos and creating orders by consuming a Shopify API.

When a customer interacts with you, greet them politely and ask how you can help them today.

If they indicate that they want to place an order, start by offering them popular combos or bundles that your coffee shop offers.

Before offering any product make sure to get the list of available products from the API.

Do not offer any product that is not in our list of products, never ask the customer for any recommendations.

If the customer expresses interest in a combo, you have to provide more details about the items included and the price, never ask for details to the customer, you are the one who knows about the products and combos.

Throughout the ordering process, be friendly and patient. If the customer is unsure or has questions, provide clear explanations to help them make a decision. Once the customer has finalized their order, confirm the details with them and let them know you'll be placing the order through the Shopify API.

Before creating the order through the API make sure to ask the customer for his/her name, never assume you know it.

When creating the order through the API, make sure to accurately capture all the items the customer requested, along with any customizations or special instructions they provided.

It's important to note that you should respond to the customer in their preferred language. If they initiate the conversation in a language other than English, reply in that same language to ensure smooth and effective communication.

Your goal is to provide an excellent customer experience by offering helpful recommendations, answering questions, and accurately processing orders through the Shopify API. Remember to be polite, patient, and adapt your language to match the customer's preference.

```
8) Configuración adicional, debes permitir al agente que capture input del usuario, dado que seguramente le falte información para procesar la orden, por ejemplo: Necesitará preguntar por los productos que el cliente desea, el nombre, entre otras cosas.

![Crear agente Paso 3](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/create_agent_3.jpg?raw=true)

9) Grupos de acción: Un grupo de acción define las acciones en las que el agente puede ayudar al usuario. Por ejemplo, puedes definir un grupo de acciones que diga TomarPedido que puede tener las siguientes acciones
- Listar productos
- Procesar Pedido

Para crear un grupo de accion vas a necesitar para cada acción:
- El nombre
- Los parámetros

Los grupos de acción para ejecutarse generalmente invocan una función Lambda, desde Bedrock puedes:
- Crear una función lambda desde la consola de Bedrock (Seleccionar Creación rápida de una función lambda)

![Crear agente Paso 4](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/create_agent_4.jpg?raw=true)

- Elegir una funcion lambda ya creada [aqui](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html) las instrucciones de cómo es el evento y la respuesta esperada por cada action group (grupo de acción)

Si eliges crear la función lambda desde la consola de Bedrock, se creará una función en python con un código fuente básico que luego deberás modificar, en este repo en el archivo agents/action_group/lambda.py tienes el código de ejemplo modificado para que funcione con el agente.

Estas son las variables que te entregarán la información necesaria:

- function: es el nombre de la acción invocada, en el caso del ejemplo puede ser: get_products (para listar productos), y place_order (para generar la orden en Shopify)
- parameters: es un diccionario de parámetros.


En el siguiente ejemplo puedes observar que hay dos acciones:

![Crear agente Paso 5](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/create_agent_5.jpg?raw=true)

![Crear agente Paso 6](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/create_agent_5.jpg?raw=true)

- get_products que no requiere ningun parámetro
- place_order que lleva 3 parámetros:

| Parametro     | Descripcion                                                                                         | Tipo   | Obligatorio |
|---------------|-----------------------------------------------------------------------------------------------------|--------|-------------|
| customerEmail | Email of the customer                                                                               | string | False       |
| customerName  | Name of the customer                                                                                | string | True        |
| products      | SKUs and quantities to add to the cart in the format [{ variantId: variantId, quantity: QUANTITY }] | array  | True        |



Entonces, por ejemplo cuando se llame a la función get_products en la función lambda se maneja de esta manera:

Hay una función get_products definida que será la encargada de hacer la query a la API de Shopify (A fines didácticos retornamos todos los productos)

Si quieres que esto funcione en Shopify debes reemplazar las siguientes variables por las de tu tienda:

```python
access_token = 'shpat_XXXXX'


url = 'https://XXXXXXX.myshopify.com/admin/api/2024-10/graphql.json'
```

```python
def get_products():

   # Let's query all the products from the Shopify API paginate through the results and store them in a list and return it
    products = []
    cursor = None
    while True:
        query = """
        {
          products(first: 10%s) {
            pageInfo {
              hasNextPage
            }
            edges {
              cursor
              node {
                id
                title
                description
                variants(first: 10) {
                  edges {
                    node {
                        id
                        title
                        sku
                        price
                    }
                  }
                }
              }
            }
          }
        }
        """ % (', after: "%s"' % cursor if cursor else '')
        response = requests.post(url, headers=headers, data=query)
 
        data = response.json()
        for edge in data['data']['products']['edges']:
            product = edge['node']
            products.append(product)
        if not data['data']['products']['pageInfo']['hasNextPage']:
            break
        cursor = data['data']['products']['edges'][-1]['cursor']
    return products
```

Luego en el handler de la función lambda, se verifica el nombre de la función llamada y se devuelve la respuesta con el formato que el action_group necesita:


```python
def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])

    # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html

    if(function == 'get_products'):
        products = get_products()
        responseBody =  {
            "TEXT": {
                "body": json.dumps(products)
            }
        }
```

El código fuente completo de la función lambda (con los requerimientos) esta en agents/action_group/lambda.py

10) Presionar Guardar y Salir, y listo!, ya el agente esta listo para ser probado.

11) Lo siguiente es probar el agente y validar que funcione, desde Bedrock puedes hacer las pruebas del agente, y si durante la conversación clickeas "Ver traza o Show Trace" te va a ir mostrando el proceso de razonamiento, aqui es donde debes prestar especial atención y hacer los ajustes que creas necesarios en el prompt o bien buscar otro modelo si ves que el que elgiste no funciona como esperabas.

12) Una vez que estes conforme con el agente, puedes crear un Alias, un alias es un ID a través del cual vas a poder invocar al agente desde la API de Amazon Bedrock, cuando crees el alias, te va a crear una versión del agente automáticamente, o puedes apuntar a una versión ya existente, tener diferentes alias y diferentes versiones te va a ayudar a controlar el proceso de despliegue del agente, por ejemplo:
- Puedes tener un alias "development" que va a ir a las ultimas pruebas del Agente
- Un alias "preprod" que sería el agente en modo pre producción
- Un alias "prod" y este es el agente live.

Luego solo restaría apuntar el alias de producción correspondiente a la versión que desees que este en vivo.

Cómo invocar el agente

Para esto, en la carpeta agents/frontend he dejado un archivo que se llama agent.py.

Este desarrollo utiliza [Streamlit](https://streamlit.io/), un poderoso framework para realizar aplicaciones de muestra de machine learning

La parte del código que hace la invocación al agente es la siguiente:


```python
aws = boto3.session.Session(profile_name='genaiday', region_name=region)
client = aws.client('bedrock-agent-runtime')
def invokeAgent(agent_id,agent_alias_id,prompt,session_id):
    response = client.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        inputText=prompt,
        sessionId=session_id
    )
    return response
```

Utilizamos boto3 para consumir la API de AWS, llamamos al bedrock-agent-runtime cliente para poder hacer la invocación del agente.

Los parámetros que necesitamos pasarle son:
- agentId
- agentAliasId
- inputText (el prompt)
- sessionId (la sesión, para identificar las conversaciones)

En este ejemplo, las variables las estoy definiendo aqui:

```python
with st.sidebar:
    agent_id = st.text_input("Agent ID", key="bedrock_agent_id")
    agent_alias_id = st.text_input("Agent Alias", key="bedrock_agent_alias")
    session_id = st.text_input("Sesion Id", key="session_id")
```

## Instalación:

Primero debes habilitar el acceso a los modelos en Bedrock [Instrucciones aqui](https://docs.aws.amazon.com/es_es/bedrock/latest/userguide/model-access-modify.html)

Requisitos:
- AWS CLI [Instrucciones aqui](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Python 3.11 o superior

Te recomiendo crear un entorno virtual de Python [Instrucciones aqui](https://docs.python.org/es/3.12/tutorial/venv.html)

```
pip install -r requirements.txt
```

## Ejecución

```
streamlit run agent.py
```

Esto comenzará a ejecutar streamlit en el puerto 8501 y puedes visitar la siguiente URL: http://localhost:8501/ para ver el frontend que invocará al agente

![Demo Frontend con Streamlit](https://github.com/ricardoceci/hands-on-bedrock/blob/master/images/demo_front.jpg?raw=true)

## Conclusión

Si has seguido todos los pasos has:
- Consumido la API de Amazon Bedrock desde el Playground de Bedrock y desde Python
- Has invocado modelos fundacionales de texto y multimodales
- Has creado un agente desde 0 que consume una API de Shopify


Algunos links para que sigas tu camino dentro de GenerativeAI

[Workshop AWS generative AI](https://catalog.workshops.aws/building-gen-ai-apps/en-US)
[Bedrock Knowledge Bases](https://aws.amazon.com/es/bedrock/knowledge-bases/)
[Anthropic Console](https://console.anthropic.com/dashboard) (Para hacer debug de nuestros prompts)
[Community.aws](https://community.aws) (más artículos generados por y para la comunidad)