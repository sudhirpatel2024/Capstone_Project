from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
import os
import time
import datetime

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import re
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn import svm
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


global classifier
global vectorizer
global labels
global doctor

def preprocess(text_string):
    space_pattern = '\s+'
    giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
        '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    mention_regex = '@[\w\-]+'
    parsed_text = re.sub(space_pattern, ' ', text_string)
    parsed_text = re.sub(giant_url_regex, '', parsed_text)
    parsed_text = re.sub(mention_regex, '', parsed_text)
    return parsed_text

def tokenize(symptoms):
    symptoms = " ".join(re.split("[^a-zA-Z]*", symptoms.lower())).strip()
    tokens = [t for t in symptoms.split()]
    tokens = ''.join(tokens)
    return tokens


def TrainML(request):
    global classifier
    global vectorizer
    global labels
    global doctor
    if request.method == 'GET':
        output = ''
        doctor = pd.read_csv('Doctors.csv', encoding ="ISO-8859-1")
        doctor = doctor.values
        dataset = pd.read_csv('dataset.csv', encoding ="ISO-8859-1")
        labels = dataset['Source'].unique().tolist()
        print(type(labels))
        symptoms = dataset.Target
        diseases = dataset.Source
        Y = []
        for i in range(len(diseases)):
            index = labels.index(diseases[i])
            Y.append(index)
        print(Y)    
        X = []
        for i in range(len(symptoms)):
            arr = symptoms[i]
            X.append(arr)
        vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=False, norm=None, decode_error='replace', max_features=1000)
        tfidf = vectorizer.fit_transform(X).toarray()        
        X = pd.DataFrame(tfidf, columns=vectorizer.get_feature_names())    
        print(X.head())
        Y = np.asarray(Y)
        c1 = RandomForestClassifier()
        c1.fit(X, Y)
        c2 = BernoulliNB()
        c2.fit(X, Y)
        c3 = DecisionTreeClassifier()
        c3.fit(X,Y)
        c4 = LogisticRegression()
        c4.fit(X,Y)
        c5 = svm.SVC(C=2.0,gamma='scale',kernel = 'rbf', random_state = 2)
        c5.fit(X,Y)
        classifier = c1

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)
        y_pred = c1.predict(X_test)
        acc1 = accuracy_score(y_test,y_pred)
        print(acc1)

        y_pred = c2.predict(X_test)
        acc2 = accuracy_score(y_test,y_pred)
        print(acc2)
    
        y_pred = c3.predict(X_test)
        acc3 = accuracy_score(y_test,y_pred)
        print(acc3)

        y_pred = c4.predict(X_test)
        acc4 = accuracy_score(y_test,y_pred)
        print(acc4)

        y_pred = c5.predict(X_test)
        acc5 = accuracy_score(y_test,y_pred)
        print(acc5)

        output='<tr>'
        output+='<td><font size=3 color=black>Random Forest Algorithm</td><td><font size=3 color=black>'+str(acc1*100)+'</font></td>'
        output+='<tr><td><font size=3 color=black>Naive Bayes Algorithm</td><td><font size=3 color=black>'+str(acc2*100)+'</font></td>'
        output+='<tr><td><font size=3 color=black>Decision Tree Algorithm</td><td><font size=3 color=black>'+str(acc3*100)+'</font></td>'
        output+='<tr><td><font size=3 color=black>Logistic Regression Algorithm</td><td><font size=3 color=black>'+str(acc4*100)+'</font></td>'
        output+='<tr><td><font size=3 color=black>SVM Algorithm</td><td><font size=3 color=black>'+str(acc5*100)+'</font></td>'
        context= {'data':output}
        return render(request, 'TrainML.html', context)

def PredictDisease(request):
    if request.method == 'POST':
        symptoms = request.POST.get('t1', False)
        temp = symptoms
        #symptoms = spell(symptoms)
        symptoms = ' '.join(symptoms.split(" "))
        print(symptoms)
        val = vectorizer.transform([symptoms]).toarray()
        val = pd.DataFrame(val)
        predict = classifier.predict(val)
        print(predict)
        predict = predict[0]
        disease = labels[predict]
        print(disease)
        output = '<table border=1 align=center>'
        output+='<tr><th>Symptoms</th><th>Predicted Disease</th></tr>'
        color = '<font size="" color="black">'
        output+='<tr><td>'+color+temp+'</td><td>'+color+disease+'</td></tr>'
        context= {'data':output}
        return render(request, 'Prediction.html', context)
        
        

def DiseasePrediction(request):
    if request.method == 'GET':
       return render(request, 'DiseasePrediction.html', {})

def AddDoctors(request):
    if request.method == 'GET':
       return render(request, 'AddDoctors.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Admin(request):
    if request.method == 'GET':
       return render(request, 'Admin.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})


def Doctor(request):
    if request.method == 'GET':
       return render(request, 'Doctor.html', {})

def Patients(request):
    if request.method == 'GET':
       return render(request, 'Patients.html', {})

def BookAppointment(request):
    if request.method == 'GET':
        doctor = request.GET.get('doctor', False)
        output = '<tr><td><font size="" color="black">Doctor Name</b></td><td><input type="text" name="t1" value='+doctor+' size="30" readonly/></td></tr>'
        context= {'data':output}
        return render(request, 'BookAppointment.html', context)
            
def ViewAppointments(request):
    if request.method == 'GET':
        output = ''
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM Appointment where doctor_name='"+user+"'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr>'
                
                output+='<td><font size=3 color=black>'+str(row[0])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[1])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[2])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[3])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[4])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[5])+'</font></td>'
                
        context= {'data':output}
        return render(request, 'ViewAppointments.html', context) 

