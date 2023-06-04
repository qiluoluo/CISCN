var dropZone = document.getElementById('drop_zone');

dropZone.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', function(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', function(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');

    var files = e.dataTransfer.files;
    var formData = new FormData();
    formData.append('file', files[0]);

    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
            var percentComplete = Math.round((e.loaded / e.total) * 100);
            document.getElementById('progress-bar').value = percentComplete;
        }
    });

    xhr.open('POST', '/upload', true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var responseData = JSON.parse(xhr.responseText);
            if (responseData.success) {
                console.log('File uploaded successfully.');

                // 隐藏进度条
                document.getElementById('progress-bar').style.display = 'none';

                // 显示上传成功的消息
                // document.getElementById('file-list').innerHTML += files[0].name + "上传成功" + '<br>';
                document.getElementById('preview').src = URL.createObjectURL(files[0]);

                // 显示扫描状态
                var scanStatus = document.getElementById('scan-status');
                scanStatus.innerHTML = '正在扫描...';

                var previewImg = document.getElementById('preview');
                previewImg.src = URL.createObjectURL(files[0]);

                // 获取图像宽度并设置扫描线宽度
                previewImg.onload = function() {
                    var scanLine = document.querySelector('.scan-line');
                    scanLine.style.width = (previewImg.offsetWidth + 10) + "px"; // 偏移量为10像素
                }




                // 添加扫描特效
                var scanner = document.createElement('div');
                scanner.classList.add('scanner');
                document.getElementById('drop_zone').appendChild(scanner);

                // 扫描完成后添加残影效果
                // var scanLine = document.querySelector('.scan-line');
                // scanLine.classList.add('scan-line-after');
                // setTimeout(function() {
                //   scanLine.classList.remove('scan-line-after');
                // }, 1000); // 1秒后移除.scan-line-after

                var xhr2 = new XMLHttpRequest();
                xhr2.open('GET', '/predict?data=picture', true);
                xhr2.onload = function() {
                    // 在这里执行相应的操作
                    scanStatus.innerHTML = '扫描完成';
                    scanner.style.display = 'none';
                    // 存储预测结果
                    var predictionResult = JSON.parse(xhr2.responseText);

                    // 将预测结果作为URL参数传递到/display页面
                    window.location.href = '/display?result=' + encodeURIComponent(JSON.stringify(predictionResult));
                };
                xhr2.send()

            } else {
                console.log('File upload failed.');
                alert(files[0].name + "上传失败：" + responseData.message);
            }
        }
    };

    // 隐藏进度条和扫描条
    document.getElementById('progress-bar').style.display = 'none';


    xhr.send(formData);
});
