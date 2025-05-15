import base64
import mimetypes
import os
from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection, transaction
import json



def index(request):
    return render(request, 'Pages/Main.html')

def index2(request, Student_Id):

    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT CoursesList.course_id, CoursesList.course_name, CoursesList.course_level
        FROM CoursesList INNER JOIN StudentCourses ON CoursesList.course_id = StudentCourses.course_id
        WHERE StudentCourses.Student_ID = %s 
        """, [Student_Id])
        records = cursor.fetchall()

        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_Level, Class, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [Student_Id])
        StudentRecord = cursor.fetchall()

        Student_data = []
        if StudentRecord:
            for Record in StudentRecord:
                Student_Name = Record[0]
                Student_Image = Record[1]
                Student_Level = Record[2]
                Class = Record[3]
                Student_ID = Record[4]


            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'Student_Level': Student_Level,
                'Class': Class,
                'StudentID': Student_ID
            })

        context = {
            'Record': records,
            'StudentRecord': Student_data
        }
        
        return render(request, 'Pages/Attendance_History.html', context)


def index3(request, Teacher_Id, Course_Id, CourseName):
    context = {
        'Teacher_Id': Teacher_Id,
        'Course_Id': Course_Id,
        'CourseName': CourseName
    }
    return render(request, 'Pages/temp.html', context)



def index4(request):
    return render(request, 'Pages/Attendance_History.html')

def add_course_Page(request):

    return render(request, 'Pages/add_course.html')

def AddannouncementsPage(request):
    return render(request, 'Pages/add_announcement.html')


def AddTeacherCoursPage(request):
    return render(request, 'Pages/AddTeacherCourse.html')


def SaveFinalGrade(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received data:", data)

            student_id = data.get('StudentID')
            studentGrades = data.get('Grades')
            assignment = data.get('Assignment')
            quiz = data.get('Quiz')
            midterm = data.get('MidTerm')
            finalExam = data.get('Final')
            participation = data.get('Participation')
            attendance = data.get('Attendance')
            CourseID = data.get('CourseID')
            Credit = ""
            StudentStatus = ""

            # Assign credit and status based on grades
            if studentGrades >= 90:
                Credit = "A"
                StudentStatus = "Passed"
            elif studentGrades >= 80:
                Credit = "B"
                StudentStatus = "Passed"       
            elif studentGrades >= 70:
                Credit = "C"
                StudentStatus = "Passed" 
            elif studentGrades >= 60:
                Credit = "D"
                StudentStatus = "Passed" 
            else:
                Credit = "F"
                StudentStatus = "Failed" 

            print("Student ID:", student_id, "Total mark:", studentGrades)

            # Use a single cursor for all database operations
            with connection.cursor() as cursor:
                # Check if the student grade already exists
                cursor.execute("""
                    SELECT Student_ID
                    FROM FinalGrade
                    WHERE Student_ID = %s 
                """, [student_id])
                StudentGrade = cursor.fetchone()

                if StudentGrade:
                    # Update the existing record
                    cursor.execute("""
                        UPDATE FinalGrade   
                        SET TotalQuizMark = %s,
                            TotalAssignment = %s,
                            MidTerm = %s,
                            Final = %s,
                            ClassParticipation = %s,
                            ClassAttendance = %s,
                            Total = %s,
                            course_id = %s,
                            Credit = %s,
                            StudentStatus = %s
                        WHERE Student_ID = %s
                    """, [quiz, assignment, midterm, finalExam, participation, attendance, studentGrades, CourseID, Credit, StudentStatus, student_id])
                else: 
                    # Insert a new record
                    cursor.execute("""
                        INSERT INTO FinalGrade 
                        (TotalQuizMark, TotalAssignment, MidTerm, Final, ClassParticipation, ClassAttendance, Total, Student_ID, course_id, Credit, StudentStatus)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [quiz, assignment, midterm, finalExam, participation, attendance, studentGrades, student_id, CourseID, Credit, StudentStatus])

            # Return a success response
            return JsonResponse({"message": "Grades confirmed successfully!"}, status=200)

        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




def GenerateGrades(request, CourseID):
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT Student_Name, Student_Image, Student_ID, Class
                FROM StudentInformation
                ORDER BY Class, Student_ID ASC;
                    """)
        StudentRecord = cursor.fetchall()

    Student_data = []
    if StudentRecord:
        for Record in StudentRecord:
            Student_Name = Record[0]
            Student_Image = Record[1]
            Student_ID = Record[2]
            Class = Record[3]
            with connection.cursor() as cursor:
                cursor.execute("""
                            SELECT 
                                SUM(MarksObtained) AS TotalMarksObtained
                            FROM 
                                HomeWorkGrades
                            WHERE 
                                Student_ID = %s

                            """, [Student_ID])
                AssignmentGrade = cursor.fetchall()

                cursor.execute("""
                            SELECT 
                                SUM(MarksObtained) AS TotalMarksObtained
                            FROM 
                                QuizGrades
                            WHERE 
                                StudentID = %s
                            """, [Student_ID])
                QuizGrade = cursor.fetchall()


                cursor.execute("""
                        SELECT 
                            SUM(AttendanceList.Mark) AS TotalMark
                        FROM 
                            AttendanceList 
                        WHERE
                            AttendanceList.course_id = 1201 AND AttendanceList.Student_ID = %s
                            """, [Student_ID])
                AttendanceGrade = cursor.fetchall()

            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'StudentID': Student_ID,
                'Class': Class,
                'TotalAssignmentGrade': AssignmentGrade[0][0],
                'TotalQuizGrade': QuizGrade[0][0],
                'TotalAttendanceGrade': AttendanceGrade[0][0],
                'CourseID': CourseID

            })
    
    context = {
            'StudentRecord': Student_data,
        }
    return render(request, 'Pages/GenerateGrades.html', context)

def AddAnnouncementsCoursePage(request, Teacher_Id, Course_Id):
    context = {
    'TeacherID': Teacher_Id,
    'CourseID': Course_Id
    }

    return render(request, 'Pages/AddCourseAnnouncement.html', context)


def AddStudentCourse(request):
    return render(request, 'Pages/AddStudentCourse.html')

def AddStudentCourse2(request):
    return render(request, 'Pages/AddStudentCourse.html', {
        'messages': messages.get_messages(request),  
    })

def ParentLogIn(request):
    return render(request, 'Pages/ParentLogIn.html')

def TeacherLogIn(request):
    return render(request, 'Pages/TeacherLogIn.html')


def StudentLogIn(request):
    return render(request, 'Pages/StudentLogIn.html')

def StudentSchedulePage(request, Student_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [Student_ID])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
        SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.course_image
        FROM StudentCourses 
        INNER JOIN Courses ON Courses.course_id = StudentCourses.course_id
        INNER JOIN StudentInformation ON  StudentCourses.Student_ID = StudentInformation.Student_ID
        WHERE  StudentInformation.Student_ID = %s 
                """, [Student_ID])        
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
        """, [Student_ID]) 

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

    return render(request, 'Pages/StudentSchedule.html', context)


def CoursePageStudent(request, Student_ID, course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PublisherImage, PublisherName, DateOfPublish,
            DescriptionText, MaterialPath, MaterialType 
            FROM CourseContents
            WHERE course_id = %s
            ORDER BY MaterialID DESC
        """, [course_id])
        materials = cursor.fetchall()

        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_Id
            FROM StudentInformation
            WHERE Student_ID = %s
        """, [Student_ID])
        StudentRecords = cursor.fetchall()

        cursor.execute("""
            SELECT course_id, course_name
            FROM Courses
            WHERE course_id = %s
        """, [course_id])
        CourseRecord = cursor.fetchall()

    Student_data = []
    if StudentRecords:
        for StudentRecord in StudentRecords:
            Student_Name = StudentRecord[0]
            Student_Image = StudentRecord[1]
            Student_Id = StudentRecord[2]

            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'StudentId': Student_Id,
            })



    material_data = []

    if materials:
        for material in materials:
            publisher_image = material[0]
            publisher_name = material[1]
            publish_date = material[2]
            description = material[3]
            material_path = material[4]
            materialType = material[5]

    

            material_data.append({
                'publisher_image': base64.b64encode(publisher_image).decode('utf-8') ,
                'publisher': publisher_name,
                'publish_date': publish_date,
                'description': description,
                'file_url': base64.b64encode(material_path).decode('utf-8'),
                'material_type': materialType,
                'Course_Id': course_id
            })

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS UnreadAnnouncements
            FROM CourseAnnouncementReadStatus
            WHERE Student_ID = %s AND IsRead = 0;
        """, [Student_ID]) 

        AnnouncementNum = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS UnreadAnnouncements
            FROM QuizTakeStatus
            WHERE Student_ID = %s AND IsTaken = 0 AND course_id = %s;
        """, [Student_ID, course_id]) 

        QuizNum = cursor.fetchall()

    context = {
        'materials': material_data,
        'StudentRecord': Student_data,
        'CourseRecord': CourseRecord,
        'AnnouncementNum': AnnouncementNum,
        'QuizNum': QuizNum

    }

    return render(request, 'Pages/CoursePageStudent.html', context)


def CoursePageTeacher(request):
    return render(request, 'Pages/CoursePage.html')


def FinalGrade(request, StudentID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [StudentID])
        Record = cursor.fetchall()



    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TotalAssignment, TotalQuizMark, MidTerm, Final, ClassParticipation, ClassAttendance,
                    Credit, StudentStatus, course_id, Total
            FROM FinalGrade
            WHERE Student_ID = %s 
        """, [StudentID])
        FinalGradeRecord = cursor.fetchall()


        Student_data = []
        if Record:
            for Record in Record:
                Student_Name = Record[0]
                Student_Image = Record[1]
                Student_ID = Record[2]


            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'StudentID': Student_ID,
    
            })



        FinalGrade_data = []
        if Record:
            for Record in FinalGradeRecord:
                TotalAssignment = Record[0]
                TotalQuizMark = Record[1]
                MidTerm = Record[2]
                Final = Record[3]
                ClassParticipation = Record[4]
                ClassAttendance = Record[5]
                Credit = Record[6]
                StudentStatus = Record[7]
                course_id = Record[8]
                Total = Record[9]
                with connection.cursor() as cursor:
                    cursor.execute("""
                            SELECT course_name FROM Courses 
                            WHERE course_id = %s

                    """, [course_id])
                    CourseNmae = cursor.fetchall()

                FinalGrade_data.append({
                    'CourseNmae': CourseNmae[0][0],
                    'TotalAssignment': TotalAssignment,
                    'TotalQuizMark': TotalQuizMark,
                    'MidTerm': MidTerm,
                    'Final': Final,
                    'ClassParticipation': ClassParticipation,
                    'ClassAttendance': ClassAttendance,
                    'Credit': Credit,
                    'StudentStatus': StudentStatus,
                    'Total': Total
                })

        context = {
            'StudentRecord': Student_data,
            'FinalGrades': FinalGrade_data
        }

    return render(request, 'Pages/FinalGrades.html', context)


