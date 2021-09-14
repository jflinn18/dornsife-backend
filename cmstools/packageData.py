import boto3, json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test')
filename = input('Input filename to save data: ')
if filename.split('.')[-1] != 'json':
    filename = filename + '.json'
with open('mydir/' + filename,'w') as myFile:
    myFile.write(str(json.dumps(table.scan()['Items'])))
