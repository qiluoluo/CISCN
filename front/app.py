import json

from flask import Flask, render_template, url_for, redirect, request
from flask_wtf.form import FlaskForm
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
import os
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


UPLOAD_PATH = os.getcwd()
CHECK_PATH = os.path.dirname(os.getcwd())
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
        pichead.save(os.path.join(UPLOAD_PATH, "static", "pic", "PIC.jpg"))
        return redirect(url_for("index2"))


@app.route('/main', methods=['GET', 'POST'])
def index2():
    return render_template('databash.html')


@app.route('/predict', methods=['GET', 'POST'])
def pre():
    if request.method == 'GET':
        from backend.model import model
        from backend.predict import predict
        from backend.heatmap import cam
        from backend.windows import windows
        # 例子
        # model_name = 'tsnet-815'
        #
        # training_set = "FF++"
        # # FF++ celeb-df-v2
        # training_forgery_type = "deepfakes"
        # # deepfakes neuraltextures face2face faceshifter faceswap all testdata None
        # training_compression = "c23"
        # # c23 c40 None
        # testing_set = "FF++"
        # # FF++ celeb-df-v2
        # testing_forgery_type = "deepfakes"
        # # deepfakes neuraltextures face2face faceshifter faceswap all testdata None
        # testing_compression = "c23"
        # # c23 c40 None
        # checkpoint_save_path = CHECK_PATH + '/backend/output/checkpoint/{0}_{1}({2})--{3}_{4}({5})/{6}/'.format(training_set,
        #                                                                                     training_forgery_type,
        #                                                                                     training_compression,
        #                                                                                     testing_set,
        #                                                                                     testing_forgery_type,
        #                                                                                     testing_compression,
        #                                                                                     model_name)
        model_name = request.args.get('model_name')

        training_set = request.args.get('model_name')
        # FF++ celeb-df-v2
        training_forgery_type = request.args.get('training_forgery_type')
        # deepfakes neuraltextures face2face faceshifter faceswap all testdata None
        training_compression = request.args.get('training_compression')
        # c23 c40 None
        testing_set = request.args.get('testing_set')
        # FF++ celeb-df-v2
        testing_forgery_type = request.args.get('testing_forgery_type')
        # deepfakes neuraltextures face2face faceshifter faceswap all testdata None
        testing_compression = request.args.get('testing_compression')
        # c23 c40 None
        checkpoint_save_path = CHECK_PATH + '/backend/output/checkpoint/{0}_{1}({2})--{3}_{4}({5})/{6}/'.format(training_set,
                                                                                            training_forgery_type,
                                                                                            training_compression,
                                                                                            testing_set,
                                                                                            testing_forgery_type,
                                                                                            testing_compression,
                                                                                            model_name)
        image_path = os.path.join(UPLOAD_PATH, "static", "pic", "PIC.jpg")
        # 获取模型
        model = model(checkpoint_save_path)
        # 获取预测结果参数
        predict, pred = predict(model, image_path)
        real_rate = "{:.8f}".format(predict.item()*100)
        real = True if pred == 1 else False
        # 获取热力图和自增强图
        save_path = os.path.join(UPLOAD_PATH, "static", "pic")
        cam_pic_path = cam(checkpoint_save_path, image_path, save_path)
        # 获取敏感板块
        win_pic_path = windows(checkpoint_save_path, image_path, save_path)

        info_dict = {}
        info_dict["real_rate"] = real_rate
        info_dict["real"] = real
        info_dict["cam_pic_path"] = cam_pic_path
        info_dict["win_pic_path"] = win_pic_path

        return json.dumps(info_dict, ensure_ascii=False)


if __name__ == '__main__':
    app.run(port=3690, debug=False)
