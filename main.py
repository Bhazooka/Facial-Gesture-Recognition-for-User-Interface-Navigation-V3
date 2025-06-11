import cv2
import mediapipe as mp
from datetime import datetime

from utils.morse import morse
from gestures.gesture_engine import GestureEngine
from utils.draw_utils import draw_frame
from config.settings import (
    CAMERA, RECORDING, FPS, RECORDING_FILENAME
)
from camera.frame_grabber import get_video_capture, get_frame, release_capture
from camera.landmark_tracker import get_face_mesh, process_face_mesh

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Initialize gesture engine
gesture_engine = GestureEngine()

cap = get_video_capture(CAMERA)

if RECORDING:
    frame_size = (int(cap.get(3)), int(cap.get(4)))
    recording = cv2.VideoWriter(
        RECORDING_FILENAME, cv2.VideoWriter_fourcc(*'MJPG'), FPS, frame_size)

face_mesh = get_face_mesh()
while cap.isOpened():
    success, image = get_frame(cap)
    if not success:
        break

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = process_face_mesh(face_mesh, image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
        face_landmarks = results.multi_face_landmarks[0]
        # All gesture recognition is now handled by the gesture engine
        gesture_engine.process_gestures(face_landmarks.landmark)

        draw_frame(
            image, face_landmarks,
            mp_drawing, mp_drawing_styles, mp_face_mesh,
            gesture_engine.current_morse
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
