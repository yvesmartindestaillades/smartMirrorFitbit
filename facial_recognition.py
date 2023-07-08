import uuid
import face_recognition
import matplotlib.pyplot as plt
import time
import os
import numpy as np
import cv2
from my_queue import Queue
from firebase import firebase
import base64
from server import Server
from datetime import datetime

CAMERA_IDX = int(os.environ['CAMERA_IDX'])
PATH_TO_FACES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faces')

class Camera:

    def __init__(self, camera_idx = 0) -> None:
        self.camera = cv2.VideoCapture(camera_idx)

    def read(self):
        self.ret, self.frame = self.camera.read()

    def release(self):
        self.camera.release()

    def get_frame(self):
        return self.frame

    def get_ret(self):
        return self.ret


class FacialRecognition:

    """A class that runs the facial recognition algorithm. The identification of the user is stored in a queue, so that when a user is identified, the user is not switched immediately.
    Instead, the user must be identified for a certain amount of time before the user is switched.

    The queue is updated every refresh_frequency seconds. The returned user is the user that is the most frequent in the queue. The queue has a time length of buffer_time_for_switching_users.

    If the image is assigned to a user, the picture is saved in the user's profile.

    Hyperparameters:
    refresh_frequency: the frequency at which the camera is refreshed
    buffer_time_for_switching_users: the last x seconds of the queue is used to determine the user
    config: a dictionary containing the root of the profiles and the camera index

    Example:
    >>> facial = FacialRecognition()
    >>> facial.run()
    >>> print(facial.current_user)
    None
    >>> facial.run('test')
    >>> facial.run('test')
    >>> print(facial.current_user)
    barack_obama
    """

    refresh_frequency = 1. #Hz
    buffer_time_for_switching_users = 2 #secs

    def __init__(self) -> None:

        # Load the path
        self.path = PATH_TO_FACES

        # Load the faces from the profiles
        self.known_faces_encodings = self.load_facials_from_profiles()

        # Start the camera
        self.camera = Camera(CAMERA_IDX)

        # Initialize the queue of users
        self.users_queue = Queue(int(self.buffer_time_for_switching_users*self.refresh_frequency))

        # This is the current user state
        self.current_user = None
        self.user_switched = False


    def run(self):
        """Runs the facial recognition algorithm."""

        print('Running the facial recognition algorithm...')
        # Read the camera
        self.camera.read()

        # Identify the user
        identified_user = self.identify_user()

        # Add the user to the queue
        self.users_queue.enqueue(identified_user)

        # Assign the user if the user is different from the current user
        self.current_user, self.user_switched = self.new_user()

        # If no user is identified, return None
        if self.current_user is None:
            return None

        # Save the image when you're sure that the user is the current user
        if self.current_user == identified_user:
            # encode image to base64    
            _, buffer = cv2.imencode('.jpg', self.camera.frame)
            image_as_text = base64.b64encode(buffer).decode('utf-8')
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            firebase.push({date:image_as_text}, 'facials', user = self.current_user)


    def identify_user(self):
        """Returns the name of the user who is the closest match to the facial.

        If found multiple users, the user with the highest score is returned. If there's a tie, the user that is the most frequent in the queue is returned.

        If no user is found, None is returned.

        Example:
        >>> facial = FacialRecognition()
        >>> # This is the facial of barack_obama, yeah I'm cheating here
        >>> facial.camera.frame = plt.imread(Path('test_data').get_profile_facials_folder('barack_obama') + '/img0.jpg')
        >>> facial.identify_user()
        'barack_obama'
        """

        # Get the encoding of the unknown image
        unknown_image_encoding = face_recognition.face_encodings(self.camera.frame)
        if len(unknown_image_encoding) == 0:
            return None
        unknown_image_encoding = unknown_image_encoding[0]

        # Get the scores of the users
        users_scores = {}
        for user, known_image_encodings in self.known_faces_encodings.items():
            matches = face_recognition.compare_faces(known_image_encodings, unknown_image_encoding)
            users_scores[user] = sum(matches)

        # Return the user with the highest score
        if max(users_scores.values()) == 0:
            return None

        if list(users_scores.values()).count(max(users_scores.values())) == 1:
            return max(users_scores, key=users_scores.get)

        # If there's a tie, return the user that is the most frequent in the queue
        if list(users_scores.values()).count(max(users_scores.values())) > 1:
            max_users = [user for user, score in users_scores.items() if score == max(users_scores.values()) and user in self.users_queue.queue]

            # if no user is found in the queue, return the user with the highest score
            if len(max_users) == 0:
                return max(users_scores, key=users_scores.get)

            # return the user that is the most frequent in the queue
            max_users.sort(key=lambda user: self.users_queue.count(user), reverse=True)
            return max_users[0]


    def new_user(self):
        """Returns the user that is the most frequent in the queue.
        If the user is different from the current user, the user is switched.

        Example:
        >>> facial = FacialRecognition()
        >>> facial.camera.frame = plt.imread(Path('test_data').get_profile_facials_folder('barack_obama') + '/img0.jpg')
        >>> facial.users_queue.enqueue(facial.identify_user())
        >>> facial.new_user()
        ('barack_obama', True)
        >>> facial.camera.frame = plt.imread(Path('test_data').get_profile_facials_folder('barack_obama') + '/img0.jpg')
        >>> facial.users_queue.enqueue(facial.identify_user())
        >>> facial.new_user()
        ('barack_obama', False)
        """

        new_user = self.users_queue.most_frequent()
        if new_user != self.current_user:
            self.current_user = new_user
            return new_user, True
        else:
            return new_user, False


    def load_facials_from_profiles(self):
        """Returns a dictionary of all facials as numpy arrays, loaded with face_recognition

        Example:
        >>> facial = FacialRecognition()
        >>> facial.load_facials_from_profiles().keys()
        dict_keys(['barack_obama', 'yves_martin'])
        >>> len(facial.load_facials_from_profiles()['barack_obama'])
        3
        """

        facials = {}

        for user in os.listdir(PATH_TO_FACES):
            facials[user] = []
            for facial_path in os.listdir(p:=os.path.join(PATH_TO_FACES, user)):
                if '.DS_Store' in facial_path:
                    continue
                # load the images for each profile
                loaded_img = face_recognition.load_image_file(os.path.join(p, facial_path))
                # append the facial encodings to the facials dictionary
                facials[user].append(face_recognition.face_encodings(loaded_img)[0])

        return facials