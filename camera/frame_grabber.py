import cv2

def get_video_capture(camera_index):
    cap = cv2.VideoCapture(camera_index)
    return cap

def get_frame(cap):
    success, frame = cap.read()
    return success, frame

def release_capture(cap):
    cap.release()
    cv2.destroyAllWindows()