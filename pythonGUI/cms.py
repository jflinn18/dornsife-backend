import boto3, urllib, urllib.request, csv, os, json, platform, ast, hashlib, pdb

# Open their AWS credentials from a file to avoid hard-coding it
credentialsFile = open('mydir/misc/rootkey.csv','r')
credentials = credentialsFile.read()
credentialsFile.close()
credentials = credentials.split('\n')
credentials[0] = credentials[0].split('=')
credentials[1] = credentials[1].split('=')
awsAccessKey = credentials[0][1]
awsSecretKey = credentials[1][1]

# Create the session to allow boto3 to access AWS
mysession = boto3.session.Session(aws_access_key_id=awsAccessKey, aws_secret_access_key=awsSecretKey, region_name='us-west-2')
dynamodb = mysession.resource('dynamodb')
s3 = mysession.resource('s3')

# Open their bucket names from a file to avoid hard-coding it
bucketFile = open('mydir/misc/bucketNames.txt','r')
bucketNameData = bucketFile.read()
bucketNames = dict(ast.literal_eval(bucketNameData))
bucketFile.close()

# Set bucket name variables
tourBucket = s3.Bucket(bucketNames['tour'])
businessBucket = s3.Bucket(bucketNames['business'])
imageBucket = s3.Bucket(bucketNames['image'])
audioBucket = s3.Bucket(bucketNames['audio'])
miscBucket = s3.Bucket(bucketNames['misc'])

# Open their table name from a file to avoid hard-coding it
tableNameFile = open('mydir/misc/pointsTableName.txt','r')
pointsTableName = tableNameFile.read()
tableNameFile.close()

# csv2matrix(csvFilename)
# makeTable(tableName)
# scanChanges(csvFilename, tableName)
# updateTable(csvFilename, tableName)
# getToursCsv()
# downloadFromS3()
# downloadFromURL(filename, bucketName)
# individualDelete(tableName)   --basically all on console
# loadBackup(filename)
# packageData(filename, tableName)
# reloadDate(newDataFilename, backupFilename, tableName)
# uploadToS3()

# Converts a .csv file into a list and dictionary of the file
# Assumes that the first row of the .csv is the dictionary names
# Takes in the filename of the .csv
# Returns the data in list and dictionary form
def csv2matrix(csvFilename):
    if csvFilename.split('.')[-1] != 'csv':
        csvFilename += '.csv'
    #csvFilename = input("Enter data file name (.csv): ")
    try:
        #defaulting utf-8 encoding to hopefully fix the first-character charmap issue
        myFile = open(csvFilename, encoding='utf-8')
        csvF = csv.reader(myFile)
        data = []
        tableHeight = 0
        tableWidth = 0
        for line in csvF:
            data.append(line)
            tableHeight += 1
    except:
        #alternative, using default encoding
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
        #make sure the utf character goes away
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
                #Tyler wants an array for the websites, so I split on space
                if name == 'additionalWebsites':
                    tempDict[name] = data[row][index].split(' ')
                    #pdb.set_trace()
                else:
                    tempDict[name] = data[row][index]
        #Removed the hashing function with the introduction of the CMS GUI
        #adding the hashing. Change this hashing function later!
        #tempDict['Verify']=hashlib.sha256(str(data[row]).encode('utf-8','ignore')).hexdigest()
        #tempDict['Verify']=str(hash(tuple(data[row])))
        dataDict[tempDict['ID']] = tempDict
        dataList.append(tempDict)
    #pdb.set_trace()
    return (dataList, dataDict)

# Creates a DynamoDB table with the specified name.
# Pauses to wait for the table to exist to avoid issues with false tablenames
# Takes in the name of the table to be created
# Returns nothing
def makeTable(tableName):
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                #We're always hashing on 'ID'
                'AttributeName': 'ID',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                #Our IDs are string, even though they are numbers
                'AttributeName': 'ID',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            #Trying to keep costs down, minimum capacity units
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)

