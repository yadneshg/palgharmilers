import uuid
from functools import wraps
from sqlalchemy.orm import session
from models import *
import datetime as dt
import os
from werkzeug.utils import secure_filename
import os.path
from functools import wraps
import csv
import urllib3
import json
import requests
from flask import Flask, redirect, request, url_for, render_template, flash, session, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient


app = Flask(__name__)

__author__ = 'Yadnesh'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Cyber123@localhost:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = '25296'
app.config['SESSION_TYPE'] = 'filesystem'

# Configuration
GOOGLE_CLIENT_ID = "894510096466-4a3dofffj91rhea17ibu710r4b6r86no.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "QlPMrROw-GtH0E5DnzZhTHGi"
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

lm = LoginManager(app)
lm.login_view = 'index'
db.init_app(app)

@lm.user_loader
def load_user(id):
    return Guser.query.get(str(id))

client = WebApplicationClient(GOOGLE_CLIENT_ID)

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
    message = ""
    now = dt.datetime.now() #todays date
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

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login")
def login():
    return render_template('login.html')

#user Login
@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    username = request.form.get("username")
    password = request.form.get("password")
    member = Member.query.filter_by(username=username).first()

    #members = Member.query.all()
    if  (username==member.username and password==member.password) or (username=="admin" and password=="123"):
            session['logged_in'] = True
            session['googleuser'] = False
            session['profilepicid'] = member.id
            session['username'] = username
            message= "You are Logged In"
            print(session['profilepicid'])
            return render_template('index.html', message=message)
    flash("Invalid Credentils")
    return render_template('login.html')


#for login session
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        message=""
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            message = "You need to login first"
            return render_template('login.html', message=message)
    return wrap


@app.route("/google_login")
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/google_login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    print(f"Userinfo --{userinfo_response.json()} ")
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        print(users_name)
    else:
        return "User email not available or not verified by Google.", 400
    session['username'] = users_name
    # Create a user in your db with the information provided
    # by Google
    user = Guser.query.get(unique_id)

    # Doesn't exist? Add it to the database.
    if user is None:
        user = Guser(id=unique_id, name=users_name, email=users_email, profile_pic=picture)
        db.session.add(user)
        db.session.commit()
    # Begin user session by logging the user in

    login_user(user)
    session['logged_in'] = True
    session['googleuser'] = True
   #message="Logged in with Google account "
    # Send user back to homepage
    return render_template('index.html', name=user.name, emailid =user.email,profilepic=user.profile_pic)


#for Logout
@app.route("/logout")
@login_required
def logout():
   # loggedingoogleuser=session.get('loggedingoogleuser')
    logout_user()
    session.pop('logged_in', None)
    print(session.get('username'))
 #   print(loggedingoogleuser)
    message = 'You were logged out of Palghar Milers.'
    print(session.get('googleuser'))
    if session.get('googleuser'):
        flash('Logout from Google')
    return render_template('logout.html', message=message)

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
        if username=='admin':
            return render_template("index.html", message="Can Not Use This Username.")
    user=Member(firstname=fname, middlename=mname, lastname=lname, email=email, mobile=mobile, dob=dob, strava_id=strava_id, username=username)

    if user is None:
        return render_template("index.html", message="No Such Member.")

        db.session.add(user)
        db.session.commit()

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
    print(f"uuuuu :{member.username}")
    print(session.get('username'))
    if (member.username == session.get('username')) or (session.get('username') == 'admin'):
        db.session.commit()
    else:
        flash("Cannot update data of other members")
        return redirect('/members')
    db.session.commit()
    return render_template("memberdetails.html", member=member)


# to register new member
@app.route("/removemember", methods=["post", "GET"])
@login_required
def removemember():
    memberid = request.form.get("rmemberid")
    removemember=Member.query.get(memberid)
    print(removemember.username)
    print(session.get('username'))

    if removemember is None:
        return render_template("index.html", message="No Such Member.")
    if (removemember.username == session.get('username')) or (session.get('username')=='admin'):
        db.session.delete(removemember)
        db.session.commit()
        return render_template("index.html", message="Member Successfully Removed")
    flash("Cannot remove other members")
    return redirect('/members')

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
@login_required
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

# Add new Blog
@app.route('/add')
@login_required
def add():
    return render_template('add.html')

@app.route('/addpost', methods=['POST'])
@login_required
def addpost():
    title = request.form['title']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, author=author, content=content, date_posted=dt.datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('blogs'))

#about us
@app.route("/aboutus")
def aboutus():
    return render_template("about.html")

@app.route("/clubdetails/<int:club_id>")
@login_required
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
@login_required
def for_club_data():
    club_id=request.form.get("club_id")
    members = Member.query.order_by(Member.id).all()
    return render_template("forclubdata.html", club_id=club_id,  members=members)

