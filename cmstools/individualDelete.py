import boto3, os, platform

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test')
data = table.scan()
tableDataList = data['Items']
tableDataList = sorted(tableDataList, key=lambda item:int(item['ID']))
tableDict = {}
deleteIDs = []
for item in tableDataList:
    tableDict[item['ID']] = item['Name']




while True:
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
    print('ID\tName')
    print('--\t----')
    for key,value in tableDict.items():
        print(key + '\t' + value)
    answer = input("What ID would you like to delete? ")
    if answer not in tableDict.keys():
        break
    del tableDict[answer]
    deleteIDs.append(answer)

with table.batch_writer() as batch:
    for item in deleteIDs:
        batch.delete_item(
            Key={
                'ID': item
            }
        )
