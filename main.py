import cv2
import mediapipe as mp
from datetime import datetime
import pyautogui

from agent.eye_gaze_runtime import predict_gaze
from logs.eye_performance import EyePerformanceMetrics
# from utils.keystroke import KEY_STROKES
from gestures.gesture_engine import GestureEngine
from utils.draw_utils import draw_frame
from config.settings import (
    CAMERA, RECORDING, FPS, RECORDING_FILENAME, SHOW_EYE_WINDOW
)
from camera.frame_grabber import get_video_capture, get_frame, release_capture
from camera.landmark_tracker import get_face_mesh, process_face_mesh



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Initialize gesture engine and performance metrics
gesture_engine = GestureEngine()
metrics = EyePerformanceMetrics()

cap = get_video_capture(CAMERA)

if RECORDING:
    frame_size = (int(cap.get(3)), int(cap.get(4)))
    recording = cv2.VideoWriter( #videowirter is used to compres and save video
        # MJPG is Motion JPEG
        RECORDING_FILENAME, cv2.VideoWriter_fourcc(*'MJPG'), FPS, frame_size) 

face_mesh = get_face_mesh()
while cap.isOpened():
    success, image = get_frame(cap) # handles the process of reading single frame frp, video stream [success: image sucessfully read | image: holds frame ]
    if not success:
        break

    image.flags.writeable = False # tells program mp wont modify image data directly. Avoids need for mp to create copy of image in memory
    # Flip the image horizontally for a later selfie-view display
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = process_face_mesh(face_mesh, image)

    # gaze_x, gaze_y = predict_gaze(image)
    # if gaze_x is not None and gaze_y is not None:
    #     pyautogui.moveTo(gaze_x, gaze_y)

    gaze_x, gaze_y, eye_img = predict_gaze(image, return_eye=SHOW_EYE_WINDOW, metrics=metrics)
    if gaze_x is not None and gaze_y is not None:
        pyautogui.moveTo(gaze_x, gaze_y)

    # Show eye window if enabled
    if SHOW_EYE_WINDOW and eye_img is not None:
        cv2.imshow("Eye View", eye_img)

    #
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
        face_landmarks = results.multi_face_landmarks[0]
        # gesture recognition is handled by the gesture engine
        gesture_engine.process_gestures(face_landmarks.landmark)

        draw_frame(
            image, face_landmarks,
            mp_drawing, mp_drawing_styles, mp_face_mesh,
            gesture_engine.current_keys
        )
        if RECORDING:
            recording.write(image)

    # Type 'q' on the video frame to quit
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

if RECORDING:
    recording.release()

release_capture(cap)
cv2.destroyAllWindows()

# Display performance metrics
metrics.plot_metrics()
