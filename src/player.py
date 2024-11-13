import os
import cv2
import threading
import numpy as np
from cv2 import aruco
import pyrr
import shutil
from tqdm import tqdm
from utils.camera_pose_estimation import estimatePoseSingleMarkers, detect_checker_board
from utils.images_to_video import images_to_video
from utils.images_to_video import overlay_images


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.player_camera_calib_parameters = None
        self.player_camera_calib_parameters_lock = threading.Lock()
        self.player_camera_pose = None
        self.player_camera_pose_lock = threading.Lock()
        self.fy = None
        self.player_control = 0
        self.virtual_view = None
        self.virtual_view_lock = threading.Lock()
        self.virtual_view_count = 0

        self.stored_frame = None
        self.stored_corners = None
        self.marker_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.parameters = aruco.DetectorParameters() 

        self.calib_images = 0
        self.calib_folder = f"./temp_images/{self.player_id}"
        os.makedirs(self.calib_folder, exist_ok=True)

        self.flags = {
        'up': False,
        'down': False,
        'left': False,
        'right': False,
        'scaleXPlus': False,
        'scaleXMinus': False,
        'scaleYPlus': False,
        'scaleYMinus': False
        }
        self.score = 0

    def LoadCameras(self):
        folder_path = "./saved_cameras"
        data = np.load("./saved_cameras/calib1h7Ic7u-v1Y1MChmAAAD.npz")

        camMatrix = data["camMatrix"]
        distCof = data["distCoef"]
        rVector = data["rVector"]
        tVector = data["tVector"]

        # print("camMatrix: ", camMatrix)
        # print("distCoeff: ", distCof)
        # print("rVector: ", rVector)
        # print("tVector: ", tVector)

        print("loaded calibration data successfully")

        with self.player_camera_calib_parameters_lock:
            self.player_camera_calib_parameters = (camMatrix, distCof, rVector, tVector)
            self.f = camMatrix[1,1]
        # TO DO: Load all npz files from folder_path
    def CalibrateCamera(self, calib_images_folder, calib_save_folder):
        # Checker board size
        CHESS_BOARD_DIM = (9, 6)

        # The size of Square in the checker board.
        SQUARE_SIZE = 16  # millimeters

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        obj_3D = np.zeros((CHESS_BOARD_DIM[0] * CHESS_BOARD_DIM[1], 3), np.float32)

        obj_3D[:, :2] = np.mgrid[0 : CHESS_BOARD_DIM[0], 0 : CHESS_BOARD_DIM[1]].T.reshape(
            -1, 2
        )
        obj_3D *= SQUARE_SIZE
        # print(obj_3D)

        # Arrays to store object points and image points from all the images.
        obj_points_3D = []  # 3d point in real world space
        img_points_2D = []  # 2d points in image plane.

        files = os.listdir(calib_images_folder)
        images_used = 0
        for i in tqdm(range(len(files))):
            if i % 2 != 0:
                continue

            file = f"img_{i}.png"
            # print(file)
            imagePath = f"{calib_images_folder}/{file}"

            try:
                image = cv2.imread(imagePath)
                grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            except:
                continue
            ret, corners = cv2.findChessboardCorners(image, CHESS_BOARD_DIM, None)
            if ret == True:
                obj_points_3D.append(obj_3D)
                corners2 = cv2.cornerSubPix(grayScale, corners, (3, 3), (-1, -1), criteria)
                img_points_2D.append(corners2)
                images_used += 1

        print(f"Using {images_used} images for calibration")

        # Remove temp images folder
        # shutil.rmtree(calib_images_folder)
        # os.rmdir(calib_images_folder)

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points_3D, img_points_2D, grayScale.shape[::-1], None, None
        )
        print("calibrated")

        print("dumping the data into one file using numpy ")
        np.savez(
            f"{calib_save_folder}/calib{self.player_id}",
            camMatrix=mtx,
            distCoef=dist,
            rVector=rvecs,
            tVector=tvecs,
        )

        print("-------------------------------------------")

        print("loading data stored using numpy savez function\n")

        data = np.load(f"{calib_save_folder}/calib{self.player_id}.npz")

        camMatrix = data["camMatrix"]
        distCof = data["distCoef"]
        rVector = data["rVector"]
        tVector = data["tVector"]

        # print("camMatrix: ", camMatrix)
        # print("distCoeff: ", distCof)
        # print("rVector: ", rVector)
        # print("tVector: ", tVector)

        print("loaded calibration data successfully")

        with self.player_camera_calib_parameters_lock:
            self.player_camera_calib_parameters = (camMatrix, distCof, rVector, tVector)
    def DetectArucoCorners(self, image):
        frame = image
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(gray_frame, self.marker_dict, parameters=self.parameters)
        if ids is not None:
            self.stored_frame = frame
            self.stored_corners = corners[0][0]
            return True
        else:
            return False
    def TrackCornersFromPrev(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prev_gray_frame = cv2.cvtColor(self.stored_frame, cv2.COLOR_BGR2GRAY)

        new_corners, status, error = cv2.calcOpticalFlowPyrLK(prev_gray_frame, gray_frame, self.stored_corners, None)
        # print(f"stored_corners: {self.stored_corners}\nnew_corners: {new_corners}")

        if not np.any(status == 0):
            self.stored_frame = frame
            self.stored_corners = new_corners
        else:
            self.stored_corners = None
            with self.player_camera_pose_lock:
                self.player_camera_pose = None
    def UpdateCamPoseFromCorners(self):
        frame = self.stored_frame.copy()
        corners = (np.array([self.stored_corners]),)
        
        ids = np.array([[0]])
        # aruco.drawDetectedMarkers(frame, corners, ids)
        for i, marker_id in enumerate(ids):
            corner = corners[i][0]
            x, y = int(corner[0][0]), int(corner[0][1])
            cv2.putText(frame, f"ID: {marker_id[0]}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        rvec, tvec, _ = estimatePoseSingleMarkers(corners, 0.1, self.player_camera_calib_parameters[0], self.player_camera_calib_parameters[1])
        cv2.drawFrameAxes(frame, self.player_camera_calib_parameters[0], self.player_camera_calib_parameters[1], rvec[0], tvec[0], 0.1 * 0.5)

        rvec = rvec[0]
        tvec = 3 * tvec[0]
        tvec = tvec.flatten()

        rotation_matrix, _ = cv2.Rodrigues(rvec)

        transformation_matrix = np.eye(4)
        transformation_matrix[:3, :3] = rotation_matrix
        transformation_matrix[:3, 3] =  tvec.flatten()
        transformation_matrix = np.dot(np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]]), transformation_matrix)
        
        with self.player_camera_pose_lock:
            self.player_camera_pose = transformation_matrix

        return frame
    def UpdateFrame(self, frame, flags):
        updated_frame = None
        self.flags = flags
        if self.player_control == 0: # Uncalibrated camera: either calibrate or choose from saved cameras
            # self.LoadCameras()
            # self.player_control = 2
            # return frame
        
            ret, updated_frame = detect_checker_board(frame.copy())
            
            if ret:
                cv2.imwrite(f"{self.calib_folder}/img_{self.calib_images}.png", frame)
                self.calib_images += 1 

            if self.calib_images == 100:
                self.player_control = 1
                my_thread = threading.Thread(target=self.CalibrateCamera(self.calib_folder, "./saved_cameras"))
                my_thread.start()

            cv2.putText(updated_frame, f"Calibrating: {self.calib_images} %", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        elif self.player_control == 1: # Calibrating camera, wait...
            updated_frame = frame.copy()
            cv2.putText(updated_frame, f"Calibrating: Loading...", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            with self.player_camera_calib_parameters_lock:
                if self.player_camera_calib_parameters is not None:
                    self.player_control = 2
        
        elif self.player_control == 2: # Calibrated, ready to play
            updated_frame = frame.copy()
            
            # Detect Aruco Marker
            status = self.DetectArucoCorners(updated_frame)

            # If Marker not detected but previously had been detected check for optical flow based tracking
            if (self.stored_corners is not None) and (not status):
                self.TrackCornersFromPrev(updated_frame)
            
            # Finally if corners exist right now, update camera_pose using it
            if self.stored_corners is not None:
                updated_frame = self.UpdateCamPoseFromCorners()

            # cv2.putText(updated_frame, f"Ready to Play!", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            # cv2.putText(updated_frame, f"Camera Matrix: ", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            # if self.player_camera_pose is not None:
            #     cv2.putText(updated_frame, f"{self.player_camera_pose[0]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
            #     cv2.putText(updated_frame, f"{self.player_camera_pose[1]}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
            #     cv2.putText(updated_frame, f"{self.player_camera_pose[2]}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
            #     cv2.putText(updated_frame, f"{self.player_camera_pose[3]}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
            
            with self.virtual_view_lock:
                if self.virtual_view is not None:
                    # cv2.imwrite(f"{self.calib_folder}/1.jpg", updated_frame)
                    # cv2.imwrite(f"{self.calib_folder}/2.jpg", self.virtual_view)
                    updated_frame = overlay_images(self.virtual_view, updated_frame)
                    # cv2.imwrite(f"{self.calib_folder}/3.jpg", updated_frame)
        return updated_frame