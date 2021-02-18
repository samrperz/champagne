from flask import Flask, render_template, request, redirect, url_for
from flaskext.markdown import Markdown
import pickle
from os import path as os_path, mkdir as os_mkdir, remove as os_remove
from datetime import datetime
import sys, getopt
import boto3
from botocore.config import Config
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

app = Flask("Champagne")
Markdown(app)

noteList = []




#get dynamodb database
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
#table = dynamodb.Table('notes')

#response = dynamodb.scan(TableName='notes')
#notesList = response['Items']
#pp.pprint(notesList)


lastModifiedDate = datetime.now()
lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")

#dynamodb.put_item(TableName='notes', Item={
#    'noteid': {'S': str(time.time())},
#    'title': {'S': 'note1'},
#    'message': {'S': 'hello world!'},
#    'last_modified': {'S': lastModifiedDate}
#})





@app.route("/")
def home():
    response = dynamodb.scan(TableName='notes')
    notesList = response['Items']
    pp.pprint(notesList)
    return render_template("home.html", notes=notesList)

@app.route("/addNote")
def addNote():
    return render_template("noteForm.html", headerLabel="New Note", submitAction="createNote", cancelUrl=url_for('home'))


@app.route("/createNote", methods=["post"])
def createNote():
    noteId = str(time.time())#note id is current time

    lastModifiedDate = datetime.now()
    lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")

    noteTitle = request.form['noteTitle']
    noteMessage = request.form['noteMessage']

    dynamodb.put_item(TableName='notes', Item={
        'noteid': {'S': str(noteId)},
        'title': {'S': noteTitle},
        'message': {'S': noteMessage},
        'last_modified': {'S': lastModifiedDate}
    })
    return redirect(url_for('viewNote', noteId=noteId))# edit note id to be the key for id

@app.route("/viewNote/<string:noteId>")
def viewNote(noteId):
    noteId = noteId

    note = dynamodb.get_item(TableName='notes', Key={'noteid': {'S': noteId}})

    note = note['Item']
    pp.pprint(note)
    
    return render_template("viewNote.html", note=note, submitAction="/saveNote")

@app.route("/editNote/<string:noteId>")
def editNote(noteId):
    noteId = str(noteId)


    note = dynamodb.get_item(TableName='notes', Key={'noteid': {'S': noteId}})
    note = note['Item']

    cancelUrl = url_for('viewNote', noteId=noteId)
    return render_template("noteForm.html", headerLabel="Edit Note", note=note, submitAction="/saveNote", cancelUrl=cancelUrl)

@app.route("/saveNote", methods=["post"])
def saveNote():
    lastModifiedDate = datetime.now()
    lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")

    noteId = str(request.form['noteId'])
    noteTitle = request.form['noteTitle']
    noteMessage = request.form['noteMessage']
    
    note = dynamodb.put_item(TableName='notes', Item={
        'noteid': {'S': noteId}, 
        'title': {'S': noteTitle}, 
        'last_modified': {'S': lastModifiedDate}, 
        'message': {'S': noteMessage}})
    return redirect(url_for('viewNote', noteId=noteId))

@app.route("/deleteNote/<string:noteId>")
def deleteNote(noteId):
    noteId = str(noteId)
    note = dynamodb.delete_item(TableName='notes', Key={'noteid': {'S': noteId}})


    return redirect("/")




if __name__ == "__main__":
    debug = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:", ["debug"])
    except getopt.GetoptError:
        print('usage: main.py [-h 0.0.0.0] [-p 5000] [--debug]')
        sys.exit(2)

    port = "5000"
    host = "0.0.0.0"
    print(opts)
    for opt, arg in opts:
        if opt == '-p':
            port = arg
        elif opt == '-h':
            host = arg
        elif opt == "--debug":
            debug = True

    app.run(host=host, port=port, debug=debug)

