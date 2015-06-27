import suds
import json


url = 'http://inspired.jsu.edu/autotune/service/autotune.wsdl'
# Create the client
client = suds.client.Client(url)
print client


# Get file contents for tuning
baseModelFile = open("AutoTuneMediumOfficeNew2004.idf", "r")
baseModelContent = baseModelFile.read()
baseModelContent = unicode(baseModelContent, errors='ignore')

schedule = ""

parameterFile = open("MediumOffice.csv", "r")
parameterContent = parameterFile.read()

userDataFile = open("SampleMonthlyUserInput.csv")
uDataContent = userDataFile.read()

weatherFile = "USA_IL_Chicago-Midway.AP.725340_TMY"

email = "agarrett@jsu.edu"


# Tune
result = client.service.tune(uDataContent, baseModelContent, schedule, parameterContent, weatherFile, email)
print result

# Interpret output -> tracking
jsonObj = json.loads(result)
tracking = jsonObj['autotune']['tracking']
print "\nYour new tracking number is " + tracking

# Show information on the tracking
print "\n\nFunction: getOutput";
result = client.service.getOutput(tracking)
print result

# Terminate 
print "\n\nFunction: terminate"
result = client.service.terminate(tracking)
jsonObj = json.loads(result)
terminate = jsonObj['autotune']['terminate']
print "Terminate is now " + terminate

# Resume
print "\n\nFunction: resume"
result = client.service.resume(tracking)
jsonObj = json.loads(result)
terminate = jsonObj['autotune']['terminate']
print "Terminate is now " + terminate

# Retune
print "\n\nFunction: retune"
result = client.service.retune(tracking)
jsonObj = json.loads(result)
newTracking = jsonObj['autotune']['tracking']
print "Your new tracking number is " + newTracking



