import os, sys, json

from flask import Flask, render_template, request, jsonify

sys.path.append("..")
UPLOAD_PATH = os.getcwd()
CHECK_PATH = os.path.dirname(os.getcwd())
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["SECRET_KEY"] = "ABCDFWA"
app.config["UPLOAD_FOLDER"] = "static/pic"
app.config['UPLOAD_VIDEO_FOLDER']="static/video"


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS2 = {'avi', 'mp4', 'mov', 'wmv'}


# csrf = CSRFProtect(app)
"""
图片上传
"""
@app.route('/')
def picture():
    return render_template('cover.html')


"""
视频上传
"""
@app.route('/video')
def video():
    return render_template('cover2.html')


"""
图片上传处理
"""
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # time.sleep(1000)
    file = request.files.get('file')
    if file:
        if allowed_file(file.filename):
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'msg': 'No file part in the request'})

            file = request.files['file']

            if file.filename == '':
                return jsonify({'status': 'error', 'msg': 'No file selected'})

            if not allowed_file(file.filename):
                return jsonify({'status': 'error', 'msg': 'Invalid file type'})

            # # 获取安全的文件名
            # filename = secure_filename(file.filename)
            #
            # # 生成随机数
            # random_num = random.randint(0, 100)
            # filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + \
            #            filename.rsplit('.', 1)[1]
            file_path = app.config['UPLOAD_FOLDER']

            if not os.path.exists(file_path):
                os.makedirs(file_path)

            file.save(os.path.join(file_path, "PIC.jpg"))
            # 处理上传文件的代码
            return jsonify({'success': True, 'message': '上传成功'})
        else:
            return jsonify({'unsafe': True, 'message': '非法文件'})
    else:
        return jsonify({'success': False, 'message': '未选择文件'})


"""
视频上传处理
"""
@app.route('/upload_video', methods=['POST', 'GET'])
def upload_video():
    file = request.files.get('file')
    if file:
        if allowed_video_file(file.filename):
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'msg': 'No file part in the request'})

            file = request.files['file']

            if file.filename == '':
                return jsonify({'status': 'error', 'msg': 'No file selected'})

            if not allowed_video_file(file.filename):
                return jsonify({'status': 'error', 'msg': 'Invalid file type'})

            # # 获取安全的文件名
            # filename = secure_filename(file.filename)
            #
            # # 生成随机数
            # random_num = random.randint(0, 100)
            # filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + \
            #            filename.rsplit('.', 1)[1]
            file_path = app.config['UPLOAD_VIDEO_FOLDER']

            if not os.path.exists(file_path):
                os.makedirs(file_path)

            file.save(os.path.join(file_path, "PIC.mp4"))
            # 处理上传文件的代码
            return jsonify({'success': True, 'message': '上传成功'})
        else:
            return jsonify({'unsafe': True, 'message': '非法文件'})
    else:
        return jsonify({'success': False, 'message': '未选择文件'})


"""
展示页
"""
@app.route('/display', methods=['GET'])
def display():
    info_dict = json.loads(request.args.get("result"))

    # info_dict = {
    #     "real": "是",
    #     "real_rate": 0.1,
    #     "activation_map": "pic/activation_map.png",
    #     "box_images": ["pic/box_raw_images.png", "pic/box_srm_images.png"],
    #     "heatmap": "pic/heatmap.png",
    #     "raw_images": "pic/raw_images.png",
    #     "win_images": [f'pic/win_images{i}.png' for i in range(0, 6, 1)],
    #     "win_srm": [f'pic/win_srm{i}.png' for i in range(0, 6, 1)]
    # }
    # info_dict = pre()
    """
    info_dict["real_rate"] = real_rate
        info_dict["real"] = real
        info_dict["cam_pic_path"] = cam_pic_path
        info_dict["win_pic_path"] = win_pic_path
    """
    return render_template('databash_new.html', info_dict=info_dict)


"""
预测接口
"""
@app.route('/predict', methods=['GET', 'POST'])
def pre():
    from backend.model import model
    from backend.predict import predict
    from backend.heatmap import heat
    from backend.windows import windows
    from backend.cam import cam
    import cv2

    # 例子
    model_name = 'tsnet-727'

    training_set = "FF++"
    # FF++ celeb-df-v2
    training_forgery_type = "all"
    # deepfakes neuraltextures face2face faceshifter faceswap all testdata None
    training_compression = "c40"
    # c23 c40 None
    testing_set = "DFD"
    # FF++ celeb-df-v2
    testing_forgery_type = "all"
    # deepfakes neuraltextures face2face faceshifter faceswap all testdata None
    testing_compression = "c23"
    # c23 c40 None
    checkpoint_save_path = CHECK_PATH + '/backend/output/checkpoint/{0}_{1}({2})--{3}_{4}({5})/{6}/'.format(
        training_set,
        training_forgery_type,
        training_compression,
        testing_set,
        testing_forgery_type,
        testing_compression,
        model_name)
    data = request.args.get("data")
    data_path = os.path.join(UPLOAD_PATH, "static", "pic", "PIC.jpg")
    if data == "video":
        video_path = os.path.join(UPLOAD_PATH, "static", "video", "PIC.mp4")
        cap = cv2.VideoCapture(video_path)
        while True:
            ret, frame = cap.read()
            if cap.get(cv2.CAP_PROP_POS_FRAMES) == 100:
                cv2.imwrite(data_path, frame)
                break

    # 获取模型
    model = model(checkpoint_save_path)
    # 获取预测结果参数
    predict, pred = predict(model, data_path)
    real_rate = "{:.4f}".format((1 - predict.item()) * 100)
    save_path = os.path.join(UPLOAD_PATH, "static", "pic")
    real = True if pred == 1 else False
    # 获取敏感板块
    windows(data_path, save_path, model)
    # 获取热力图和自增强图
    cam(data_path, save_path, model)
    heat(data_path, save_path, model)
    info_dict = {"real": "是" if real == False else "否", "real_rate": real_rate,
                 "activation_map": "pic/activation_map.png",
                 "box_images": ["pic/box_raw_images.png", "pic/box_srm_images.png"], "heatmap": "pic/heatmap.png",
                 "raw_images": "pic/raw_images.png",
                 "srm_images": "pic/srm_images.png",
                 "win_images": [f'pic/win_images{i}.png' for i in range(0, 6, 1)],
                 "win_srm": [f'pic/win_srm{i}.png' for i in range(0, 6, 1)]}

    # return json.dumps(info_dict, ensure_ascii=False)
    return jsonify(info_dict)


"""
检查上传图片是否在可上传图片允许列表
"""
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


"""
检查上传图片是否在可上传视频允许列表
"""
def allowed_video_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS2



if __name__ == '__main__':
    # pre()
    app.run(host="0.0.0.0", port=3069, debug=True)