def TeacherSchedule(request, teacher_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Teacher_Name, Teacher_Image, Teacher_Id
            FROM TeacherInformation
            WHERE Teacher_Id = %s 
        """, [teacher_id])
        TeacherRecord = cursor.fetchall()

        Teacher_data = []
        if TeacherRecord:
            for Record in TeacherRecord:
                Teacher_Name = Record[0]
                Teacher_Image = Record[1]
                Teacher_ID = Record[2]


            Teacher_data.append({
                'TeacherName': Teacher_Name,
                'TeacherImage': base64.b64encode(Teacher_Image).decode('utf-8'),
                'TeacherID': Teacher_ID,
    
            })

        context = {
            'TeacherRecord': Teacher_data,
        }

    return render(request, 'Pages/TeacherSchedule.html', context)





def AddTeacherPage(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 Teacher_Id FROM TeacherInformation ORDER BY Teacher_Id DESC")
        last_record = cursor.fetchone() 
        last_Teacher_Id = last_record[0] if last_record else 0  

    new_Teacher_Id = last_Teacher_Id + 1  

    context = {
        'LastRecord': new_Teacher_Id
    }

    return render(request, 'Pages/AddTeacher.html', context)


def AddCoursePage(request):
    return render(request, 'Pages/add_course.html')

def AddStudentForm(request):
    return render(request, 'Pages/AddStudent.html')

def AddTeacherForm(request):
    return render(request, 'Pages/AddTeacher.html')

def AddParentForm(request):
    return render(request, 'Pages/AddParent.html')

def StudentInformation(request, Student_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID, Nationality, Student_Level, Enrolmenet_Date, Student_DateOfBirth
            FROM StudentInformation
            WHERE Student_ID = %s
        """, [Student_ID])
        StudentRecord = cursor.fetchall()

        Student_data = []
        if StudentRecord:
            for Record in StudentRecord:
                Student_Name = Record[0]
                Student_Image = Record[1]
                Student_ID = Record[2]
                Nationality = Record[3]
                Student_Level = Record[4]
                Enrolment_Date = Record[5]
                StudentDateOfBirth = Record[6]



            Student_data.append({
                'StudentName': Student_Name,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'StudentID': Student_ID,
                'Nationality': Nationality,
                'Student_Level': Student_Level,
                'Enrolment_Date': Enrolment_Date,
                'StudentDateOfBirth': StudentDateOfBirth
    
            })
        
        context = {
            'StudentRecord': Student_data,
        }

    return render(request, 'Pages/StudentInformation.html', context)




def TeacherInformation(request, Teacher_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Teacher_Name, Teacher_Image, Teacher_Id, Nationality, Teacher_specialist, EnrolmentDate, DateOfBirth
            FROM TeacherInformation
            WHERE Teacher_Id = %s
        """, [Teacher_ID])
        TeacherRecord = cursor.fetchall()

        Teacher_data = []
        if TeacherRecord:
            for Record in TeacherRecord:
                Teacher_Name = Record[0]
                Teacher_Image = Record[1]
                Teacher_ID = Record[2]
                Nationality = Record[3]
                Specialist = Record[4]
                Enrolment_Date = Record[5]
                DateOfBirth = Record[6]



            Teacher_data.append({
                'TeacherName': Teacher_Name,
                'TeacherImage': base64.b64encode(Teacher_Image).decode('utf-8'),
                'TeacherID': Teacher_ID,
                'Nationality': Nationality,
                'Specialist': Specialist,
                'Enrolment_Date': Enrolment_Date,
                'DateOfBirth': DateOfBirth
    
            })
        
        context = {
            'TeacherRecord': Teacher_data,
        }

    return render(request, 'Pages/TeacherInformation.html', context)



def GenerateQuizPage(request, teacher_id, course_id):
    context = {
        'TecherID': teacher_id,
        'CourseID': course_id
    }
    return render(request, 'Pages/GenerateQuiz.html', context)


def GenerateReportPage(request):
    return render(request, 'Pages/GenerateReport2.html')


def UploadMaterialPage(request, Teacher_Id, course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Teacher_Name, Teacher_Id
            FROM TeacherInformation
            WHERE Teacher_Id = %s 
        """, [Teacher_Id])
        
        TeacherRecord = cursor.fetchall()

        cursor.execute("""
                SELECT course_id
                FROM Courses
                WHERE course_id = %s
            """, [course_id])
        CourseRecord = cursor.fetchall()


    if TeacherRecord:
        context = {
            'Record1': TeacherRecord,
            'Record2': CourseRecord
        }
        return render(request, 'Pages/UploadMaterials.html', context)
    else:
        return HttpResponse("Null record")
        




def UpdateMaterial(request, Teacher_Id, course_id, content_id):
    if request.method == 'POST':
        print("In the UodateMaterialFunction")
        description = request.POST.get('description')
        media_type = request.POST.get('media-type')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE CourseContents
                SET DescriptionText = %s, MaterialType = %s
                WHERE MaterialID = %s
            """, [description, media_type, content_id])

        return JsonResponse({"message": "Material updated successfully!"}, status=200)


  




def UpdateMaterialPage(request, Teacher_Id, course_id, content_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Teacher_Name, Teacher_Id
            FROM TeacherInformation
            WHERE Teacher_Id = %s 
        """, [Teacher_Id])
        
        TeacherRecord = cursor.fetchall()

        cursor.execute("""
                SELECT course_id
                FROM Courses
                WHERE course_id = %s
            """, [course_id])

        CourseRecord = cursor.fetchall()

        cursor.execute("""
        SELECT CourseContents.MaterialID, CourseContents.DescriptionText,  CourseContents.MaterialType
        FROM CourseContents 
        INNER JOIN Courses ON Courses.course_id = CourseContents.course_id
        WHERE  CourseContents.MaterialID = %s
            """, [content_id])
        CourseContent = cursor.fetchall()


    if TeacherRecord:
        context = {
            'Record1': TeacherRecord,
            'Record2': CourseRecord,
            'CourseContent': CourseContent
        }
        
    return render(request, 'Pages/UpdateMaterial.html', context)
 



def CourseContent(request):
    return render(request, 'Pages/CoursePage.html')

def Upload(request):
    return render(request, 'Pages/add_course.html')

