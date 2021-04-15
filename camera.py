import cv2
import os
import glob
import numpy as np
import face_recognition

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor = 0.6


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.known_face_encodings = []
        self.known_face_names = []
        self.allName = []
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'known_people/')
        list_of_files = [f for f in glob.glob(path + '*.jpg')]
        number_files = len(list_of_files)
        names = list_of_files.copy()
        for i in range(number_files):
            globals()['image_{}'.format(i)] = face_recognition.load_image_file(
                list_of_files[i])
            globals()['image_encoding_{}'.format(i)] = face_recognition.face_encodings(
                globals()['image_{}'.format(i)])[0]
            self.known_face_encodings.append(globals()['image_encoding_{}'.format(i)])

            names[i] = names[i].replace("known_people/", "")
            self.known_face_names.append(names[i])

        self.process_this_frame = True

    def __del__(self):
        self.video.release()

    def get_frame(self):
        face_locations = []
        face_encodings = []
        face_names = []
        ret, frame = self.video.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        if self.process_this_frame and len(self.allName) < 20:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                self.allName.append(name.split('/')[-1].split('.')[0])
                face_names.append(name.split('/')[-1].split('.')[0])
        if len(self.allName) == 20:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)
            face_names.append("attendance marked")

        self.process_this_frame = not self.process_this_frame

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), self.allName
