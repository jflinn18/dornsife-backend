import ast
print('What is the file name of the backup?')
fileName = input()
myFile = open(fileName,'r')
data = myFile.read()
myFile.close()
dataDict = dict(ast.literal_eval(data))
print(dataDict)
