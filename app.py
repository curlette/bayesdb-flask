from flask import Flask, request, session, url_for, redirect, send_from_directory
import glob
import os
from werkzeug.utils import secure_filename

from bayesdb_pred_prob import compute_pred_prob

app=Flask(__name__)

app.debug =True

app.secret_key = "P\x11]\xe5\xb6\xf6r=\xc8a\x11O\xcf\x12\xa2W4\x9d\xbfm&\xef6#"

UPLOAD_FOLDER = './tmp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# only allow csvs
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        keys = ['bdb', 'population', 'table', 'column']
        for key in keys:
            if key in request.form.keys() and request.form[key] != '':
                session[key] = request.form[key]
                return redirect(url_for('setup'))
        if 'file' in request.files.keys() and request.files['file'].filename != '':
            # remove old files - only deal with one csv at a time
            files = glob.glob(app.config['UPLOAD_FOLDER'] + '*')
            for f in files:
                os.remove(f)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                session['filename'] = filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('setup'))
    else:
        keys = ['filename', 'bdb', 'population', 'table', 'column']
        for key in keys:
            if key not in session.keys():
                session[key] = ''
        return '''
            <!doctype html>
            <head>
                <link href="./static/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <title><center>Upload an excel file</title>
                <h1><center><br>Anomaly detection with BayesDB</h1>
                <div style="margin: auto; width: 1333px; padding:25px">
                    <div style="float:left; width:300px; padding:25px">
                        <form action="" method=post>
                            <label>Set bdb file name:</label><br>
                            <input type="text" name="bdb">
                            <input type="submit" name="bdb" value="Set">
                            <p>%s</p><br>
                        </form>
                    </div>
                    <div style="float:left; width:300px; padding:25px">
                        <form action="" method=post>
                            <label>Set population name:</label><br>
                            <input type="text" name="population">
                            <input type="submit" name="population" value="Set">
                            <p>%s</p><br>
                        </form>
                    </div>
                    <div style="float:left; width:300px; padding:25px" >
                        <form action="" method=post>
                            <label>Set table name:</label><br>
                            <input type="text" name="table">
                            <input type="submit" name="table" value="Set">
                            <p>%s</p><br>
                        </form>
                    </div>
                    <div style="float:left; width:300px; padding:25px" >
                        <form action="" method=post>
                            <label>Set column name:</label><br>
                            <input type="text" name="column">
                            <input type="submit" name="column" value="Set">
                            <p>%s</p><br>
                        </form>
                    </div>
                </div>
                <br><br>
                <div style="clear:left; margin: auto; width: 400px; table-cell; vertical-align: middle; text-align: center;">
                    <div style="display: inline-block; vertical-align: middle;">
                        <form action="" method=post enctype=multipart/form-data><center><p>
                            <label>Select a csv to upload:</label><br>
                            <input type=file name=file><input type=submit value=Upload>
                            <p>%s</p><br>
                        </form>
                    </div>
                    <div style="display: inline-block; vertical-align: middle;">
                        <form action="/analyze" method=post>
                             <input type=submit value="Analyze data">
                        </form><br>
                    </div style="display: inline-block; vertical-align: middle;">
                    <div style="margin: auto; width: 400px;">
                        <form action="/export" method=post>
                             <input type=submit value="Export result">
                        </form>
                    </div>
                </div>
            </body>
            ''' % ("bdb set to " + session['bdb'] if session['bdb'] != '' else '', "Population set to " + session['population'] if session['population'] != '' else '', "Table set to " + session['table'] if session['table'] != '' else '', "Column set to " + session['column'] if session['column'] != '' else '', "Uploaded " + session['filename'] if session['filename'] != '' else '')

@app.route("/analyze", methods=['POST','GET'])
def analyze():
    # the following call creates a new csv with pred. probs. added
    compute_pred_prob(session['filename'], session['bdb'], session['population'], session['table'], session['column'])
    return redirect(url_for('setup'))

@app.route("/export", methods=['POST','GET'])
def export():
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename='%s_processed.csv' %(os.path.splitext(os.path.basename(session['filename']))[0]), as_attachment=True)

if __name__ == "__main__":
    app.run(host='localhost', port=5000)
