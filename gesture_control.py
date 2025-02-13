import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Open the webcam
cap = cv2.VideoCapture(0)

# Initialize variables for debouncing
last_action_time = time.time()
debounce_interval = 1.0  # Time in seconds to wait between actions

def detect_gesture(landmarks):
    # Extracting the positions of the thumb and index finger
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]
    
    # Compute distance between thumb and index finger (for pinch gesture)
    pinch_distance = np.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
    
    # Define gesture thresholds
    if pinch_distance < 0.05:
        return "pinch"
    
    # Swipe gestures
    if index_tip.x < 0.3:  # Swipe left
        return "swipe_left"
    
    if index_tip.x > 0.7:  # Swipe right
        return "swipe_right"
    
    # Assuming thumb and index finger distance is large for zoom-out
    if pinch_distance > 0.2:  # Adjust this threshold as needed
        return "zoom_out"
    
    return None

def detect_two_handed_palm(results):
    if len(results.multi_hand_landmarks) == 2:
        # If both hands are detected, consider it as palm detection
        return True
    return False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Flip the frame horizontally to correct mirroring
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (required by MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe
    results = hands.process(rgb_frame)

    # If hands are detected, proceed
    if results.multi_hand_landmarks:
        # Draw hand landmarks on the frame
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Detect two-handed palm detection
        palm_detected = detect_two_handed_palm(results)
        gesture = None
        
        if not palm_detected:
            # Detect single hand gestures if two hands are not detected
            for hand_landmarks in results.multi_hand_landmarks:
                gesture = detect_gesture(hand_landmarks)
                if gesture:
                    break
        
        current_time = time.time()
        
        # Check if enough time has passed since the last action
        if palm_detected and (current_time - last_action_time > debounce_interval):
            # Take a screenshot
            screenshot = pyautogui.screenshot()  # Take a screenshot
            screenshot.save('screenshot.png')  # Save the screenshot
            print("Gesture detected: Both Hands - Screenshot taken and saved as screenshot.png")
            
            # Update the last action time
            last_action_time = current_time

        elif gesture and (current_time - last_action_time > debounce_interval):
            if gesture == "swipe_left":
                pyautogui.press('left')  # Move to previous slide
                print("Gesture detected: Swipe Left - Previous Slide")
            elif gesture == "swipe_right":
                pyautogui.press('right')  # Move to next slide
                print("Gesture detected: Swipe Right - Next Slide")
            elif gesture == "pinch":
                pyautogui.hotkey('ctrl', '+')  # Zoom In
                print("Gesture detected: Pinch - Zoom In")
            elif gesture == "zoom_out":
                pyautogui.hotkey('ctrl', '-')  # Zoom Out
                print("Gesture detected: Zoom Out")
            
            # Update the last action time
            last_action_time = current_time

    # Show the webcam feed
    cv2.imshow('Gesture-Controlled Presentation', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# import cv2

# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("Failed to open camera.")
# else:
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to capture frame")
#             break
#         cv2.imshow('Camera Test', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     cap.release()
#     cv2.destroyAllWindows()

"""
cd C:\Users\kirth\OneDrive\Desktop\python.py\GestureRecognition

myenv\Scripts\activate

python gesture_control.py

q

"""