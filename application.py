from functools import wraps

from flask import Flask, render_template, jsonify, request
from sqlalchemy.orm import session

from models import *

from flask import Flask, render_template, request, url_for, redirect, flash, session
import datetime
import csv
import os
from werkzeug.utils import secure_filename
import os.path

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Cyber123@localhost:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


app.secret_key = '25296'
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)
if __name__ == "__main__":
    app.run(debug=True)


UPLOAD_FOLDER = 'd:/cs50/workspace/flasksqlalchemy/static/uploads'
IMAGE_FOLDER = 'd:/cs50/workspace/flasksqlalchemy/static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    now = datetime.datetime.now()
    d = now.day
    m = now.month
    y = now.year
    members = Member.query.all()
    if members is None:
        return render_template("error.html", message="No one has birthday today.")
    birthday_boy=""

    for member in members:
        memberbirthday=str(member.dob)
        member_month=int(memberbirthday[5:7])
        member_date = int(memberbirthday[8:10])
        if d==member_date and m== member_month:
            print(f"first: {member.firstname}")
            birthday_boy += "Happy Birthday,"+member.firstname+"!  "

    return render_template("index.html",birthday_boy=birthday_boy)


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    message = ""
    if request.method == 'POST':
        if (request.form['username'] != 'yad') \
                or request.form['password'] != '123':
            message = 'Invalid Credentials. Please try again.'
            return render_template('login.html', message=message)
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return render_template('index.html', message=message)
    return render_template('login.html', message=message)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            message = "You need to login first"
            return render_template('login.html', message=message)
    return wrap

@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    message = 'You were logged out.'
    return render_template('index.html', message=message)

@app.route("/members")
@login_required
def members():
    members = Member.query.all()
    return render_template("members.html", members=members)

@app.route("/memberdetails/<int:member_id>")
@login_required
def memberdetails(member_id):
    member=Member.query.get(member_id)
    #member=db.execute("SELECT * from members where id = :member_id", {"member_id": member_id}).fetchone()
    if member is None:
        return render_template("error.html", message="No Such Member.")
    return render_template("memberdetails.html", member=member)


@app.route("/registermember",methods=["post","GET"])
@login_required
def registermember():
    fname = request.form.get("memberfname")
    lname = request.form.get("memberlname")
    dob = request.form.get("memberdob")

    member=Member(firstname=fname,lastname=lname,dob=dob)

    db.session.add(member)
    db.session.commit()
    if member is None:
        return render_template("error.html", message="No Such Member.")

    mid=member.id

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ff=f"d:/cs50/workspace/flasksqlalchemy/static/uploads/{filename}"
            print(f"FF{ff}")
            dd=f"d:/cs50/workspace/flasksqlalchemy/static/uploads/{mid}.jpg"
            os.rename(ff,dd)
    return render_template("success.html", message="Member Registered")

@app.route("/forupdatemember",methods=["post","GET"])
@login_required
def forupdatemember():
    fname = request.form.get("updatefname")
    lname = request.form.get("updatelname")
    dob = request.form.get("updatedob")

    try:
        member_id = int(request.form.get("updateid"))
    except ValueError:
        return render_template("error.html", message="Invalid member ID.")
    except TypeError:
        return render_template("error.html", message="No Changes Made!")
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ff=f"d:/cs50/workspace/flasksqlalchemy/static/uploads/{filename}"
            if os.path.exists(f'd:/cs50/workspace/flasksqlalchemy/static/uploads/{member_id}.jpg'):
                os.remove(f'd:/cs50/workspace/flasksqlalchemy/static/uploads/{member_id}.jpg')

            dd = f"d:/cs50/workspace/flasksqlalchemy/static/uploads/{member_id}.jpg"
            os.rename(ff,dd)

    member = Member.query.get(member_id)
    member.firstname=fname
    member.lastname=lname
    member.dob=dob
    db.session.commit()
    return render_template("memberdetails.html", member=member, memberid=member_id)


@app.route("/tshirtsize", methods=["POST"])
@login_required
def tshirtsize():
    tshirtsize = request.form.get("tshirtsize")
    tshirtnumber = request.form.get("tshirtnumber")

    try:
        member_id = int(request.form.get("member_id"))
    except ValueError:
        return render_template("error.html", message="Invalid member ID.")

    member = Member.query.get(member_id)
    if not member:
        return render_template("error.html", message="No such member with that id.")

    member = Member.query.get(member_id)
    member.t_size=tshirtsize
    member.t_number=tshirtnumber
    db.session.commit()

    return render_template("success.html", message="T-Shirt Details Updated.")

@app.route('/blogs')
@login_required
def blogs():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('blogs.html', posts=posts)

@app.route("/aboutus")
def aboutus():
    return render_template("about.html")

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

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


@app.route("/imagegalary",methods=["post","GET"])
@login_required
def imagegalary():
    counter = 0
    file_count=0
    if request.method == 'POST':
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            ff=f"d:/cs50/workspace/flasksqlalchemy/static/images/{filename}"
            while os.path.exists(f"d:/cs50/workspace/flasksqlalchemy/static/images/{counter}.jpg"):
                counter+=1
            dd=f"d:/cs50/workspace/flasksqlalchemy/static/images/{counter}.jpg"
            os.rename(ff,dd)
    path, dirs, files = next(os.walk("d:/cs50/workspace/flasksqlalchemy/static/images"))
    file_count = len(files)
    print(file_count)

    return render_template("imagegalary.html", file_count=file_count)