# Finds differences between a .csv file and the current DynamoDB table data
# Calls the csv2matrix function to put the .csv into useable data types
# Takes in the .csv file name and the name of the DynamoDB table
# Returns a list of the new data, a list of the changed data, and a dictionary of the DynamoDB current data
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
    #for dictionary in tableDataList:
    #    tableHashes.append(dictionary['Verify'])
        #tableIDs.append(dictionary['ID'])
    #newHash = []
    newData = []
    changedData = []
    answer = ''
    #for item in dataList:
    #    if item['Verify'] not in tableHashes:
    #        newHash.append(item)

    #for item in newHash:
    #    if item['ID'] not in tableDataDict.keys():
    #        newData.append(item)
    #    else:
    #        changedData.append(item)
    #pdb.set_trace()
    return (dataList, [], tableDataDict)
    #second return deprecated with new CMS GUI
    #return (newData, changedData, tableDataDict)

# Updates DynamoDB with new, edited, and deleted points
# Order is: Upload new, delete edited, upload edited, delete old
# Takes in dictionaries of new and edited points, a list of deleted point IDs, and the name of the DynamoDB table
# Returns nothing, as it directly updates DynamoDB
def updatePoints(createdPointsDict, editedPointsDict, deletedPointsIDList, tableName):
    table = dynamodb.Table(tableName)

    """    newCreatedPointsDict = {}
    for key,point in createdPointsDict.items():


    for key, point in createdPointsDict.items():
        for innerKey, value in point.items():
            if value == "":
                deleteThese.append(innerKey)
                del createdPointsDict[key][innerKey]
        for item in deleteThese:
            del createdPointsDict

    for key, point in editedPointsDict.items():
        for innerKey, value in point.items():
            if value == "":
                del editedPointsDict[key][innerKey]"""

    #Upload all the new points
    with table.batch_writer() as batch:
        for newItem in createdPointsDict.values():
            batch.put_item(
                Item = newItem
            )

    #Deleting old points that are being edited
    for key in editedPointsDict.keys():
        table.delete_item(
            Key={
                'ID': key
            }
        )

    #Upload all the edited points
    with table.batch_writer() as batch:
        for newItem in editedPointsDict.values():
            batch.put_item(
                Item = newItem
            )

    #Deleting points that you want to delete
    for key in deletedPointsIDList:
        table.delete_item(
            Key={
                'ID': key
            }
        )

# Deletes specified tour names from the S3 Tours Bucket
# Takes in a list of tour names that will be deleted
# Returns nothing, as it directly modifies S3
def deleteTours(tourFileList):
    client = mysession.client('s3')
    for item in tourFileList:
        client.delete_object(Bucket=tourBucket.name, Key=item)

# Updates DynamoDB to reflect changes from a .csv
# has an optional parameter to confirm changes with the user in the console
# Takes in the name of the .csv, the name of DynamoDB table, and the 'prompts' boolean
# Returns nothing, as it directly updates DynamoDB
def updateTable(csvFilename, tableName, prompts = False):
    newData, changedData,tableDataDict = scanChanges(csvFilename, tableName)

    table = dynamodb.Table(tableName)
    updatedData = []
    answer = None
    if prompts == False:
        updatedData = changedData
    else:
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
                        if key in tableDataDict[item['ID']].keys():
                            if item[key] != tableDataDict[item['ID']][key] and key != 'Verify':
                                print("Old " + key + ": " + tableDataDict[item['ID']][key])
                                print("New " + key + ": " + item[key] + '\n')
                    print("Would you like to change this item? (y/n)")
                    answer = input()
                    if answer == 'y':
                        updatedData.append(item)

    #Delete old item
    for item in updatedData:
        table.delete_item(
            Key={
                'ID': item['ID']
            }
        )
        newData.append(item)

    #Upload new item
    with table.batch_writer() as batch:
        for i in range(len(newData)):
            batch.put_item(
                Item = newData[i]
            )

# Downloads the tour objects from S3 and writes them to a .csv file
# Takes in nothing, as it receives filenames from the S3 REST API
# Returns nothing, as it's creating a new file
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

# Downloads tour json objects from S3
# Takes in nothing, as it receives filenames from the S3 REST API
# Returns nothing, as it creates new files
def downloadFromS3():
    bucket = tourBucket
    bucketKeys = bucket.objects.all()
    bucketKeyList = []
    for item in bucketKeys:
        bucketKeyList.append(item.key)

    for key in bucketKeyList:
        bucket.download_file(key, 'download/' + key)

