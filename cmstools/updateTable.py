from scanChanges import newData, changedData, tableDataDict
import boto3
import pdb

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test')
updatedData = []
answer = None

if len(changedData) == 1:
    print('\nItem with ID ' + changedData[0]['ID'] + ' has changed.\n')
    for key, value in changedData[0].items():
        if changedData[0][key] != tableDataDict[changedData[0]['ID']][key] and key != 'Verify':
            print("Old " + key + ": " + tableDataDict[changedData[0]['ID']][key])
            print("New " + key + ": " + changedData[0][key] + '\n')
    print("Would you like to change this item? (y/n)")
    answer = input()
    if answer == 'y':
        updatedData.append(changedData[0])
elif len(changedData) >= 2:
    print('\n' + str(len(changedData)) + ' items have changed.')
    print('Would you like to update these items?')
    print('1. Yes to all')
    print('2. No to all')
    print('3. Individual update')
    answer = input()
    if answer == '1':
        updatedData = changedData
    elif answer == '3':
        for item in changedData:
            print('\nItem with ID ' + item['ID'] + ' has changed.\n')
            for key, value in item.items():
                if item[key] != tableDataDict[item['ID']][key] and key != 'Verify':
                    print("Old " + key + ": " + tableDataDict[item['ID']][key])
                    print("New " + key + ": " + item[key] + '\n')
            print("Would you like to change this item? (y/n)")
            answer = input()
            if answer == 'y':
                updatedData.append(item)

for item in updatedData:
    table.delete_item(
        Key={
            'ID': item['ID']
        }
    )
    newData.append(item)

with table.batch_writer() as batch:
    for i in range(len(newData)):
        batch.put_item(
            Item = newData[i]
        )
