import boto3, os

s3 = boto3.resource('s3')
bucket = s3.Bucket('dornsifetourtest')
bucketKeys = bucket.objects.all()
bucketKeyList = []
for item in bucketKeys:
    bucketKeyList.append(item.key)

for key in bucketKeyList:
    bucket.download_file(key, 'download/' + key)
