import boto3, urllib, urllib.request, csv, os, json, platform, ast, hashlib, pdb

mysession = boto3.session.Session(aws_access_key_id='SECRET', aws_secret_access_key='SECRET', region_name='us-west-2')

dynamodb = mysession.resource('dynamodb')

s3 = mysession.resource('s3')
tourBucket = s3.Bucket('dornsifetourtest')
imageBucket = s3.Bucket('dornsifeimagetest')
audioBucket = s3.Bucket('dornsifeaudiotest')


def csv2matrix(csvFilename):
    if csvFilename.split('.')[-1] != 'csv':
        csvFilename += '.csv'
    #csvFilename = input("Enter data file name (.csv): ")
    try:
        myFile = open(csvFilename, encoding='utf-8')
        csvF = csv.reader(myFile)
        data = []
        tableHeight = 0
        tableWidth = 0
        for line in csvF:
            data.append(line)
            tableHeight += 1
    except:
        myFile2 = open(csvFilename)
        csvF2 = csv.reader(myFile2)
        data = []
        tableHeight = 0
        tableWidth = 0
        for line in csvF2:
            data.append(line)
            tableHeight += 1
    myFile.close()
    try:
        data[0][0] = data[0][0].replace('\ufeff','')
        tableWidth = len(data[0])
    except:
        print("There are no rows of data")

    dataDict = {}
    dataList = []
    fieldNames = data[0]
    for row in range(1,len(data)):
        tempDict = {}
        for index, name in enumerate(fieldNames):
            if data[row][index] != "":
                tempDict[name] = data[row][index]
        #adding the hashing. Change this hashing function later!
        tempDict['Verify']=hashlib.sha256(str(data[row]).encode('utf-8','ignore')).hexdigest()
        #tempDict['Verify']=str(hash(tuple(data[row])))
        dataDict[tempDict['ID']] = tempDict
        dataList.append(tempDict)
    return (dataList, dataDict)

def makeTable(tableName):
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'ID',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ID',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)

def scanChanges(csvFilename, tableName):
    dataList, dataDict = csv2matrix(csvFilename)

    table = dynamodb.Table(tableName)
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
    answer = ''
    for item in dataList:
        if item['Verify'] not in tableHashes:
            newHash.append(item)

    for item in newHash:
        if item['ID'] not in tableDataDict.keys():
            newData.append(item)
        else:
            changedData.append(item)
    return (newData, changedData, tableDataDict)

def updateTable(csvFilename, tableName):
    newData, changedData,tableDataDict = scanChanges(csvFilename, tableName)

    table = dynamodb.Table(tableName)
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

def getToursCsv():
    bucket = tourBucket
    bucketKeys = bucket.objects.all()
    bucketKeyList = []
    for item in bucketKeys:
        bucketKeyList.append(item.key)

    for key in bucketKeyList:
        dictKeys = []
        bigString = ""
        keyString = ""
        responseList = json.loads(bucket.Object(key).get()['Body'].read())
        responseList = sorted(responseList, key=lambda item:int(item['ID']))
        for item in responseList:
            if len(item.keys())>len(dictKeys):
                dictKeys = item.keys()
        for thisKey in dictKeys:
            keyString += thisKey
            keyString += ','
        keyString += '\n'
        bigString += keyString
        for item in responseList:
            itemString = ""
            for thisKey in dictKeys:
                try:
                    #if item[key].contains('green collar'):
                    #    pdb.set_trace()
                    itemString += '\"' + item[thisKey].replace('\"','\"\"') + '\"'
                except:
                    pass
                itemString += ','
            itemString += '\n'
            bigString += itemString
        with open(key.replace('.json','') + '.csv', 'w') as write:
            write.write(bigString)

def downloadFromS3():
    bucket = tourBucket
    bucketKeys = bucket.objects.all()
    bucketKeyList = []
    for item in bucketKeys:
        bucketKeyList.append(item.key)

    for key in bucketKeyList:
        bucket.download_file(key, 'download/' + key)

def downloadFromURL(filename, bucketName):
    urllib.request.urlretrieve('https://s3-us-west-2.amazonaws.com/' + bucketName + filename, 'download/' + filename)

#basically all on console
def individualDelete(tableName):
    table = dynamodb.Table(tableName)
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

def loadBackup(filename):
    if filename.split('.')[-1] != 'json':
        filename += '.json'
    myFile = open(filename,'r')
    data = myFile.read()
    myFile.close()
    dataDict = dict(ast.literal_eval(data))
    return dataDict['Items']

def packageData(filename, tableName):
    if filename.split('.')[-1] != 'json':
        filename += '.json'
    table = dynamodb.Table(tableName)
    with open('mydir/' + filename,'w') as myFile:
        myFile.write(str(json.dumps(table.scan()['Items'])))

def reloadData(newDataFilename, backupFilename, tableName):
    if backupFilename.split('.')[-1] != 'json':
        backupFilename += '.json'
    table = dynamodb.Table(tableName)
    data = table.scan()
    tableDataList = data['Items']

    myFile = open(backupFilename, 'w')
    myFile.write(str(data))
    myFile.close()

    with table.batch_writer() as batch:
        for item in tableDataList:
            batch.delete_item(
                Key={
                    'ID': item['ID']
                }
            )

    updateTable(newDataFilename, tableName)

def uploadToS3():
    imageExtensions = ['jpg','png','jpeg','JPG']
    audioExtensions = ['mp3']
    junk = False

    tourKeys = tourBucket.objects.all()
    imageKeys = imageBucket.objects.all()
    audioKeys = audioBucket.objects.all()
    bucketKeyList = []
    for item in tourKeys:
        bucketKeyList.append(item.key)
    for item in imageKeys:
        bucketKeyList.append(item.key)
    for item in audioKeys:
        bucketKeyList.append(item.key)

    for filename in os.listdir(os.getcwd() + '/mydir/'):
        if filename not in bucketKeyList:
            data = open(os.getcwd() + '/mydir/' + filename, 'rb')
            extension = filename.split('.')[-1]
            #bucket.upload_file(os.getcwd() + '/mydir/' + filename, filename) #Could be upload_fileobj
            if extension == 'json':
                tourBucket.put_object(Key=filename, Body = data, ACL = 'public-read', ContentType = 'application/json')
            elif extension in imageExtensions:
                imageBucket.put_object(Key=filename, Body = data, ACL = 'public-read')
            elif extension in audioExtensions:
                audioBucket.put_object(Key=filename, Body = data, ACL = 'public-read')
            else:
                junk = True
                #bucket.put_object(Key=filename, Body = data, ACL = 'public-read')
            data.close()
    return junk
