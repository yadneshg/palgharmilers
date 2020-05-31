import uuid
from functools import wraps
from sqlalchemy.orm import session
from models import *
from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify, send_from_directory
import datetime
import os
from werkzeug.utils import secure_filename
import os.path
from functools import wraps
import csv
import json
import urllib3
import requests

app = Flask(__name__)

__author__ = 'Yadnesh'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Cyber123@localhost:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = '25296'
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

base_url = "https://www.strava.com/api/v3"
auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
clubs_url = "https://www.strava.com/api/v3/athlete/clubs"
athlete_url = "https://www.strava.com/api/v3/athlete"

def renew_token():
    payload = {
        'client_id': "47979",
        'client_secret': 'e3938884e234926885109ba4726449f7e036be1a',
        'refresh_token': 'a0c2468b904c99aca9ad0d68f17c781304007e47',
        'grant_type': "refresh_token",
        'f': 'json'
    }
    print("Requesting Token...\n")
    res = requests.post(auth_url, data=payload, verify=False)
    try:
        access_token = res.json()['access_token']
    except :
        print("json.decoder.JSONDecodeError")
    print("Access Token = {}\n".format(access_token))
    return access_token

@app.route("/")
def index():
    message = "Welcome to Palghar Milers!"
    now = datetime.datetime.now() #todays date
    d = now.day  #day
    m = now.month #month
    y = now.year #year
    members = Member.query.order_by(Member.id).all()
    if members is None:
        return render_template("error.html")
    #To Check whether any mamber has birthday today
    birthday_boy=""
    for member in members:
        memberbirthday=str(member.dob)
        member_month=int(memberbirthday[5:7])
        member_date = int(memberbirthday[8:10])
        if d==member_date and m== member_month:
            birthday_boy += "Happy Birthday,"+member.firstname+"!  "

    return render_template("index.html",birthday_boy=birthday_boy, message=message)

@app.route("/login")
def login():
    return render_template('login.html')

#user Login
@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    username = request.form.get("username")
    password = request.form.get("password")
    members = Member.query.all()
    for member in members:
        if  (username==member.username and password==member.password) or (username=="admin" and password=="123"):
            session['logged_in'] = True
            message = 'You are Logged In'
            return render_template('index.html', message=message)
    return render_template('login.html', message="Invalid Credentils")

#for login session
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            message = "You need to login first"
            return render_template('login.html', message=message)
    return wrap

#for Logout
@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    message = 'You were logged out.'
    return render_template('index.html', message=message)

#to display list of members
@app.route("/members")
@login_required
def members():
    members = Member.query.order_by(Member.id).all()
    return render_template("members.html", members=members)

#@app.route("/athlete_details/<int:athlete_id>")
#def athlete_details(athlete_id):
#    access_token = renew_token()
#    header = {'Authorization': 'Bearer ' + access_token}
#    #param = {'per_page': 200, 'page': 1}
#    athletedetails = requests.get(athlete_url, headers=header).json()
#    return render_template("athletedetails.html", athletedetails=athletedetails)

@app.route("/athlete_stats/<int:athlete_id>")
def athlete_stats(athlete_id):
    access_token = renew_token()
    stats= "/athletes/"+ str(athlete_id)+ "/stats"
    athletestat_url = base_url + stats
    header = {'Authorization': 'Bearer ' + access_token}
    athletestats = requests.get(athletestat_url, headers=header).json()
    return render_template("athletestats.html", athletestats=athletestats, athlete_id=athlete_id)

#to display details of perticular member
@app.route("/memberdetails/<int:member_id>")
@login_required
def memberdetails(member_id):
    member=Member.query.get(member_id)
    #member=db.execute("SELECT * from members where id = :member_id", {"member_id": member_id}).fetchone()
    if member is None:
        return render_template("error.html", message="No Such Member.")
    return render_template("memberdetails.html", member=member)

@app.route("/forregistermember")
def forregistermember():
    return render_template('registermember.html')

#to register new member
@app.route("/registermember",methods=["post","GET"])
def registermember():
    fname = request.form.get("memberfname")
    mname = request.form.get("membermname")
    lname = request.form.get("memberlname")
    email = request.form.get("memberemail")
    mobile = request.form.get("membermobile")
    dob = request.form.get("memberdob")
    strava_id=request.form.get("stravaid")
    username = (fname + lname).lower()
    members = Member.query.all()
    for member in members:
        if fname==member.firstname and lname==member.lastname:
            return render_template("index.html", message="Member already exists.")
        i = 1
        while True:
            if username == member.username:
                username+=i
            else:
                break
        if email==member.email:
            return render_template("index.html", message="email already exists.")
    user=Member(firstname=fname, middlename=mname, lastname=lname, email=email, mobile=mobile, dob=dob, strava_id=strava_id, username=username)

    db.session.add(user)
    db.session.commit()
    if user is None:
        return render_template("index.html", message="No Such Member.")
    mid=user.id
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.relpath(f"static/uploads/{filename}"))
            ff=f"static/uploads/{filename}"
            dd=f"static/uploads/{mid}.jpg"
            os.rename(ff,dd)
    return render_template("password.html", user=user, message="Member Registered")

