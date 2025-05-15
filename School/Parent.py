import base64
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
import cv2
import csv
import os
import datetime
import time
import pandas as pd
import numpy as np
from threading import Thread
from PIL import Image

             
    


def Request(request):
    return render(request, 'Pages/ParentLogIn.html')


        


def LogInAccount(request):
        
    ID = request.POST.get('id')  
    password =  request.POST.get('password')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Parent_Name, Parent_Id, Parent_Image
            FROM ParentInformation
            WHERE Parent_Id = %s AND Passwordd = %s
        """, [ID, password])
        ParentRecord = cursor.fetchall()


    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_ID FROM ParentInformation
            WHERE Parent_Id = %s 
        """, [ID])
        Result = cursor.fetchall()
        StudentID = Result[0][0]


    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [StudentID])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
        SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.course_image
        FROM StudentCourses 
        INNER JOIN Courses ON Courses.course_id = StudentCourses.course_id
        INNER JOIN StudentInformation ON  StudentCourses.Student_ID = StudentInformation.Student_ID
        WHERE  StudentInformation.Student_ID = %s 
                """, [StudentID])        
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
        """, [StudentID]) 

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

        Parent_data = []
        if ParentRecord:
            for Record in ParentRecord:
                Parent_Name = Record[0]
                Parent_ID = Record[1]
                Parent_Image = Record[2]


            Parent_data.append({
                'ParentName': Parent_Name,
                'ParentImage': base64.b64encode(Parent_Image).decode('utf-8'),
                'ParentID': Parent_ID,
    
            })


        context = {
            'StudentRecord': Student_data,
            'CourseRecord': Course_data,
            'AnnouncementNum': AnnouncementNum,
            'ParentRecord': Parent_data
        }

    return render(request, 'Pages/Parent.html', context)