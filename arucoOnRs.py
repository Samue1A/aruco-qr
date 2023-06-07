import pyrealsense2 as rs
import numpy as np
import cv2
from cv2 import aruco
import copy
from math import floor
import time



def main():
    #-----------------------------------------------------------------
    #!!TO EDIT!!

    aruco_dict = cv2.aruco.Dictionary_get(
        cv2.aruco.DICT_6X6_250
    )


    locations = ['obstacle1', 'obstacle2', 'obstacle3', 'obstacle4', 'obstacle5', 'obstacle6', 'obstacle7', 'obstacle8', 'obstacle9', 'obstacle10', 'obstacle11', 'obstacle12']
    #NOTE: For the rest to work make sure the index of each location matches up with the marker_id of its aruco marker
    #------------------------------------------------------------------

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))


    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    

    # Start streaming
    pipeline.start(config)

    last = None
    lasts = []

    aruco_params = cv2.aruco.DetectorParameters_create()


    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        marker_corners, marker_ids, rejectedImgPoints = cv2.aruco.detectMarkers(color_image, aruco_dict, parameters=aruco_params)
        #the aruco.detectMArkers function does ALL the work for me and finds then scans any aruco marker providing the info above
        #marker corners shows the corners of the detected marker in a numpy array; if there are no markers it returns an empty list (which is the feature i used to see if there was a marker)
        #marker id returns the id of the scanned marker
        #rejected points shows all the areas where there are no aruco markers (I think, honestly I haven't really looked into this one; seems relatively useless)
        
        
        if marker_corners:
            markerID = marker_ids[0][0]
            try:
                if markerID != last and markerID <= len(locations):
                    #they format it in a way where there are multiple lists with a single item: ex: [[[1]]]

                    print(f'You have scanner marker: {markerID}') 
                    #---------------------------------------
                    #!!TO EDIT!! (possibly, maybe this can be used):
                    print(f'you are at {locations[markerID-1]}')
                    #-1 because the prebuilt library has their first markerID to be 1 and not 0
                    #---------------------------------------
            except ValueError:
                if all(markerID != last):
                    print(f'You have scanner marker: {markerID}') 
                    #---------------------------------------
                    #!!TO EDIT!! (possibly, maybe this can be used):
                    print(f'you are at {locations[markerID-1]}')
                    #-1 because the prebuilt library has their first markerID to be 1 and not 0
                    #---------------------------------------


            last = copy.copy(markerID)
            #makes sure you don't show the same qr code twice in a row. copy.copy ensures you make a deep copy
            lines = []
            for i in range(4):
                lines.append((floor(np.array(marker_corners[0][0])[i][0]), floor(np.array(marker_corners[0][0])[i][1])))
                #puts each point's coordinates in a tuple (the extra [0]s are because there are multiple lists with a single item: ex: [[[1]]]
            for i in range(4):
                cv2.line(color_image, lines[i],lines[i-(len(lines)-1)],(3, 232, 252),5)
                #makes a line between the coordinates to make a square that unlike the prebuilt function can tilt diagonally
                #the tpoints[i-(len(lines)-1] is the same as tpoints[i-3] it takes the point after tpoint[i] (so like tpoints[i+1]) but makes sure to go back to the first element when i = 3 so that when we make the line between tpoints[3] and tpoints[0] it doesn't try to access tpoints[4]
                #also the colour is bgr not rbg (I know, so confusing right?)

            xs = 0
            ys = 0
            for point in marker_corners[0][0]:
                xs += floor(np.array(point[0]))
                ys += floor(np.array(point[1]))
            avr = (xs//len(marker_corners[0][0]), ys//len(marker_corners[0][0]))
            #avr here is the center of the aruco marker. I chose the center as it shouldn't change even if your rotate the marker along of axis that passes through the center

            distInCm = round(depth_frame.get_distance(int(avr[0]), int(avr[1]))*100)
            #here we use the prebuilt function to find the distance to the center of the marker
            #the *100 is to convert from m to cm
            #avr[0] is the x and avr[1] is the y

            if distInCm:
                #sometimes the function makes a mistake and qualifies the distance as 0 even when it isn't this removes those cases and even if the distance where truly 0 the following info wouldn't be of much use, justifying why i put it in an if statement
                distFromCenter_Px = floor(((320-avr[0])**2)**0.5)
                #finds the distance on the x axis from the center of the x axis the **2**0.5 makes it positif as it is a distance and therefore must be positive
                #i did not find the distance on the y as i doubt the robot dog could fly
                turn = round(distFromCenter_Px*2/13)
                #this turns the distance in px to a degree value. the constant 2/13 was found thanks to an experiment
                direction = 'left'*((320-avr[0]<0)) or 'right'
                #this finds whether it as right or left based on if (320-the x-value of the aruco marker) is positiveor negative


                if not lasts or (lasts[-1] != [turn,direction,distInCm] and lasts[0] != [turn,direction,distInCm]):
                    #the above if statement makes sure we don't repeat the same info
                    #lasts[0] != [turn,direction,distInCm]  is because the distance function can hover between two values
                    if len(lasts) < 2 or distInCm-(sum(list(zip(lasts[0], lasts[-1]))[-1])/2) < 20:
                        #This is because the distance function would sometimes have wild outliars ex: 8cm, 8cm, 50cm
                        #This avoids the 50cm filtering it out
                        print(f" turn {turn} degrees {direction}; then walk {distInCm}cm forward")
                        lasts.append(copy.copy([turn,direction,distInCm]))
                    if len(lasts) == 2:
                        lasts.pop(0)
                    



        # If depth and color resolutions are different, resize color image to match depth image for display    
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))   



        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)



        # Breaks the loop if 'q' is pressed
        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    # Stop streaming
    pipeline.stop()


if __name__ == '__main__':
    main()



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
