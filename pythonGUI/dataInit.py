import cms, copy

import pdb

# Downloads the current tours from S3 and converts them to .csv files

"""
Traceback (most recent call last):
  File "dataInit.py", line 6, in <module>
    getToursCsv()
  File "/home/joseph/code/Dornsife/dornsife_backend/pythonGUI/cms.py", line 184, in getToursCsv
    responseList = json.loads(bucket.Object(key).get()['Body'].read())
  File "/usr/lib/python3.5/json/__init__.py", line 312, in loads
    s.__class__.__name__))
TypeError: the JSON object must be str, not 'bytes'

"""

#getToursCsv()  ## Not working, at least on my computer with Linux. ^^

# We need to download these and then convert them to dictionaries that I can use
# to create and edit tours. Then when the user exits the program, it can compile
# the new tour points and upload them to S3 as well as upload the points to
# DynamoDB.


# This pulls all of the POIs from DynamoDB

tourData = {}

existingTourNames = []
existingPOINames = []

poiData = {}
waypointData = {}
IDLookupTable = {}
nextID = -1
tableName = cms.pointsTableName


deletedTours = []
editedPOIs = {}
createdPOIs = {}
deletedPOIs = []


rawPOIData = cms.scanDynamoDBTable(tableName)
oldPOIData = copy.deepcopy(rawPOIData)

for index in range(len(rawPOIData)):
    try:
        rawPOIData[index]["name"]
    except KeyError:
        rawPOIData[index]["name"] = rawPOIData[index]["ID"]


for poi in rawPOIData:
    if poi["type"] == "Waypoint":
        waypointData[poi["ID"]] = poi
    else:
        poiData[poi["ID"]] = poi


def downloadAndFormatData(nextID):
    tourNames = []
    for name in cms.tourBucket.objects.all():
        tourNames.append(name.key)

    rawTourData = {}
    for name in tourNames:
        s3rawTourData = cms.mysession.client('s3').get_object(Bucket=cms.bucketNames['tour'], Key=name)["Body"].read().decode('utf-8')
        rawTourData[name] = (cms.ast.literal_eval(s3rawTourData))

    for tourName, tour in rawTourData.items():
        tempTour = []
        for point in tour:
            tempTour.append(point["ID"])
        tourData[tourName.split(".")[0].replace("_", " ")] = tempTour


    for poiID, data in poiData.items():
        IDLookupTable[data["name"]] = poiID
        try:
            tempString = ""
            for website in data["additionalWebsites"]:
                tempString += (website + " ")
            poiData[poiID]["additionalWebsites"] = tempString
        except:
            # This is to catch the ones that don't have this item in the dictionary.
            pass
    for poiID, data in waypointData.items():
        try:
            IDLookupTable[data["name"]] = poiID
        except KeyError:
            print("[!] Adding Waypoins to IDLookupTable Failed")

    for key, value in poiData.items():
        if int(key) > nextID:
            nextID = int(key)
        existingPOINames.append(value["name"])
    for key, point in waypointData.items():
        if int(key) > nextID:
            nextID = int(key)
        existingPOINames.append(point["name"])

    nextID += 1
    existingTourNames.extend(tourData.keys())

    return nextID


def formatDataForUpload(listToursToDelete=None):
    for poiID, point in createdPOIs.items():
        try:
            tempList = []
            websitesSplit = point["additionalWebsites"].split(" ")
            for item in websitesSplit:
                if item != "":
                    tempList.append(item)
            createPOIs[poiID]["additionalWebsites"] = tempList
            #print("[+] Created", point["name"], ": ", tempList)
        except Exception as e:
            #print("[!]", e)
            # This is to catch the ones that don't have this item in the dictionary.
            pass
    for poiID, point in editedPOIs.items():
        try:
            tempList = []
            websitesSplit = point["additionalWebsites"].split(" ")
            for item in websitesSplit:
                if item != "":
                    tempList.append(item)
            editedPOIs[poiID]["additionalWebsites"] = tempList
            #print("[+] Edited", point["name"], ": ", tempList)
        except Exception as e:
            #print("[!]", e)
            # This is to catch the ones that don't have this item in the dictionary.
            pass

    cms.updatePoints(createdPOIs, editedPOIs, deletedPOIs, tableName)
    cms.updateBusinesses(tableName)


    # Tours to Upload
    newTourObjects = {}

    for tourName, tour in tourData.items():
        # upload the new json files
        tempTourName = tourName.replace(" ", "_")
        newTour = []
        for point in tour:
            try:
                newTour.append(poiData[point])
            except KeyError:
                try:
                    newTour.append(waypointData[point])
                except KeyError:
                    print("[+] Repackaging " + tourName + " without deleted point")

        newTourObjects[tempTourName] = cms.json.dumps(newTour)

    for tourName, jsonTourData in newTourObjects.items():
        cms.tourBucket.put_object(Key=tourName + ".json", Body=jsonTourData, ACL="public-read", ContentType="application/json")

    # Tours to delete
    for item in listToursToDelete:
        tempItem = item.replace(" ", "_") + ".json"
        if tempItem in deletedTours:
            deletedTours.remove(tempItem)
    cms.deleteTours(deletedTours)

    deletedTours.clear()
    editedPOIs.clear()
    createdPOIs.clear()
    deletedPOIs.clear()

def uploadFiles():
    cms.uploadToS3(tableName)

nextID = downloadAndFormatData(nextID)


#formatDataForUpload()
#pdb.set_trace()
