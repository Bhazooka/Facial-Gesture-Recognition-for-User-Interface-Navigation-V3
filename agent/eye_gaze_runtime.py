import torch
from torchvision import transforms
import cv2 as cv
from PIL import Image
import mediapipe as mp

# Same CNN model from training
class EyeGazeCNN(torch.nn.Module):
    def __init__(self):
        # 2 conv layers, 
        super(EyeGazeCNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2) 
        self.conv2 = torch.nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2)
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=0) # maxpooling used to reduce image size to make process faster and save space. [reduce computational load]
        # 3 fully connected layers
        self.fc1 = torch.nn.Linear(64 * 25 * 12, 512) # 64*25*12 represemts number of input features, flattened size from conv layer, 512 number of neurons in hidden layer
        self.fc2 = torch.nn.Linear(512, 128) # takes 512 outputs from prev layer and reduces to 128 nuerons
        self.fc3 = torch.nn.Linear(128, 2) # final layer, takes 128 output from prev layer and outputs 2 values (x,y) corrdinates for gaze on screen

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x))) # apply the 2 convolutional layers first
        x = self.pool(torch.relu(self.conv2(x))) 
        x = x.view(-1, 64 * 25 * 12) # flatten
        x = torch.relu(self.fc1(x)) # pass output to activation function
        x = torch.relu(self.fc2(x)) # relu is chosen because its computationally simple and helps prevent vanishing gradient problem (which can slow down training)
        x = self.fc3(x)
        return x

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = EyeGazeCNN()
model.load_state_dict(torch.load('models/best_eye_gaze_model.pth', map_location=device)) #load trained model
model.to(device)
model.eval()

# Preprocessing transform. series of image processing steps to before feeding into model
transform = transforms.Compose([
    transforms.Resize((50, 100)), # resize image to consistent size of 50*100 pixels
    transforms.ToTensor(),  # convert image to pytorch tensor
    transforms.Normalize(mean=[0.5], std=[0.5]) # pixel values normalized to a standard range which helps the model perform better.
])

# MediaPipe face mesh
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# EMA (exponential moving average) smoothing used ti make predicated gaze coordinates smoother and more stable by combining current prediction with weighted average of past prediction,
# reducing jitter
# an alternative is SMA (simple moving average)
alpha = 0.7
prev_x, prev_y = None, None

def predict_gaze(frame, return_eye=False): # core logic, runs on each video frame
    global prev_x, prev_y    # previous gaze coord to smooth gaze pred
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB) 
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks: # if landmarks found, use specific landmarks...
        landmarks = result.multi_face_landmarks[0].landmark #returns list of faces - [0] selects first detected face in frame
        h, w = frame.shape[:2]
        try:
            eye_box = frame[ # to calc eye boundaries
                int(landmarks[27].y * h):int(landmarks[23].y * h),
                int(landmarks[226].x * w):int(landmarks[190].x * w)
            ]
            eye_box = cv.cvtColor(eye_box, cv.COLOR_BGR2GRAY) # convert to grayscale
            eye_box = cv.resize(eye_box, (100, 50)) # resize image
        except:
            return None, None, None

        pil_image = Image.fromarray(eye_box)
        eye_tensor = transform(pil_image).unsqueeze(0).to(device)

        with torch.no_grad(): # dont calc gradient, saves memory and speeds up inference
            output = model(eye_tensor)
            x, y = output.cpu().numpy()[0] # output tensor moved to cpu, convert to numpy array & extract predicted values

            if prev_x is None: prev_x = x
            if prev_y is None: prev_y = y
            # apply EMA smoothing to produce stable results
            x = alpha * prev_x + (1 - alpha) * x # EMA formula, smooth value is 70% old value + 30% new raw prediction
            y = alpha * prev_y + (1 - alpha) * y 
            prev_x, prev_y = x, y

            if return_eye: # if return eye is treu show eyebox image
                return int(x), int(y), eye_box
            else:
                return int(x), int(y), None # otherwise nothing
    return None, None, None