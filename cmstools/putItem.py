import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test1')
table.put_item(
   Item={
        'number': '4258779247',
        'firstName': 'Craig',
        'lastName': 'Colegrove',
        'age': 21,
        'address': '9722 N Stevens St. Spokane, WA',
    }
)
