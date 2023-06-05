import numpy
import cv2
from cv2 import aruco
import copy
from math import floor




video = cv2.VideoCapture(0)     # Open default Webcam, gotta change when i get hands on intel rlsense
if not video.isOpened():
    print("Cannot open camera")
    exit()



#-----------------------------------------------------------------
#!!TO EDIT!!

aruco_dict = cv2.aruco.Dictionary_get(
     cv2.aruco.DICT_6X6_250
)


locations = ['obstacle1', 'obstacle2', 'obstacle3', 'obstacle4', 'obstacle5', 'obstacle6', 'obstacle7', 'obstacle8', 'obstacle9', 'obstacle10', 'obstacle11', 'obstacle12']
#NOTE: For the rest to work make sure the index of each location matches up with the marker_id of its aruco marker
#------------------------------------------------------------------



aruco_params = cv2.aruco.DetectorParameters_create()
last = None



while True:    
        ret, aruco_image = video.read()
        #ret is a boolean that checks if the camera is reding anything
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break


        

        marker_corners, marker_ids, rejectedImgPoints = cv2.aruco.detectMarkers(aruco_image, aruco_dict, parameters=aruco_params)
        #the aruco.detectMArkers function does ALL the work for me and finds then scans any aruco marker providing the info above
        #marker corners shows the corners of the detected marker in a numpy array; if there are no markers it returns an empty list (which is the feature i used to see if there was a marker)
        #marker id returns the id of the scanned marker
        #rejected points shows all the areas where there are no aruco markers (I think, honestly I haven't really looked into this one; seems relatively useless)
        if marker_corners:
            if marker_ids != last:
                markerID = marker_ids[0][0] 
                #they format it in a way where there are multiple lists with a single item: ex: [[[1]]]

                print(f'You have scanner marker: {markerID}') 
                #---------------------------------------
                #!!TO EDIT!! (possibly, maybe this can be used):
                print(f'you are at {locations[markerID-1]}')
                #-1 because the prebuilt library has their first markerID to be 1 and not 0
                #---------------------------------------


                last = copy.copy(marker_ids)
                #makes sure you don't show the same qr code twice in a row. copy.copy ensures you make a deep copy
            lines = []
            for i in range(4):
                lines.append((floor(numpy.array(marker_corners[0][0])[i][0]), floor(numpy.array(marker_corners[0][0])[i][1])))
                #puts each point's coordinates in a tuple (the extra [0]s are because there are multiple lists with a single item: ex: [[[1]]]
            for i in range(4):
                cv2.line(aruco_image,lines[i],lines[i-(len(lines)-1)],(3, 232, 252),5)
                #makes a line between the coordinates to make a square that unlike the prebuilt function can tilt diagonally
                #the tpoints[i-(len(lines)-1] is the same as tpoints[i-3] it takes the point after tpoint[i] (so like tpoints[i+1]) but makes sure to go back to the first element when i = 3 so that when we make the line between tpoints[3] and tpoints[0] it doesn't try to access tpoints[4]
                #also the colour is bgr not rbg (I know, so confusing right?)
            



        # aruco_image = imutils.resize(aruco_image, width=600)
        # aruco_image = cv2.imshow('aruco_image', aruco_image)


        # Draw the detected markers
        
                

        cv2.imshow("Frame", aruco_image)    # Show video frame
        
        key = cv2.waitKey(1)        # Breaks the loop if 'q' is pressed
        if key == ord('q'):
            break

video.release()
cv2.destroyAllWindows()




#WHEN THERE IS A MARKER (example):

# [[8]] 
# '----> marker id


# (array([[[398., 355.],
#         [400., 372.],
#         [385., 374.],
#         [384., 357.]]], dtype=float32), array([[[177., 437.],
#         [183., 433.],
#         [190., 433.],
#         [195., 435.]]], dtype=float32), array([[[256., 252.],
#         [257., 256.],
#         [252., 260.],
#         [252., 254.]]], dtype=float32), array([[[366., 217.],
#         [369., 215.],
#         [383., 216.],
#         [380., 218.]]], dtype=float32), array([[[569., 332.],
#         [584., 408.],
#         [580., 426.],
#         [564., 344.]]], dtype=float32), array([[[294., 309.],
#         [300., 304.],
#         [344., 304.],
#         [331., 313.]]], dtype=float32), array([[[442., 218.],
#         [479., 214.],
#         [497., 223.],
#         [449., 226.]]], dtype=float32))
# '----> rejected points


# (array([[[283., 295.],
#         [436., 291.],
#         [439., 455.],
#         [283., 471.]]], dtype=float32),)
# '----> marker corners




#-------------------------------------------------------------------------------------------------------------




# WHEN THERE ARE NO MARKERS (example):


# None
# '----> marker id (note: there are said to be multiple objects and you will be forced to use .any() or .all())


# (array([[[291., 406.],
#         [296., 404.],
#         [312., 405.],
#         [309., 407.]]], dtype=float32), array([[[477., 318.],
#         [513., 320.],
#         [507., 325.],
#         [489., 326.]]], dtype=float32), array([[[524., 322.],
#         [495., 328.],
#         [469., 318.],
#         [521., 316.]]], dtype=float32), array([[[480.,  50.],
#         [488.,  55.],
#         [502.,  71.],
#         [499.,  71.]]], dtype=float32))
# '----> rejected points


# ()
# '----> marker corners