#  Gesture-Controlled Virtual Presenter

A Python application that allows you to control a slide presentation and draw on it in real-time using hand gestures, all captured through a webcam.

---

### 🚀 Features

* **Slide Navigation:** Change slides with a "Thumb Up" (Next) or "Pinky Up" (Previous).
* **Virtual Pointer:** Use your index and middle finger to get a live pointer.
* **Live Annotation:** Use your index finger as a virtual pencil to draw on the slides.
* **Erase:** Use a three-finger gesture to erase the last annotation.

---

### 🛠️ Tech Stack

* **Python:** The core programming language.
* **OpenCV:** For capturing the webcam feed and handling image processing.
* **MediaPipe:** For real-time hand and finger landmark detection.
* **NumPy:** For handling image and canvas manipulation.

---

### 🏃‍♂️ How to Run

1.  **Export Your Slides:** Export your PowerPoint presentation as a folder of JPEG images.
2.  **Move Folder:** Place this folder (e.g., `PresentationSlides`) inside the project directory.
3.  **Update Code:** Make sure the `PRESENTATION_FOLDER` variable in `virtual_presenter.py` matches your folder's name.
4.  **Install Dependencies:**
    ```bash
    pip install opencv-python mediapipe numpy
    ```
5.  **Clone Repository:**
    ```bash
    git clone https://github.com/KARTIKRATHOD2005/Presentation-controller-using-hand-gestures.git
    ```
6.  **Navigate to the project directory:**
    ```bash
    Presentation-controller-using-hand-gestures
    ```
7.  **Run the Script:**
    ```bash
    python virtual_presenter.py
  
