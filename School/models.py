from django.db import models

class Info(models.Model):
    Fname = models.CharField(max_length=250)
    id = models.CharField(max_length=10, primary_key=True)
    
    def __str__(self):
        return f"{self.id} - {self.Fname}"


class Courses(models.Model):
    course_name = models.CharField(max_length=250)
    course_id = models.IntegerField(primary_key=True)
    course_level = models.CharField(max_length=250)
    image_url = models.CharField(max_length=250)
    link_url = models.CharField(max_length=250)

    def __str__(self):
        return self.course_name


class New_previous_Profiles(models.Model):
    Student_ID = models.IntegerField()
    Teacher_ID = models.IntegerField()
    Student_url = models.CharField(max_length=250)
    Teacher_url = models.CharField(max_length=250)


    def __str__(self):
        return f"Student ID: {self.Student_ID}, Teacher ID: {self.Teacher_ID}"
    
class StudentInformation(models.Model):
    Student_Name = models.CharField(max_length=250)
    Student_ID = models.IntegerField(primary_key=True)
    Student_Age = models.CharField(max_length=250)
    Student_Level = models.CharField(max_length=250)
    Student_Gender = models.CharField(max_length=250)
    Student_Image = models.CharField(max_length=250)
    Passwordd = models.CharField(max_length=250)


    def __str__(self):
        return self.Student_Name 

class ParentInformation(models.Model):
    Parent_Name = models.CharField(max_length=250)
    Parent_Id = models.IntegerField(primary_key=True)
    Parent_Image = models.CharField(max_length=250)
    Student = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    Passwordd = models.CharField(max_length=250)

    def __str__(self):
        return self.Parent_Name  # Or any other field you want to display

class TeacherInformation(models.Model):
    Teacher_Name = models.CharField(max_length=250)
    Teacher_Id = models.IntegerField(primary_key=True)
    Teacher_Age = models.CharField(max_length=250)
    Teacher_Gender = models.CharField(max_length=250)
    Course_Handle = models.CharField(max_length=250)
    Teacher_Image = models.CharField(max_length=250)
    Passwordd = models.CharField(max_length=250)


    def __str__(self):
        return self.Teacher_Name 
    

class StudentTeacherCommunications(models.Model):
    Message_text = models.CharField(max_length=4000)
    Message_ID = models.AutoField(primary_key=True) 
    Message_Date = models.CharField(max_length=250)
    Message_Hour = models.IntegerField()
    Message_Minute = models.IntegerField()
    Message_Source = models.IntegerField()
    Student_ID = models.ForeignKey(StudentInformation, on_delete=models.CASCADE)
    Teacher_ID = models.ForeignKey(TeacherInformation, on_delete=models.CASCADE)

    def __str__(self):
        return f"Message ID: {self.Message_ID}"


class CourseContents(models.Model):
    MaterialID = models.AutoField(primary_key=True) 
    PublisherImage = models.CharField(max_length=250)
    PublisherName = models.CharField(max_length=250)
    DateOfPublish = models.CharField(max_length=250)
    DescriptionText = models.CharField(max_length=4000)
    MaterialPath = models.CharField(max_length=250)
    MaterialIcon = models.CharField(max_length=250)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)


    def __str__(self):
        return self.MaterialID 