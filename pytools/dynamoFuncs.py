import boto3

#dynamodb = boto3.resource('dynamodb')

def createTable(manual=True, data=None):
    if manual:
        tableName = input("Table name: ")
        attributes = []
        attributeNames = []
        
        print("Enter Attributes for table\n")
        attrName = " "
        while attrName != "":
            attrName = input("Attribute Name: ")
            attributeNames.append(attrName)
            
            
        for attribute in attributeNames:
            print("\nAttribute", attribute)
            attrKeyType = input("Key Type: ")
            attrType = input("Type: ")
                
            attributes.append((attribute, attrKeyType, attrType))
                
        for attribute in attributes:
            print(attribute)
                    
        provisionedThroughput={'ReadCapacityUnits':'5', 'WriteCapacityUnits':'5'}
        #readCapacityUnits = input("ReadCapacityUnits (5): ")
        #writeCapacityUnits = input("WriteCapactiyUnits (5): ")
                    
                    
        keySchema = []
        attributeDefinitions = []
        
        tempSchema = {}
        tempDef = {}
        
        for attribute in attributes:
            tempSchema["AttributeName"] = attribute[0]
            tempSchema["KeyType"] = attribute[1]
            
            tempDef["AttributeName"] = attribute[0]
            tempDef["AttributeType"] = attribute[2]
            
            keySchema.append(tempSchema)
            attributeDefinitions.append(tempDef)

            # don't need to reinitialize the dicts
            # still using the same keys, just different values

        table = dynamodb.create_table(tableName, keySchema, attributeDefinitions, provisionedThroughput)
        table.meta.client.get_waiter('table_exists').wait(TableName=tableName)

        
    else:
        print("Impliment the automated table creation")
        print("-- First three rows are used: AttributeNames, KeyType, AttributeType")
