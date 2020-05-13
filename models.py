import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True)
    firstname=db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    dob=db.Column(db.DateTime)
    t_size=db.Column(db.Integer)
    t_number=db.Column(db.Integer)

class Blogpost(db.Model):
    __tablename__ = "blogposts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
