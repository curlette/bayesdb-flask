from flask import Flask, request, session, url_for, redirect, send_from_directory
import glob
import os
from werkzeug.utils import secure_filename

from bayesdb_pred_prob import compute_pred_prob

app=Flask(__name__)

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
        if 'bdb' in request.form.keys() and request.form['bdb'] != '':
            session['bdb'] = request.form['bdb']
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
        if 'filename' not in session.keys():
            session['filename'] = ''
        if 'bdb' not in session.keys():
            session['bdb'] = ''
        return '''
            <!doctype html>
            <title><center>Upload an excel file</title>
            <link href="./static/bootstrap.min.css" rel="stylesheet" media="screen">
            <h1><center><br>Anomaly detection with BayesDB</h1>
            <br><br>
            <form action="" method=post>
                <p><center>Set bdb file name of desired bdb:</p>
                <input type="text" name="bdb">
                <input type="submit" name="bdb" value="Set">
            </form>
            <p><center>%s</p><br>
            <form action="" method=post enctype=multipart/form-data><center><p>
                <p>Select a csv to upload:</p>
                <input type=file name=file><input type=submit value=Upload>
            </form>
            <p><center>%s</p><br>
            <form action="/analyze" method=post>
                 <input type=submit value="Analyze data">
            </form><br>
            <form action="/export" method=post>
                 <input type=submit value="Export result">
            </form>
            ''' % ("bdb set to " + session['bdb'] if session['bdb'] != '' else '', "Uploaded " + session['filename'] if session['filename'] != '' else '')

@app.route("/analyze", methods=['POST','GET'])
def analyze():
    # the following call creates a new csv with pred. probs. added
    compute_pred_prob(session['filename'], session['bdb'])
    return redirect(url_for('setup'))

@app.route("/export", methods=['POST','GET'])
def export():
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename='%s_processed.csv' %(os.path.splitext(os.path.basename(session['filename']))[0]))

if __name__ == "__main__":
    app.run(host='localhost', port=5000)
