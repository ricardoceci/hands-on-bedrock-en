# Getting Started with Amazon Bedrock

Today, I'll explain how to get hands-on with Bedrock safely and reliably while also learning a bit about coffee.

You’ll learn how to use the [Amazon Bedrock API](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) for Text and Multimodal models using Python to generate names, logos, and menus for your coffee shop, and how to create an agent that connects to a Shopify API to take orders.

Shopify is (in my opinion) the best eCommerce platform out there.

And just like AWS, [Shopify](https://shopify.com) has an API for everything and a [developer platform](https://shopify.dev/).

Lastly, you’ll create a frontend using Streamlit to deliver a unique user experience and bring your agent to life.

## 📝 Table of Contents

- [Invoking the Bedrock API](#bedrockapi)
- [Creating an Amazon Bedrock Agent That Interacts with Shopify](#agent)


## 🧐 Invoking the Amazon Bedrock API to to generate, logo and menu for your Coffee Store<a name = "bedrockapi"></a>

The moment of opening a coffee shop or coming up with creative business ideas is an excellent opportunity to leverage Generative AI (GenAI) and make the most of it.

With Amazon Bedrock, you can utilize it, but... how do you consume this service?

Every AWS service has an API, and Amazon Bedrock is no exception. Below, I’ll explain how to consume the Amazon Bedrock API through an example to generate names and a menu for a coffee shop.

Additionally, I’ll show you how to consume a multimodal model capable of analyzing images.

### Instructions for Writing a Python Script to Run Locally or in a Lambda Function to Invoke Amazon Bedrock

First, you need to enable access to models in Bedrock [Instructions here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html).

### Requirements:

- An AWS account. If you don’t have one, you can create it [here](https://signin.aws.amazon.com/signup?request_type=register).
- AWS CLI [Instructions here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
- Python 3.11 or higher.

### Step 1: Create a Python Virtual Environment [Instructions here](https://docs.python.org/3.12/tutorial/venv.html)

In the `bedrock_examples` folder of [this repository](https://github.com/ricardoceci/hands-on-bedrock-en), you’ll find different examples used below to invoke the foundational model.

In the `prompts` folder, you’ll find example prompts that you can use to generate:
- The name.
- The menu.
- A prompt to pass to an image generation model, which you can invoke either in the [Amazon Bedrock Playground](https://docs.aws.amazon.com/bedrock/latest/userguide/playgrounds.html) or via the API using Python.

### Step 2: Install the Requirements
```bash
pip install -r requirements.txt
```


### Step 3: Configure Boto3 [More info on Boto3](https://aws.amazon.com/sdk-for-python/)

Here, I configure the AWS client by specifying that it should use the `genaiday` profile installed on my computer. 

```python
#Cambiar la region y el perfil de AWS
aws = boto3.session.Session(profile_name='genaiday', region_name=region)
client = aws.client('bedrock-runtime')
```

### Step 4: Example - Invoking a Text Model

This function calls the **invoke_model** method, passing the prompt provided by the user and returning the response.

The most important part is the messages sent:

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

Example:

```python
print("Haiku")
print(call_text("I am looking to set up a grab-and-go coffee shop. Give me 5 names for the shop.")
```

### Step 5: Example - Invoking a Multimodal Model

The process here is similar, except that **you need to add the MIME type** of the file being sent. For this, there is a function that obtains the MIME type based on the file name.


```python
def read_mime_type(file_path):
    # This hack is for Python versions prior to 3.13
    # This function reads the MIME type of a file
    mimetypes.add_type('image/webp', '.webp')
    mime_type = mimetypes.guess_type(file_path)
    return mime_type[0]
```

Then, to invoke the model, the messages should be as follows:


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

Model invocation final code:

```python
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
```

Example:

```python
pic_path = "./TEST_IMAGE.jpg"
caption = "How many people are in the image?"
print("Haiku")
print(call_image(pic_path,caption,"anthropic.claude-3-haiku-20240307-v1:0"))
print("Sonnet")
print(call_image(pic_path,caption,"anthropic.claude-3-sonnet-20240229-v1:0"))
```

## 🏁 Creating an Amazon Bedrock Agent That Interacts with Shopify <a name="agente"></a>

To create an Amazon Bedrock agent:

Make sure the Bedrock models you want to use have access enabled. [Instructions here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html). In this case, we will use Claude 3 Haiku and Sonnet.

Then, create the Bedrock agent in the AWS Console:

1. Go to the Bedrock service.
2. Select **Agents**.
3. Click on **Create Agent**.

![Create Agent](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/create_agent_1.jpg?raw=true)

4. Give the agent a name, in our case, "Pausa-Cafetera-Agente."
5. The description is optional.
6. One of the most important steps is selecting the foundational model that will make your agent work effectively. If you want to learn how to choose the best model for your use case, [this guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html) provides insights on Amazon Bedrock Model Evaluation.
7. The next step is defining the prompt that will guide your model. Be as precise as possible and showcase your skills as a prompt engineer. If you’re not sure where to start, I recommend checking out [this guide](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html) for the best practices for the model you’re using. Another helpful resource is [Anthropic's console](https://console.anthropic.com/dashboard).

![Create Agent Step 2](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/create_agent_2.jpg?raw=true)

This is the prompt I used for the example agent. I recommend writing the prompt in English since the models are trained in English, and using the original training language can help avoid erroneous behaviors.

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
8) **Additional Configuration**: You need to allow the agent to capture user input, as it will likely require more information to process the order. For example, the agent may need to ask for the products the customer wants, their name, and other details.

![Create Agent Step 3](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/create_agent_3.jpg?raw=true)

9) **Action Groups**: An action group defines the tasks the agent can assist the user with. For example, you can define an action group named `TakeOrder` that includes the following actions:
   - List products
   - Process order

To create an action group, you will need the following for each action:
   - **Name**
   - **Parameters**

Action groups are typically executed by invoking a Lambda function. From Bedrock, you can:
   - Create a Lambda function directly from the Bedrock console (select **Quick Create a Lambda Function**).

![Create Agent Step 4](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/create_agent_4.jpg?raw=true)

   - Use an existing Lambda function. [Instructions here](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html) describe the expected event and response format for each action group.

If you choose to create the Lambda function from the Bedrock console, it will generate a basic Python function, which you will need to modify. In this [repository](https://github.com/ricardoceci/hands-on-bedrock-en/) under `agents/action_group/lambda.py`, you’ll find an example of modified code to work with the agent.

### Variables Provided for Action Groups:
- **`function`**: The name of the invoked action. For example, this could be `get_products` (to list products) or `place_order` (to generate an order in Shopify).
- **`parameters`**: A dictionary of parameters.

### Example: Action Definitions
In the following example, you can see two actions:

![Create Agent Step 5](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/create_agent_5.jpg?raw=true)

![Create Agent Step 6](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/create_agent_5.jpg?raw=true)

- **`get_products`**: Does not require any parameters.
- **`place_order`**: Requires three parameters:

| Parameter      | Description                                                                                         | Type   | Required |
|----------------|-----------------------------------------------------------------------------------------------------|--------|----------|
| `customerEmail`| Email of the customer                                                                               | string | False    |
| `customerName` | Name of the customer                                                                                | string | True     |
| `products`     | SKUs and quantities to add to the cart in the format [{ variantId: variantId, quantity: QUANTITY }] | array  | True     |

### Example: Handling `get_products` in the Lambda Function

There is a `get_products` function defined to query the Shopify API (for demonstration purposes, all products are returned).

To make this work with Shopify, replace the following variables with those from your store:


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

Next, in the Lambda function handler, the name of the called function is verified, and the response is returned in the format required by the action group:


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

LThe code snippets shown above are part of the Lambda function, which can be found [here](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/agents/action_group/lambda.py).

10) Press **Save and Exit**, and that’s it! The agent is now ready to be tested.

## The Agent in Action

The next step is to test the agent and validate its functionality. From Bedrock, you can test the agent. During the conversation, if you click on **"Show Trace"**, it will display the reasoning process. This is where you should pay close attention and make any necessary adjustments to the prompt or consider switching to a different model if the one chosen does not perform as expected.

Once you’re satisfied with the agent, you can create an **Alias**. An alias is an ID you can use to invoke the agent via the Amazon Bedrock API. When you create an alias, a version of the agent is created automatically, or you can point to an existing version. Having multiple aliases and versions allows you to control the agent's deployment process effectively. For example:
- An alias **"development"** for the latest tests of the agent.
- An alias **"preprod"** for the agent in pre-production mode.
- An alias **"prod"** for the live agent.

You then just need to point the production alias to the version you want live.

### How to Invoke the Agent

For this, in the [agents/frontend](https://github.com/ricardoceci/hands-on-bedrock-en/tree/master/agents/frontend) folder, you’ll find a file called `agent.py`.

This implementation uses [Streamlit](https://streamlit.io/), a powerful framework for building machine learning demo applications.

The part of the code that invokes the agent is as follows:


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

We use Boto3 to consume the AWS API, calling the `bedrock-agent-runtime` client to invoke the agent.

The parameters we need to pass are:
- **agentId**
- **agentAliasId**
- **inputText** (the prompt)
- **sessionId** (the session to identify conversations)

In this example, the variables are defined as follows:


```python
with st.sidebar:
    agent_id = st.text_input("Agent ID", key="bedrock_agent_id")
    agent_alias_id = st.text_input("Agent Alias", key="bedrock_agent_alias")
    session_id = st.text_input("Sesion Id", key="session_id")
```

## Installation:

First, enable access to the models in Bedrock [Instructions here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html).

### Requirements:
- **AWS CLI**: [Instructions here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Python 3.11 or higher**

It is recommended to create a Python virtual environment. [Instructions here](https://docs.python.org/3.12/tutorial/venv.html).


```
pip install -r requirements.txt
```

## Execution

```
streamlit run agent.py
```

This will start Streamlit on port 8501, and you can visit the following URL: [http://localhost:8501/](http://localhost:8501/) to view the frontend that will invoke the agent.

![Demo Frontend with Streamlit](https://github.com/ricardoceci/hands-on-bedrock-en/blob/master/images/demo_front.jpg?raw=true)

## Conclusion

If you have followed all the steps, you have:
- Consumed the Amazon Bedrock API from the Bedrock Playground and from Python.
- Invoked foundational text and multimodal models.
- Created an agent from scratch that consumes a Shopify API.

### Useful Links to Continue Your Generative AI Journey:
- [AWS Generative AI Workshop](https://catalog.workshops.aws/building-gen-ai-apps/en-US)
- [Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)
- [Anthropic Console](https://console.anthropic.com/dashboard) (For debugging prompts)
- [AWS Community](https://community.aws) (More articles created by and for the community)