def upload_assignment_Page(request, Teacher_Id, Course_Id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Teacher_Name, Teacher_Image, Teacher_Id
            FROM TeacherInformation
            WHERE Teacher_ID = %s 
        """, [Teacher_Id])
        TeacherRecord = cursor.fetchall()

        cursor.execute("""
            SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.course_image
            FROM TeacherCourses 
            INNER JOIN Courses ON Courses.course_id = TeacherCourses.course_id
            INNER JOIN TeacherInformation ON  TeacherCourses.Teacher_Id = TeacherInformation.Teacher_Id
            WHERE  TeacherInformation.Teacher_Id = %s 
                    """, [Teacher_Id]) 
            
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


    Teacher_data = []
    if TeacherRecord:
        for Record in TeacherRecord:
            Teacher_Name = Record[0]
            Teacher_Image = Record[1]
            TeacherID = Record[2]


        Teacher_data.append({
            'TeacherName': Teacher_Name,
            'TeacherImage': base64.b64encode(Teacher_Image).decode('utf-8'),
            'TeacherID': TeacherID
        })
        
        context = {
            'TeacherID': Teacher_Id,
            'CourseID': Course_Id,
            'TeacherRecords': Teacher_data,
            'CourseRecord': Course_data
        }

        return render(request, 'Pages/UploadAssignment.html', context)





def CoursePage(request,  course_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Courses WHERE course_id = %s", [course_id])
        profiles = cursor.fetchall()

    if profiles:
        print(course_id)
        return render(request, 'Pages/CoursePage.html', {'profiles': profiles})
    else:
        return HttpResponse("Null record")




def insert_data(request):
    if request.method == 'POST':
        # Extract data from the form submission
        fname = request.POST.get('Fname')
        id = request.POST.get('id')

        # Execute raw SQL query to insert data into the Info table
        query = "INSERT INTO Info (Fname, id) VALUES (%s, %s)"
        params = [fname, id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)

        return render(request, 'index.html')
    else:
        return render(request, 'Main.html')

def display_data(request):
     if request.method == 'GET':
        id = request.GET.get('id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT Fname, id FROM Info WHERE id = %s", [id])
            row = cursor.fetchone()
            if row:
                record = {'name': row[0], 'id': row[1]}
            else:
                record = None
        return render(request, 'Pages/index.html', {'record': record})
    

def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_id = request.POST.get('course_id')
        course_level = request.POST.get('course_level')
        course_image = request.FILES['course_image']
        image_binary = None
        
        if isinstance(course_image, InMemoryUploadedFile):
            image_binary = course_image.read()  

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Courses (course_name, course_id, course_level, course_image)
                VALUES (%s, %s, %s, %s)
            """, [course_name, course_id, course_level,  image_binary])
            
            Temp =  course_name + "-" + str(course_id) 
            cursor.execute("""
                INSERT INTO CoursesList (course_id, course_name, course_level)
                VALUES (%s, %s, %s)
            """, [course_id, Temp,  course_level])
        
        
        return JsonResponse({"message": "Student added successfully"})
        
    return render(request, 'Pages/Main.html')






def course_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Courses")
        courses = cursor.fetchall()

    if courses:
        return render(request, 'Pages/course_list.html', {'courses': courses})
    else:
        return HttpResponse("Null record")
    



def get_records(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM CourseRecord")
            Records = cursor.fetchall()
        
        if Records:
            Records_data = [{'Avatar': msg[0], 'PublisherName': msg[1], 'Date': msg[2], 'PdfPath': msg[3]} for msg in Records]
            return JsonResponse({'messages': Records_data})
        else:
            return JsonResponse({'messages': []})

    



def get_records(request, course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT CourseContents.PublisherImage, CourseContents.PublisherName, CourseContents.DateOfPublish,
            CourseContents.DescriptionText, CourseContents.MaterialPath, CourseContents.MaterialIcon
            FROM CourseContents
            INNER JOIN Courses ON CourseContents.course_id = Courses.course_id
            WHERE Courses.course_id = %s
            ORDER BY CourseContents.MaterialID
        """, [course_id])
 #("SELECT PublisherImage, PublisherName, DateOfPublish, DescriptionText, MaterialPath, MaterialIcon  FROM CourseContents")      
        course_contents = cursor.fetchall()

    if course_contents:
        records_data = []
        for record in course_contents:
            file_path = record[4]
            if file_path.endswith('.pdf'):
                content_type = 'pdf'
            elif file_path.endswith('.mp4'):
                content_type = 'video'
            else:
                content_type = 'unknown'  
            records_data.append({
                'avatar': record[0],
                'publisher_name': record[1],
                'date': record[2],
                'description': record[3],
                'Icon': record[5],
                'file_path': file_path,
                'content_type': content_type
            })

        return render(request, 'Pages/Try.html', {'records': records_data})
    else:
        return HttpResponse("Null record")





def get_course_contents(request,course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT CourseContents.PublisherImage, CourseContents.PublisherName, CourseContents.DateOfPublish,
            CourseContents.DescriptionText, CourseContents.MaterialPath, CourseContents.MaterialIcon
            FROM CourseContents
            INNER JOIN Courses ON CourseContents.course_id = Courses.course_id
            WHERE Courses.course_id = %s
            ORDER BY CourseContents.MaterialID
        """, [course_id])
       
        course_contents = cursor.fetchall()

    if course_contents:
        print(course_id)
        return render(request, 'Pages/Try.html', {'course_contents': course_contents})
    else:
        return HttpResponse("Null record")



def add_student_page(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 Student_ID FROM StudentInformation ORDER BY Student_ID DESC")
        last_record = cursor.fetchone() 
        last_student_id = last_record[0] if last_record else 0  

    new_student_id = last_student_id + 1  

    context = {
        'LastRecord': new_student_id
    }

    return render(request, 'Pages/AddStudent.html', context)


def add_parent_page(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 Parent_Id FROM ParentInformation ORDER BY Parent_Id DESC")
        last_record = cursor.fetchone() 
        last_parent_id = last_record[0] if last_record else 0  

    if not last_record :
        ParentID = 2000
    else:
        ParentID = last_parent_id + 1


    context = {
        'LastRecord': ParentID
    }

    return render(request, 'Pages/AddParent.html', context)



def add_student(request):
    if request.method == 'POST':
        student_name = request.POST['student_name']
        student_id = request.POST['student_id']
        student_age = request.POST['student_age']
        student_nationality = request.POST['student_nationality']
        student_level = request.POST['student_level']
        student_class = request.POST['student_class']
        student_gender = request.POST['student_gender']
        date_of_birth = request.POST['dateOfBirth']
        student_class = student_class + "-" + student_level



        current_date = datetime.now()
        enrollment_date = current_date.strftime("%b %d")

        student_image = request.FILES['student_image']
        image_binary = None
        
        if isinstance(student_image, InMemoryUploadedFile):
            image_binary = student_image.read()  

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO StudentInformation (
                    Student_Name, 
                    Student_ID, 
                    Student_Age, 
                    Nationality, 
                    Student_Level, 
                    Student_Gender, 
                    Student_Image, 
                    Student_DateOfBirth, 
                    Enrolmenet_Date, 
                    Passwordd,
                    Class
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                student_name,
                student_id,
                student_age,
                student_nationality,
                student_level,
                student_gender,
                image_binary,
                date_of_birth,
                enrollment_date,  
                "123",
                student_class 
            ])

    return JsonResponse({"message": "Student added successfully"})






def add_parent(request):
    if request.method == 'POST':
        parent_name = request.POST['parent_name']
        parent_id = request.POST['parent_id']
        student_id = request.POST['student_id']
        parent_image = request.FILES['parent_image']
        image_binary = None
        
        if isinstance(parent_image, InMemoryUploadedFile):
            image_binary = parent_image.read() 

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ParentInformation (
                    Parent_Name, 
                    Parent_Id, 
                    Student_ID, 
                    Parent_Image, 
                    Passwordd 
                ) VALUES (%s, %s, %s, %s, %s)
            """, [
                parent_name,
                parent_id,
                student_id,
                image_binary,
                "123"
            ])

    return JsonResponse({"message": "Parent record added successfully"})













def AddTeacher(request):
    if request.method == 'POST':
        teacher_name = request.POST['teacher_name']
        teacher_id = request.POST['teacher_id']
        teacher_age = request.POST['teacher_age']
        teacher_specialist = request.POST['teacher_specialist']
        teacher_nationality = request.POST['teacher_nationality']
        teacher_gender = request.POST['teacher_gender']
        date_of_birth = request.POST['dateOfBirth']

        current_date = datetime.now()
        enrollment_date = current_date.strftime("%b %d")

        teacher_image = request.FILES['teacher_image']
        image_binary = None
        
        if isinstance(teacher_image, InMemoryUploadedFile):
            image_binary = teacher_image.read()  

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TeacherInformation (
                    Teacher_Name, 
                    Teacher_Id, 
                    Teacher_Age,
                    Teacher_specialist, 
                    Nationality, 
                    Teacher_Gender, 
                    Teacher_Image, 
                    DateOfBirth, 
                    EnrolmentDate, 
                    Passwordd
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                teacher_name,
                teacher_id,
                teacher_age,
                teacher_specialist,
                teacher_nationality,
                teacher_gender,
                image_binary,
                date_of_birth,
                enrollment_date,  
                "123"  
            ])

        return JsonResponse({"message": "Teacher added successfully"})
    

def redirectAddStudent(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 Student_ID FROM StudentInformation ORDER BY Student_ID DESC")
        last_record = cursor.fetchone() 
        last_student_id = last_record[0] if last_record else 0  

    new_student_id = last_student_id + 1  

    context = {
        'LastRecord': new_student_id
    }

    return render(request, 'Pages/AddStudent.html', context)






def UploadMaterial(request, Teacher_Id, course_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        media_type = request.POST.get('media-type')
        media_file = request.FILES.get('media-file')

        current_date = datetime.now()
        day = current_date.day
        month = current_date.strftime("%b")
        date = f"{day} {month}"

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Teacher_Name, Teacher_Image
                FROM TeacherInformation
                WHERE Teacher_ID = %s
            """, [Teacher_Id])
            Techer = cursor.fetchall()

        for Record in Techer:
            TeacherName = Record[0]
            TeacherImage = Record[1]

        material_path = media_file.read()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO CourseContents(PublisherImage, PublisherName, DateOfPublish, DescriptionText, MaterialPath, course_id, Teacher_Id, MaterialType) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [TeacherImage, TeacherName, date, description, material_path, course_id, Teacher_Id, media_type])

        return JsonResponse({"status": "success", "message": "Material uploaded successfully!"})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def DeleteMaterial(request, MaterialID):   
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM CourseContents
                WHERE MaterialID = %s
            """, [MaterialID])
        return JsonResponse({"success": True, "message": "Material deleted successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

    




    



def upload_material_view(request):
    return render(request, 'Pages/CoursePage2.html')


def Get_Course_Contents(request):
    with connection.cursor() as cursor:
        course_id = 1
        cursor.execute("""
            SELECT CourseContents.PublisherImage, CourseContents.PublisherName, CourseContents.DateOfPublish,
            CourseContents.DescriptionText, CourseContents.MaterialPath
            FROM CourseContents
            INNER JOIN Courses ON CourseContents.course_id = Courses.course_id
            WHERE Courses.course_id = %s
            ORDER BY CourseContents.MaterialID
        """, [course_id])
       
        course_contents = cursor.fetchall()

    if course_contents:
        formatted_contents = []
        for content in course_contents:
            publisher_image, publisher_name, date_of_publish, description_text, material_path = content
            
            file_type, _ = mimetypes.guess_type(material_path)
            if file_type:
                if file_type.startswith('image'):
                    content_type = 'image'
                elif file_type.startswith('video'):
                    content_type = 'video'
                elif file_type.startswith('audio'):
                    content_type = 'audio'
                elif file_type == 'application/pdf':
                    content_type = 'pdf'
                else:
                    content_type = 'unknown'
            else:
                content_type = 'unknown'
            
            formatted_contents.append({
                'publisher_image': publisher_image,
                'publisher_name': publisher_name,
                'date_of_publish': date_of_publish,
                'description_text': description_text,
                'material_path': material_path,
                'content_type': content_type
            })

        return render(request, 'Pages/CoursePage.html', {'course_contents': formatted_contents})
    else:
        return HttpResponse("Null record")
    
 #("SELECT PublisherImage, PublisherName, DateOfPublish, DescriptionText, MaterialPath, MaterialIcon  FROM CourseContents")      




def get_file_type(file_data):

    if file_data.startswith(b'%PDF'):
        return 'pdf'
    elif file_data.startswith(b'\xFF\xD8'):
        return 'image'  
    elif file_data.startswith(b'\x89PNG'):
        return 'image'  
    elif file_data.startswith(b'\x00\x00\x00\x18ftypmp4'):
        return 'video'  
    elif file_data.startswith(b'OggS'):
        return 'video'  
    return 'unknown'



def materials_view(request, Teacher_Id, course_id):
    print( "ID: ", Teacher_Id, "Course_Id: ", course_id)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT PublisherImage, PublisherName, DateOfPublish,
                DescriptionText, MaterialPath, MaterialType, MaterialID
            FROM CourseContents
            WHERE course_id = %s
            ORDER BY MaterialID DESC
        """, [course_id])
        materials = cursor.fetchall()

        cursor.execute("""
            SELECT Teacher_Name, Teacher_Image, Teacher_Id
            FROM TeacherInformation
            WHERE Teacher_Id = %s
        """, [Teacher_Id])
        TeacherRecords = cursor.fetchall()

        Teacher_data = []
        if TeacherRecords:
            for Record in TeacherRecords:
                Teacher_Name = Record[0]
                Teacher_Image = Record[1]
                Teacher_Id = Record[2]


            Teacher_data.append({
                'TeacherName': Teacher_Name,
                'TeacherImage': base64.b64encode(Teacher_Image).decode('utf-8'),
                'TeacherID': Teacher_Id,
    
            })


        cursor.execute("""
            SELECT course_id, course_name
            FROM Courses
            WHERE course_id = %s
        """, [course_id])
        CourseRecord = cursor.fetchall()

    material_data = []

    if materials:
        for material in materials:
            publisher_image = material[0]
            publisher_name = material[1]
            publish_date = material[2]
            description = material[3]
            material_path = material[4]
            materialType = material[5]
            materialID = material[6]



            material_data.append({
                'publisher': publisher_name,
                'publisher_image': base64.b64encode(publisher_image).decode('utf-8'),
                'publish_date': publish_date,
                'description': description,
                'file_url': base64.b64encode(material_path).decode('utf-8'),
                'material_type': materialType,
                'Course_Id': course_id,
                'MaterialID': materialID
            })

            print("The description: ", description)
        

    context = {
        'materials': material_data,
        'TeacherRecords': Teacher_data,
        'CourseRecord': CourseRecord,
        'TeacherID': Teacher_Id
    }

    return render(request, 'Pages/CoursePage2.html', context)




