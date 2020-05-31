import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True)
    firstname=db.Column(db.String, nullable=False)
    middlename=db.Column(db.String(20))
    lastname = db.Column(db.String, nullable=False)
    email=db.Column(db.String(355))
    mobile=db.Column(db.Unicode(255), nullable=False)
    dob=db.Column(db.DateTime)
    strava_id= db.Column(db.Integer)
    t_size=db.Column(db.Integer)
    t_number=db.Column(db.Integer)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    password=db.Column(db.String(),nullable=False )
    firstname=db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email=db.Column(db.String(355))
    mobile=db.Column(db.Unicode(255), nullable=False)

class Blogpost(db.Model):
    __tablename__ = "blogposts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)



