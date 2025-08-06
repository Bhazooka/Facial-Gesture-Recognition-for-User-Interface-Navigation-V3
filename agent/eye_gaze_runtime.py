import torch
from torchvision import transforms
import cv2 as cv
from PIL import Image
import mediapipe as mp

# Same CNN model from training
class EyeGazeCNN(torch.nn.Module):
    def __init__(self):
        super(EyeGazeCNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2)
        self.conv2 = torch.nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2)
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = torch.nn.Linear(64 * 25 * 12, 512)
        self.fc2 = torch.nn.Linear(512, 128)
        self.fc3 = torch.nn.Linear(128, 2)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(-1, 64 * 25 * 12)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = EyeGazeCNN()
model.load_state_dict(torch.load('models/best_eye_gaze_model.pth', map_location=device))
model.to(device)
model.eval()

# Preprocessing transform
transform = transforms.Compose([
    transforms.Resize((50, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# MediaPipe face mesh
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# EMA smoothing
alpha = 0.7
prev_x, prev_y = None, None

def predict_gaze(frame):
    global prev_x, prev_y
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]
        try:
            eye_box = frame[
                int(landmarks[27].y * h):int(landmarks[23].y * h),
                int(landmarks[226].x * w):int(landmarks[190].x * w)
            ]
            eye_box = cv.cvtColor(eye_box, cv.COLOR_BGR2GRAY)
            eye_box = cv.resize(eye_box, (100, 50))
        except:
            return None, None

        pil_image = Image.fromarray(eye_box)
        eye_tensor = transform(pil_image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(eye_tensor)
            x, y = output.cpu().numpy()[0]

            if prev_x is None: prev_x = x
            if prev_y is None: prev_y = y

            x = alpha * prev_x + (1 - alpha) * x
            y = alpha * prev_y + (1 - alpha) * y
            prev_x, prev_y = x, y

            return int(x), int(y)
    return None, None