def ViewStudentsCourse(request, Course_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT StudentInformation.Student_Image ,StudentInformation.Student_Name,
            StudentInformation.Student_ID,
            StudentInformation.Student_Level, StudentInformation.Class FROM
            StudentInformation
            INNER JOIN StudentCourses ON StudentInformation.Student_ID = StudentCourses.Student_ID
            INNER JOIN CoursesList ON StudentCourses.course_id = StudentCourses.course_id
            WHERE StudentCourses.course_id = %s
        """, [Course_ID])
        StudentRecords = cursor.fetchall()

        Student_data = []
        if StudentRecords:
            for Record in StudentRecords:
                StudentImage = Record[0]
                StudentName = Record[1]
                StudentID = Record[2]
                StudentLevel = Record[3]
                StudentClass = Record[4]


                Student_data.append({
                    'StudentImage': base64.b64encode(StudentImage).decode('utf-8'),
                    'StudentName': StudentName,
                    'StudentID': StudentID,
                    'StudentLevel': StudentLevel,
                    'StudentClass': StudentClass,
                })

        Context = {
        'StudentRecords': Student_data,

        }

    return render(request, 'Pages/StudentInformationCourse.html', Context)

    





def StudentDashboard(request, Student_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [Student_ID])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
        SELECT Courses.course_id, Courses.course_name,  Courses.course_level, Courses.course_image
        FROM StudentCourses 
        INNER JOIN Courses ON Courses.course_id = StudentCourses.course_id
        INNER JOIN StudentInformation ON  StudentCourses.Student_ID = StudentInformation.Student_ID
        WHERE  StudentInformation.Student_ID = %s 
                """, [Student_ID])        
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
        """, [Student_ID]) 

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



    

def attendance_history(request, Name, Student_Id):
    print("In the Attendance Function: ", Name, Student_Id)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT LectureNumber, CourseName, 
                Attendance_Date, 
                AttendanceTime, AttendanceStatus 
            FROM AttendanceList
            WHERE CourseName = %s AND Student_ID = %s
            ORDER BY AttendanceID ASC
        """, [Name, Student_Id])  
        AttendanceRecord = cursor.fetchall()



    attendance_data = [
        {'Student_ID': record[0], 'CourseName': record[1], 'Attendance_Date': record[2], 'AttendanceTime':
          record[3], 'AttendanceStatus': record[4]}  
        for record in AttendanceRecord
    ]

    return JsonResponse(attendance_data, safe=False)


from django.db import connection

