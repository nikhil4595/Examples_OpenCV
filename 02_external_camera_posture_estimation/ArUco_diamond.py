import sys
sys.path.append('/usr/local/python/3.5')

# Standard imports
import os
import cv2
from cv2 import aruco
import numpy as np
from os import listdir
from os.path import isfile, join
#import yaml
import unittest


#############################Read Dictionary#######################################################
squareLength = 0.40
markerLength = 0.25
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )
# board = aruco.CharucoBoard_create(5, 7, 0.04, 0.03, aruco_dict)
# board = aruco.CharucoBoard_create(5, 7, 0.162, 0.081, aruco_dict)
# img = board.draw((512*2,512*3))
# cv2.imwrite("board.png", img)
###################################################################################################


#############################Read Stereo Calibrated Parameters#####################################
# Load Calibrated Parameters
stereoCalibrationFile = "/media/peijia/cinetec/Databases/cinetech/calibration/stereo_pointgrey_feb24_2.xml"
stereoCalibrationParams = cv2.FileStorage(stereoCalibrationFile, cv2.FILE_STORAGE_READ)
# image_width = stereoCalibrationParams.getNode("image_width")
# image_height = stereoCalibrationParams.getNode("image_height")
image_width = 1280
image_height = 1024
image_size = (image_width, image_height)
camera_matrix_l = stereoCalibrationParams.getNode("camera_matrix_l").mat()
distortion_coefficients_l = stereoCalibrationParams.getNode("distortion_coefficients_l").mat()
camera_matrix_r = stereoCalibrationParams.getNode("camera_matrix_r").mat()
distortion_coefficients_r = stereoCalibrationParams.getNode("distortion_coefficients_r").mat()
r_matrix = stereoCalibrationParams.getNode("r_matrix").mat()    # rotation between stereo
# t_matrix = stereoCalibrationParams.getNode("t_matrix").mat()    # translation between stereo
r1_matrix = stereoCalibrationParams.getNode("r1_matrix").mat()
r2_matrix = stereoCalibrationParams.getNode("r2_matrix").mat()
new_rect_cam_matrix_l = stereoCalibrationParams.getNode("new_rect_cam_matrix_l").mat()
new_rect_cam_matrix_r = stereoCalibrationParams.getNode("new_rect_cam_matrix_r").mat()
mapx_l, mapy_l = cv2.fisheye.initUndistortRectifyMap(camera_matrix_l, distortion_coefficients_l, r1_matrix, new_rect_cam_matrix_l, image_size, cv2.CV_16SC2)
mapx_r, mapy_r = cv2.fisheye.initUndistortRectifyMap(camera_matrix_r, distortion_coefficients_r, r2_matrix, new_rect_cam_matrix_r, image_size, cv2.CV_16SC2)
###################################################################################################


#####################################List All Image Pairs##########################################
# List video file
videoFile = "/media/peijia/cinetec/Databases/cinetech/calibration/videos/aruco_diamond.mp4"
# List image names
# leftImgsDir = "/media/peijia/cinetec/Databases/cinetech/calibration/07_charuco"
# rightImgsDir = "/media/peijia/cinetec/Databases/cinetech/calibration/07_charuco"


# leftImgFileNames = [os.path.join(leftImgsDir, fn) for fn in next(os.walk(leftImgsDir))[2]]
# rightImgFileNames = [os.path.join(rightImgsDir, fn) for fn in next(os.walk(rightImgsDir))[2]]
# if (len(leftImgFileNames) != len(rightImgFileNames)):
#     print("The number of left images must be equal to the number of right images.")
#     exit()
###################################################################################################


########################################aruco Detector#############################################
# Setup aruco parameters.
arucoParams = aruco.DetectorParameters_create()
###################################################################################################


