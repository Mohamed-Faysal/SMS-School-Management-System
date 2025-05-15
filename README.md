# School Management System (SMS)

A comprehensive and intelligent **School Management System** that utilizes **Facial Recognition** for student authentication, streamlines administrative tasks, and enhances communication between students, instructors, and parents. This system provides a secure, efficient, and integrated platform for managing educational activities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Components](#system-components)
- [Face Recognition Model](#face-recognition-model)
- [Tech Stack](#tech-stack)
- [Future Work](#future-work)
- [Team](#team)

---

## Overview

The School Management System (SMS) is designed to overcome challenges in traditional school systems like manual attendance, lack of real-time communication, and fragmented data handling. By integrating modern technologies, SMS offers an all-in-one platform for students, instructors, parents, and admins.

---

## Features

- **Facial Recognition Login** for students
- **Automated Attendance Tracking**
- **Online Quizzes & Homework Submission**
- **Grade Management & Real-time Monitoring**
- **Parent Portal** for real-time progress tracking
- **Role-based Interfaces** (Admin, Instructor, Student, Parent)

---

## System Components

- **Website Interface**

  - Student Dashboard (Grades, Attendance, Courses)
  - Instructor Dashboard (Manage Materials, Attendance, Grades)
  - Parent Dashboard (Monitor Student Progress)
  - Admin Dashboard (Manage Users, Courses)

- **Face Recognition Model**

  - Built using CNN
  - 92.81% Training Accuracy
  - 95.56% Validation Accuracy

- **Database**
  - Stores users, attendance logs, course materials, and more

---

## Face Recognition Model

The system uses a custom-trained **Convolutional Neural Network (CNN)** for recognizing student faces with high accuracy.

### Model Highlights:

- **Dataset**: 13,500 training images and 4,019 validation images for 9 students
- **Techniques Used**: Data Augmentation (rotation, zoom, shift, flip, darken)
- **CNN Structure**: 3 convolutional layers with increasing filters (32, 64, 128)
- **Dropout**: Applied at varying levels to prevent overfitting

---

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask/Django (assumed)
- **Database**: MySQL / PostgreSQL
- **Machine Learning**: TensorFlow / Keras
- **Tools**: OpenCV, CNN, Git, GitHub

---

## Future Work

- Improve model accuracy with advanced deep learning architectures
- Implement **Face Aging** for better long-term recognition
- Add **AI-powered performance reports**
- Launch a **mobile app** for better accessibility

---

## Team

Supervised by:  
**Dr. Elham Shawky Salama**  
Associate Professor, Information Technology Department

**Team Members:**

- Abubaker Saeed Omer
- Ibrahim Mohammed Essa
- Mohammed Fisal

---

## License

MIT License

Copyright (c) Olli-Pekka Heinisuo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
