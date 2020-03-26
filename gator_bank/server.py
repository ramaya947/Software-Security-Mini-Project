from flask import Flask, render_template, request, flash, redirect, session, Markup
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import json
from utils.security_functions.functions import get_transactions, search_trans_description_unsafe, search_trans_description_safe, remove_html_tags
from utils.bank_functions.functions import send_money, deposit_money, update_profile_pic, get_contacts, get_contacts_data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gatorbank.db"
app.config["SECRET_KEY"] = "ef7d4b36ba2ee50940b99b42a7e39596"
#sess = Session(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    balance = db.Column(db.Float, default = 0)
    profile_picture = db.Column(db.String(60))
    recent_contact1 = db.Column(db.String(60))
    recent_contact2 = db.Column(db.String(60))
    recent_contact3 = db.Column(db.String(60))
    def __repr__(self):
        return "User(user:{u} pass:{p} balance:{b} profilepic:{pp})".format(u=self.username, p=self.password, b=self.balance, pp=self.profile_picture)



@app.route("/")
def main():
    return redirect("login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    errormsg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and password:
            print(password)
            print (user.password)
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                session['user'] = username
                session['sitetype'] = request.form['sitetype']
                return redirect("home")

        flash("Incorrect username or password.")
        print("Incorrect username or password")
        return render_template("login.html", errormsg="Incorrect username or password")

    return render_template("login.html", errormsg=errormsg)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif User.query.filter_by(username=username).first():
            error = 'User {} is already registered.'.format(username)

        if error is None:
            #Hash, Salt and Pepper
            password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            print(password)

            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("login")

	flash(error)
        print("There was an error")
        return render_template("register.html", errormsg= error)

    return render_template("register.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
    try:
        version = session['sitetype']
        validated = session['user']
       # Get user data
        user_data = User.query.filter_by(username=validated).first()
        user_balance = user_data.balance
        user_profile_pic = user_data.profile_picture
    except:
        #sitetype not found, render the deny_access
        return render_template("deny_access.html")
    if request.method == 'GET':
        if validated:
            transactions = json.dumps(get_transactions(validated))
        
            return render_template("home.html", trans=transactions, user=validated, balance=user_balance, img_url=user_profile_pic)
        else:
            print("You aren't supposed to be here")
    elif request.method == 'POST':
        if validated:
            print("Got to the search functionality");
            term = request.form['transSearch']
            if version == "Unsafe":
                transactions = json.dumps(search_trans_description_unsafe(validated, term))
                return render_template("home_unsafe.html", trans=transactions, user=validated, balance=user_balance, img_url=user_profile_pic, trans_term=term)
            elif version == "Safe":
                transactions = json.dumps(search_trans_description_safe(validated, term))
                term = remove_html_tags(term)
                return render_template("home.html", trans=transactions, user=validated, balance=user_balance, img_url=user_profile_pic, trans_term=term)
        else:
            print("You aren't supposed to be here");
            render_template("deny_access.html")

@app.route("/home-unsafe", methods=["GET", "POST"])
def home_unsafe():
    version = "Unsafe"
    if request.method == 'GET':
        validated = ""
        try:
            validated = session['user']
        except:
            validated = ""
        transactions = json.dumps(get_transactions(validated))
        return render_template("home_unsafe.html", trans=transactions, user=validated)
    elif request.method == 'POST':
        validated = ""
        try:
            validated = session['user']
        except:
            validated = ""
        term = request.form['transSearch']
        transactions = json.dumps(search_trans_description_unsafe(validated, term))
        return render_template("home_unsafe.html", trans=transactions, user=validated)

@app.route("/sendmoney", methods=["GET", "POST"])
def sendmoney():
    version = session['sitetype']
    if request.method == 'GET':
        try:
            validated = session['user']
            args = request.args
            if len(args) == 2 and version == 'Unsafe':
                # Do attack here
                sender = validated
                recipient = args['recipient']
                amount = args['amount']

                updated_sender, updated_recipient = send_money(sender, recipient, amount, User)
                db.session.commit()

            user_data = User.query.filter_by(username=validated).first()
            recent_contacts = get_contacts(user_data)
            recent_contacts_data = get_contacts_data(recent_contacts, User)

            return render_template("send_money.html", user=validated, recent_contacts=recent_contacts_data)
        except:
            return render_template("deny_access.html")
    if request.method == 'POST':
        try: 
            sender = session['user']
            recipient = request.form['recipient']
            amount = request.form['amount']

            updated_sender, updated_recipient = send_money(sender, recipient, amount, User)
            db.session.commit()
            return redirect("home")
        except:
            print("uhhhh")

@app.route("/depositmoney", methods=["GET", "POST"])
def depositmoney():
    if request.method == 'GET':
        try:
            validated = session['user']
            return render_template("deposit_money.html", user=validated)
        except:
            return render_template("deny_acess.html")
    if request.method == 'POST':
        try: 
            user = session['user']
            amount = request.form['amount']
            updated_user = deposit_money(user, amount, User)
            db.session.commit()
            return redirect("home")
        except:
            print("uh oh")

@app.route("/update_pic", methods=["GET", "POST"])
def update_pic():
    if request.method == 'GET':
	    return render_template("update_pic.html")
    if request.method == 'POST':
	try:
	    user = session['user']
	    url = request.form['url']
	    updated_user = update_profile_pic(user, url, User)
	    db.session.commit()
	    return redirect("home")
	except:
	    print("Picture not updated")

@app.route("/signout")
def signout():
        session.clear()
        return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

