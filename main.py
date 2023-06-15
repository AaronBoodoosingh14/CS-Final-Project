from flask import Flask, render_template, url_for, send_from_directory, send_file, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
from flask_wtf import Form
import sqlite3
import cv2
from steg.LSBSteg import *
from stegano import lsb 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'monkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class FileUploadForm(Form):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("download")

class SteganographyForm(FlaskForm):
    carrier_file = FileField("Carrier Image", validators=[InputRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    message = StringField("Message", validators=[InputRequired()])
    submit = SubmitField("Encrypt and Save")


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SteganographyForm()
    if form.validate_on_submit():
        carrier = form.carrier_file.data
        message = form.message.data

        filename = secure_filename(carrier.filename)
        carrier.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        carrier_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        steg_image = os.path.join(app.config['UPLOAD_FOLDER'], "steg_" + secure_filename(carrier.filename))

        # Encoding
        carrier_image = cv2.imread(carrier_path)
        encoded_image = lsb.hide(carrier_image, message)
        cv2.imwrite(steg_image, encoded_image)

        image_files = os.listdir(app.config['UPLOAD_FOLDER'])
        uploaded_images = []
        for image in image_files:
            uploaded_images.append(url_for('uploaded_file', filename=image))

        return render_template('index.html', form=form, uploaded_images=uploaded_images)

    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    uploaded_images = []
    for image in image_files:
        uploaded_images.append(url_for('uploaded_file', filename=image))

    return render_template('index.html', form=form, uploaded_images=uploaded_images)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/downloads', methods=["GET", "POST"])

def downloads():

    form = FileUploadForm()

    if request.method == "POST":

        conn= sqlite3.connect("YTD.db")
        cursor = conn.cursor()
        print("IN DATABASE FUNCTION ")
        c = cursor.execute(""" SELECT * FROM  my_table """)

        for x in c.fetchall():
            name_v=x[0]
            data_v=x[1]
            break

        conn.commit()
        cursor.close()
        conn.close()

        return send_file(BytesIO(data_v), attachment_filename='flask.pdf', as_attachment=True)

    return render_template("download.html", form=form)


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')





@app.route('/image')
def image_showcase():
    return render_template('image_showcase.html')


@app.route('/decryptor')
def decryptor():
    im = cv2.imread("my_new_image.png")
    steg = LSBSteg(im)
    print("Text value:",steg.decode_text())

    return render_template('decryptor.html')


def database(name, data):
    conn = sqlite3.connect("YTD.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS my_table (name TEXT, data BLOB)""")
    cursor.execute("""INSERT INTO my_table (name, data) VALUES (?, ?)""", (name, data))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
