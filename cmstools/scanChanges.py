import boto3, pdb
from csv2matrix import dataList, dataDict

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test')

data = table.scan()
tableDataList = data['Items']
tableDataDict = {}
for item in tableDataList:
    tableDataDict[item['ID']] = item
tableHashes = []
tableIDs = []
for dictionary in tableDataList:
    tableHashes.append(dictionary['Verify'])
    #tableIDs.append(dictionary['ID'])
newHash = []
newData = []
changedData = []
#itemsToChange = []
answer = ''
for item in dataList:
    if item['Verify'] not in tableHashes:
        newHash.append(item)

for item in newHash:
    if item['ID'] not in tableDataDict.keys():
        newData.append(item)
    else:
        changedData.append(item)
        #pdb.set_trace()
        #changedData.append(item)
#print('\n' + len()
#print('\nItem with ID ' + item['ID'] + ' has changed.\n')

"""for key, value in item.items():
    if item[key] != tableDataDict[item['ID']][key] and key != 'Verify':
        print("Old " + key + ": " + tableDataDict[item['ID']][key])
        print("New " + key + ": " + item[key] + '\n')
print("Would you like to change this item? (y/n)")
answer = input()
if answer == 'y':
    changedData.append(item)"""
