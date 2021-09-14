import boto3, os, pdb


mysession = boto3.session.Session(aws_access_key_id='SECRET', aws_secret_access_key='SECRET', region_name='us-west-2')
s3 = mysession.resource('s3')

tourBucket = s3.Bucket('dornsifetourtest')
imageBucket = s3.Bucket('dornsifeimagetest')
audioBucket = s3.Bucket('dornsifeaudiotest')
imageExtensions = ['jpg','png','jpeg','JPG']
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
        elif extension == 'mp3':
            audioBucket.put_object(Key=filename, Body = data, ACL = 'public-read')
        else:
            junk = True
            #bucket.put_object(Key=filename, Body = data, ACL = 'public-read')
        data.close()
