import cv2
from cv2 import imread  # openCV
import numpy as np  # for numpy arrays
import sqlite3
import dlib
import os  # for creating folders


# ///////////////////////////////////////
# Global Variable
# ///////////////////////////////////////

personGroupId = "test1"

key = "hidden"

BASE_URL = "https://hidden.api.cognitive.microsoft.com/face/v1.0"


#
import sys

nameeee = sys.argv[1]
rolllll = sys.argv[2]

#


# ///////////////////////////////////////
# Adding Name and RRn and take down the images of student
# ///////////////////////////////////////


cap = cv2.VideoCapture(-1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
# cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

detector = dlib.get_frontal_face_detector()


def insertOrUpdate(Id, Name, roll):  # this function is for database
    connect = sqlite3.connect("Face-DataBase")  # connecting to the database
    cmd = (
        "SELECT * FROM Students WHERE ID = " + Id
    )  # selecting the row of an id into consideration
    cursor = connect.execute(cmd)
    isRecordExist = False

    for row in cursor:  # checking wheather the id exist or not
        isRecordExist = True
    # print(isRecordExist)

    if isRecordExist == True:
        print("record is updated")  # updating name and roll no
        connect.execute("UPDATE Students SET Name = ? WHERE ID = ?", (Name, Id))
        connect.execute("UPDATE Students SET Roll = ? WHERE ID = ?", (roll, Id))
    else:
        print("record is entered")
        params = (Id, Name, roll)  # insering a new student data
        connect.execute("INSERT INTO Students(ID, Name, Roll) VALUES(?, ?, ?)", params)
    connect.commit()  # commiting into the database
    connect.close()  # closing the connection


name = nameeee
roll = rolllll
# name = input("Enter student's name : ")
# roll = input("Enter student's Roll Number : ")
Id = roll[-2:]
insertOrUpdate(Id, name, roll)  # calling the sqlite3 database


folderName = "user" + Id  # creating the person or user folder
folderPath = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "dataset/" + folderName
)
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

sampleNum = 0


while True:
    ret, img = cap.read()  # reading the camera input
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Converting to GrayScale
    dets = detector(img, 1)
    for i, d in enumerate(dets):  # loop will run for each face detected
        sampleNum += 1
        cv2.imwrite(
            folderPath + "/User." + Id + "." + str(sampleNum) + ".jpg",
            img[d.top() : d.bottom(), d.left() : d.right()],
            [int(cv2.IMWRITE_JPEG_QUALITY), 1000000],
        )  # Saving the faces
        size = img.shape
        print(size)
        cv2.rectangle(
            img, (d.left(), d.top()), (d.right(), d.bottom()), (0, 255, 0), 2
        )  # Forming the rectangle
        cv2.waitKey(200)  # waiting time of 200 milisecond
    cv2.imshow("frame", img)  # showing the video input from camera on window
    cv2.waitKey(1)
    if sampleNum >= 20:  # will take 20 faces
        break

cap.release()  # turning the webcam off
cv2.destroyAllWindows()  # Closing all the opened windows


# ///////////////////////////////////////
# Adding the student face into databse
# ///////////////////////////////////////

import sys
import cognitive_face as CF
import sqlite3
import os, time
import urllib
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


CF.Key.set(key)

CF.BaseUrl.set(BASE_URL)

print("personGroupId = %s" % (personGroupId))


res = CF.person.create(personGroupId, "dataset/" + folderName)
# print("res = {}".format(res))
print(res)
extractId = folderName[-2:]
connect = sqlite3.connect("Face-DataBase")
cmd = "SELECT * FROM Students WHERE ID = " + extractId
cursor = connect.execute(cmd)
isRecordExist = 0
for row in cursor:  # checking wheather the id exist or not
    isRecordExist = 1
if isRecordExist == 1:  # updating name and roll no
    connect.execute(
        "UPDATE Students SET personID = ? WHERE ID = ?",
        (res["personId"], extractId),
    )
connect.commit()  # commiting into the database
connect.close()
print("Person ID successfully added to the database")


def get_person_id():
    person_id = ""
    extractId = folderName[-2:]
    # extractId = folderName
    connect = sqlite3.connect("Face-DataBase")
    c = connect.cursor()
    cmd = "SELECT * FROM Students WHERE ID = " + extractId
    c.execute(cmd)
    row = c.fetchone()
    person_id = row[3]
    connect.close()
    return person_id


currentDir = os.path.dirname(os.path.abspath(__file__))
imageFolder = os.path.join(currentDir, "dataset/" + folderName)
person_id = get_person_id()
for filename in os.listdir(imageFolder):
    if filename.endswith(".jpg"):
        print(filename)
        imgurl = urllib.request.pathname2url(os.path.join(imageFolder, filename))
        # imgurl = imgurl[3:]
        print("imageurl = {}".format(imgurl))

        res = CF.face.detect(imgurl)
        if len(res) != 1:
            print("No face detected in image")
        else:
            res = CF.person.add_face(imgurl, personGroupId, person_id)
            print(res)
        time.sleep(6)


# ///////////////////////////////////////
# Training the dataset with azure
# ///////////////////////////////////////
import cognitive_face as CF
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


CF.Key.set(key)

CF.BaseUrl.set(BASE_URL)


res = CF.person_group.train(personGroupId)
print(res)
