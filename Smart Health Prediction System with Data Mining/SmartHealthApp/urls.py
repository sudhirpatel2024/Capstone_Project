from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('Admin.html', views.Admin, name="Admin"), 
	       path('Patients.html', views.Patients, name="Patients"),
	       path('Doctor.html', views.Doctor, name="Doctor"),
	       path('Register.html', views.Register, name="Register"),
	       path('Signup', views.Signup, name="Signup"),
	       path('AdminLogin', views.AdminLogin, name="AdminLogin"),
	       path('DoctorLogin', views.DoctorLogin, name="DoctorLogin"),
	       path('PatientLogin', views.PatientLogin, name="PatientLogin"),	
	       path('AddDoctors.html', views.AddDoctors, name="AddDoctors"),
	       path('AddDoctorAction', views.AddDoctorAction, name="AddDoctorAction"),
	       path('ViewDoctors', views.ViewDoctors, name="ViewDoctors"),
	       path('TrainML', views.TrainML, name="TrainML"),
	       path('DiseasePrediction.html', views.DiseasePrediction, name="DiseasePrediction"),
	       path('PredictDisease', views.PredictDisease, name="PredictDisease"),
	       path('SearchDoctor', views.SearchDoctor, name="SearchDoctor"),
	       path('ViewMap', views.ViewMap, name="ViewMap"),
	       path('BookAppointment', views.BookAppointment, name="BookAppointment"),
	       path('BookAppointmentAction', views.BookAppointmentAction, name="BookAppointmentAction"),
	       path('ViewAppointments', views.ViewAppointments, name="ViewAppointments"),
]