import cv2
import mediapipe as mp

# Define some constants
LINE_THICKNESS = 3
MIN_HAND_CONFIDENCE = 0.5

# Create a VideoCapture object to read from the webcam
cap = cv2.VideoCapture(0)

# Initialize the hand tracking model
mp_hands = mp.solutions.hands.Hands(min_detection_confidence=MIN_HAND_CONFIDENCE)

# Initialize the previous finger position to None
prev_finger_pos = None

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect hands using the mediapipe model
    results = mp_hands.process(gray)

    # If at least one hand is detected, get the coordinates of the index finger
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        index_finger_pos = (int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1]),
                            int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0]))

        # If this is not the first frame, draw a line between the current and previous finger positions
        if prev_finger_pos is not None:
            cv2.line(frame, prev_finger_pos, index_finger_pos, (0, 0, 255), LINE_THICKNESS)

        # Update the previous finger position
        prev_finger_pos = index_finger_pos

    # Display the image
    cv2.imshow('Hand tracking', frame)

    # Break the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close the window
cap.release()
cv2.destroyAllWindows()
