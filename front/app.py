from flask import Flask, render_template, url_for, redirect, request
from flask_wtf.form import FlaskForm
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
import os
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

UPLOAD_PATH = os.getcwd()
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["SECRET_KEY"] = "ABCDFWA"
csrf = CSRFProtect(app)


class UploadData(FlaskForm):
    photo = FileField(label='图片上传', validators=[FileRequired(), FileAllowed(['jpg', 'png'])])
    submit = SubmitField("提交")


@app.route('/', methods=['GET', 'POST'])
def index():  # 主页面
    x = UploadData()
    if request.method == "GET":
        return render_template("cover.html", up=x)
    else:
        pichead = x.photo.data
        filename = secure_filename('PIC')
        pichead.save(os.path.join(UPLOAD_PATH, filename))
        return redirect(url_for("index2"))


@app.route('/main', methods=['GET', 'POST'])
def index2():
    return render_template('databash.html')


if __name__ == '__main__':
    app.run(port=3690, debug=False)
