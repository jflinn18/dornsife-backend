import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test')
data = table.scan()
tableDataList = data['Items']

print('The current table data will be backed up. What should the backup file name be?')
fileName = input()

myFile = open(fileName, 'w')
myFile.write(str(data))
myFile.close()

with table.batch_writer() as batch:
    for item in tableDataList:
        batch.delete_item(
            Key={
                'ID': item['ID']
            }
        )

import updateTable
