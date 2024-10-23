
import json
import requests
access_token = 'shpat_XXXXX'


url = 'https://XXXXXXX.myshopify.com/admin/api/2024-10/graphql.json'
headers = {"Content-Type": "application/graphql",
           "X-Shopify-Access-Token": access_token}

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
def format_line_items(line_items):
    formatted_items = []
    for item in line_items:
        formatted_item = '{variantId: "%s", quantity: %d}' % (item['variantId'], item['quantity'])
        formatted_items.append(formatted_item)
    return '[%s]' % ', '.join(formatted_items)

def place_order(order):
  #Let's create a Shopify draft order, the lineItems should be a list of dictionaries
  

  query = """
  mutation {
    draftOrderCreate(input: {
      lineItems: %s,
      email: "%s",
      note: "%s",
      shippingAddress: {
        address1: "123 4th Street",
        city: "Minneapolis"
      }
      billingAddress: {
        address1: "123 4th Street",
        city: "Minneapolis"
       
      }
    }) {
      draftOrder {
        id
        name
        email
        lineItems(first: 10) {
          edges {
            node {
              title
              quantity
            }
          }
        }
      }
    }
  }
  """ % (format_line_items(order['lineItems']), order['email'], order['note']['value'])

  response = requests.post(url, headers=headers, data=query)
  data = response.json()
  return data



def lambda_handler(event, context):
    #Example of event

    ''' 
  {'messageVersion': '1.0', 'function': 'place_order', 'parameters': [{'name': 'customerName', 'type': 'string', 'value': 'Ricardo'}, {'name': 'products', 'type': 'array', 'value': '\n        [\n          {\n            "variantId": "gid://shopify/ProductVariant/44890218332291",\n            "quantity": 1\n          }\n        ]\n      '}], 'sessionId': '390844784120977', 'agent': {'name': 'pausa-cafetera-agent', 'version': 'DRAFT', 'id': 'AOOKJTKOGC', 'alias': 'TSTALIASID'}, 'sessionAttributes': {}, 'promptSessionAttributes': {}, 'inputText': '', 'actionGroup': 'ofrecer-productos-action'}
    '''
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
    
    if(function == 'place_order'):
     
      customerName = next((x for x in parameters if x['name'] == 'customerName'), None)
      customerEmail = next((x for x in parameters if x['name'] == 'customerEmail'), None)
      if customerEmail is None:
        customerEmail = {'value': 'ricardoceci@gmail.com'}
      
      cartProducts = next((x for x in parameters if x['name'] == 'products'), None)

      order = {
          'email': customerEmail['value'],
          'lineItems': []
      }

      for product in json.loads(cartProducts['value']):

        lineItem = {
          'variantId': product['variantId'],
          'quantity': product['quantity']
        }
        order['lineItems'].append(lineItem)
        order['note'] = customerName



      
      orderData = place_order(order)
      responseBody =  {
          "TEXT": {
              "body": json.dumps(orderData)
          }
      }


    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }

    }

    dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(dummy_function_response))

    return dummy_function_response
