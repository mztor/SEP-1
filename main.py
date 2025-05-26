from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging

import userManagement as dbHandler
import databaseManager as db
import re

# Code snippet for logging a message
# app.logger.critical("message")

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)


# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)


@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("/index.html")

@app.route("/play.html", methods=["POST","GET"])
def play():
    if request.method == "POST":
        # We will get the answer from the form
        answer = request.form["answer"]
        # We will get the original verse from the form
        original_verse = request.form["actual_answer"]

        print(answer, original_verse)
        # We will check if the answer is correct
        if answer == original_verse:
            return render_template("/play.html", game_verse="Correct!", answer=answer)
        else:
            #alert incorrect message and show the same verse again
            print("Incorrect answer")
            return render_template(
                "/play.html",
                game_verse=request.form["game_verse"],
                answer=request.form["answer"],
                alert_message="incorrect"
            )
    # If the request method is GET, we will get a random verse from the database
    # and blank out the longest word in the verse
    og_verse = db.getRandomVerse() #get the verse as a tuple
    game_verse,word = blankOutVerse(og_verse[1])
    # We will return the original verse and the blanked out verse
    print(game_verse,word)
    return render_template("/play.html",game_verse=game_verse, answer=word)

def blankOutVerse(verse):
    #We want to return a blanked out version of the verse
    words = verse.split(" ")
    longest_word = max(words, key=len)
  
    longest_word = re.sub(r'[^\w\s]', '', longest_word)
    print(longest_word)
    # We will blank out the longest word in the verse
    
    blanked_out_verse = verse.replace(longest_word, "_____")
    #blanked_out_verse = verse.replace(longest_word, longest_word[0:2]+"_____" + longest_word[-1])
    return blanked_out_verse, longest_word


@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        return render_template("/form.html")
    else:
        return render_template("/form.html")


# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
