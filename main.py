import requests
import json
import csv
import sys
import getopt
from datetime import datetime, timedelta


def convertJsonArray(jsonObj, fieldName):
    jsonFile = json.loads(jsonObj)
    allRecords = []
    recordList = []
    for record in jsonFile:
        allRecords.append(record)
    for record in allRecords:
        recordList.append(record[fieldName])
    return recordList


def getInboxDataRange(apiKey, domain, startDate, endDate):
    # Pull inbox data from Inbox Tracker
    apiURL = "http://api.edatasource.com/v4/inbox/deliverability/" + domain
    parameters = {
        "qd": "between:" + startDate + "," + endDate,
        "Authorization": apiKey
    }
    response = requests.get(apiURL, parameters)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print("error getting inbox data: " + response.reason)


def manageArgs(argv):
    opts, args = getopt.getopt(argv, "hk:d:o:")

    instructions = "test.py -k <api_key> -d <number_of_days> -o <output_file>"
    argsArray = []

    for opt, arg in opts:
        if opt == '-h':
            print(instructions)
            sys.exit()
        elif opt == "-k":
            apiKey = arg
            argsArray.append(apiKey)
        elif opt == "-d":
            maxDays = arg
            argsArray.append(maxDays)
        elif opt == "-o":
            outputFile = arg
            argsArray.append(outputFile)

    if len(argsArray) == 3:
        return argsArray
    else:
        print("incorrect number of arguments: " + instructions)


# Initialize
argArray = manageArgs(sys.argv[1:])
apiKey = argArray[0]
maxDays = argArray[1]
destFile = argArray[2]


# Pull Domains
apiURL = "http://api.edatasource.com/v4/inbox/domains/available"
parameters = {
    "Authorization": apiKey
}
response = requests.get(apiURL, parameters)

data_file = open(destFile, 'w')

if response.status_code == 200:
    domainList = convertJsonArray(response.text, "domain")  # Pull domain array from JSON

    # Loop through domains
    for domain in domainList:
        day = 1  # Initialize day; set as 1 so that the series begins at day before now

        while day <= maxDays:  # Loop through days

            # Set date parameters
            newDate = datetime.today() - timedelta(days=day)  # Determine date by subtracting from current
            testDate = newDate.strftime('%Y%m%d')  # Convert date format
            startDate = testDate+"000000"  # Add hour, minute, second
            endDate = testDate+"235959"  # Add hour, minute, second

            # Pull inbox data
            jsonRecord = getInboxDataRange(apiKey, domain, startDate, endDate)
            dateRecord = {'date': newDate.date()}
            jsonRecord.update(dateRecord)
            header = jsonRecord.keys()

            # Save to CSV
            csv_writer = csv.writer(data_file)

            if day == 1 and domain == domainList[0]:  # Check if it's the first record
                csv_writer.writerow(header)  # Write headers
            csv_writer.writerow(jsonRecord.values())  # Write values

            day += 1  # Iterate to next day
else:
    print("error getting domain information: " + response.reason)

data_file.close()

print('done')
