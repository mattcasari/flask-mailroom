import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donation, Donor, User
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY').encode()
app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/bydonor/', methods=["GET", "POST"])
def donation_by_donor():
    if request.method == "POST":
        try:
            donor = Donor.select().where(Donor.name==request.form['donor']).get()
            donations = Donation.select().join(Donor).where(Donor.name==request.form['donor'])
            for donation in donations:
                print(f'{donation.donor.name=}: {donation.value}')
            return render_template('donor.jinja2', donations=donations)
        except Donor.DoesNotExist:
            error_msg = f'Donor {request.form["donor"]} does not exist'
            return render_template('donor.jinja2', error=error_msg)


    else:
        return render_template('donor.jinja2')

    
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/create/', methods=["GET", "POST"])
def create():
    if "username" not in session:
        return redirect(url_for('login'))
    if request.method == "POST":

        try:
            amount = float(request.form['amount'])
        except ValueError:
            return render_template('create.jinja2', error='Invalid Amount')
        
        try:
            donor = Donor.select().where(Donor.name==request.form['donor']).get()    
        except Donor.DoesNotExist:
            donor = Donor(name=request.form['donor'])
            donor.save()
        
        print(f'{donor.name=}')
        d1 = Donation(donor=donor, value=amount)
        print(f'{d1=}')
        d1.save()
        return redirect(url_for("all"))
    else:
        return render_template('create.jinja2')

@app.route("/login", methods=["GET", "POST"])
def login():
    """[summary]
    If the user is attempting to submit the login form (method is POST)
       Find a user from the database that matches the username provided in the form submission
       If you find such a user and their password matches the provided password:
           Then log the user in by settings session['username'] to the users name
           And redirect the user to the list of all tasks
       Else:
           Render the login.jinja2 template and include an error message
    Else the user is just trying to view the login form
       so render the login.jinja2 template
    Returns:
        template: rendered template or redicect
    """
    error_msg = []
    if request.method == "POST":
        username = request.form["name"]
        pw = request.form["password"]
        try:
            user = User.select().where(User.name == username).get()
            if pbkdf2_sha256.verify(pw, user.password):
                session["username"] = username
                return redirect(url_for("all"))
            else:
                error_msg = "Incorrect password"
        except User.DoesNotExist:
            error_msg = f"Incorrect username: {username}"

    return render_template("login.jinja2", error=error_msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

