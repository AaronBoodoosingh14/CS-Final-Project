from flask import Flask, render_template, url_for, send_from_directory
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Upload File")

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        database(name=file.filename, data=file.read())
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File has been uploaded."

    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    uploaded_images = []
    for image in image_files:
        uploaded_images.append(url_for('uploaded_file', filename=image))

    return render_template('index.html', form=form, uploaded_images=uploaded_images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/image_collection')
def image_collection():
    return render_template('image_collection.html')

def database(name, data):
    conn = sqlite3.connect("YTD.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS my_table (name TEXT, data BLOP)""")
    cursor.execute("""INSERT INTO my_table (name, data) VALUES (?,?)""", (name,data))

    conn.commit()
    cursor.close()
    conn.close()
if __name__ == '__main__':
    app.run(debug=True)
