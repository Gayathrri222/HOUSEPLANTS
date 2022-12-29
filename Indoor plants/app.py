from flask import Flask, render_template, url_for, request, session, redirect, flash
import ibm_db
import re
import os
import requests
import json

app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30875;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=pfb66196;PWD=qECsMnPTHIopEJZ6", '', '')
print("connected")


@app.route('/')
@app.route('/login', methods=["POST", "GET"])
def login():
    msg = ''

    if request.method == 'POST':
        USERNAME = request.form['username']
        PASSWORD = request.form['password']

        sql = "SELECT * FROM REGISTER WHERE USERNAME = ? AND PASSWORD = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        # print('good')
        if account:
            session['Loggedin'] = True
            session['USERNAME'] = account['USERNAME']
            session['EMAIL'] = account['EMAIL']
            return render_template("home.html")
        else:
            flash("Incorrect username / Password !")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def Register():
    msg = ' '

    if request.method == 'POST':
        USERNAME = request.form['username']
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE USERNAME=? AND PASSWORD=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            msg = 'Account already exists! '
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = ' Invalid email address! '
        elif not re.match(r'[A-Za-z0-9]+', USERNAME):
            msg = ' username must contain only characters and numbers! '
        else:
            insert_sql = " INSERT INTO REGISTER VALUES(?,?,?) "
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, USERNAME)
            ibm_db.bind_param(prep_stmt, 2, EMAIL)
            ibm_db.bind_param(prep_stmt, 3, PASSWORD)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template("login.html", msg=msg)

    return render_template("register.html")


@app.route('/homepage', methods=['GET', 'POST'])
def Home():
    return render_template("home.html")

@app.route('/plant', methods=['GET', 'POST'])
def Plants():
    return render_template("plants.html")

@app.route('/guide', methods=['GET', 'POST'])
def Guides():
    return render_template("guides.html")

@app.route("/output", methods=['GET','POST'])
def output():
    name = request.form['plants']
    #plant name
    print(name) 
    url = "https://house-plants.p.rapidapi.com/common/" + name    
    
    
    headers = {
        "X-RapidAPI-Key": "ad8dd9e205msh1b46ee7d2f5246fp145c0bjsn4f9d4d717193",
        "X-RapidAPI-Host": "house-plants.p.rapidapi.com"
}

    response = requests.request("GET", url, headers=headers)
    
    print(response.text)
    
    output=response.json()
    
    name = ["corralberry", "lipstick"]
    for x in name:
        print(x) 
        
        latinname = output[0]['latin']
        familyname = output[0]['family']
        commonname = output[0]['common']
        categoryname = output[0]['category']
        temp1 = output[0]['tempmax']
        temp2 = output[0]['tempmin']
        light = output[0]['ideallight']
        water = output[0]['watering']
        uses = output[0]['use']
    return render_template("plantsapi.html", latinname= latinname, familyname=familyname, categoryname=categoryname,temp1=temp1,
                           temp2=temp2, light=light, name=commonname, water = water, uses=uses)


@app.route('/plantinfo', methods=['GET', 'POST'])
def plantInfo():
    return render_template('plantsapi.html')

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
