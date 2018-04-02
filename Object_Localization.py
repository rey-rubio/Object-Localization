import argparse

import cv2
import imutils
import numpy as np


def Object_Localization(frame, counter, red_pts, green_pts, blue_pts, yellow_pts):

    isv2 = imutils.is_cv2()

    isDetected = {"red": False, "green": False, "blue": False, "yellow": False}

    def distance_to_camera(knownWidth, focalLength, perWidth):
        # compute and return the distance from the image to camera
        return (knownWidth * focalLength) / perWidth

    KNOWN_DISTANCE = 24.0
    KNOWN_WIDTH = 2.65
    marker = 30

    focalLength = (marker * KNOWN_DISTANCE) / KNOWN_WIDTH

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
    args = vars(ap.parse_args())

    # define the lower and upper boundaries of multiple colors
    # ball in the HSV color space, then initialize the
    # list of tracked points
    #lower = {'red': (166, 84, 141), 'green': (66, 122, 129), 'blue': (97, 100, 117), 'yellow': (23, 59, 119)}
    #upper = {'red': (186, 255, 255), 'green': (86, 255, 255), 'blue': (117, 255, 255), 'yellow': (54, 255, 255)}
    lower= {'red': (0, 100, 100), 'green': (40, 70, 70), 'blue': (97, 100, 117), 'yellow': (23, 59, 119)}
    upper = {'red': (10, 255, 255), 'green': (80, 200, 200), 'blue': (117, 255, 255), 'yellow': (54, 255, 255)}

    # define standard colors for circle around the object
    colors = {'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0), 'yellow': (0, 255, 255)}

    _counter = counter

    inches = 0


    _red_xyz_pts = {'x': 0, 'y': 0, 'z': 0, 'pts': red_pts}
    _green_xyz_pts = {'x': 0, 'y': 0, 'z': 0, 'pts': green_pts}
    _blue_xyz_pts = {'x': 0, 'y': 0, 'z': 0, 'pts': blue_pts}
    _yellow_xyz_pts = {'x': 0, 'y': 0, 'z': 0, 'pts': yellow_pts}


    # resize the frame, blur it, and convert it to the HSV color space
    _frame = imutils.resize(frame, width=600)
    blurredFrame = cv2.GaussianBlur(_frame, (11, 11), 0)
    hsv = cv2.cvtColor(_frame, cv2.COLOR_BGR2HSV)

    for key, value in upper.items():
        print("key: " + str(key))
        # construct a mask for the each color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        # mask = cv2.inRange(hsv, greenLower, greenUpper)
        kernel = np.ones((9, 9), np.uint8)
        mask = cv2.inRange(hsv, lower[key], upper[key])
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # mask = cv2.erode(mask, None, iterations=2)
        # =mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]

        # if isv2:
        #     contours = contours[0]
        # else:
        #     contours = contours[1]
        # and initialize center of the ball
        center = None
        # only proceed if at least one contour was found


        #for(cnt in contours):
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # Get distance for Z-axis using reference image (In inches)
            marker = cv2.minAreaRect(c)
            inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])

            # only proceed if the radius meets a minimum size
            if radius > 1:
                # draw the circle and centroid on the frame
                # cv2.circle(thisFrame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(_frame, (int(x), int(y)), int(radius), colors[key], 2)
                cv2.circle(_frame, center, 5, (0, 0, 255), -1)

                if(key == "red"):
                    isDetected['red'] = True
                    _red_xyz_pts['pts'].appendleft(center)

                elif (key == "green"):
                    isDetected['green'] = True
                    _green_xyz_pts['pts'].appendleft(center)

                elif (key == "blue"):
                    isDetected['blue'] = True
                    _blue_xyz_pts['pts'].appendleft(center)

                elif (key == "yellow"):
                    isDetected['yellow'] = True
                    _yellow_xyz_pts['pts'].appendleft(center)


            if (key == "red"):

                print(" red pts length:\t" + str(len(_red_xyz_pts['pts'])))
                for i in np.arange(1, len(_red_xyz_pts['pts'])):
                    # if either of the tracked points are None, ignore
                    if _red_xyz_pts['pts'][i - 1] is None or _red_xyz_pts['pts'] is None:
                        print(" Not Enough Points ")
                        continue

                    # check to see if enough points have been accumulated in
                    # the buffer
                    if _counter >= 10 and i == 1 and _red_xyz_pts['pts'][-1] is not None:
                        _red_xyz_pts['x'] = _red_xyz_pts['pts'][-1][0] - _red_xyz_pts['pts'][i][0]
                        _red_xyz_pts['y'] = _red_xyz_pts['pts'][-1][1] - _red_xyz_pts['pts'][i][1]
                        _red_xyz_pts['z'] = round(inches)


            elif (key == "green"):
                print(" green pts length:\t" + str(len(_green_xyz_pts['pts'])))
                for i in np.arange(1, len(_green_xyz_pts['pts'])):
                    # if either of the tracked points are None, ignore
                    if _green_xyz_pts['pts'][i - 1] is None or _green_xyz_pts['pts'][i] is None:
                        print(" Not Enough Points ")
                        continue

                    # check to see if enough points have been accumulated in
                    # the buffer
                    if _counter >= 10 and i == 1 and _green_xyz_pts['pts'][-1] is not None:
                        # COMPUTE POINTS AND STORE INTO DATA STRUCTURE
                        _green_xyz_pts['x'] = _green_xyz_pts['pts'][-1][0] - _green_xyz_pts['pts'][i][0]
                        _green_xyz_pts['y'] = _green_xyz_pts['pts'][-1][1] - _green_xyz_pts['pts'][i][1]
                        _green_xyz_pts['z'] = round(inches)


            elif (key == "blue"):
                print(" blue pts length:\t" + str(len(_blue_xyz_pts['pts'])))
                for i in np.arange(1, len(_blue_xyz_pts['pts'])):
                    # if either of the tracked points are None, ignore
                    if _blue_xyz_pts['pts'][i - 1] is None or _blue_xyz_pts['pts'][i] is None:
                        print(" Not Enough Points ")
                        continue

                    # check to see if enough points have been accumulated in
                    # the buffer
                    if _counter >= 10 and i == 1 and _blue_xyz_pts['pts'][-1] is not None:
                        # COMPUTE POINTS AND STORE INTO DATA STRUCTURE
                        _blue_xyz_pts['x'] = _blue_xyz_pts['pts'][-1][0] - _blue_xyz_pts['pts'][i][0]
                        _blue_xyz_pts['y'] = _blue_xyz_pts['pts'][-1][1] - _blue_xyz_pts['pts'][i][1]
                        _blue_xyz_pts['z'] = round(inches)


            elif (key == "yellow"):

                print(" yellow pts length:\t" + str(len(_yellow_xyz_pts['pts'])))
                for i in np.arange(1, len(_yellow_xyz_pts['pts'])):
                    # if either of the tracked points are None, ignore
                    if _yellow_xyz_pts['pts'][i - 1] is None or _yellow_xyz_pts['pts'] is None:
                        print(" Not Enough Points ")
                        continue

                    # check to see if enough points have been accumulated in
                    # the buffer
                    if _counter >= 10 and i == 1 and _yellow_xyz_pts['pts'][-1] is not None:

                        if(abs(_yellow_xyz_pts['pts'][-1][0] - _yellow_xyz_pts['pts'][i][0]) > 2 ):
                            _yellow_xyz_pts['x'] = _yellow_xyz_pts['pts'][-1][0] - _yellow_xyz_pts['pts'][i][0]
                        else:
                            _yellow_xyz_pts['x'] = _yellow_xyz_pts['pts'][-1][0]

                        if (abs(_yellow_xyz_pts['pts'][-1][1] - _yellow_xyz_pts['pts'][i][1]) > 2):
                            _yellow_xyz_pts['y'] = _yellow_xyz_pts['pts'][-1][1] - _yellow_xyz_pts['pts'][i][1]
                        else:
                            _yellow_xyz_pts['y'] = _yellow_xyz_pts['pts'][-1][1]

                        _yellow_xyz_pts['z'] = round(inches)

            #contours = contours.h_next()

    # draw the connecting lines
    #thickness = int(np.sqrt(args["buffer"] / float(i + 1)))
    #cv2.line(thisFrame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # return the frame and increment counter
    _counter += 1


    print("COUNTER: " + str(_counter) +
          "\t\t\nRED:\t" + str(isDetected['red']) +
          " \t\tx_red:\t\t" + str(_red_xyz_pts['x']) +
          "\t\ty_red:\t\t" + str(_red_xyz_pts['y'])
          + "\t\tz_red:\t\t" + str(_red_xyz_pts['z']) +
          "\t\t\nGREEN:\t" + str(isDetected['green']) +
          " \t\tx_green:\t" + str(_green_xyz_pts['x']) +
          "\t\ty_green:\t" + str(_green_xyz_pts['y']) +
          "\t\tz_green:\t" + str(_green_xyz_pts['z']) +
          "\t\t\nBLUE:\t" + str(isDetected['blue']) +
          " \t\tx_blue:\t\t" + str(_blue_xyz_pts['x']) +
          "\t\ty_blue:\t\t" + str(_blue_xyz_pts['y']) +
          "\t\tz_blue:\t\t" + str(_blue_xyz_pts['z']) +
          "\t\t\nYELLOW:\t" + str(isDetected['yellow']) +
          "\t\tx_yellow:\t" + str(_yellow_xyz_pts['x']) +
          "\t\ty_yellow:\t" + str(_yellow_xyz_pts['y']) +
          "\t\tz_yellow:\t" + str(_yellow_xyz_pts['z'])
          )
    # print("counter: " + str(counter) + "\tpts: " + str(len(pts)) + " \t\t\tx: " + str(x) + "\t\t\ty: " + str(y) + "\t\t\tz: " + str(z))
    return _frame, _counter, _red_xyz_pts, _green_xyz_pts, _blue_xyz_pts, _yellow_xyz_pts, isDetected
