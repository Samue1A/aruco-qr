import cv2
import copy
import numpy
from math import floor

#---------------------------------------------------------------------------------------------------------

last = None

video = cv2.VideoCapture(0)     # Open default Webcam, gotta change when i get hands on intel rlsense
if not video.isOpened():
    print("Cannot open camera")
    exit()

#-----------------------------------------


while True:    
        ret, img = video.read()
        #ret is a boolean that checks if the camera is reding anything
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        qcd = cv2.QRCodeDetector()
        #the qrcodedetector function does ALL the work for me and finds then scans any qr code providing the info below
        retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(img)
        #retval is a boolean that shows if there is a QR code
        #decoded_info returns the 'value' of the qr code in this format ('info',) with the tuple having no second value as far as my tests see
        #points gives the edges of the QR code undes a numpy array
        #straight_qr is a tuple whose elements are numpy.ndarray. The numpy.ndarray is a binary value of 0 and 255 representing the black and white of each cell of the QR code.
        if decoded_info:
            decoded_info = decoded_info[0] #they format it weird; otherwise it would be ('text',)
            if decoded_info != last:
                print(decoded_info)
            tpoints = [] #stands for tuple points as the openCV functions work with tuples, I reformatted points to make it tpoints
            for i in range(4):
                tpoints.append((floor(numpy.array(points[0][i])[0]), floor(numpy.array(points[0][i])[1])))
                #puts each point's coordinates in a tuple (the extra [0] is because the numpy array is in another array that has a single item, ex: [[1,2]])
            for i in range(4):
                cv2.line(img,tpoints[i], tpoints[i-(len(tpoints)-1)],(3, 232, 252),5)
                #makes a line between the coordinates to make a square that unlike the prebuilt function can tilt diagonally
                #the tpoints[i-(len(lines)-1] is the same as tpoints[i-3] it takes the point after tpoint[i] (so like tpoints[i+1]) but makes sure to go back to the first element when i = 3 so that when we make the line between tpoints[3] and tpoints[0] it doesn't try to access tpoints[4]
                #also the colour is bgr not rbg (I know, so confusing right?)
            last = copy.copy(decoded_info)
            #makes sure you don't scan the same qr code twice in a row. copy.copy ensures you make a deep copy
        

        cv2.imshow("Frame", img)    # Show video frame
        
        key = cv2.waitKey(1)        # Breaks the loop if 'q' is pressed
        if key == ord('q'):
            break

video.release()
cv2.destroyAllWindows()





     


