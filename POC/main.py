from flask import Flask ,  render_template , request 
from analyse import analyse
import os
from io import BufferedReader

app = Flask(__name__)

 

@app.route('/')
def tutorialspoint():
    return "Welcome to TutorialsPoint"
@app.route("/uploadPdf",methods=["POST","GET"])
def fileupload():
    if(request.method == "POST"):
        f = request.files["file"]
        if len(request.form) > 0 :
            save = request.form["save"]
            print(save)
            if(save == "True" or save  == "on"):
                f.save("pdfs/"+f.filename)
        f = BufferedReader(f)
        return  analyse(f)
    else:
        return render_template('upload.html')

if __name__ == "__main__" :
    app.run(debug=True,port=5001)