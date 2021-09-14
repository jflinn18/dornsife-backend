import boto3, os, pdb, json

s3 = boto3.resource('s3')
bucket = s3.Bucket('dornsifetourtest')
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
    with open( key.replace('.json','') + '.csv', 'w') as write:
        write.write(bigString)
