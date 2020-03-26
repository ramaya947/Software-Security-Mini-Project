from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gatorbank.db"
app.config["SECRET_KEY"] = "ef7d4b36ba2ee50940b99b42a7e39596"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return "User({username})".format(username=self.username)



@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and password:
            if user.password == password:
                return redirect("home")

        flash("Incorrect username or password.")

    return render_template("login.html")

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
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("login")

        flash(error)

    return render_template("register.html")

@app.route("/home")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
