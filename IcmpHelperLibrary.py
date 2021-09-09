# #################################################################################################################### #
# Imports                                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
import os
from socket import *
import struct
import time
import select


# #################################################################################################################### #
# Class IcmpHelperLibrary                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
class IcmpHelperLibrary:
    # ################################################################################################################ #
    # Class IcmpPacket                                                                                                 #
    #                                                                                                                  #
    # References:                                                                                                      #
    # https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml                                           #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    

    class IcmpPacket:
        # ############################################################################################################ #
        # IcmpPacket Class Scope Variables                                                                             #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __icmpTarget = ""               # Remote Host
        __destinationIpAddress = ""     # Remote Host IP Address
        __header = b''                  # Header after byte packing
        __data = b''                    # Data after encoding
        __dataRaw = ""                  # Raw string data before encoding
        __icmpType = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __icmpCode = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __packetChecksum = 0            # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetIdentifier = 0          # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetSequenceNumber = 0      # Valid values are 0-65535 (unsigned short, 16 bits)
        __ipTimeout = 60
        __ttl = 255                     # Time to live

        __DEBUG_IcmpPacket = False     # Allows for debug output

        # ############################################################################################################ #
        # IcmpPacket Class Getters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpTarget(self):
            return self.__icmpTarget

        def getDataRaw(self):
            return self.__dataRaw

        def getIcmpType(self):
            return self.__icmpType

        def getIcmpCode(self):
            return self.__icmpCode

        def getPacketChecksum(self):
            return self.__packetChecksum

        def getPacketIdentifier(self):
            return self.__packetIdentifier

        def getPacketSequenceNumber(self):
            return self.__packetSequenceNumber

        def getTtl(self):
            return self.__ttl

        # ############################################################################################################ #
        # IcmpPacket Class Setters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIcmpTarget(self, icmpTarget):
            self.__icmpTarget = icmpTarget

            # Only attempt to get destination address if it is not whitespace
            if len(self.__icmpTarget.strip()) > 0:
                self.__destinationIpAddress = gethostbyname(self.__icmpTarget.strip())

        def setIcmpType(self, icmpType):
            self.__icmpType = icmpType

        def setIcmpCode(self, icmpCode):
            self.__icmpCode = icmpCode

        def setPacketChecksum(self, packetChecksum):
            self.__packetChecksum = packetChecksum

        def setPacketIdentifier(self, packetIdentifier):
            self.__packetIdentifier = packetIdentifier

        def setPacketSequenceNumber(self, sequenceNumber):
            self.__packetSequenceNumber = sequenceNumber

        def setTtl(self, ttl):
            self.__ttl = ttl

        # ############################################################################################################ #
        # IcmpPacket Class Private Functions                                                                           #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __recalculateChecksum(self):
            print("calculateChecksum Started...") if self.__DEBUG_IcmpPacket else 0
            packetAsByteData = b''.join([self.__header, self.__data])
            checksum = 0

            # This checksum function will work with pairs of values with two separate 16 bit segments. Any remaining
            # 16 bit segment will be handled on the upper end of the 32 bit segment.
            countTo = (len(packetAsByteData) // 2) * 2

            # Calculate checksum for all paired segments
            print(f'{"Count":10} {"Value":10} {"Sum":10}') if self.__DEBUG_IcmpPacket else 0
            count = 0
            while count < countTo:
                thisVal = packetAsByteData[count + 1] * 256 + packetAsByteData[count]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture 16 bit checksum as 32 bit value
                print(f'{count:10} {hex(thisVal):10} {hex(checksum):10}') if self.__DEBUG_IcmpPacket else 0
                count = count + 2

            # Calculate checksum for remaining segment (if there are any)
            if countTo < len(packetAsByteData):
                thisVal = packetAsByteData[len(packetAsByteData) - 1]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture as 32 bit value
                print(count, "\t", hex(thisVal), "\t", hex(checksum)) if self.__DEBUG_IcmpPacket else 0

            # Add 1's Complement Rotation to original checksum
            checksum = (checksum >> 16) + (checksum & 0xffff)   # Rotate and add to base 16 bits
            checksum = (checksum >> 16) + checksum              # Rotate and add

            answer = ~checksum                  # Invert bits
            answer = answer & 0xffff            # Trim to 16 bit value
            answer = answer >> 8 | (answer << 8 & 0xff00)
            print("Checksum: ", hex(answer)) if self.__DEBUG_IcmpPacket else 0

            self.setPacketChecksum(answer)

        def __packHeader(self):
            # The following header is based on http://www.networksorcery.com/enp/protocol/icmp/msg8.htm
            # Type = 8 bits
            # Code = 8 bits
            # ICMP Header Checksum = 16 bits
            # Identifier = 16 bits
            # Sequence Number = 16 bits
            self.__header = struct.pack("!BBHHH",
                                   self.getIcmpType(),              #  8 bits / 1 byte  / Format code B
                                   self.getIcmpCode(),              #  8 bits / 1 byte  / Format code B
                                   self.getPacketChecksum(),        # 16 bits / 2 bytes / Format code H
                                   self.getPacketIdentifier(),      # 16 bits / 2 bytes / Format code H
                                   self.getPacketSequenceNumber()   # 16 bits / 2 bytes / Format code H
                                   )

        def __encodeData(self):
            data_time = struct.pack("d", time.time())               # Used to track overall round trip time
                                                                    # time.time() creates a 64 bit value of 8 bytes
            dataRawEncoded = self.getDataRaw().encode("utf-8")

            self.__data = data_time + dataRawEncoded

        def __packAndRecalculateChecksum(self):
            # Checksum is calculated with the following sequence to confirm data in up to date
            self.__packHeader()                 # packHeader() and encodeData() transfer data to their respective bit
                                                # locations, otherwise, the bit sequences are empty or incorrect.
            self.__encodeData()
            self.__recalculateChecksum()        # Result will set new checksum value
            self.__packHeader()                 # Header is rebuilt to include new checksum value

        def __validateIcmpReplyPacketWithOriginalPingData(self, icmpReplyPacket):
            # Hint: Work through comparing each value and identify if this is a valid response.
            
            # check if sequence numbers are the same
            if icmpReplyPacket.getIcmpSequenceNumber() == self.getPacketSequenceNumber():
                icmpReplyPacket.setIcmpSequenceNumber_isValid(True)
            else: 
                icmpReplyPacket.setIcmpSequenceNumber_isValid(False)
            #debug message
            print("-------------Debug Info---------------") \
                    if self.__DEBUG_IcmpPacket else 0
            print("-------------Expected Sequence Number: ", self.getPacketSequenceNumber()) \
                    if self.__DEBUG_IcmpPacket else 0
            print("-------------Actual Sequence Number: ", icmpReplyPacket.getIcmpSequenceNumber()) \
                    if self.__DEBUG_IcmpPacket else 0


            # check if packet identifiers are the same
            if icmpReplyPacket.getIcmpIdentifier() == self.getPacketIdentifier():
                icmpReplyPacket.setIcmpIdentifier_isValid(True)
            else: 
                icmpReplyPacket.setIcmpIdentifier_isValid(False)
            #debug message
            print("-------------Expected Identifier: ", self.getPacketIdentifier()) \
                    if self.__DEBUG_IcmpPacket else 0
            print("-------------Actual Identifier: ", icmpReplyPacket.getIcmpIdentifier()) \
                    if self.__DEBUG_IcmpPacket else 0
            
            # check if packet raw data are the same
            if icmpReplyPacket.getIcmpData() == self.getDataRaw():
                icmpReplyPacket.setIcmpData_isValid(True)
            else:
                icmpReplyPacket.setIcmpData_isValid(False)
            #debug message
            print("-------------Expected Raw Data: ", self.getDataRaw()) \
                    if self.__DEBUG_IcmpPacket else 0
            print("-------------Actual Raw Data: ", icmpReplyPacket.getIcmpData()) \
                    if self.__DEBUG_IcmpPacket else 0

            
            # check if the reply is valid
            if icmpReplyPacket.getIcmpSequenceNumber_isValid() and \
                icmpReplyPacket.getIcmpIdentifier_isValid() and \
                icmpReplyPacket.getIcmpData_isValid():
                
                icmpReplyPacket.setIsValidResponse(True)
            else:
                icmpReplyPacket.setIsValidResponse(False)
            

        # ############################################################################################################ #
        # IcmpPacket Class Public Functions                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def buildPacket_echoRequest(self, packetIdentifier, packetSequenceNumber):
            self.setIcmpType(8)
            self.setIcmpCode(0)
            self.setPacketIdentifier(packetIdentifier)
            self.setPacketSequenceNumber(packetSequenceNumber)
            self.__dataRaw = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            self.__packAndRecalculateChecksum()

        def sendEchoRequest(self):
            if len(self.__icmpTarget.strip()) <= 0 | len(self.__destinationIpAddress.strip()) <= 0:
                self.setIcmpTarget("127.0.0.1")

            if self.getTtl() >= 0:
                print("Pinging (" + self.__icmpTarget + ") " + self.__destinationIpAddress)\
                    if self.__DEBUG_IcmpPacket else 0
                
                mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
                mySocket.settimeout(self.__ipTimeout)
                mySocket.bind(("", 0))
                #print("Ttl: ", self.getTtl())
                mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', self.getTtl()))  # Unsigned int - 4 bytes
                try:
                    mySocket.sendto(b''.join([self.__header, self.__data]), (self.__destinationIpAddress, 0))
                    timeLeft = 30
                    pingStartTime = time.time()
                    startedSelect = time.time()
                    whatReady = select.select([mySocket], [], [], timeLeft)     #return three new lists: readable, writable, exceptional
                    endSelect = time.time()
                    howLongInSelect = (endSelect - startedSelect)
                    if whatReady[0] == []:  # Timeout
                        print("  *        *        *        *        *    Request timed out.")
                    recvPacket, addr = mySocket.recvfrom(1024)  # recvPacket - bytes object representing data received
                    # addr  - address of socket sending data
                    timeReceived = time.time()
                    timeLeft = timeLeft - howLongInSelect
                    
                    packets_received = 0

                    if timeLeft <= 0:
                        print("  *        *        *        *        *    Request timed out (By no remaining time left).")

                    else:
                        # Fetch the ICMP type and code from the received packet
                        #print("recvPacket: ", recvPacket)
                        icmpType, icmpCode = recvPacket[20:22]

                        
                        if icmpType == 11:                          # Time Exceeded
                            # error message for type 11
                            if self.getIcmpCode() == 0:
                                error_message = "Time to Live exceeded in Transit"
                            elif self.getIcmpCode() == 1:
                                error_message = "Fragment Reassembly Time Exceeded"
                            
                            RTT = (timeReceived - pingStartTime) * 1000
                            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    Identifier=%d    Sequence=%d    %s" %
                                    (
                                        self.getTtl(),
                                        (timeReceived - pingStartTime) * 1000,
                                        icmpType,
                                        icmpCode,
                                        self.getPacketIdentifier(),
                                        self.getPacketSequenceNumber(),
                                        addr[0]
                                    )
                                    + "    Error: " + error_message
                                   )
                            
                            return RTT, packets_received, addr[0]

                        elif icmpType == 3:                         # Destination Unreachable
                            # error message
                            if self.getIcmpCode() == 0:
                                error_message = "Net Unreachable"
                            elif self.getIcmpCode() == 1:
                                error_message = "Host Unreachable"
                            elif self.getIcmpCode() == 2:
                                error_message = "Protocol Unreachable"
                            elif self.getIcmpCode() == 3:
                                error_message = "Port Unreachable"
                            elif self.getIcmpCode() == 4:
                                error_message = "Fragmentation Needed and Don't Fragment was Set"
                            elif self.getIcmpCode() == 5:
                                error_message = "Source Route Failed"
                            elif self.getIcmpCode() == 6:
                                error_message = "Destination Network Unknown"
                            elif self.getIcmpCode() == 7:
                                error_message = "Destination Host Unknown"
                            elif self.getIcmpCode() == 8:
                                error_message = "Source Host Isolated"
                            elif self.getIcmpCode() == 9:
                                error_message = "Communication with Destination Network is Administratively Prohibited"
                            elif self.getIcmpCode() == 10:
                                error_message = "Communication with Destination Host is Administratively Prohibited"
                            elif self.getIcmpCode() == 11:
                                error_message = "Destination Network Unreachable for Type of Service"
                            elif self.getIcmpCode() == 12:
                                error_message = "Destination Host Unreachable for Type of Service"
                            elif self.getIcmpCode() == 13:
                                error_message = "Communication Administratively Prohibited"
                            elif self.getIcmpCode() == 14:
                                error_message = "Host Precedence Violation"
                            elif self.getIcmpCode() == 15:
                                error_message = "Precedence cutoff in effect"

                            RTT = (timeReceived - pingStartTime) * 1000
                            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    Identifier=%d    Sequence=%d    %s" %
                                      (
                                          self.getTtl(),
                                          (timeReceived - pingStartTime) * 1000,
                                          icmpType,
                                          icmpCode,
                                          self.getPacketIdentifier(),
                                          self.getPacketSequenceNumber(),
                                          addr[0]
                                          ) 
                                      + "    Error: " + error_message
                                  )
                        
                            return RTT, packets_received, addr[0]
                        
                        if icmpType == 0:                         # Echo Reply
                            # increment packets received
                            packets_received += 1
                            RTT = (timeReceived - pingStartTime) * 1000
                            icmpReplyPacket = IcmpHelperLibrary.IcmpPacket_EchoReply(recvPacket)
                            self.__validateIcmpReplyPacketWithOriginalPingData(icmpReplyPacket)
                            icmpReplyPacket.printResultToConsole(self.getTtl(), timeReceived, addr)
                            
                            return RTT, packets_received, addr[0]   # Echo reply is the end and therefore should return

                        else:
                            print("error")
                except timeout:
                    print("  *        *        *        *        *    Request timed out (By Exception).")
                finally:
                    mySocket.close()

        def printIcmpPacketHeader_hex(self):
            print("Header Size: ", len(self.__header))
            for i in range(len(self.__header)):
                print("i=", i, " --> ", self.__header[i:i+1].hex())

        def printIcmpPacketData_hex(self):
            print("Data Size: ", len(self.__data))
            for i in range(len(self.__data)):
                print("i=", i, " --> ", self.__data[i:i + 1].hex())

        def printIcmpPacket_hex(self):
            print("Printing packet in hex...")
            self.printIcmpPacketHeader_hex()
            self.printIcmpPacketData_hex()

    # ################################################################################################################ #
    # Class IcmpPacket_EchoReply                                                                                       #
    #                                                                                                                  #
    # References:                                                                                                      #
    # http://www.networksorcery.com/enp/protocol/icmp/msg0.htm                                                         #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket_EchoReply:
        # ############################################################################################################ #
        # IcmpPacket_EchoReply Class Scope Variables                                                                   #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __recvPacket = b''
        __isValidResponse = False
        __IcmpIdentifier_isValid = False
        __IcmpSequenceNumber_isValid = False
        __IcmpData_isValid = False

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Constructors                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __init__(self, recvPacket):
            self.__recvPacket = recvPacket

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Getters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpType(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[20:20 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 20)

        def getIcmpCode(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[21:21 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 21)

        def getIcmpHeaderChecksum(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[22:22 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 22)

        def getIcmpIdentifier(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[24:24 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 24)

        def getIcmpSequenceNumber(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[26:26 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 26)

        def getDateTimeSent(self):
            # This accounts for bytes 28 through 35 = 64 bits
            return self.__unpackByFormatAndPosition("d", 28)   # Used to track overall round trip time
                                                               # time.time() creates a 64 bit value of 8 bytes

        def getIcmpData(self):
            # This accounts for bytes 36 to the end of the packet.
            return self.__recvPacket[36:].decode('utf-8')

        def getIcmpIdentifier_isValid(self):
            return self.__IcmpIdentifier_isValid

        def getIcmpSequenceNumber_isValid(self):
            return self.__IcmpSequenceNumber_isValid

        def getIcmpData_isValid(self):
            return self.__IcmpData_isValid


        def isValidResponse(self):
            return self.__isValidResponse



        # ############################################################################################################ #
        # IcmpPacket_EchoReply Setters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIsValidResponse(self, booleanValue):
            self.__isValidResponse = booleanValue


        def setIcmpIdentifier_isValid(self, booleanValue):
            self.__IcmpIdentifier_isValid = booleanValue

        def setIcmpSequenceNumber_isValid(self, booleanValue):
            self.__IcmpSequenceNumber_isValid = booleanValue

        def setIcmpData_isValid(self, booleanValue):
            self.__IcmpData_isValid = booleanValue
        # ############################################################################################################ #
        # IcmpPacket_EchoReply Private Functions                                                                       #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __unpackByFormatAndPosition(self, formatCode, basePosition):
            numberOfbytes = struct.calcsize(formatCode)
            return struct.unpack("!" + formatCode, self.__recvPacket[basePosition:basePosition + numberOfbytes])[0]

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Public Functions                                                                        #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def printResultToConsole(self, ttl, timeReceived, addr):
            bytes = struct.calcsize("d")
            timeSent = struct.unpack("d", self.__recvPacket[28:28 + bytes])[0]
            
            if self.isValidResponse():
                print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    Identifier=%d    SequenceNumber=%d    %s" %
                      (
                          ttl,
                          (timeReceived - timeSent) * 1000,
                          self.getIcmpType(),
                          self.getIcmpCode(),
                          self.getIcmpIdentifier(),
                          self.getIcmpSequenceNumber(),
                          addr[0]
                      )
                    )
            # print expected and actual value difference if not valid.
            else:
                if not self.getIcmpIdentifier_isValid():
                    print("----------Identifier Error-----------")
                    print("Expected value: ", IcmpPacket.getPacketIdentifier())
                    print("Actual value: ", self.getIcmpIdentifier())
                if not self.getIcmpSequenceNumber_isValid():
                    print("----------SequenceNumber Error----------")
                    print("Expected value: ", IcmpPacket.getPacketSequenceNumber())
                    print("Actual value: ", self.getIcmpSequenceNumber())
                if not self.getIcmpData_isValid():
                    print("----------RawData Error----------")
                    print("Expected value: ", IcmpPacket.getDataRaw())
                    print("Actual value: ", self.getIcmpData())

    # ################################################################################################################ #
    # Class IcmpHelperLibrary                                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #

    # ################################################################################################################ #
    # IcmpHelperLibrary Class Scope Variables                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #

    __DEBUG_IcmpHelperLibrary = False                  # Allows for debug output
    # ################################################################################################################ #
    # IcmpHelperLibrary Private Functions                                                                              #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __sendIcmpEchoRequest(self, host, Ttl):
        print("sendIcmpEchoRequest Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        

        # array of RTTs
        RTTs = []
        packets_received = 0

        destination = None

        print("Ping 4 packets to ", gethostbyname(host.strip()))
        for i in range(4):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()
            icmpPacket.setTtl(Ttl)
            
            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i

            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            temp = icmpPacket.sendEchoRequest()
            
            if temp != None:
                RTT, num, destination = temp                                            # Build IP

                RTTs.append(RTT)
                packets_received += num

            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            # we should be confirming values are correct, such as identifier and sequence number and data

        # initialize value
        min_RTT = float("inf")
        max_RTT = float("-inf")
        average_RTT = 0

        if len(RTTs) != 0:
            min_RTT = min(RTTs)
            max_RTT = max(RTTs)
            average_RTT = sum(RTTs)/len(RTTs)

        packet_loss_rate = (4 - packets_received) / 4

        #print("-------------Ping Info-------------")
        print("Min=%.0f ms  Max=%.0f ms  Average=%.0f ms  Packet_Loss=%.2f"%
                  (
                      min_RTT,
                      max_RTT,
                      average_RTT,
                      packet_loss_rate,
                  )
                  + "  Addr=", destination
              )
        return destination

    def __sendIcmpTraceRoute(self, host):
        print("sendIcmpTraceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        # Build code for trace route here

        host_ip = gethostbyname(host.strip())
        Ttl = 1
        destination = None

        while destination != host_ip and Ttl <= 255:
            
            destination = self.__sendIcmpEchoRequest(host, Ttl)
            #print("Host: ", host_ip)
            #print("Destination: ", destination)
            Ttl += 1


    # ################################################################################################################ #
    # IcmpHelperLibrary Public Functions                                                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def sendPing(self, targetHost):
        print("ping Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpEchoRequest(targetHost, 255)

    def traceRoute(self, targetHost):
        print("traceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpTraceRoute(targetHost)


# #################################################################################################################### #
# main()                                                                                                               #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
def main():
    icmpHelperPing = IcmpHelperLibrary()


    # Choose one of the following by uncommenting out the line
    icmpHelperPing.sendPing("209.233.126.254")
    # icmpHelperPing.sendPing("www.google.com")
    # icmpHelperPing.sendPing("oregonstate.edu")
    # icmpHelperPing.sendPing("gaia.cs.umass.edu")
    #icmpHelperPing.sendPing("256.123.1.1")
    # icmpHelperPing.traceRoute("oregonstate.edu")
    # icmpHelperPing.traceRoute("209.233.126.254")
    #icmpHelperPing.traceRoute("www.google.com")
    # icmpHelperPing.traceRoute("www.sousou.co.jp")
    #icmpHelperPing.traceRoute("australia.gov.au")
    # icmpHelperPing.traceRoute("256.123.1.1")
    #icmpHelperPing.traceRoute("facebook.com")

if __name__ == "__main__":
    main()
