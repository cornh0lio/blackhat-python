############################################################################
## Install Firts: apt-get install python-opencv python-numpy python-scipy ##
############################################################################

import re
import zlib
import cv2

from scapy.all import *

pictures_directory   = "carved_img"
faces_directory     = "faces_img"
pcap_file           = "arper.pcap"

def get_http_headers(http_payload):
    try:
        # split the headers off if it is HTTP traffic
        # string.index() determines if string str occurs in string or in a substring of 
        # string if starting index beg and ending index end are given.
        headers_raw = http_payload[:http_payload.index("\r\n\r\n")+2]

        # if the first character after the question mark is a P, 
        # you know that it's an extension that's specific to Python
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers_raw))
    except:
        return None

    if "Content-Type" not in headers:
        return None

    return headers    


def extract_image(headers, http_payload):

    image = None
    image_type = None
    
    try:
        # if the Content-Type has image as MIME type
        if "image" in headers['Content-Type']:
            # grab the image type from the header            
            # image header:
            # Content-Type: image/gif ==> gif
            image_type = headers['Content-Type'].split("/")[1]

            #grab the image body
            image = http_payload[http_payload.index("\r\n\r\n")+4:]

            # if we detect compression decompress the image
            try: 
                if "Content-Encoding" in headers.keys():
                    if headers['Content-Encoding'] == "gzip":
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == "deflate":
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None, None

    return image, image_type


# Face detection with Python: http://fideloper.com/facial-detection/
def face_detect(path, file_name):
    
    # read the image
    img     = cv2.imread(path)
    # apply a classifier, this classifier can detect faces in a front-facing orientation
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

    # http://www.pyimagesearch.com/2015/11/16/hog-detectmultiscale-parameters-explained/
    # After the detection has been run, it will return rectangle coordinates 
    # that correspond to where the face was detected in the image.
    rects   = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return False

    # slicing operation: http://stackoverflow.com/questions/4012340/python-colon-in-list-index
    rects[:, 2:] += rects[:, :2]

    # highlight the faces in the image        
    for x1,y1,x2,y2 in rects:
        cv2.rectangle(img,(x1,y1),(x2,y2),(127,255,0),2)

    # write out the resulting image
    cv2.imwrite("%s/%s-%s" % (faces_directory,pcap_file,file_name),img)

    return True


def http_assembler(pcap_file):

    carved_images = 0
    faces_detected = 0
    
    # https://itgeekchronicles.co.uk/2014/12/02/scapy-sessions-or-streams/
    # lets load a pcap file into Scapy
    a = rdpcap(pcap_file)

    # load the packets into a new variable to hold each the sessions
    # This separates each TCP session into a new variable as a dictionary object
    sessions = a.sessions()
    
    for session in sessions:
        http_payload = ""
        
        for packet in sessions[session]:
            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    # reassemble the stream, similar to the Wireshark "Follow TCP Stream"
                    http_payload += str(packet[TCP].payload)
                    # debug payload: redirect the output to a file
                    #print http_payload
            except:
                pass

        headers = get_http_headers(http_payload)

        if headers is None:
            continue

        # extract the raw image from the response
        image, image_type = extract_image(headers, http_payload)
        
        if image is not None and image_type is not None:
            #store the image
            file_name = "%s-pic_carver_%d.%s" % (pictures_directory, carved_images, image_type)
            #fd = open("%s/%s" % (pictures_directory, file_name), "wb")
            #fd.write(image)
            #fd.close()

            carved_images += 1
            
            #now attempt face detection
            try:
                # print "[*] Trying to detect faces on picture %s/%s" % (pictures_directory, file_name)
                result = face_detect("%s/%s" % (pictures_directory, file_name), file_name)
                if result == True:
                    faces_detected += 1
            except:
                pass

    return carved_images, faces_detected

carved_images, faces_detected = http_assembler(pcap_file)

print "[*] Extracted: %d images" % carved_images
print "[*] Detected: %d faces" % faces_detected
        






