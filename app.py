from flask import Flask, request, session, url_for, redirect, send_from_directory, render_template
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
        keys = ['bdb', 'population', 'table', 'column', 'filename']
        for key in keys:
            if key not in session.keys():
                session[key] = ''
        bdb_msg = 'bdb set to %s' %(session['bdb']) if session['bdb'] != '' else ''
        population_msg = 'Population set to %s' %(session['population']) if session['population'] != '' else ''
        table_msg = 'Table set to %s' %(session['table']) if session['table'] != '' else ''
        column_msg = 'Column set to %s' %(session['column']) if session['column'] != '' else ''
        upload_msg = 'Uploaded %s' %(session['filename']) if session['filename'] != '' else ''
        return render_template('index.html', bdb_msg=bdb_msg, population_msg=population_msg, table_msg=table_msg, column_msg=column_msg, upload_msg=upload_msg)

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