############################For Loop, for All Captured Image Pairs#################################
# http://docs.opencv.org/trunk/d9/d6d/tutorial_table_of_content_aruco.html
# http://stackoverflow.com/questions/41656236/opencv-aruco-pose-estimation-example-code-from-tutorial
# nbOfImgs = len(leftImgFileNames)
# for i in range(0, 1000):
# for i in range(0, nbOfImgs):
cap = cv2.VideoCapture(videoFile)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
# for i,frame in enumerate(camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)):
# i = 0
    # Load images
    # imLeft = cv2.imread(leftImgFileNames[i], cv2.IMREAD_GRAYSCALE)
    # imRight = cv2.imread(rightImgFileNames[i], cv2.IMREAD_GRAYSCALE)
    if ret == True:
        imLeft = frame
        imRight = frame

        # Calibration
        imLeftRemapped_color = imLeft
        imRightRemapped_color = imRight
        imLeftRemapped = cv2.cvtColor(imLeftRemapped_color, cv2.COLOR_BGR2GRAY)
        imRightRemapped = cv2.cvtColor(imRightRemapped_color, cv2.COLOR_BGR2GRAY)
        # imLeftRemapped = cv2.remap(imLeft, mapx_l, mapy_l, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
        # imRightRemapped = cv2.remap(imRight, mapx_r, mapy_r, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
        # imLeftRemapped_color = cv2.cvtColor(imLeftRemapped, cv2.COLOR_GRAY2BGR)
        # imRightRemapped_color = cv2.cvtColor(imRightRemapped, cv2.COLOR_GRAY2BGR)
        # cv2.imwrite("diamondLeft.jpg", imLeftRemapped_color)
        # cv2.imwrite("diamondRight.jpg", imRightRemapped_color)

        # Detect markers
        cornersLeft, idsLeft, rejectedImgPointsLeft = aruco.detectMarkers(imLeftRemapped, aruco_dict, parameters=arucoParams)
        cornersRight, idsRight, rejectedImgPointsRight = aruco.detectMarkers(imRightRemapped, aruco_dict, parameters=arucoParams)

        # Estimate board pose
        if idsLeft != None:
            diamondCornersLeft, diamondIdsLeft = aruco.detectCharucoDiamond(imLeftRemapped, cornersLeft, idsLeft, squareLength/markerLength)
            if len(diamondCornersLeft) >= 1:
                im_with_diamond_left = aruco.drawDetectedDiamonds(imLeftRemapped_color, diamondCornersLeft, diamondIdsLeft, (0,255,0))
                rvecLeft, tvecLeft = aruco.estimatePoseSingleMarkers(diamondCornersLeft, squareLength, camera_matrix_l, distortion_coefficients_l)
                im_with_diamond_left = aruco.drawAxis(im_with_diamond_left, camera_matrix_l, distortion_coefficients_l, rvecLeft, tvecLeft, 1)
        else:
            im_with_diamond_left = imLeftRemapped_color

        if idsRight != None:
            diamondCornersRight, diamondIdsRight = aruco.detectCharucoDiamond(imLeftRemapped, cornersRight, idsRight, squareLength/markerLength)
            if len(diamondCornersRight) >= 1:
                im_with_diamond_right = aruco.drawDetectedDiamonds(imRightRemapped_color, diamondCornersRight, diamondIdsRight, (0,255,0))
                rvecRight, tvecRight = aruco.estimatePoseSingleMarkers(diamondCornersRight, squareLength, camera_matrix_r, distortion_coefficients_r)
                im_with_diamond_right = aruco.drawAxis(im_with_diamond_right, camera_matrix_r, distortion_coefficients_r, rvecRight, tvecRight, 1)
        else:
            im_with_diamond_right = imRightRemapped_color

        # Save/show circule grid
        # cv2.imwrite("diamondLeft.jpg", im_with_diamond_left)
        # cv2.imwrite("diamondRight.jpg", im_with_diamond_right)
        cv2.imshow("diamondLeft", im_with_diamond_left)
        cv2.imshow("diamondRight", im_with_diamond_right)

        if cv2.waitKey(2) & 0xFF == ord('q'):
            break

    else:
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

