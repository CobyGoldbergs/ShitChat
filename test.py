from flask import Flask, flash, session, request, url_for, render_template

app = Flask(__name__)

@app.route("/home", methods = ["POST", "GET"])
def home():
    return render_template("home.html")


if __name__=="__main__":
    app.debug = True
    app.run()
