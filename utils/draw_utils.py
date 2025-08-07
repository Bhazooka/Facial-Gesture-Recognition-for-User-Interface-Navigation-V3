import cv2

def draw_frame(image, face_landmarks, mp_drawing, mp_drawing_styles, mp_face_mesh, current_morse):
    mp_drawing.draw_landmarks(
        image=image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_TESSELATION, # draws the individual triangles make up the face mesh.
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
    
    mp_drawing.draw_landmarks(
        image=image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_CONTOURS, # draw key face contours (eyebrows, eyes, mouth, nose)
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())
    
    mp_drawing.draw_landmarks(
        image=image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_IRISES, # (draw outline of iris)
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style())
    
    frame = cv2.flip(image, 1)  # flip the image
    cv2.putText(frame, current_morse, (620, 30),    # writes morse stringonto fram at specified position
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2) # font color
    cv2.imshow('face', frame) 