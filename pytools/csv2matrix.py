fileName = input("Enter data file name (.csv): ")
myFile = open(fileName, 'r')

data = [[]]
tableHeight = 0
tableWidth = 0

for line in myFile:
    tempLine = line.split(",")
    newFormattedLine = []
    for tempData in tempLine:
        newFormattedLine.append(tempData)

    data.append(newFormattedData)
    tableHeight += 1

try:
    tableWidth = len(data[0])
except:
    print "There are no rows of data"