def SearchDoctor(request):
    if request.method == 'GET':
        output = ''
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM adddoctor")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr>'
                
                output+='<td><font size=3 color=black>'+str(row[2])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[3])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[4])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[5])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[6])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[7])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[8])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[9])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[10])+'</font></td>'
                output+='<td><a href=\'BookAppointment?doctor='+str(row[0])+'\'><font size=3 color=black>Click Here</font></a></td>'
                output+='<td><a href=\'ViewMap?lat='+str(row[9])+"&lon="+str(row[10])+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        context= {'data':output}
        return render(request, 'SearchDoctor.html', context)    

    
def ViewMap(request):
    if request.method == 'GET':
        lat = request.GET['lat']
        lon = request.GET['lon']
        html = ''
        html+='<input type=\"hidden\" name=\"t1\" id=\"t1\" value='+lat+'>'
        html+='<input type=\"hidden\" name=\"t2\" id=\"t2\" value='+lon+'>'
        context= {'data':html}
        return render(request, 'ViewMap.html', context)

def BookAppointmentAction(request):
    if request.method == 'POST':
      docname = request.POST.get('t1', False)
      docname = docname.replace("_"," ")
      for i in range(len(doctor)):
          name = str(doctor[i,1]).strip()
          if name == docname:
              docname = str(doctor[i,2])
              break
      appointment_time = request.POST.get('t3', False)
      desc = request.POST.get('t2', False)
      appointment_time = str(datetime.datetime.strptime(appointment_time, "%d-%m-%Y %H:%M:%S").strftime("'%Y-%m-%d %H:%M:%S'"))
      booking = str(time.strftime('%Y-%m-%d'))
      user = ''
      print(appointment_time)
      with open("session.txt", "r") as file:
          for line in file:
              user = line.strip('\n')
      aid = 0
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
      with db_connection:
          cur = db_connection.cursor()
          cur.execute("select count(*) FROM Appointment")
          rows = cur.fetchall()
          for row in rows:
              aid = row[0]
      aid = aid + 1
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO Appointment(appointment_id,patient_name,doctor_name,disease_desc,booking_date,appointment_date) VALUES('"+str(aid)+"','"+user+"','"+docname+"','"+desc+"','"+booking+"',"+appointment_time+")"
      print(student_sql_query)
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      context= {'data':'Appointment confirmed with doctor '+docname+' & its id '+str(aid)}
      return render(request, 'PatientScreen.html', context)
      
                                  

def Signup(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
      index = 0
      with db_connection:
          cur = db_connection.cursor()
          cur.execute("select username FROM register")
          rows = cur.fetchall()
          for row in rows:
              if row[0] == username:
                  index = 1
                  break
      if index == 0:
          db_cursor = db_connection.cursor()
          student_sql_query = "INSERT INTO register(username,password,contact,email,address,usertype) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"','user')"
          db_cursor.execute(student_sql_query)
          db_connection.commit()
          print(db_cursor.rowcount, "Record Inserted")
          context= {'data':'Signup Process Completed'}
          return render(request, 'Register.html', context)
      else:
          context= {'data':username+' Username already exists'}
          return render(request, 'Register.html', context)    
        
def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Admin.html', context)

def PatientLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        utype = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    utype = 'success'
                    break
        if utype == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'PatientScreen.html', context)
        if utype == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Patients.html', context)

def DoctorLogin(request):
    if request.method == 'POST':
        global doctor
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        utype = 'none'
        for i in range(len(doctor)):
            usr = str(doctor[i,2]).strip()
            pwrd = str(doctor[i,3]).strip()
            if usr == username and password == pwrd:
                utype = "success"
                break
        if utype == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'DoctorScreen.html', context)
        if utype == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Doctor.html', context)

def ViewDoctors(request):
    if request.method == 'GET':
        output = ''
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM adddoctor")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size=3 color=black>'+row[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+row[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[2])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[3])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[4])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[5])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[6])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[7])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[8])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[9])+'</font></td>'
                output+='<td><font size=3 color=black>'+str(row[10])+'</font></td>'
        context= {'data':output}
        return render(request, 'ViewDoctors.html', context)

def AddDoctorAction(request):
    if request.method == 'POST':
        user = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        gender = request.POST.get('t3', False)
        speciality = request.POST.get('t4', False)
        qualification = request.POST.get('t5', False)
        exp = request.POST.get('t6', False)
        email = request.POST.get('t7', False)
        contact = request.POST.get('t8', False)
        address = request.POST.get('t9', False)
        latitude = request.POST.get('t10', False)
        longitude = request.POST.get('t11', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'SmartHealthApp',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO adddoctor(username,password,gender,speciality,qualification,experience,emailid,contact_no,hospital_address,latitude,longitude) "
        student_sql_query+=" VALUES('"+user+"','"+password+"','"+gender+"','"+speciality+"','"+qualification+"','"+exp+"','"+email+"','"+contact+"','"+address+"','"+latitude+"','"+longitude+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        context= {'data':'Doctor details added'}
        return render(request, 'AddDoctors.html', context)



        
           
