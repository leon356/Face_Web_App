import pandas as pd
import cv2
import numpy as np
import os
from datetime import datetime
import face_recognition
import serial
import time
import dropbox
import json

# === Dropbox Configuration ===
DROPBOX_ACCESS_TOKEN = 'sl.u.AFzl8z8Kd5vPydS1uFEfbN11N6oxyIaqhS7aGnhQKF0uC7P6pcO5jh0Hr0eFAFU6PGPAAdstcPcQY9rs808noUOb8siuA16qogu1KCShGlP8kHBGydGeo8Ty-vKuiRpJv-OF2VXb-75j9ATMUy9uCsAtoJx2T3dGqMyVLAv6edFELV2xbEVqYKNmcgJ9fXGtnfkYy55ZkG1FD7jR5C98ThB-UWyd1_rlWGA0hgSjlm1TSMcbH-hYYTvJT8el2X3tVmmGHtUcgEFr9V8Bu9rH9EBBVgfhd9bjlDhfTWWb9jPaqgjPYe2hEZV898yg7I7wC334RnW6LPH41PDRH2KCQk3x0J6iIUcgA0iMVwnEHYZobuntGz4v_IkdTUjwAP_7HUViCaMPws41e_aj0QubkEKLimp-dM2mEAx4dylwELg0QYbi94U8JKRN-sB_Xuh_4RN7_Rp1RHU1Aq05JKTkY5fsC8JlbW19Q59axhq3Ua2jrOMFj3uHH9Bg5--zhBgfv22ymY0oC50Z7G88BMYCw00phkTR1CKe5CLpnFqDOC57sbZ7Nw4Ppues2wlr8Z10zdbFcfrWeZSoJhe-RfVmnMcGWFbBKW69qyGUrxUdef2_Nnxk2RRHZxQDC0dhFP9ckoDd4XtrkP0jobT_R3MUjxg6THVXj5Ush-syKNnNK_sKOrp3D0BQKydWKIdTffZ1i5AsH3MtSr2Plc_yvMeb0HnTqa_j-J32tG8LJw1oZSEbAw8yEt5HYkUdqYom5TYiodOl2CVin_VSjEYC-ukTftPZeEdEXOvhxs9bGG1anp_cyrwhzdsgqo9dBj04SPpVWqo8zgo_jIn7ij5ocYd0AT5QhzZsp0O00FrmuJUzDGsOBxcXMTuuJ98XceUXf_WKZPUdHzEB1z5_PkvP_Y5Z6eK23gc_IxV8GwxA_rZXEjFE8caRknoME7t0yxAu2JdRfb_E1krbtghW0iH6HO_5-yYPXWLZPlPMEPTRbX5J3TXbN0cOZGNNwrwoKDz2XHok6tlGtCg5Gr2SOSJrH_zPt-Y0UdLk4CWrD8eqD_MwyzKSJZTtFJvFuj1uiipaoPE4ZLWWx6zU19olKP1iOAQfSdN2IVbzsxQzeNVA0ejHccy73cydcVSfxcdH_TkJod5JYvpr49Xew4R7rwQa3cKPThK4vhrH8fkrb0gTMCTOP2GVwP2AUMJOy-R5rGjoMphTVW2X9gJBndimb0XNEL5sZI-TsnvclSHkU9rIoEk9dKZk_aJ_Essg1jXVKE6sq45UExLZNuiyB1dSbRWeF7kPRIrV'
DROPBOX_FOLDER = '/faces'
TEMP_LOCAL_FOLDER = 'temp_faces'

dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def download_images_from_dropbox(local_folder):
    os.makedirs(local_folder, exist_ok=True)
    entries = dbx.files_list_folder(DROPBOX_FOLDER).entries
    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            local_path = os.path.join(local_folder, entry.name)
            dbx.files_download_to_file(local_path, entry.path_lower)

# === UART Setup ===
uart = serial.Serial(port='COM15', baudrate=9600, timeout=1)
time.sleep(2)

attendance_path = os.path.join(os.path.dirname(__file__), "Attendance.csv")
if os.path.exists(attendance_path):
    os.remove(attendance_path)
else:
    pd.DataFrame().to_csv(attendance_path)

def markAttendance(name):
    if not os.path.exists(attendance_path):
        with open(attendance_path, 'w') as f:
            f.write('Name,Time\n')
    with open(attendance_path, 'r+') as f:
        names = [line.split(',')[0] for line in f.readlines()]
        if name not in names:
            now = datetime.now().strftime('%H:%M:%S')
            f.write(f'\n{name},{now}')

def findEncodings(images):
    encodings = []
    for img in images:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(rgb)
        if enc:
            encodings.append(enc[0])
    return encodings

def load_user_config(name):
    config_path = os.path.join(TEMP_LOCAL_FOLDER, f"{name}.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

# === Step 1: Download and Load Face Images ===
download_images_from_dropbox(TEMP_LOCAL_FOLDER)

images, classNames = [], []
for cl in os.listdir(TEMP_LOCAL_FOLDER):
    if cl.lower().endswith(('.png', '.jpg', '.jpeg')):
        img = cv2.imread(os.path.join(TEMP_LOCAL_FOLDER, cl))
        if img is not None:
            images.append(img)
            classNames.append(os.path.splitext(cl)[0].upper())

encodeListKnown = findEncodings(images)

fan_on = False
fan_end_time = 0
current_person = None

# === Webcam Start ===
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb_small)
    encodes = face_recognition.face_encodings(rgb_small, boxes)

    now = time.time()

    for encodeFace, box in zip(encodes, boxes):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        distances = face_recognition.face_distance(encodeListKnown, encodeFace)
        idx = np.argmin(distances)

        y1, x2, y2, x1 = [v * 4 for v in box]

        if matches[idx]:
            name = classNames[idx]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0,255,0), cv2.FILLED)
            cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
            markAttendance(name)

            config = load_user_config(name)
            if config:
                duration = int(config.get("duration", 30))
                fan = config.get("fan", False)
                lights = config.get("lights", False)
                second_led = config.get("second_led", False)

                if fan:
                    uart.write(b'F1\n')
                if lights:
                    uart.write(b'L1\n')
                if second_led:
                    uart.write(b'S1\n')

                fan_on = True
                fan_end_time = now + duration
                current_person = {
                    "name": name,
                    "fan": fan,
                    "lights": lights,
                    "second_led": second_led
                }

                print(f"{name}: Fan={fan}, Lights={lights}, Second LED={second_led}, Duration={duration}s")

        else:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0,0,255), cv2.FILLED)
            cv2.putText(img, "INTRUDER", (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)

    # === Turn OFF if timer expired ===
    if fan_on and now > fan_end_time:
        if current_person:
            if current_person["fan"]:
                uart.write(b'F0\n')
            if current_person["lights"]:
                uart.write(b'L0\n')
            if current_person["second_led"]:
                uart.write(b'S0\n')
            print(f"{current_person['name']}: All devices OFF")
        fan_on = False
        current_person = None

    cv2.imshow('Webcam', img)
    if cv2.waitKey(5) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