def AssignStudentCourse(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_id = request.POST.get('student_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM StudentCourses 
                WHERE Student_ID = %s AND course_id = %s
            """, [student_id, course_id])
            exists = cursor.fetchone()[0]  

            if exists > 0:
                print("Duplicate entry: Record already exists")
                messages.error(request, 'Duplicate entry: Record already exists')
                return redirect('/AddStudentCourse3/?success=true')

            else:
                cursor.execute("""
                    INSERT INTO StudentCourses (Student_ID, course_id)
                    VALUES (%s, %s)
                """, [student_id, course_id])
                
                if cursor.rowcount == 1:
                    print("Record inserted successfully")
                    messages.success(request, 'Record inserted successfully')
                    return redirect('/AddStudentCourse3/?success=true')

                else:
                    print("Insertion failed")
                    messages.success(request, 'Failed to insert the record')
                    return redirect('/AddStudentCourse3/?success=true')




def fetchcoursesLists(request):
    print("In the CourseList Function: ")
    with connection.cursor() as cursor:

        cursor.execute("SELECT *FROM CoursesList")
        rows = cursor.fetchall()
        courses = [{'id': row[0], 'name': row[1], 'level': row[2]} for row in rows] 

    return JsonResponse(courses, safe=False)



from django.http import JsonResponse

def AssignStudentCourse2(request):
    if request.method == 'POST'  and  request.headers.get('x-requested-with') == 'XMLHttpRequest':
        course_id = request.POST.get('course_id')
        student_id = request.POST.get('student_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM StudentCourses 
                WHERE Student_ID = %s AND course_id = %s
            """, [student_id, course_id])
            exists = cursor.fetchone()[0]

            if exists > 0:
                return JsonResponse({'status': 'error', 'message': 'Duplicate entry: Record already exists'})
            else:
                cursor.execute("""
                    INSERT INTO StudentCourses (Student_ID, course_id)
                    VALUES (%s, %s)
                """, [student_id, course_id])

                if cursor.rowcount == 1:
                    return JsonResponse({'status': 'success', 'message': 'Record inserted successfully'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Failed to insert the record'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def AssignTeacherCourse(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("In the function AssignTeacherCourse")
        course_id = request.POST.get('course_id')
        teacher_id = request.POST.get('teacher_id')

        if not course_id or not teacher_id:
            return JsonResponse({'status': 'error', 'message': 'Both Course ID and Teacher ID are required.'})
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM TeacherCourses 
                WHERE Teacher_Id = %s AND Course_Id = %s
            """, [teacher_id, course_id])
            exists = cursor.fetchone()[0]

            if exists > 0:
                print("Duplicate entry: Record already exists")
                return JsonResponse({'status': 'error', 'message': 'Duplicate entry: Record already exists'})
            else:
                cursor.execute("""
                    INSERT INTO TeacherCourses (Teacher_Id, Course_Id)
                    VALUES (%s, %s)
                """, [teacher_id, course_id])

                if cursor.rowcount == 1:
                    print("Record inserted successfully")
                    return JsonResponse({'status': 'success', 'message': 'Record inserted successfully'})
                else:
                    print("Insertion failed")
                    return JsonResponse({'status': 'error', 'message': 'Failed to insert the record'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})









def AddStudentCourse3(request):
    return render(request, 'Pages/AddStudentCourse.html', {
        'messages': messages.get_messages(request),  
    })


def upload_media(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        
        uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        file_name = uploaded_file.name
        file_path = os.path.join(uploads_dir, file_name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        file_type = None
        if file_name.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
            file_type = 'image'
        elif file_name.lower().endswith(('mp4', 'avi', 'mov')):
            file_type = 'video'
        elif file_name.lower().endswith('pdf'):
            file_type = 'pdf'
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO MediaFiles (file_path, file_type, uploaded_at)
                VALUES (%s, %s, GETDATE())
            """, ['/media/uploads/' + file_name, file_type])

        return redirect('media_list')
    
    return render(request, 'upload_media.html')


def media_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, file_path, file_type FROM MediaFiles")
        media_records = cursor.fetchall()

    return render(request, 'Pages/media_list.html', {'media_records': media_records})






def Addannouncements(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            publisher = request.POST.get('publisher')
            content = request.POST.get('content')
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT Admin_image FROM AdminAccount WHERE Admin_ID = 1")
                Record = cursor.fetchone()
            
            admin_image = Record[0] if Record and Record[0] is not None else None

            pdf_file = None
            video_file = None

            if 'pdf_file' in request.FILES:
                pdf_file_upload = request.FILES['pdf_file']
                fs = FileSystemStorage()
                pdf_filename = fs.save(pdf_file_upload.name, pdf_file_upload)
                pdf_path = fs.path(pdf_filename)
                with open(pdf_path, 'rb') as pdf:
                    pdf_file = pdf.read()

            if 'video_file' in request.FILES:
                video_file_upload = request.FILES['video_file']
                video_filename = fs.save(video_file_upload.name, video_file_upload)
                video_path = fs.path(video_filename)
                with open(video_path, 'rb') as video:
                    video_file = video.read()

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Announcement (publisher, content, publisher_image, pdf_file, video_file, Admin_ID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [publisher, content, admin_image, pdf_file, video_file, 1])
                cursor.execute(" SELECT TOP 1 id  FROM Announcement ORDER BY id DESC ")
                result = cursor.fetchone()
                announcement_id = result[0]

            with connection.cursor() as cursor:
                cursor.execute("SELECT Teacher_Id FROM TeacherInformation")
                teacher_ids = [row[0] for row in cursor.fetchall()]

            with connection.cursor() as cursor:
                cursor.execute("SELECT Student_ID FROM StudentInformation")
                student_ids = [row[0] for row in cursor.fetchall()]

            for teacher_id in teacher_ids:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO AnnouncementReadStatus (Teacher_Id, AnnouncementId, IsRead, ReadDate)
                        VALUES (%s, %s, 0, NULL)
                    """, [teacher_id, announcement_id])

            for student_id in student_ids:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO AnnouncementReadStatus (Student_ID, AnnouncementId, IsRead, ReadDate)
                        VALUES (%s, %s, 0, NULL)
                    """, [student_id, announcement_id])    
            
            return JsonResponse({'message': 'Announcement added successfully!'}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method or type.'}, status=400)




def AddAnnouncementsCourse(request, Teacher_Id, Course_Id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            print("In the function")
            content = request.POST.get('content')
            
            TeacherID = Teacher_Id
            with connection.cursor() as cursor:
                cursor.execute("""SELECT Teacher_Image, Teacher_Name FROM TeacherInformation WHERE Teacher_Id = %s
                """, [TeacherID])
                Record = cursor.fetchone()
            
            Teacher_image = Record[0] if Record and Record[0] is not None else None
            Teacher_Name = Record[1]

            pdf_file = None
            video_file = None

            if 'pdf_file' in request.FILES:
                pdf_file_upload = request.FILES['pdf_file']
                fs = FileSystemStorage()
                pdf_filename = fs.save(pdf_file_upload.name, pdf_file_upload)
                pdf_path = fs.path(pdf_filename)
                with open(pdf_path, 'rb') as pdf:
                    pdf_file = pdf.read()

            if 'video_file' in request.FILES:
                video_file_upload = request.FILES['video_file']
                video_filename = fs.save(video_file_upload.name, video_file_upload)
                video_path = fs.path(video_filename)
                with open(video_path, 'rb') as video:
                    video_file = video.read()

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO CourseAnnouncement (publisher, content, publisher_image, pdf_file, video_file, Teacher_Id, course_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [Teacher_Name, content, Teacher_image, pdf_file, video_file, TeacherID, Course_Id])
                cursor.execute(" SELECT TOP 1 id  FROM CourseAnnouncement ORDER BY id DESC ")
                result = cursor.fetchone()
                announcement_id = result[0]


            with connection.cursor() as cursor:
                cursor.execute("SELECT Student_ID FROM StudentInformation")
                student_ids = [row[0] for row in cursor.fetchall()]


            for student_id in student_ids:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO CourseAnnouncementReadStatus (Student_ID, AnnouncementId, IsRead, ReadDate, course_id)
                        VALUES (%s, %s, 0, NULL, %s)
                    """, [student_id, announcement_id, Course_Id])    
            
            return JsonResponse({'message': 'Announcement added successfully!'}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method or type.'}, status=400)


    

def course_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Courses")
        courses = cursor.fetchall()

    if courses:
        return render(request, 'Pages/course_list.html', {'courses': courses})
    else:
        return HttpResponse("Null record")





def announcement_list(request, ID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,  
                publisher, 
                content, 
                CONCAT(LEFT(DATENAME(MONTH, publish_date), 3), ' ', DAY(publish_date), ' ', YEAR(publish_date)) AS publish_date,
                publisher_image,
                pdf_file,  
                video_file 
            FROM 
                Announcement 
            ORDER BY 
                id DESC
        """)
        AnnouncementRecord = cursor.fetchall()
    

        with connection.cursor() as cursor:
            cursor.execute("""
                update AnnouncementReadStatus
                set IsRead = 1  where Teacher_Id = %s
            """, [ID])

            cursor.execute("""
                update AnnouncementReadStatus
                set IsRead = 1  where Student_ID = %s
            """, [ID])

    announcements = []
    pdf_data = None
    for record in AnnouncementRecord:
        image_data = record[4]
        pdf_data = None
        if record[5]:  
            pdf_data = base64.b64encode(record[5]).decode('utf-8')

        video_data = None
        if record[6]:  
            video_data = base64.b64encode(record[6]).decode('utf-8')

        announcements.append({
            'id': record[0],
            'publisher': record[1],
            'content': record[2],
            'publish_date': record[3],
            'publisher_image': base64.b64encode(image_data).decode('utf-8'),
            'pdf_file': pdf_data,
            'video_file': video_data
        })
    
    return render(request, 'Pages/announcement_list.html', {'announcements': announcements})




def announcement_list2(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id, 
                publisher, 
                content, 
                CONCAT(LEFT(DATENAME(MONTH, publish_date), 3), ' ', DAY(publish_date), ' ', YEAR(publish_date)) AS publish_date,
                publisher_image,
                pdf_file,  -- Fetch the PDF column here
                video_file -- Fetch the video column here
            FROM 
                Announcement 
            ORDER BY 
                id DESC
        """)
        AnnouncementRecord = cursor.fetchall()
    

    announcements = []
    for record in AnnouncementRecord:
        image_data = None
        if record[4]:  
            image_data = base64.b64encode(record[4]).decode('utf-8')

        pdf_data = None
        if record[5]:  
            pdf_data = base64.b64encode(record[5]).decode('utf-8')

        video_data = None
        if record[6]:  
            video_data = base64.b64encode(record[6]).decode('utf-8')

        announcements.append({
            'id': record[0],
            'publisher': record[1],
            'content': record[2],
            'publish_date': record[3],
            'publisher_image': image_data,
            'pdf_file': pdf_data,
            'video_file': video_data
        })
    
    return render(request, 'Pages/announcement_list.html', {'announcements': announcements})




def CourseAnnouncement(request, StudentID, Course_Id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id, 
                publisher, 
                content, 
                CONCAT(LEFT(DATENAME(MONTH, publish_date), 3), ' ', DAY(publish_date), ' ', YEAR(publish_date)) AS publish_date,
                publisher_image,
                pdf_file,  -- Fetch the PDF column here
                video_file -- Fetch the video column here
            FROM 
                CourseAnnouncement WHERE course_id = %s 
            ORDER BY 
                id DESC
        """, [Course_Id])
        AnnouncementRecord = cursor.fetchall()
    
    
        cursor.execute("""
                update CourseAnnouncementReadStatus
                set IsRead = 1  where Student_ID = %s AND course_id = %s
            """, [StudentID, Course_Id])

    announcements = []
    for record in AnnouncementRecord:
        image_data = None
        if record[4]:  
            image_data = base64.b64encode(record[4]).decode('utf-8')

        pdf_data = None
        if record[5]:  
            pdf_data = base64.b64encode(record[5]).decode('utf-8')

        video_data = None
        if record[6]:  
            video_data = base64.b64encode(record[6]).decode('utf-8')

        announcements.append({
            'id': record[0],
            'publisher': record[1],
            'content': record[2],
            'publish_date': record[3],
            'publisher_image': image_data,
            'pdf_file': pdf_data,
            'video_file': video_data
        })
    
    return render(request, 'Pages/CourseAnnouncement.html', {'announcements': announcements})


def upload_assignment(request, Teacher_Id, Course_Id):
    if request.method == 'POST':

        file = request.FILES['fileInput']  
        description = request.POST['description']  
        deadline_date = request.POST['deadlineDate']
        deadline_hour = request.POST['deadlineHour']
        deadline_minute = request.POST['deadlineMinute']
        TotalMark = request.POST['TotalMark']

        current_date = datetime.now()
        UploadDate = str(current_date.strftime("%b %d"))
        deadline = f"{deadline_date} {deadline_hour}:{deadline_minute}:00"
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Teacher_Image FROM TeacherInformation 
                WHERE Teacher_Id = %s
            """, [Teacher_Id])
            Record = cursor.fetchall()
            PublisherImage = Record[0][0] 
     

            cursor.execute("""
                SELECT COUNT(*) FROM Assignments 
                WHERE course_id = %s
            """, [Course_Id])
            Record = cursor.fetchall() 

            if Record:
                Num = Record[0][0] + 1
            else:
                Num = 1

        sql = """
            INSERT INTO Assignments (FileContent, DescriptionContent, DeadlineDate, AssignementNumber, course_id, Teacher_Id, PublisherImage, CreatedAt, TotalMark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, [file.read(), description, deadline, Num, Course_Id, Teacher_Id, PublisherImage, UploadDate, TotalMark])  # Execute the query
            return JsonResponse({'success': True, 'message': 'Assignment uploaded successfully!'})


def SaveHomeWorkGrade(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_id = data['student_id']
            question_id = data['question_id']
            grade = data['grade']

            Grade.objects.create(student_id=student_id, question_id=question_id, grade=grade)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})




def HomeWork(request, Course_ID, StudentID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                FileContent, 
                DescriptionContent, 
                DeadlineDate, 
                AssignementNumber,  
                PublisherImage, 
                CreatedAt, 
                AssignmentId,
                Teacher_Id,
                Flag       
            FROM Assignments
            WHERE course_id = %s           
        """, [Course_ID])
        assignments = cursor.fetchall()
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [StudentID])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
            SELECT course_name
            FROM CoursesList
            WHERE course_id = %s 
        """, [Course_ID])
        CourseRecord = cursor.fetchall()
        CourseName = CourseRecord[0][0]


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
                'CourseID': Course_ID
    
            })

    

    assignment_list = []
    now = datetime.now()

    for record in assignments:
        pdf_data = base64.b64encode(record[0]).decode('utf-8') if record[0] else None
        publisher_image = base64.b64encode(record[4]).decode('utf-8') if record[4] else None
        deadline_date = record[2]

        deadline_passed = deadline_date < now
        TeacherID = record[7]
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Teacher_Name
                FROM TeacherInformation
                WHERE Teacher_Id = %s 
            """, [TeacherID])
            TeacherRecord = cursor.fetchall()
            TeacherName = TeacherRecord[0][0]
            cursor.execute(""" SELECT Flag FROM SubmittedAssignmentFlag WHERE Student_ID = %s AND AssignmentId = %s
            """, [StudentID, record[6]])
            result = cursor.fetchone()
            if not result:
                Flag = 0
            else:
                Flag = result[0]

        assignment_list.append({
            'File_Content': pdf_data,
            'Description': record[1],
            'Deadline_Date': deadline_date,
            'Assignement_Number': record[3],
            'PublisherImage': publisher_image,
            'DateOfPublish': record[5],
            'Deadline_Passed': deadline_passed,
            'AssignmentID': record[6],
            'TeacherName': TeacherName,
            'CourseID': Course_ID,
            'StudentID': StudentID,
            'CourseName': CourseName,
            'Flag': Flag

        })

    context = {
        'assignments': assignment_list,
        'StudentRecord': Student_data
    }

    return render(request, 'Pages/HomeWork.html', context)





@csrf_exempt
def HomeworkDelivered(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        assignment_id = request.POST.get('assignment_id')
        file = request.FILES.get('file')
        BinaryFile = file.read()

        print("CourseID, StudentID: ", course_id, student_id)
        print("The assignment id = ", assignment_id)

        check_query = """
            SELECT COUNT(*) FROM HomeworkDelivered 
            WHERE course_id = %s AND Student_ID = %s AND AssignmentId = %s;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(check_query, [course_id, student_id, assignment_id])
            result = cursor.fetchone()
            record_exists = result[0] > 0  

        if record_exists:
            update_query = """
                UPDATE HomeworkDelivered
                SET FileContent = %s, DeliveredDate = GETDATE()
                WHERE course_id = %s AND Student_ID = %s AND AssignmentId = %s;
            """
            with connection.cursor() as cursor:
                cursor.execute(update_query, [BinaryFile, course_id, student_id, assignment_id])

            message = 'File updated successfully!'
        else:
            insert_query = """
                INSERT INTO HomeworkDelivered (course_id, Student_ID, AssignmentId, DeliveredDate, FileContent, AssignmentNumber, TotalMark, Flag)
                VALUES (%s, %s, %s, GETDATE(), %s, %s, %s, 0);
            """
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Assignments")
                result = cursor.fetchone()
                AssignmentNumber = result[0]
                cursor.execute("SELECT TotalMark FROM Assignments WHERE AssignmentId = %s ", [assignment_id])
                result = cursor.fetchone()
                TotalMark = result[0]
                cursor.execute(insert_query, [course_id, student_id, assignment_id, BinaryFile, AssignmentNumber, TotalMark])

                cursor.execute("""
                INSERT INTO SubmittedAssignmentFlag (AssignmentId, Flag, course_id, Student_ID)
                Values(%s, 1, %s, %s)
            """, [assignment_id, course_id, student_id])

            message = 'Homework submitted successfully!'

        return JsonResponse({
            'message': message,
            'assignment_id': assignment_id,
            'student_id': student_id,
            'file_name': file.name
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)



def Grade(request, Course_ID, StudentID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_Name, Student_Image, Student_ID
            FROM StudentInformation
            WHERE Student_ID = %s 
        """, [StudentID])
        StudentRecord = cursor.fetchall()

        cursor.execute("""
            SELECT course_id, course_name
            FROM CoursesList
            WHERE course_id = %s 
        """, [Course_ID])
        CourseRecord = cursor.fetchall()


        cursor.execute("""
            SELECT AssignmentNumber, MarksObtained, TotalMarks FROM HomeWorkGrades
            WHERE Student_ID = %s
            ORDER BY AssignmentNumber ASC;
        """, [StudentID])
        AssignmentGrades = cursor.fetchall()

        cursor.execute("""
            SELECT 
                QuizNumber, 
                SUM(MarksObtained) AS TotalMarksObtained, 
                SUM(TotalMarks) AS TotalPossibleMarks
            FROM 
                QuizGrades
            WHERE 
                StudentID = %s
            GROUP BY 
                StudentID, 
                QuizNumber
            ORDER BY 
                StudentID, 
                QuizNumber;

        """, [StudentID])
        QuizGrades = cursor.fetchall()

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
                    'CourseID': Course_ID
                })

        AssignmentGrades_data = []
        if AssignmentGrades:
            for Record in AssignmentGrades:
                AssignmentNumber = Record[0]
                MarksObtained = Record[1]
                TotalMarks = Record[2]

                AssignmentGrades_data.append({
                    'AssignmentNumber': AssignmentNumber,
                    'MarksObtained': MarksObtained,
                    'TotalMarks': TotalMarks,
                })

        QuizGrades_data = []
        if QuizGrades:
            for Record in QuizGrades:
                QuizNumber = Record[0]
                MarksObtained = Record[1]
                TotalMarks = Record[2]

                QuizGrades_data.append({
                    'QuizNumber': QuizNumber,
                    'MarksObtained': MarksObtained,
                    'TotalMarks': TotalMarks,
                })


    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS UnreadAnnouncements
            FROM CourseAnnouncementReadStatus
            WHERE Student_ID = %s AND IsRead = 0;
        """, [Student_ID]) 

        AnnouncementNum = cursor.fetchall()

    context = {
        'StudentRecord': Student_data,
        'CourseRecord': CourseRecord,
        'AnnouncementNum': AnnouncementNum,
        'AssignmentGradeRecord': AssignmentGrades_data,
        'QuizGradeRecord': QuizGrades_data

    }

    return render(request, 'Pages/Grade.html', context)



def CourseAttendanceHistory(request, Course_ID, StudentID):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Student_ID, CourseName, 
                Attendance_Date, 
                AttendanceTime, AttendanceStatus, LectureNumber 
            FROM AttendanceList
            WHERE course_id = %s AND Student_ID = %s
            ORDER BY AttendanceID ASC
        """, [Course_ID, StudentID])  
        AttendanceRecord = cursor.fetchall()


        Attendance_data = []
        if AttendanceRecord:
            for Record in AttendanceRecord:
                Student_ID = Record[0]
                CourseName = Record[1]
                Attendance_Date = Record[2]
                AttendanceTime = Record[3]
                AttendanceStatus = Record[4]
                LectureNumber = Record[5]


            Attendance_data.append({
                'Student_ID': Student_ID,
                'CourseName': CourseName,
                'Attendance_Date': Attendance_Date,
                'AttendanceTime': AttendanceTime,
                'AttendanceStatus': AttendanceStatus,
                'LectureNumber': LectureNumber
            })

    context = {
        'AttendanceRecord': Attendance_data,
    }

    return render(request, 'Pages/CourseAttendanceHistory.html', context)

    



def QuizInsertion(request):
    print("In the QuizInsertion function")

    if request.method == 'POST':
        print("Received a POST request")
        try:
            data = json.loads(request.body)
            print("Received data:", data)
            
            quiz_name = data.get('quiz_name')
            teacher_id = data.get('TeacherID')
            course_id = data.get('CourseID')
            questions_data = data.get('questions')

            if not quiz_name or not questions_data:
                print("Missing quiz name or questions")
                return JsonResponse({"error": "Quiz name and questions are required!"}, status=400)

            with connection.cursor() as cursor:
                print("Inserting into Quizzes table")
                cursor.execute("SELECT COUNT(*) FROM Quizzes")
                QuizNumber = cursor.fetchone()[0]
                if QuizNumber == 0:
                    QuizNumber = 1
                else:
                    QuizNumber += 1

                cursor.execute("""
                    INSERT INTO Quizzes (Teacher_Id, course_id, QuizName, QuizNumber)
                    VALUES (%s, %s, %s, %s)
                """, [teacher_id, course_id, quiz_name, QuizNumber])
                
                cursor.execute("SELECT TOP 1 QuizID FROM Quizzes ORDER BY QuizID DESC")
                quiz_id = cursor.fetchone()[0]
                print("Inserted Quiz with ID:", quiz_id)

            with transaction.atomic():
                print("Starting transaction for questions and options")
                for question in questions_data:
                    question_text = question.get('text')
                    question_type = question.get('type')
                    mark = question.get('mark')
                    options = question.get('options', [])
                    correct_option = question.get('correct_option', None)

                    print(f"Inserting question: {question_text}")
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO Questions (QuizID, QuestionText, QuestionType, Marks)
                            VALUES (%s, %s, %s, %s)
                        """, [quiz_id, question_text, question_type, mark])
                        
                        cursor.execute("SELECT TOP 1 QuestionID FROM Questions ORDER BY QuestionID DESC")
                        question_id = cursor.fetchone()[0]
                        print("Inserted Question with ID:", question_id)

                    if question_type == 'mcq' and options:
                        print(f"Inserting options for question ID {question_id}")
                        for i, option in enumerate(options):
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO Options (QuestionID, OptionText, IsCorrect)
                                    VALUES (%s, %s, %s)
                                """, [question_id, option.strip(), (1 if i == correct_option else 0)])


            with connection.cursor() as cursor:
                cursor.execute("SELECT Student_ID FROM StudentInformation")
                student_ids = [row[0] for row in cursor.fetchall()]

            for student_id in student_ids:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO QuizTakeStatus (Student_ID, QuizID, IsTaken, TakenDate, course_id)
                        VALUES (%s, %s, 0, NULL, %s)
                    """, [student_id, quiz_id, course_id])  
                    
            return JsonResponse({"message": "Quiz created successfully!"}, status=200)

        except Exception as e:
            print("Error occurred:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)




def take_quiz(request, StudentID, CourseID):
    Flag = 0
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 QuizID FROM Quizzes WHERE course_id = %s ORDER BY QuizID DESC", [CourseID])
        Record = cursor.fetchone()
        if Record:
            quiz_id = Record[0]
        else:
            quiz_id = None

        cursor.execute("SELECT TOP 1 Flag FROM StudentAnswers WHERE QuizID = %s AND StudentID = %s", [quiz_id, StudentID])
        Record = cursor.fetchone()
        if Record:
            Flag = Record[0]
        else:
            pass

        print("The flag in take Quiz is: ", Flag)



        cursor.execute("SELECT QuizName FROM Quizzes WHERE QuizID = %s", [quiz_id])
        quiz = cursor.fetchone()

        
        cursor.execute("""
            SELECT QuestionID, QuestionText, QuestionType, Marks 
            FROM Questions 
            WHERE QuizID = %s
        """, [quiz_id])
        questions = cursor.fetchall()

        cursor.execute("""
                update QuizTakeStatus
                set IsTaken = 1  where Student_ID = %s
            """, [StudentID])
        

        question_data = []
        for question in questions:
            question_id, text, q_type, marks = question
            cursor.execute("""
                SELECT OptionID, OptionText, IsCorrect 
                FROM Options 
                WHERE QuestionID = %s
            """, [question_id])
            options = cursor.fetchall()
            question_data.append({
                'id': question_id,
                'text': text,
                'type': q_type,
                'marks': marks,
                'options': options
            })

    if quiz:
        context = {
            'StudentID': StudentID,
            'quiz_name': quiz[0],
            'questions': question_data,
            'Flag': Flag

        }
        return render(request, 'Pages/StudentQuiz.html', context)
    
    else:
        return HttpResponse("No quiz uploaded at the moment")




def submit_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            student_id = data.get('studentId')

            print("The studentID in Submit_Quiz function:", student_id)
            print("The received answers:", answers)

            if not answers:
                return JsonResponse({'error': 'No answers received.'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("SELECT TOP 1 QuizID FROM Quizzes ORDER BY QuizID DESC")
                quiz_id = cursor.fetchone()[0]

                for question_id, student_answer in answers.items():
                    if student_answer.isdigit():  
                        answer_type = 'mcq'
                        selected_option = int(student_answer)
                    else:  
                        answer_type = 'written'
                        selected_option = None

                    print("Inserting answer:", {
                        "StudentID": student_id,
                        "QuizID": quiz_id,
                        "QuestionID": question_id,
                        "AnswerType": answer_type,
                        "StudentAnswer": student_answer,
                        "SelectedOption": selected_option,
                    })

                    try:
                        cursor.execute(
                            """
                            INSERT INTO StudentAnswers (StudentID, QuizID, QuestionID, AnswerType, StudentAnswer, SelectedOption, Flag)
                            VALUES (%s, %s, %s, %s, %s, %s, 1)
                            """,
                            [student_id, quiz_id, question_id, answer_type, student_answer, selected_option]
                        )
                    except Exception as db_error:
                        print("Database error:", str(db_error))
                        return JsonResponse({'error': 'Database insertion failed.'}, status=500)

            return JsonResponse({'message': 'Quiz submitted successfully!'})



        except Exception as e:
            print("Unexpected error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)



def quiz_delivered(request, CourseID):
    
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 QuizID FROM Quizzes ORDER BY QuizID DESC")
        Record = cursor.fetchone()
        if Record:
            quiz_id = Record[0]
        else:
            quiz_id = None

        cursor.execute("""
            SELECT q.QuestionID, q.QuestionText, q.QuestionType, q.Marks, o.OptionID, o.OptionText, o.IsCorrect
            FROM Questions q
            LEFT JOIN Options o ON q.QuestionID = o.QuestionID
            WHERE q.QuizID = %s
        """, [quiz_id])
        questions_data = cursor.fetchall()

        cursor.execute("""
            SELECT sa.StudentID, sa.QuestionID, sa.AnswerType, sa.StudentAnswer, sa.SelectedOption, sa.Marks, 
                   o.OptionText AS SelectedOptionText
            FROM StudentAnswers sa
            LEFT JOIN Options o ON sa.SelectedOption = o.OptionID
            WHERE sa.QuizID = %s
        """, [quiz_id])
        answers_data = cursor.fetchall()


        cursor.execute("""
            SELECT COUNT(*) FROM Quizzes 
            WHERE course_id = %s
        """, [CourseID])
        QuizNumber = cursor.fetchall()
        QuizNumber = QuizNumber[0][0]

    questions = {}
    for row in questions_data:
        question_id = row[0]
        if question_id not in questions:
            questions[question_id] = {
                "text": row[1],
                "type": row[2],
                "marks": row[3],
                "options": [],
            }
        if row[4]: 
            questions[question_id]["options"].append({
                "id": row[4],
                "text": row[5],
                "is_correct": row[6],
            })

    answers = {}
    student_data = []  
    
    for row in answers_data:
        student_id = row[0]

        if not any(student['StudentID'] == student_id for student in student_data):
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT Student_Name, Student_Image, Student_ID
                    FROM StudentInformation
                    WHERE Student_ID = %s 
                """, [student_id])
                student_record = cursor.fetchall()

            if student_record:
                for record in student_record:
                    Student_Name = record[0]
                    Student_Image = record[1]
                    Student_ID = record[2]

                    student_data.append({
                        'StudentName': Student_Name,
                        'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                        'StudentID': Student_ID,
                    })

        question_id = row[1]
        if student_id not in answers:
            answers[student_id] = {}
        print("The question type: ", row[2])
        answers[student_id][question_id] = {
            "type": row[2],
            "written_answer": row[3],
            "selected_option": row[4],  
            "selected_option_text": row[6],  
            "marks": row[5],
        }

    if quiz_id:
        context = {
            "quiz_id": quiz_id,
            "questions": questions,
            "answers": answers,
            "StudentInfo": student_data,
            "QuizNumber": QuizNumber
        }
            
        return render(request, 'Pages/quiz_delivered.html', context)
    else:

        return HttpResponse("No quiz delivered at the moment")




def confirm_grades(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_id = data.get('studentId')
            print("The student ID in confirm_grades: ", student_id)
            grades = data.get('grades', {})
            teacher_id = 1 
            with connection.cursor() as cursor:
                for question_id, marks_obtained in grades.items():
                    cursor.execute("SELECT Marks FROM Questions WHERE QuestionID = %s", [question_id])
                    print("The question_id in confirm_grades: ", question_id)
                    print("Marks obtained: ", marks_obtained)

                    total_marks = cursor.fetchone()[0]

                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM QuizGrades 
                        WHERE StudentID = %s AND QuestionID = %s
                    """, [student_id, question_id])
                    record_exists = cursor.fetchone()[0] > 0

                    if record_exists:
                        cursor.execute("""
                            UPDATE QuizGrades 
                            SET MarksObtained = %s, GradedBy = %s 
                            WHERE StudentID = %s AND QuestionID = %s
                        """, [marks_obtained, teacher_id, student_id, question_id])
                        print(f"Updated record for StudentID {student_id}, QuestionID {question_id}.")
                    else:

                        cursor.execute("""
                         SELECT QuizID FROM Questions WHERE QuestionID = %s
                         """, [question_id])    
                        QuizID = cursor.fetchone()[0] 
     
                        cursor.execute("""
                         SELECT QuizNumber FROM Quizzes WHERE QuizID = %s
                         """, [QuizID])    
                        QuizNumber = cursor.fetchone()[0] 


                        cursor.execute("""
                            INSERT INTO QuizGrades (QuizID, QuizNumber, QuestionID, StudentID, TotalMarks, MarksObtained, GradedBy) 
                            VALUES (
                                (SELECT QuizID FROM Questions WHERE QuestionID = %s), 
                                %s, %s, %s, %s, %s, %s
                            )
                        """, [question_id, QuizNumber, question_id, student_id, total_marks, marks_obtained, teacher_id])
                        print(f"Inserted record for StudentID {student_id}, QuestionID {question_id}.")

            return JsonResponse({"message": "Grades confirmed successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def HomeWork_delivered(request, CourseID):
    HomeWorkNumber = 0
    CourseName = ""
    with connection.cursor() as cursor:
 
        cursor.execute("""
            SELECT si.Student_Name, si.Student_ID, si.Student_Image, hd.FileContent,
            hd.AssignmentNumber, si.Class, hd.AssignmentId, hd.TotalMark
            FROM StudentInformation si
            INNER JOIN HomeworkDelivered hd ON si.Student_ID = hd.Student_ID
            AND hd.course_id = %s
            ORDER BY hd.AssignmentId ASC;
        """, [CourseID])
        student_record = cursor.fetchall()

        cursor.execute("""
            SELECT course_name FROM CoursesList WHERE course_id = %s
        """, [CourseID])
        result = cursor.fetchall()
        Course_name = result[0][0]



    student_data = []
    if student_record:
        for record in student_record:
            Student_Name = record[0]
            Student_ID = record[1]
            print("Student id = ", Student_ID)
            Student_Image = record[2]
            pdf_data = base64.b64encode(record[3]).decode('utf-8')
            AssignmentNumber = record[4]
            HomeWorkNumber = AssignmentNumber
            Class = record[5]
            AssignmentID = record[6]
            TotalMark = record[7]
            with connection.cursor() as cursor:
                cursor.execute("""SELECT Flag FROM HomeworkDelivered WHERE AssignmentId = %s AND Student_ID = %s
                        """, [AssignmentID, Student_ID])
                result = cursor.fetchone()
            Flag = result[0]



            

            student_data.append({
                'StudentName': Student_Name,
                'StudentID': Student_ID,
                'StudentImage': base64.b64encode(Student_Image).decode('utf-8'),
                'PDF': pdf_data,
                'AssignmentNumber': AssignmentNumber,
                'CourseName': Course_name,
                'Class': Class,
                'AssignmentID': AssignmentID,
                'CourseID': CourseID,
                'TotalMark': TotalMark,
                'Flag': Flag
            })


    context = {

        "StudentInfo": student_data,
        "CourseName": Course_name,
        'HomeWorkNumber': HomeWorkNumber

    }
    return render(request, 'Pages/HomeWorK_Delivered.html', context)


# @csrf_exempt
# def SaveAssignmentGrade(request):
#     print("In")
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             print("Received data:", data)
#             student_id = data.get('studentId')
#             Grade = data.get('grades')
#             AssignmentID = data.get('AssignmentID')
#             CourseID = data.get('CourseID')
#             TotalMark = data.get('TotalMark')
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO HomeWorkGrades 
#                     (AssignmentId, course_id, Student_ID, TotalMarks, MarksObtained, GradedAt, GradedBy)
#                     VALUES (%s, %s, %s, %s, %s, NOW(), %s)
#                 """, [AssignmentID, CourseID, student_id, TotalMark, Grade, 1])

            
#             return JsonResponse({"message": "Grades confirmed successfully!"}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
#     return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def SaveAssignmentGrade(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received data:", data)

            student_id = data.get('studentId')
            Grade = data.get('grades')
            AssignmentID = data.get('AssignmentID')
            CourseID = data.get('CourseID')
            TotalMark = data.get('TotalMark')

            if not all([student_id, Grade, AssignmentID, CourseID, TotalMark]):
                return JsonResponse({"error": "Missing or invalid data in request"}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""SELECT AssignementNumber FROM Assignments WHERE AssignmentId = %s
                               """, [AssignmentID])
                result = cursor.fetchone()
                AssignmentNumber = result[0]
                cursor.execute("""
                    INSERT INTO HomeWorkGrades 
                    (AssignmentId, course_id, Student_ID, TotalMarks, MarksObtained, GradedAt, GradedBy, AssignmentNumber)
                    VALUES (%s, %s, %s, %s, %s, GETDATE(), %s, %s)
                """, [AssignmentID, CourseID, student_id, TotalMark, Grade, 1, AssignmentNumber])

                cursor.execute("""
                    UPDATE HomeworkDelivered 
                    SET Flag = 1 
                    WHERE AssignmentId = %s AND Student_ID = %s
                """, [AssignmentID, student_id])

            return JsonResponse({"message": "Grades confirmed successfully!"}, status=200)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)
