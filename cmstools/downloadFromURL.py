import urllib, urllib.request
filename = '4gZI1Ti.jpg'
bucketName = 'testbucket425877/'
urllib.request.urlretrieve('https://s3-us-west-2.amazonaws.com/' + bucketName + filename, 'download/' + filename)
