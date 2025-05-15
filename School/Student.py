import base64
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
import cv2
import os
import datetime
import time
import pandas as pd
import numpy as np
from threading import Thread
from PIL import Image
import tensorflow as tf
import csv
from datetime import datetime, timedelta
from screeninfo import get_monitors  # Import screeninfo to get screen dimensions
from django.shortcuts import render
import ctypes  # Add this import
import cv2
import tensorflow as tf
import numpy as np
import csv
from datetime import datetime, timedelta
from screeninfo import get_monitors

def extract_features(image, width, height):
    feature = np.array(image)
    feature = feature.reshape(1, width, height, 1)
    return feature / 255.0

# Function to draw a rounded rectangle
def draw_rounded_rectangle(img, pt1, pt2, color, thickness, radius=20):
    x1, y1 = pt1
    x2, y2 = pt2
    cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
    cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
    cv2.line(img, (x2 - radius, y1), (x2, y1 + radius), color, thickness)
    cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
    cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
    cv2.line(img, (x1, y2 - radius), (x1, y2), color, thickness)
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
    cv2.line(img, (x2 - radius, y2), (x2, y2 - radius), color, thickness)
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)


def preprocess_face(image, width, height):
    image = cv2.equalizeHist(image)  # Enhance contrast
    image = cv2.GaussianBlur(image, (5, 5), 0)  # Reduce noise
    image = cv2.resize(image, (width, height))  # Resize
    return extract_features(image, width, height)


def Test(request):

    model = tf.keras.models.load_model("SudentPretrainedModel.h5")

    haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(haar_file)

    # Initialize the webcam
    webcam = cv2.VideoCapture(0)

    # Get screen dimensions
    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    # Set the webcam resolution to screen size
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

    # Create a fullscreen window
    cv2.namedWindow("Attendance", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Attendance", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Bring the OpenCV window to the front
    hwnd = ctypes.windll.user32.FindWindowW(None, "Attendance")
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
        ctypes.windll.user32.SetForegroundWindow(hwnd)

    # Define labels
    labels = {0:'20200798', 1:'20190662', 2:'20190675', 3:'20190711', 4:'20190724', 5:'20190729', 6:'2020001', 7:'2020002', 8:'20200798'}

    # Set up timing for the attendance session
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=0.10)
    data = [['ID', 'Time']]

    Width, Height = 48, 48  # Image size
    y_true = []
    y_pred = []

    while True:
        ret, im = webcam.read()
        if not ret:
            break

        overlay = im.copy()
        output = im.copy()

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        # Improved face detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50),
                                            flags=cv2.CASCADE_SCALE_IMAGE)

        current_time = datetime.now().strftime('%H:%M:%S')
        remaining_time = (end_time - datetime.now()).total_seconds()

        if remaining_time <= 0:
            break

        # Display countdown timer
        countdown_text = "Login recognition"
        cv2.rectangle(overlay, (10, 10), (300, 60), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, im, 0.6, 0, im)
        cv2.putText(im, countdown_text, (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        try:
            for (p, q, r, s) in faces:
                # Expand bounding box slightly
                margin = 10
                x, y, w, h = max(0, p - margin), max(0, q - margin), r + 2 * margin, s + 2 * margin
                face_image = gray[y:y + h, x:x + w]

                draw_rounded_rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3, radius=15)

                # Preprocess the face before passing to the model
                img = preprocess_face(face_image, Width, Height)
                pred = model.predict(img)
                prediction_label = labels[pred.argmax()]
                prediction_confidence = np.max(pred)  # Highest confidence score
                ID = prediction_label

                label_bg = overlay.copy()
                cv2.rectangle(label_bg, (x - 10, y - 30), (x + 150, y), (50, 50, 50), -1)
                cv2.addWeighted(label_bg, 0.6, im, 0.4, 0, im)

                y_pred.append(prediction_label)
                cv2.putText(im, prediction_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2,
                            cv2.LINE_AA)

                if prediction_label != 'Unknown':
                    data.append([prediction_label, current_time])

            cv2.imshow("Attendance", im)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        except cv2.error:
            pass

    webcam.release()
    cv2.destroyAllWindows()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [ID])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
        SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.course_image
        FROM StudentCourses 
        INNER JOIN Courses ON Courses.course_id = StudentCourses.course_id
        INNER JOIN StudentInformation ON  StudentCourses.Student_ID = StudentInformation.Student_ID
        WHERE  StudentInformation.Student_ID = %s 
                """, [ID])        
        CourseRecord = cursor.fetchall()

        Course_data = []
        if CourseRecord:
            for Record in CourseRecord:
                course_id = Record[0]
                course_name = Record[1]
                course_level = Record[2]
                course_image = Record[3]


                Course_data.append({
                    'CourseID': course_id,
                    'CourseName': course_name,
                    'Courselevel': course_level,
                    'CourseImage': base64.b64encode(course_image).decode('utf-8'),
        
                })



    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS UnreadAnnouncements
            FROM AnnouncementReadStatus
            WHERE Student_ID = %s AND IsRead = 0;
        """, [ID]) 

        AnnouncementNum = cursor.fetchall()

        Student_data = []
        if StudentRecord:
            for Record in StudentRecord:
                Student_Name = Record[0]
                Student_Image = Record[1]
                Student_ID = Record[2]


            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'StudentID': Student_ID,
    
            })

        context = {
            'StudentRecord': Student_data,
            'CourseRecord': Course_data,
            'AnnouncementNum': AnnouncementNum
        }

    return render(request, 'Pages/Student.html', context)   



