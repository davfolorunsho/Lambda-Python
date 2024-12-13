import json
import os
import boto3
import uuid
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path_parameters = event.get('pathParameters', {})
    item_id = path_parameters.get('id')

    if http_method == 'GET':
        if item_id:
            return get_todo_item(item_id)
        else:
            return get_all_todo_items()
    elif http_method == 'POST':
        return create_todo_item(json.loads(event['body']))
    elif http_method == 'PUT' and item_id:
        return update_todo_item(item_id, json.loads(event['body']))
    elif http_method == 'DELETE' and item_id:
        return delete_todo_item(item_id)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Unsupported method or missing item ID'})
        }

def get_all_todo_items():
    response = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }

def get_todo_item(item_id):
    response = table.get_item(Key={'id': item_id})
    if 'Item' in response:
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'])
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Item not found'})
        }

def create_todo_item(data):
    item = {
        'id': data.get('id', str(uuid.uuid4())),
        'name': data['name'],
        'description': data.get('description', ''),
        'status': data.get('status', 'todo'),
        'dueDate': data.get('dueDate', None)
    }
    table.put_item(Item=item)
    return {
        'statusCode': 201,
        'body': json.dumps(item)
    }

def update_todo_item(item_id, data):
    response = table.update_item(
        Key={'id': item_id},
        UpdateExpression="set #name = :n, description = :d, status = :s, dueDate = :dd",
        ExpressionAttributeNames={'#name': 'name'},
        ExpressionAttributeValues={
            ':n': data['name'],
            ':d': data.get('description', ''),
            ':s': data.get('status', 'todo'),
            ':dd': data.get('dueDate', None)
        },
        ReturnValues="ALL_NEW"
    )
    return {
        'statusCode': 200,
        'body': json.dumps(response['Attributes'])
    }

def delete_todo_item(item_id):
    table.delete_item(Key={'id': item_id})
    return {
        'statusCode': 204,
        'body': json.dumps({'message': 'Item deleted successfully'})
    }