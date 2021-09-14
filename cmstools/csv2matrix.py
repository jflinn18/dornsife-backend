import csv, pdb, hashlib

fileName = input("Enter data file name (.csv): ")
myFile = open(fileName, encoding='utf-8')
csvF = csv.reader(myFile)
data = []
tableHeight = 0
tableWidth = 0
for line in csvF:
    #tempLine = line.split(",")
    #newFormattedLine = []
    #for tempData in tempLine:
    #    newFormattedLine.append(tempData)

    data.append(line)
    tableHeight += 1
myFile.close()
try:
    #data[0][0] = data[0][0].replace('\ufeff','')
    tableWidth = len(data[0])
    #print(data)
    #pdb.set_trace()
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
    tempDict['Verify']=str(hash(tuple(data[row])))
    dataDict[tempDict['ID']] = tempDict
    dataList.append(tempDict)

#print(dataDict)