def Recognize_Face(request):
    ID = 0

    if request.method == 'POST':

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("Student/TrainingImageLabelStudent"+os.sep+"Trainner.yml")
        harcascadePath = "haarcascade_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath)
        df = pd.read_csv("Student/StudentDetails"+os.sep+"StudentDetails.csv")
        font = cv2.FONT_HERSHEY_SIMPLEX
        col_names = ['Id', 'Name', 'Date', 'Time']
        attendance = pd.DataFrame(columns=col_names)

        # start realtime video capture
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cam.set(3, 640) 
        cam.set(4, 480) 
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)
        i = 0
        k = 0

        while True:
            ret, im = cam.read()
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5,
                    minSize = (int(minW), int(minH)),flags = cv2.CASCADE_SCALE_IMAGE)

            for(x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x+w, y+h), (10, 159, 255), 2)
                Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                if conf < 100:
                    aa = df.loc[df['Id'] == Id]['Name'].values
                    confstr = "  {0}%".format(round(100 - conf))
                    tt = str(Id)
                else:
                    Id = '  Unknown  '
                    tt = str(Id)
                    confstr = "  {0}%".format(round(100 - conf))

                if (100-conf) > 67:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    aa = str(aa)[2:-2]
                    attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]
                    ID = Id



                tt = str(tt)[2:-2]
                if(100-conf) > 70:
                    i += 1
                    k += 1
                    cv2.putText(im, str("Recognized"), (x+5,y-5), font, 1, (0, 255, 0),2)
                    if k == 1:
                        captured_image_path = os.path.join("Student", "CapturedImages", f"captured_image_{k}.jpg")
                        cv2.imwrite(captured_image_path, im)
                    
                    print("The tt = ", tt)


                elif (100-conf) > 67:
                    tt =  str(confstr)
                    cv2.putText(im, str(tt), (x + 5, y + h - 5), font,1, (0, 255, 255) , 1)

                elif (100-conf) > 50:
                    tt =  str(confstr)
                    cv2.putText(im, str(tt), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)

                else:
                    cv2.putText(im, 'Unknown', (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)


            attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
            cv2.imshow('LogIn', im)

            if (cv2.waitKey(1) == ord('q') or i == 20):
                break

    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    fileName = "Student/Attendance"+os.sep+"Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName, index=False)
    cam.release()
    cv2.destroyAllWindows()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [ID])
        Record = cursor.fetchall()
        cursor.execute("""
        SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.image_url, Courses.link_url
        FROM StudentCourses 
        INNER JOIN Courses ON Courses.course_id = StudentCourses.course_id
		INNER JOIN StudentInformation ON  StudentCourses.Student_ID = StudentInformation.Student_ID
        WHERE  StudentInformation.Student_ID = %s 
                """, [ID])
        Record2 = cursor.fetchall()

    if Record and Record2:
        context = {
            'Record1': Record,
            'Record2': Record2
        }
        return render(request, 'Pages/Student.html', context)
    else:
        return HttpResponse("Null record")


def Request(request):
    return render(request, 'Pages/StudentLogIn.html')




def LogInAccount(request):
        
    ID = request.POST.get('id')  
    password =  request.POST.get('password')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s AND Passwordd = %s
        """, [ID, password])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
        SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.course_image
        FROM StudentCourses 
        INNER JOIN Courses ON Courses.course_id = StudentCourses.course_id
        INNER JOIN StudentInformation ON  StudentCourses.Student_ID = StudentInformation.Student_ID
        WHERE  StudentInformation.Student_ID = %s 
                """, [ID])        
        CourseRecord = cursor.fetchall()

        Course_data = []
        if CourseRecord:
            for Record in CourseRecord:
                course_id = Record[0]
                course_name = Record[1]
                course_level = Record[2]
                course_image = Record[3]


                Course_data.append({
                    'CourseID': course_id,
                    'CourseName': course_name,
                    'Courselevel': course_level,
                    'CourseImage': base64.b64encode(course_image).decode('utf-8'),
        
                })



    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS UnreadAnnouncements
            FROM AnnouncementReadStatus
            WHERE Student_ID = %s AND IsRead = 0;
        """, [ID]) 

        AnnouncementNum = cursor.fetchall()

        Student_data = []
        if StudentRecord:
            for Record in StudentRecord:
                Student_Name = Record[0]
                Student_Image = Record[1]
                Student_ID = Record[2]


            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'StudentID': Student_ID,
    
            })

        context = {
            'StudentRecord': Student_data,
            'CourseRecord': Course_data,
            'AnnouncementNum': AnnouncementNum
        }

    return render(request, 'Pages/Student.html', context)