# Downloads an existing file from an S3 bucket
# Takes in the name of the file to retreive as well as what S3 bucket it's in
# Returns the data that is returned by S3's Rest API
def downloadFromURL(filename, bucketName):
    return urllib.request.urlretrieve('https://s3-us-west-2.amazonaws.com/' + bucketName + filename, 'download/' + filename)

# Gives console prompts to delete individual points from DynamoDB
# Takes in the DynamoDB tablename from which to read
# Returns nothing, as it directly updates DynamoDB
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
        #Trying to cover different OSs, even though our client is Windows
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

# An over-arching function that calls other functions in order to get all of AWS up to date
# Calls updateTable(), uploadToS3(), and optional updateBusinesses()
# Also prepares the current .csv file for upload as a json tour
# Takes in the name of the .csv file, the name of the DynamoDB table, and a boolean to specify whether to update businesses
# Returns nothing, as it directly updates DynamoDB and S3
def updateS3(csvFilename, tableName, businessUpdate = True):
    updateTable(csvFilename, tableName, False)
    uploadToS3(tableName)
    table = dynamodb.Table(tableName)
    data = table.scan()['Items']
    #Sorting the data so that it puts the IDs in the right order
    #If this were called from the CMS, it would NOT be sorted on ID
    data = sorted(data, key=lambda item:int(item['ID']))
    jsonUpload = str(json.dumps(data))
    csvFilename = csvFilename.split('/')[-1]
    csvFilename = csvFilename.split('.')[0]
    tourBucket.put_object(Key=csvFilename + '.json', Body = jsonUpload, ACL = 'public-read', ContentType = 'application/json')
    if businessUpdate == True:
        updateBusinesses(tableName)

# Reloads a backup file that was generated by reloadData()
# takes in the name of backup file
# Returns a dictionary of the data file
def loadBackup(filename):
    if filename.split('.')[-1] != 'json':
        filename += '.json'
    myFile = open(filename,'r')
    data = myFile.read()
    myFile.close()
    #Does a literal eval because it needs to know that what it's reading in is actually a python dict
    dataDict = dict(ast.literal_eval(data))
    return dataDict['Items']

# Packages all data on DynamoDB into a json file
# Takes in the name of the file to output and the name of the DynamoDB table
# Returns nothing, as it writes with file output
def packageData(filename, tableName):
    if filename.split('.')[-1] != 'json':
        filename += '.json'
    table = dynamodb.Table(tableName)
    with open('mydir/' + filename,'w') as myFile:
        myFile.write(str(json.dumps(table.scan()['Items'])))

# Takes random pictures from each type of location and uploads them to the business bucket
# Takes in the name of the DynamoDB table from which to get the image file names
# Returns nothing, as it outputs to S3
def updateBusinesses(tableName):
    table = dynamodb.Table(tableName)
    data = table.scan()['Items']
    businesses = {}
    businessImages = {}
    #categories = []
    for item in data:
        #Getting all of the names of the businesses
        if item['type'] not in businesses:
            #categories.append(item['type'])
            businesses[item['type']] = [item]
        else:
            businesses[item['type']].append(item)
        #if item['type'].lower() == 'business':
        #    businesses.append(item)
    for key, value in businesses.items():
        if key.lower() != 'waypoint':
            #Sort the business pages by ID
            body = json.dumps(sorted(value, key=lambda item:int(item['ID'])))
            businessBucket.put_object(Key=key.lower() + '.json', Body = body, ACL = 'public-read', ContentType = 'application/json')

    for key in businesses:
        for jsonObject in businesses[key]:
            if 'pictureFile' in jsonObject:
                #lowercase filenames
                businessImages[key.lower()] = jsonObject['pictureFile']
                break
    #businesses = sorted(businesses, key=lambda item:int(item['ID']))
    #jsonBusinesses = json.dumps(businesses)
    miscBucket.put_object(Key='businessImages.json', Body = json.dumps(businessImages), ACL = 'public-read', ContentType = 'application/json')

# Simple function to scan a DynamoDB table
# Takes in the name of the table
# Returns the 'Items' dictionary value of the DynamoDB table scan
def scanDynamoDBTable(tableName):
    table = dynamodb.Table(tableName)
    return table.scan()['Items']

