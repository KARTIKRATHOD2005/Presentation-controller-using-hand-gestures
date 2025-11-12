import cv2
import mediapipe as mp
import numpy as np
import os

# --- Configuration ---
PRESENTATION_FOLDER = "PresentationSlides"  # **Make sure this matches your folder name**
WEBCAM_WIDTH, WEBCAM_HEIGHT = 1280, 720
DRAW_COLOR = (0, 0, 255)  # Red color (BGR)
DRAW_THICKNESS = 12

# --- Setup ---
cap = cv2.VideoCapture(0)
cap.set(3, WEBCAM_WIDTH)
cap.set(4, WEBCAM_HEIGHT)

# Get the list of slide images
slide_files = sorted(os.listdir(PRESENTATION_FOLDER))
total_slides = len(slide_files)
current_slide_num = 0

# MediaPipe Hand setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
tip_ids = [4, 8, 12, 16, 20]  # Fingertip landmark IDs

# Annotation variables
annotations = [[]]  # A list of lists, where each inner list is a line
annotation_number = 0
annotation_start = False

# Cooldown for slide changes
delay = 30  # Frames
counter = 0
button_pressed = False

# --- Stability Fix Variables ---
gesture_hold_frames = 5  # How many frames to hold a gesture
current_gesture = None   # The stable, confirmed gesture
previous_gesture = None  # The raw gesture from the last frame
gesture_counter = 0      # Counts frames for a stable gesture
# --- End of Stability Variables ---

# --- Main Application Loop ---
while True:
    # 1. Load the current slide
    slide_path = os.path.join(PRESENTATION_FOLDER, slide_files[current_slide_num])
    img_slide = cv2.imread(slide_path)
    img_slide = cv2.resize(img_slide, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
    
    # 2. Capture and process webcam feed
    success, img_webcam = cap.read()
    if not success:
        break
    img_webcam = cv2.flip(img_webcam, 1)  # Flip for a mirror view
    img_rgb = cv2.cvtColor(img_webcam, cv2.COLOR_BGR2RGB)
    
    results = hands.process(img_rgb)
    
    # Create a blank canvas for drawing
    img_canvas = np.zeros((WEBCAM_HEIGHT, WEBCAM_WIDTH, 3), np.uint8)

    # --- Start of Gesture Logic ---
    raw_gesture = None # The gesture in this single frame
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        # Draw hand landmarks on the webcam feed (optional)
        mp_draw.draw_landmarks(img_webcam, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        lm_list = []
        # Get landmark coordinates
        for id, lm in enumerate(hand_landmarks.landmark):
            h, w, c = img_webcam.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append([id, cx, cy])
            
        # 3. --- Detect Raw Gesture ---
        fingers = []
        if len(lm_list) != 0:
            # Thumb (checks x-coordinate)
            # Note: This logic is for a right hand. 
            # For a left hand, you might need to flip the > operator.
            if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            
            # Other 4 fingers (checks y-coordinate)
            for id in range(1, 5):
                if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            # Get index finger position
            index_finger_pos = (lm_list[8][1], lm_list[8][2])

            # --- Map fingers to a raw gesture name ---
            if fingers == [0, 1, 1, 0, 0]:
                raw_gesture = "POINTER"
            elif fingers == [0, 1, 0, 0, 0]:
                raw_gesture = "DRAW"
            elif fingers == [0, 1, 1, 1, 0]:
                raw_gesture = "ERASE"
            elif fingers == [1, 0, 0, 0, 0]:
                raw_gesture = "NEXT"
            elif fingers == [0, 0, 0, 0, 1]:
                raw_gesture = "PREVIOUS"
        
    # 4. --- Confirm Stable Gesture (The Stability Fix) ---
    if raw_gesture == previous_gesture:
        gesture_counter += 1
    else:
        gesture_counter = 0
        previous_gesture = raw_gesture

    current_gesture = None # Reset stable gesture
    
    if gesture_counter > gesture_hold_frames:
        current_gesture = raw_gesture # Promote raw gesture to stable gesture
        # NOTE: We DO NOT reset gesture_counter here, so continuous actions work
        
    # 5. --- Perform Actions Based on STABLE Gesture (Corrected Logic) ---
    
    # --- Continuous Actions (No Cooldown) ---
    if current_gesture == "POINTER":
        annotation_start = False
        cv2.circle(img_slide, index_finger_pos, 12, DRAW_COLOR, cv2.FILLED)

    elif current_gesture == "DRAW":
        if annotation_start is False:
            annotation_start = True
            annotation_number += 1
            annotations.append([])
        annotations[annotation_number].append(index_finger_pos)
        cv2.circle(img_slide, index_finger_pos, 12, DRAW_COLOR, cv2.FILLED)
    
    # --- Single-Trigger Actions (With Cooldown) ---
    elif not button_pressed: # Only check these if cooldown is off
        
        if current_gesture == "ERASE":
            if annotations:
                annotations.pop(-1)
                if annotation_number > 0:
                    annotation_number -= 1
                button_pressed = True
                print("Action: Erase")
            annotation_start = False

        elif current_gesture == "NEXT":
            if current_slide_num < total_slides - 1:
                current_slide_num += 1
                annotations = [[]]; annotation_number = 0; annotation_start = False
                button_pressed = True
                print(f"Action: Next Slide ({current_slide_num})")
            annotation_start = False

        elif current_gesture == "PREVIOUS":
            if current_slide_num > 0:
                current_slide_num -= 1
                annotations = [[]]; annotation_number = 0; annotation_start = False
                button_pressed = True
                print(f"Action: Previous Slide ({current_slide_num})")
            annotation_start = False

    # If it's not a drawing gesture, stop drawing
    if current_gesture != "DRAW":
        annotation_start = False
        
    # --- End of Gesture Logic ---

    # Cooldown logic
    if button_pressed:
        counter += 1
        if counter > delay:
            counter = 0
            button_pressed = False

    # 6. Draw Annotations on Canvas
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(img_canvas, annotations[i][j - 1], annotations[i][j], DRAW_COLOR, DRAW_THICKNESS)

    # 7. Combine Images
    # Use bitwise operations to merge the drawing onto the slide
    img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    
    img_slide = cv2.bitwise_and(img_slide, img_inv)
    img_slide = cv2.bitwise_or(img_slide, img_canvas)

    # 8. Overlay Webcam Feed
    img_small_webcam = cv2.resize(img_webcam, (320, 180))
    h, w, _ = img_slide.shape
    img_slide[0:180, w - 320: w] = img_small_webcam

    # 9. Display the final image
    cv2.imshow("Virtual Presenter", img_slide)

    # 10. Quit
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()