@app.route("/userpassword", methods=["POST"])
def userpassword():
    username=request.form.get("username")
    password=request.form.get("password")
    user=Member.query.filter_by(username=username).first()
    user.password=password
    db.session.commit()
    return render_template("index.html", message="Member Registered")

#to updates details of existing member
@app.route("/forupdatemember",methods=["post","GET"])
@login_required
def forupdatemember():
    fname = request.form.get("updatefname")
    mname = request.form.get("updatemname")
    lname = request.form.get("updatelname")
    email = request.form.get("updateemail")
    mobile = request.form.get("updatemobile")
    dob = request.form.get("updatedob")
    strava_id = request.form.get("stravaid")
    try:
        member_id = int(request.form.get("updateid"))
    except ValueError:
        return render_template("index.html", message="Invalid member ID.")
    except TypeError:
        return render_template("index.html", message="No Changes Made!")
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.relpath(f"static/uploads/{filename}"))
            ff=f"static/uploads/{filename}"
            if os.path.exists(f'static/uploads/{member_id}.jpg'):
                print("AAAAAAAA")
                os.remove(f'static/uploads/{member_id}.jpg')
            dd = f"static/uploads/{member_id}.jpg"
            os.rename(ff,dd)

    member = Member.query.get(member_id)
    member.firstname=fname
    member.middlename=mname
    member.lastname=lname
    member.email=email
    member.mobile=mobile
    member.dob=dob
    member.strava_id=strava_id
    db.session.commit()
    return render_template("memberdetails.html", member=member)


# to register new member
@app.route("/removemember", methods=["post", "GET"])
@login_required
def removemember():
    memberid = request.form.get("rmemberid")
    removemember=Member.query.get(memberid)

    if removemember is None:
        return render_template("index.html", message="No Such Member.")
    db.session.delete(removemember)
    db.session.commit()
    return render_template("index.html", message="Member Successfully Removed")


#to update tshirt size of perticular member
@app.route("/tshirtsize", methods=["POST"])
@login_required
def tshirtsize():
    memberidfortshirt=request.form.get("tshirtmemberid")
    tshirtsize = request.form.get("tshirtsize")
    tshirtnumber = request.form.get("tshirtnumber")

    member = Member.query.get(memberidfortshirt)
    if not member:
        return render_template("index.html", message="No such member with that id.")

    member = Member.query.get(memberidfortshirt)
    member.t_size=tshirtsize
    member.t_number=tshirtnumber
    db.session.commit()

    return render_template("index.html", message="T-Shirt Details Updated.")

#Blogs
@app.route('/blogs')
@login_required
def blogs():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('blogs.html', posts=posts)

# Display Blogs
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

# Add new Blog
@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, author=author, content=content, date_posted=datetime.datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('blogs'))

#about us
@app.route("/aboutus")
def aboutus():
    return render_template("about.html")

@app.route("/clubdetails/<int:club_id>")
def clubdetails(club_id):
    access_token = renew_token()
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}
    clubdetails = requests.get(clubs_url, headers=header, params=param).json()

    admins= "/clubs/"+ str(club_id)+ "/admins"
    clubadmins_url = base_url + admins
    clubadmins = requests.get(clubadmins_url, headers=header, params=param).json()

    members= "/clubs/"+ str(club_id)+ "/members"
    members_url = base_url + members
    clubmembers = requests.get(members_url, headers=header, params=param).json()
    return render_template("clubdetails.html", clubdetails=clubdetails, clubadmins=clubadmins, clubmembers=clubmembers)

@app.route("/for_club_data", methods=['GET', 'POST'])
def for_club_data():
    club_id=request.form.get("club_id")
    members = Member.query.order_by(Member.id).all()
    return render_template("forclubdata.html", club_id=club_id,  members=members)

@app.route("/club_data/<int:club_id>",  methods=['GET', 'POST'])
def club_data(club_id):
    member_strava_id=request.form.get("strava_member")
    access_token = renew_token()
    str_data_date=request.form.get("data_date")
    print(member_strava_id)
    data_date = datetime.datetime.strptime(str_data_date, '%Y-%m-%d')
    fromdateepoch = data_date.timestamp()


    club_activities = "/clubs/"+str(club_id)+"/activities?"
    club_activities_url = base_url + club_activities
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'after':fromdateepoch,'per_page': 200, 'page': 1}
    clubdata = requests.get(club_activities_url, headers=header, params=param).json()
    entries= (len(clubdata))
    print(clubdata)
    return render_template("clubdata.html", clubdata=clubdata, entries=entries, member_strava_id=member_strava_id)