# Deletes everything from the DynamoDB table and loads it again from a .csv
# Before deleting, it backs up all the data into a specified file
# Takes in the .csv file name, the desired name for the backup, and the name of the DynamoDB table
# Returns nothing, as it outputs to DynamoDB
def reloadData(newDataFilename, backupFilename, tableName):
    if backupFilename.split('.')[-1] != 'json':
        backupFilename += '.json'
    table = dynamodb.Table(tableName)
    data = table.scan()
    tableDataList = data['Items']

    myFile = open(backupFilename, 'w')
    myFile.write(str(data))
    myFile.close()

    #Delete all points from the DynamoDB
    with table.batch_writer() as batch:
        for item in tableDataList:
            batch.delete_item(
                Key={
                    'ID': item['ID']
                }
            )

    updateTable(newDataFilename, tableName)

# Uploads resources (images and audio) from '/mydir/images/' and '/mydir/audio/' to respective S3 buckets
# Takes in the DynamoDB table name
# Returns nothing, as it outputs to S3
def uploadToS3(tableName):
    #updateBusinesses(tableName)
    imageExtensions = ['jpg','jpeg','JPG']
    audioExtensions = ['mp3']

    #tourKeys = tourBucket.objects.all()
    imageKeys = imageBucket.objects.all()
    audioKeys = audioBucket.objects.all()
    audioKeyList = []
    imageKeyList = []
    """for item in tourKeys:
        bucketKeyList.append(item.key)"""
    for item in imageKeys:
        imageKeyList.append(item.key)
    for item in audioKeys:
        audioKeyList.append(item.key)

    #trying to avoid issues with paths
    for filename in os.listdir(os.getcwd() + '/mydir/audio/'):
        if filename in audioKeyList:
            response = mysession.client('s3').get_object(Bucket=bucketNames['audio'], Key=filename)
            #response=imageBucket.get_object(Key=filename)
            #Finding the size of the image in S3
            s3Size = response['ContentLength']
            localFile = os.stat(os.getcwd() + '/mydir/audio/' + filename)
            #Finding the local file size
            localSize = localFile.st_size
            #if the two are different, I assume the picture has changed and treat it like it's a new file
            if localSize != s3Size:
                audioKeyList.remove(filename)
        #Tyler says this is more clear
        if filename not in audioKeyList:
            data = open(os.getcwd() + '/mydir/audio/' + filename, 'rb')
            extension = filename.split('.')[-1]
            if extension in audioExtensions:
                audioBucket.put_object(Key=filename, Body = data, ACL = 'public-read', ContentType = 'audio/mpeg')
            data.close()

    #Same code as above, but for the image bucket
    #This code could have been combined with small additional variables containing directory names
    for filename in os.listdir(os.getcwd() + '/mydir/images/'):
        if filename in imageKeyList:
            response = mysession.client('s3').get_object(Bucket=bucketNames['image'], Key=filename)
            #response=imageBucket.get_object(Key=filename)
            s3Size = response['ContentLength']
            localFile = os.stat(os.getcwd() + '/mydir/images/' + filename)
            localSize = localFile.st_size
            if localSize != s3Size:
                imageKeyList.remove(filename)
        if filename not in imageKeyList:
            data = open(os.getcwd() + '/mydir/images/' + filename, 'rb')
            extension = filename.split('.')[-1]
            if extension in imageExtensions:
                imageBucket.put_object(Key=filename, Body = data, ACL = 'public-read', ContentType = 'image/jpeg')
            data.close()

    """for filename in os.listdir(os.getcwd() + '/mydir/'):
        if filename not in bucketKeyList:
            data = open(os.getcwd() + '/mydir/' + filename, 'rb')
            extension = filename.split('.')[-1]
            #bucket.upload_file(os.getcwd() + '/mydir/' + filename, filename) #Could be upload_fileobj
            if extension == 'json':
                tourBucket.put_object(Key=filename, Body = data, ACL = 'public-read', ContentType = 'application/json')
            elif extension in imageExtensions:
                imageBucket.put_object(Key=filename, Body = data, ACL = 'public-read', ContentType = 'image/jpeg')
            elif extension in audioExtensions:
                audioBucket.put_object(Key=filename, Body = data, ACL = 'public-read', ContentType = 'audio/mpeg')
            else:
                junk = True
                #bucket.put_object(Key=filename, Body = data, ACL = 'public-read')
            data.close()"""