@app.route("/club_data/<int:club_id>",  methods=['GET', 'POST'])
@login_required
def club_data(club_id):
    member_strava_id=request.form.get("strava_member")
    access_token = renew_token()
    str_data_date=request.form.get("data_date")
    print(member_strava_id)
    data_date = dt.datetime.strptime(str_data_date, '%Y-%m-%d')
    fromdateepoch = data_date.timestamp()


    club_activities = "/clubs/"+str(club_id)+"/activities?"
    club_activities_url = base_url + club_activities
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'after':fromdateepoch,'per_page': 200, 'page': 1}
    clubdata = requests.get(club_activities_url, headers=header, params=param).json()
    entries= (len(clubdata))
    print(clubdata)
    return render_template("clubdata.html", clubdata=clubdata, entries=entries, club_id=club_id, member_strava_id=member_strava_id)

@app.route("/club_athlete_data/<int:strava_id>",  methods=['GET', 'POST'])
def club_athlete_data(strava_id):
    print(strava_id)
    return render_template("clubathletestats.html")

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
@login_required
def imagegallery():
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
                flash("Image Uploaded")
            else:
                flash("No Image Selected")
        path, dirs, files = next(os.walk("d:/cs50/workspace/palgharmilers/static/images"))
    else:
         flash("Limit Exceeded")
    image_names = os.listdir('static/images')
    return render_template("imagegallery.html", image_names=image_names)


@app.route("/imagegallery/<filename>")
@login_required
def send_image(filename):
    return send_from_directory('static/images', filename)


@app.route('/deleteimages', methods=['GET', 'POST'])
@login_required
def deleteimages():
    message=""
    if request.method == 'POST':
        print(f"selected images{request.form.getlist('selectedimages')}")
        selectedimages=request.form.getlist('selectedimages')
    members = Member.query.all()
    if session.get('username') == 'admin':
        validmember = True
    else:
        for member in members:
            if (member.username == session.get('username')) :
                validmember=True
            else:
                validmember = False

    for image in selectedimages:

        if os.path.exists(f"static/Images/{image}") and validmember==True:
            print("Path Exist!!!")
            os.remove(f"static/Images/{image}")
            flash("Deleted Selected Images")
        else:
            flash("Error or You may not be member of Palghar Milers")
            print(message)
    image_names = os.listdir('static/images')
    return render_template("imagegallery.html", image_names=image_names)

@app.route('/calendar')
@login_required
def calendar():
    today = dt.datetime.now(dt.timezone.utc)

    try:
        events = Event.query.all()
    except Exception as e:
        print("Error")
        print(e)
    start_date_list=[]
    for event in events:
        start_date_list.append(event.start_date)
    nearestdate=nearest(start_date_list, today)
    if nearestdate:
        nearestevent = Event.query.filter_by(start_date=nearestdate).first()
        nearesteventtitle = nearestevent.title
    else:
        nearesteventtitle = ''
    return render_template('event_calendar.html',events=events,nearestdate=nearestdate, nearesteventtitle=nearesteventtitle)

def nearest(start_date_list, today):
    events=[]
    for i in start_date_list:
        if i>today:
            events.append(i)
    if events:
        latest_event=min([event for event in events], key=lambda x: abs(x - today))
        return latest_event


@app.route('/addEvent',methods=["post"])
@login_required
def addEvent():
    title=request.form.get("event_title")
    start=request.form.get("start_date")
    end=request.form.get("end_date")
    description=request.form.get("event_desciption")
    addevent=Event(title=title, start_date=start, end_date=end, event_description=description)

    db.session.add(addevent)
    db.session.commit()

    return render_template('event_calendar.html')

@app.route("/selectedEvent/<int:event_id>")
@login_required
def selectedEvent(event_id):
    selected_event = Event.query.get(event_id)
    if selected_event is None:
        return render_template("error.html", message="No Such Member.")
    return render_template('events.html', selected_event=selected_event)

#to updates details of existing member
@app.route("/foreditevent",methods=["post","GET"])
@login_required
def foreditevent():
    title = request.form.get("edittitle")
    start = request.form.get("editstartdate")
    end = request.form.get("editenddate")
    description = request.form.get("editdescription")

    try:
        eventid = int(request.form.get("editid"))
    except ValueError:
        return render_template("error.html", message="Invalid member ID.")
    except TypeError:
        return render_template("error.html", message="No Changes Made!")

    event = Event.query.get(eventid)
    event.title=title
    event.start_date=start
    event.end_date=end
    event.event_description=description

    db.session.commit()
    return redirect(url_for("calendar"))


@app.route("/removeEvent", methods=["post", "GET"])
@login_required
def removeEvent():
    eventid = request.form.get("removeeventid")
    removeevent=Event.query.get(eventid)
    if removeevent is None:
        return render_template("error.html", message="No Such Member.")
    db.session.delete(removeevent)
    db.session.commit()
    return render_template("event_calendar.html", message="Member Successfully Removed")
