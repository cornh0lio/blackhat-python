# we need to import the IBurpExtender class that is a requirement
# for every extension we write for Burp
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from java.util import List, ArrayList

import random

class BurpExtender (IBurpExtender, IIntruderPayloadGeneratorFactory):
    
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        # we use the registerIntruderPayloadGeneratorFactory to register our class
        # so that the Intruder tool is aware that we can generate payloads   
        callbacks.registerIntruderPayloadGeneratorFactory(self)

        return

    # we implement the getGeneratorName to simply return the name
    # of our generator
    def getGeneratorName(self):
        return "BHP Payload Generator"

    # this funcion returns an instance of the IIntruderPayloadGenerator class
    # which we called BHPFuzzer
    def createNewInstance(self, attack):
        return BHPFuzzer(self, attack)



# our BHPFuzzer class that extends the class IIntruderPayloadGenerator
class BHPFuzzer(IIntruderPayloadGenerator):
    
    # we define the required class variables and we 
    # define also the max_payloads variable and
    # num_iterations
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payloads = 10
        self.num_iterations = 0

        return

    # this function simply checks whether we have reached the
    # maximum number of fuzziong iterations
    def hasMorePayloads(self): 
        if self.num_iterations == self.max_payloads:
            return False
        else:
            return True

    # we receive the payload as a byte array
    def getNextPayload(self, current_payload):
        # we convert the byte array into a string
        payload = "".join(chr(x) for x in current_payload)
        # we call our simple mutator to fuzz the POST request
        payload = self.mutate_payload(payload)

        # we increment the number of fuzzing attemptes
        self.num_iterations += 1

        return payload
    
    def reset(self):
        self.num_iterations = 0
        return

    def mutate_payload(self, original_payload):

        # pick a simple mutator or even call an external script
        picker = random.randint(1,3)
        
        # select a random offset in the original payload to mutate
        offset = random.randint(0, len(original_payload)-1)
        payload = original_payload[:offset]

        # random offset insert a SQL injection attempt
        if picker == 1:
            payload += "'"

        # jam an XSS attemtp in
        if picker == 2:
            payload += "<script>alert('BHP');</script>"

        # repeat a chunk of the original payload a random number of times
        if picker == 3:
            chunk_length =  random.randint(len(payload[offset:]), len(payload)-1)
            repeater = random.randint(1,10)

            for i in range(repeater):
                payload += original_payload[offset:offset+chunk_length]
    
        # add the remaining bits of the payload
        payload += original_payload[offset:]

        return payload







