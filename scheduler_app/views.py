from django.shortcuts import render, redirect, HttpResponse
from .models import Users
from .models import students
from .models import Subject
from .models import Assignment
from .models import inbox_messages
from django.contrib import messages
import bcrypt
# Create your views here.

#GET
def index(request):
	return render(request, 'index.html')

def login_reg(request):
	return render(request, 'login_reg.html')

def add_user(request):
	return render(request, 'login_reg.html')

def logout(request):
	request.session.flush()
	return redirect('/')

def profile(request):
    if 'user_id' in request.session:
        user = Users.objects.filter(id=request.session['user_id'])
        if user:
            context = {
                'user': user[0],
                'subjects':Subject.objects.all(),

            }
            return render(request, 'profile.html', context)
    return redirect('/')

def inbox(request, id):
	user = Users.objects.get(id=request.session['user_id'])
	context = {
		'user': user,
		'messages': inbox_messages.objects.all(),
		'all_users': Users.objects.all(),
	}
	return render(request, 'inbox.html', context)

def open_message(request, id):
	user = Users.objects.get(id=request.session['user_id'])
	message = inbox_messages.objects.get(id=id)
	context = {
		'user': user,
		'message': message,
	}
	return render(request, 'opened_message.html', context)

def new_message(request):
	user = Users.objects.get(id=request.session['user_id'])
	context = {
		'user': user,
		'messages': inbox_messages.objects.all(),
		'all_users': Users.objects.all(),
	}
	return render(request, 'new_message.html', context)

#<---------POST METHODS------>

#REGISTER METHOD
def create_user(request):
	print(" Can I create a user?!")
	if request.method != "POST":
		return redirect('/')
	errors = Users.objects.validate(request.POST)
		#if the dictionary received has errors in it, reject the form, and show the error messages
		# on the template the user was on last
	if len(errors) > 0:
		print(errors)
		for key, value in errors.items():
			messages.error(request, value)
			return redirect('/')
	else:
		user_pw=request.POST['password']
		# create the hash for the password
		hash_pw=bcrypt.hashpw(user_pw.encode(), bcrypt.gensalt()).decode()
		print(hash_pw)
		# create user object 
		new_user = Users.objects.create(
			first_name=request.POST['first_name'], 
			last_name=request.POST['last_name'], 
			email=request.POST['email'], 
			role = request.POST['role'],
			password=hash_pw,
		)
		print(new_user)
		# storing user's id so I can track user's interactions on the website 
		request.session['user_id']= new_user.id 
		request.session['first_name'] = new_user.first_name
		request.session['last_name'] = new_user.last_name
		request.session['role'] = new_user.role
	
		print('Checking User Role 2')
		if new_user.role == "2":
			#return redirect('/parent')
			return redirect(f"/parent/{new_user.id}")
		else:
			return redirect('/profile')

#LOGIN METHOD
def user_login(request):
	print('Is this user_login method working?')
	if request.method == 'POST':
		# query to find the user
		logged_user=Users.objects.filter(email=request.POST['email'])

		if len(logged_user) > 0:
			logged_user = logged_user[0]
			print(logged_user)
			print(logged_user.password, request.POST['password'])

			if bcrypt.checkpw(request.POST['password'].encode(),logged_user.password.encode()):
				request.session['user_id'] = logged_user.id 
				request.session['first_name'] = logged_user.first_name
				
				print('Checking User Role 2')
				if logged_user.role == "2":
					#return redirect('/parent')
					return redirect(f"/parent/{logged_user.id}")
				else:
					return redirect('/profile')
			else :
				messages.error(request, "Your password is incorrect.")
				return redirect ('/register')
		else:
			messages.error(request, "Your email does not exist.")
			return redirect ('/register')
		
		print('Checking User Role 2')
		if logged_user.role == "2":
			#return redirect('/parent')
			return redirect(f"/parent/{logged_user.id}")
		else:
			return redirect('/profile')

#INBOX METHOD
def send_message(request):
	new_message = inbox_messages.objects.create(
        subject = request.POST['subject'],
		message = request.POST['message'],
		sender = Users.objects.get(id=request.session['user_id']),
        recipient = Users.objects.get(id=request.POST['recipient']),
    )
	return redirect('/profile')

def delete_inbox_message(request, id):
	destroyed = inbox_messages.objects.get(id=id)
	user = Users.objects.get(id=request.session['user_id'])
	if destroyed.recipient == user:
		destroyed.delete()
	return redirect('/profile')

def delete_sent_message(request, id):
	destroyed = inbox_messages.objects.get(id=id)
	user = Users.objects.get(id=request.session['user_id'])
	if destroyed.sender == user:
		destroyed.delete()
	return redirect('/profile')


def parent(request, user_id):
    if 'user_id' in request.session:  #Is the user logged in

        this_user = Users.objects.filter(id=request.session['user_id']),
        context = {
                'user': Users.objects.get(id=request.session['user_id']), #create instance of user to add to record
                'allstudents': students.objects.all(), #All students
				'mystudents': students.objects.filter(user=user_id), #Grab Only User students
				#'mystudents': this_user.students.all(),	# get all the kids this user has
				'subjects': subjects.objects.all(), #All subjects
            }
        return render(request,'parent.html', context) #if valid user than we move on to success
    return redirect("/login") #no matter what success handles the view and the session