#
# @app.route('/deleteimage', methods=['GET', 'POST'])
# def deleteimage():
#     if request.method == 'POST':
#         imagetodelete=request.form.getlist('imagetodelete')
#         print(imagetodelete)
#     for image in imagetodelete:
#         if os.path.exists(f"static/Images/{image}.jpg"):
#             print("Path Exist!!!")
#             os.remove(f"static/Images/{image}.jpg")
#             message = "Deleted Selected Images"
#         else:
#             message="Error"
#             print(message)
#     return render_template("index.html", message=message)
#
#

# #Image gallery
#     @app.route("/imagegallery",methods=["post","GET"])
#     @login_required
#     def imagegallery():
#         counter = 1
#         file_count=0
#         if request.method == 'POST':
#             image = request.files['image']
#             if image:
#                 filename = secure_filename(image.filename)
#                 print(filename)
#                 try:
#                     image.save(os.path.relpath(f"static/images/{filename}"))
#                 except FileNotFoundError:
#                     return render_template("index.html", message="Invalid File Type.")
#                 ff=f"static/images/{filename}"
#                 while os.path.exists(f"static/images/{counter}.jpg"):
#                     counter+=1
#                 dd=f"static/images/{counter}.jpg"
#                 os.rename(ff,dd)
#         path, dirs, files = next(os.walk("static/images"))
#         file_count = len(files)
#         print(file_count)
#         return render_template("imagegallery.html", file_count=file_count)

# @app.route("/imagegallery")
# def imagegallery():
#     image_names = os.listdir('static/images')
#     print(f"Names :{image_names}")
#     return render_template("imagegallery.html", image_names=image_names)

# working only files with same name upload problem

# @app.route("/imagegallery", methods=['get','POST'])
# def imagegallery():
#     message=''
#     target = os.path.join(APP_ROOT, 'static/images/')
#     print(target)
#     filename=''
#     if not os.path.isdir(target):
#         os.mkdir(target)
#     else:
#         print(f"directroy {target} already exist..")
#         new_images= request.files.getlist("image")
#     image_names = os.listdir('static/images')
#     if len(image_names)<=50:
#         for new_image in new_images:
#             print(new_image)
#             filename = new_image.filename
#             print(f"Filename : {filename}")
#             if filename:
#                 destination = "/".join([target, filename])
#                 new_image.save(destination)
#                 message = "Image Uploaded"
#             else:
#                 message = "No File Selected"
#     else:
#         message="Limit Exceeded"
#     image_names = os.listdir('static/images')
#     print(f"images in folder :{image_names}")
#     return render_template("imagegallery.html", image_name=filename, image_names=image_names, message=message)


@app.route("/imagegallery", methods=['get','POST'])
def imagegallery():
    message=""
    image_names = os.listdir('static/images')
    if len(image_names)<=50:
        target = os.path.join(APP_ROOT, 'static/images/')
        if not os.path.isdir(target):
            os.mkdir(target)
        else:
            print(f"directroy {target} already exist..")
        new_images= request.files.getlist("new_images")

        for new_image in new_images:
            if new_image:
                filename = secure_filename(new_image.filename)
                try:
                    new_image.save(os.path.join(target, filename))
                except FileNotFoundError:
                    return render_template("error.html", message="Invalid File Type.")

                uploadedfilename=f"d:/cs50/workspace/palgharmilers/static/images/{filename}"
                imgagename = uuid.uuid1()
                renamedfilename=f"d:/cs50/workspace/palgharmilers/static/images/{imgagename}.jpg"
                os.rename(uploadedfilename,renamedfilename)
                message="Image Uploaded"
            else:
                message="No Image Selected"
        path, dirs, files = next(os.walk("d:/cs50/workspace/palgharmilers/static/images"))
    else:
         message="Limit Exceeded"
    image_names = os.listdir('static/images')
    print(f"images in folder :{image_names}")
    return render_template("imagegallery.html", image_names=image_names, message=message)


@app.route("/imagegallery/<filename>")
def send_image(filename):
    print(filename)
    return send_from_directory('static/images', filename)

@app.route('/deleteimages', methods=['GET', 'POST'])
def deleteimages():
    if request.method == 'POST':
        print(f"selected images{request.form.getlist('selectedimages')}")
        selectedimages=request.form.getlist('selectedimages')
    for image in selectedimages:
        if os.path.exists(f"static/Images/{image}"):
            print("Path Exist!!!")
            os.remove(f"static/Images/{image}")
            message = "Deleted Selected Images"
        else:
            message="Error"
            print(message)
    image_names = os.listdir('static/images')
    return render_template("imagegallery.html", image_names=image_names, message=message)