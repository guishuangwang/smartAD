$(function() {
    var canvas = new fabric.Canvas('smartAdCanvas');
    // canvas.backgroundColor = 'rgb(220,220,220)';
    var nativeCanvas = document.getElementById('smartAdCanvas');
    var segImage = document.getElementById('segmentationImagePreview');
    var segImageCtx = segImage.getContext('2d');
    var segResult = document.getElementById('segmentationResult');
    var segResultCtx = segResult.getContext('2d');
    var imgElement; //当前点击的图片对象
    var scale; //抠图图片的缩放尺度
    var segStatus = ''; //抠图的功能
    var segImgUrl = ''; //抠图的原图地址
    var segRectOut; //抠图接口返回的框，用来裁剪canvas区域
    var imgData1; //保存交互操作前的原图data

    //初始化颜色选择器
    $('.colorPicker').colpick({
        layout: 'hex',
        submit: 0,
        colorScheme: 'dark',
        onChange: function (hsb, hex, rgb, el, bySetColor) {
            $(el).css('border-color', '#' + hex);
            // Fill the text box just if the color was set using the picker, and not the colpickSetColor function.
            if (!bySetColor) $(el).val(hex);
            console.log('color is: ', this.value);
        }
    }).keyup(function () {
        $(this).colpickSetColor(this.value);
        console.log('color is:', this.value)
    });
    // //add rect.
    // var rect = new fabric.Rect({
    //     top: 100,
    //     left: 100,
    //     width: 60,
    //     height: 70,
    //     fill: 'red'
    // });
    // //add circle.
    // var circle = new fabric.Circle({
    //     radius: 20,
    //     fill: 'green',
    //     left: 300,
    //     top: 300,
    // })
    // canvas.add(rect, circle);
    // //add images.
    // fabric.Image.fromURL('../images/girl.jpg', function(oImg) {
    //     // oImg.scale(0.5).set('flipX', true);
    //     oImg.scale(0.3)
    //         .set({
    //         left: 400,
    //         top: 400
    //         });
    //     canvas.add(oImg);
    // });
    // //add text.
    // var text = new fabric.IText('hello world', {
    //     left: 200,
    //     top: 50
    // });
    // canvas.add(text);
    // //customization.
    // canvas.item(0).set({
    //     borderColor: 'gray',
    //     cornerColor: 'black',
    //     cornerSize: 12,
    //     transparentCorners: true
    // });

    // //interaction.
    // canvas.on('mouse:down', function(options) {
    //     console.log(options.e.clientX, options.e.clientY);
    // });
    // rect.on('selected', function(){
    //     console.log('selected a rectangle');
    // });
    // circle.on('selected', function() {
    //     console.log('selected a circle');
    // });
    // canvas.on('after:render', function() {
    //     canvas.forEachObject(function(obj) {
    //         var bound = obj.getBoundingRect();
    //         console.log('left: ' + bound.left + ' top: '+ bound.top);
    //     });
    // });

    //add event listens.
    //左侧功能栏切换
    $('#nav-wrapper a').on('click', function(e) {
        $(this).addClass('active');
        $(this).siblings().removeClass('active');
        var toolBarId = $(this).attr('data-target');
        $('div#toolbar').children('.toolbar').hide();
        $('div#toolbar').find('div#' + toolBarId).show();
        if(toolBarId === 'toolbar-segmentation') {
            $('div#segmentationImage').show();
            $('div#canvas').hide();
        } else{
            $('div#segmentationImage').hide();
            $('div#canvas').show();         
        }
    });
    //判断当前是否选中了抠图
    function isSelectSegmentation() {
        return $('#nav-wrapper a.active').attr('data-target') === 'toolbar-segmentation' ? true : false;
    }

    //右侧panel 展开控制
    $('#panel-show-hide-btn').on('click', function(e) {
        if($('#panel').hasClass('show')){
            $('#panel').removeClass('show');
        } else {
            $('#panel').addClass('show');
        }
    });

    //事件委托处理动态添加dom
    $('div.upload-list').on('mouseover', '.upload-item', function(e) {
        //图片鼠标滑过效果    
        $(this).find('.upload-item-cover').show();
    });
    $('div.upload-list').on('mouseleave', '.upload-item', function(e) {
        //图片鼠标滑过效果    
        $(this).find('.upload-item-cover').hide();
    });    
    $('div.upload-list').on('click', '.upload-item-delete', function(e) {
        //删除预览图片  
        $(this).parents('div.upload-item').remove();
        e.stopPropagation();
    });     
    $('div.upload-list').on('click', '.upload-item', function(e) {
        imgElement = $(this).find('img')[1];
        var imgWidth = imgElement.width;
        var imgHeight = imgElement.height;
        var maxSize = 400;
        scale = imgWidth > imgHeight ? maxSize/imgWidth : maxSize/imgHeight;
        //判断是否选中了抠图
        if(isSelectSegmentation()) {
            segImgUrl = $(imgElement).attr('data-url') || '';
            //canvas预览图片，进行抠图操作
            segImage.width = imgWidth * scale;
            segImage.height = imgHeight * scale;
            segImageCtx.drawImage(imgElement, 0, 0, segImage.width, segImage.height);
            imgData1 = segImageCtx.getImageData(0, 0, segImage.width, segImage.height);
            segPush();
            //动态调整结果canvas的宽高，箭头的位置，预览canvas的位置
            segResult.width = segImage.width;
            segResult.height = segImage.height;
            $('img#segArrow').css('top', 120 + segImage.height/2);
            $('canvas#segmentationImagePreview').css('left', 450 - segImage.width);
        } else {
            //点击之后添加到中间canvas画布
            //居中功能 tbd.
            var imgInstance = new fabric.Image(imgElement, {
                left: 100,
                top: 100,
            });
            imgInstance.scale(0.3);
            canvas.add(imgInstance); 
            adPush();
        }
    });

    //打开图片文件
    $('div.add-btn').on('click', function(e) {
        $('#editorFileInput').trigger('click');
    });
    $('a#header-toolbar-openFile').on('click', function(e) {
        e && e.preventDefault();
        $('#editorFileInput').trigger('click');
    });
    //input file 选择了图片
    $('#editorFileInput').on('change', function(e) {
        var that = this;
        var imgFile = that.files[0];
        // var fileReader = new FileReader();
        // fileReader.readAsDataURL(imgFile);
        // fileReader.onload = function(e) {
        //     var imgSrc = e.target.result;
        //     //右侧预览区域显示
        //     var previewHtml = [
        //         '<div class="upload-item">',
        //             '<div class="upload-item-img">',
        //                 '<img src="' + imgSrc + '" width="100%" data-url="'+ segImgUrl + '">',
        //                 '<img src="' + imgSrc + '" style="display:none" data-url="'+ segImgUrl + '">',
        //             '</div>',
        //             '<div class="upload-item-cover"><div class="upload-item-delete"></div></div>',
        //         '</div>'
        //     ].join('');                  
        //     $('div.upload-list').append(previewHtml);
        // }

        //上传文件到服务器获取图片地址
        var formData = new FormData();
        formData.append('image', imgFile);
        $.ajax({
            type: "post",
            url: "/api/uploadImageForSeg",
            data: formData,
            // dataType: "dataType",
            contentType: false,
            processData: false,
            success: function (response) {
                console.log(response);
                var imgURL = JSON.parse(response).add_image_name || '';
                var previewHtml = [
                    '<div class="upload-item">',
                        '<div class="upload-item-img">',
                            '<img src="' + imgURL + '" width="100%" data-url="'+ imgURL + '">',
                            '<img src="' + imgURL + '" style="display:none" data-url="'+ imgURL + '">',
                        '</div>',
                        '<div class="upload-item-cover"><div class="upload-item-delete"></div></div>',
                    '</div>'
                ].join('');                  
                $('div.upload-list').append(previewHtml);
            }
        });
        
    });
    //删除选中对象
    $('a#header-toolbar-delete').on('click', function(e) {
        e && e.preventDefault();
        if(canvas && canvas.getActiveObject()) {
            var activeObj = canvas.getActiveObject();
            canvas.remove(activeObj);
        } else {
            new Noty({
                text: '请先选择对象',
                // layout: 'topCenter',
                type: 'error',
                timeout: 1000
            }).show();
        }
    });
    //删除所有图片
    $('a#trash-box').on('click', function(e) {
        e && e.preventDefault();
        $('div.upload-list').empty();
    });

    //保存canvas图片 
    $('a#header-toolbar-save').on('click', function(e) {
        var fileName = '智能广告_' + (new Date()).getTime();
        //这里宽高直接取nativeCanvas属性会出现下载失败，感觉是fabric添加的元素宽高有关
        Canvas2Image.saveAsPNG(nativeCanvas, 1090, 811, fileName);
    });     

    //添加文字
    $('div.toolbar-list p#addTextToCanvas span').on('click', function(e) {
        //add text.
        var txt = $('input#typeText').val();
        var fontSize = $('input#fontSize').val();
        var fontColor = '#' + $('input#pickerFont').val();
        var bgColor = '#' + $('input#pickerBG').val();
        var text = new fabric.IText(txt, {
            left: 200,
            top: 50,
            fontFamily: 'Comic Sans',
            fontSize: fontSize,
            fill: fontColor,
            textBackgroundColor: bgColor
            // stroke: color,
            // strokeWidth: 1
            // textAlign: 'right'
            // fontStyle: 'italic',
            // shadow: 'rgba(0,0,0,0.3) 5px 5px 5px'
            // underline; true
            // linethrough: true
            // overline: true
            // fontWeight: 'bold'
            // fontWeight: 'normal'
        });
        canvas.add(text);
    });

    //滤镜图片预览
    $('div.image-effect-preview').on('mouseover', function(e) {
        // $(this).find('div.image-effect-tips').css('bottom', '0');
        $(this).find('div.image-effect-tips').show();
    });
    $('div.image-effect-preview').on('mouseout', function(e) {
        // $(this).find('div.image-effect-tips').css('bottom', '-40px');
        $(this).find('div.image-effect-tips').hide();
    });   
    $('div.image-effect-preview').on('click', function(e) {
        //为了选中的图片应用filter
        var activeObj = canvas && canvas.getActiveObject();
        var effectType = $(this).attr('data-effect');
        if(activeObj && activeObj instanceof fabric.Image) {
            switch(effectType) {
                case 'grayscale':
                    activeObj.filters.push(new fabric.Image.filters.Grayscale());
                    break;
                case 'brightness':
                    activeObj.filters.push(new fabric.Image.filters.Brightness({brightness: 0.05}));               
                    break;
                case 'threshold':
                    activeObj.filters.push(new fabric.Image.filters.Threshold());            
                    break;
                // case 'sobel':
                //     activeObj.filters.push(new fabric.Image.filters.Sobel());            
                // break;                    
                case 'sharpen':
                    activeObj.filters.push(new fabric.Image.filters.Convolute({
                        matrix: [ 0, -1,  0,
                                -1,  5, -1,
                                0, -1,  0 ]
                    }));               
                    break;
                case 'Emboss':
                    activeObj.filters.push(new fabric.Image.filters.Convolute({
                        matrix: [ 1, 1, 1,
                            1, 0.7, -1,
                           -1,  -1, -1 ]
                    }));               
                    break;                    
                case 'sepia':
                    activeObj.filters.push(new fabric.Image.filters.Sepia());               
                    break;
                case 'blur':
                    activeObj.filters.push(new fabric.Image.filters.Blur({blur: 0.5}));               
                    break;                    
                default:
                    break;
            }
            activeObj.applyFilters();
            canvas.remove(activeObj);
            canvas.add(activeObj);
        } else {
            new Noty({
                text: '请先选择图片',
                // layout: 'topCenter',
                type: 'warning',
                timeout: 1000
            }).show();
        }
    }); 
    
    //点击模板 渲染模板
    $('div.template-item').on('click', function(e) {
        //clear canvas and load from JSON file
        var jsonFileUrl = $(this).attr('data-json');
        canvas.clear();
        $.getJSON(jsonFileUrl, function (data, textStatus, jqXHR) {
            // console.log(data);
            // JSON string or object
            // canvas.loadFromJSON(JSON.stringify(data));
            canvas.loadFromJSON(data);
        });
    });

    //清空抠图的画布
    $('div#segmentationReset').on('click', function(e) {
        segImageCtx.clearRect(0, 0, segImage.width, segImage.height);
        segResultCtx.clearRect(0, 0, segResult.width, segResult.height);
    });

    //抠图功能按钮点击
    $('div.segmentationInteraction').on('click', function(e) {
        $(this).addClass('activeFunc');
        $(this).siblings('.segmentationInteraction').removeClass('activeFunc');
        segStatus = $(this).attr('data-func');
    });

    //抠图的框选功能 & 画笔功能
    var flag = false;
    var startX = 0;
    var startY = 0;
    var endX = 0;
    var endY = 0;
    var foregroundBrushArray = []; //抠图前景数组
    var backgroundBrushArray = []; //抠图背景数组
    segImage.addEventListener('mousedown', function(e) {
        // console.log('startX:', e.offsetX);
        // console.log('startY:', e.offsetY);
        switch(segStatus) {
            case 'region':
                flag = true;
                startX = e.offsetX;
                startY = e.offsetY;
                break;
            case 'foregroundBrush':
                flag = true;
                foregroundBrushArray = [];
                foregroundBrushArray.push(-4, scale, e.offsetX, e.offsetY);
                break;
            case 'backgroundBrush':
                flag = true;
                backgroundBrushArray = [];
                backgroundBrushArray.push(-4, scale, e.offsetX, e.offsetY);
                break;                
            default:
                break;
        }

    });
    segImage.addEventListener('mousemove', function(e) {
        // console.log('e.offsetX:', e.offsetX);
        // console.log('e.offsetY:', e.offsetY); 
        switch(segStatus) {
            case 'region':
                if(flag) {
                    segImageCtx.clearRect(0, 0, segImage.width, segImage.height);
                    segImageCtx.drawImage(imgElement, 0, 0, segImage.width, segImage.height);
                    segImageCtx.strokeRect(startX, startY, e.offsetX - startX, e.offsetY - startY);
        
                }
                break;
            case 'foregroundBrush':
                if(flag) {
                    foregroundBrushArray.push(e.offsetX, e.offsetY);
                    brushPaint(foregroundBrushArray, 'blue');
                }
                break;
            case 'backgroundBrush':
                if(flag) {
                    backgroundBrushArray.push(e.offsetX, e.offsetY);
                    brushPaint(backgroundBrushArray, 'red');
                }
                break;
            default:
                break;
        }

    });
    segImage.addEventListener('mouseup', function(e) {
        // console.log('endX:', endX);
        // console.log('endY:', endY);
        switch(segStatus) {
            case 'region':
                flag = false;
                endX = e.offsetX;
                endY = e.offsetY;
                segPush();
                break;
            case 'foregroundBrush':
            case 'backgroundBrush':
                flag = false;
                segPush();
                break;
            default:
                break;
        }
    });

    //画笔功能
    function brushPaint(arr, brushColor) {
        segImageCtx.strokeStyle = brushColor;
        segImageCtx.lineWidth = 4;
        var pointArr = arr.slice(2);
        if(pointArr.length >= 4) {
            segImageCtx.beginPath();
            for(var i = 0; i < pointArr.length - 2; i += 2) {
                segImageCtx.moveTo(pointArr[i], pointArr[i+1]);
                segImageCtx.lineTo(pointArr[i+2], pointArr[i+3]);
            }
            segImageCtx.closePath();
            segImageCtx.stroke();
        }
    }

    //智能抠图
    $('a#smartSegmentation').on('click', function(e) {
        console.log('startX:', startX);
        console.log('startY:', startY);
        console.log('endX:', endX);
        console.log('endY:', endY);
        var segTips = new Noty({
            text: '智能计算中，请稍等。。。',
            layout: 'topCenter',
            type: 'information',
            // timeout: 1000
        }).show();
        var data = {
            origin_url: segImgUrl, //上传图片返回的URL
            pkl_name: '',
            algo_status: 'init',
            pos_rect: segStatus === 'region' ? JSON.stringify([startX, startY, endX, endY, scale]) : JSON.stringify([]),
            pos_p_brush: segStatus === 'region' ? JSON.stringify([]) : JSON.stringify(foregroundBrushArray), //前景 
            pos_m_brush: segStatus === 'region' ? JSON.stringify([]) : JSON.stringify(backgroundBrushArray), //背景
        };
        $.ajax({
            type: "post",
            url: "/api/sendInteraction",
            data: data,
            // dataType: "dataType",
            success: function (response) {
                console.log(response);
                var resObj = JSON.parse(response);
                //写死图片服务地址
                var maskUrl = resObj.mask_url;
                segRectOut = resObj.rect_out;
                var img = new Image();
                img.src = maskUrl;
                img.onload = function() {
                    var imgWidth = img.width;
                    var imgHeight = img.height;
                    var maxSize = 400;
                    scale = imgWidth > imgHeight ? maxSize/imgWidth : maxSize/imgHeight;
                    //canvas预览图片，进行抠图操作
                    segResult.width = imgWidth * scale;
                    segResult.height = imgHeight * scale;
                    segResultCtx.drawImage(img, 0, 0, segResult.width, segResult.height);

                    //对原图和mask进行处理，产生抠图的效果
                    //注意：原图进行框选或者画笔交互之后，ImageData会变，所以这里的imgData1 应该提前获取
                    // var imgData1 = segImageCtx.getImageData(0, 0, segImage.width, segImage.height);
                    var imgData2 = segResultCtx.getImageData(0, 0, segResult.width, segResult.height); // canvas 跨域问题。。。
                    for(var i = 0; i < imgData2.data.length; i += 4) {
                        imgData1.data[i + 3] = imgData2.data[i];
                    }
                    segResultCtx.putImageData(imgData1, 0, 0);
                    segTips.close();
                }
            }
        });
    });

    //输出到广告
    $('a#exportSegToAD').on('click', function(e) {
        //新建一个隐藏的抠图区域canvas
        var hiddenCanvas = document.createElement('canvas');
        var hiddenCanvasCtx = hiddenCanvas.getContext('2d');
        // hiddenCanvas.width = endX - startX;
        // hiddenCanvas.height = endY - startY;
        // var resultImgData = segResultCtx.getImageData(startX, startY, hiddenCanvas.width, hiddenCanvas.height);
        //根据接口返回的rect来进行裁剪canvas区域
        hiddenCanvas.width = segRectOut[2] * scale;
        hiddenCanvas.height = segRectOut[3] * scale;
        var resultImgData = segResultCtx.getImageData(segRectOut[0] * scale, segRectOut[1] * scale, hiddenCanvas.width, hiddenCanvas.height);
        hiddenCanvasCtx.putImageData(resultImgData, 0, 0);
        var image = new Image();
        image.src = hiddenCanvas.toDataURL('image/png');
        image.onload = function() {
            var imgInstance = new fabric.Image(image, {
                left: 100,
                top: 100,
            });
            canvas.add(imgInstance); 
        }
    });

    //undo & redo
    //抠图部分
    var segPushArray = new Array(); // 保存抠图canvas快照
    var segStep = -1;
    function segPush() {
        segStep++;
        if(segPushArray.length > segStep) {
            segPushArray.length = segStep;
        }
        segPushArray.push(segImage.toDataURL());

    }
    function segUndo() {
        if(segStep > 0) {
            segStep--;
            var tmpImg = new Image();
            tmpImg.src = segPushArray[segStep];
            tmpImg.onload = function() {
                segImageCtx.drawImage(tmpImg, 0, 0);
            }
        }
    }
    function segRedo() {
        if(segStep < segPushArray.length - 1) {
            segStep++;
            var tmpImg = new Image();
            tmpImg.src = segPushArray[segStep];
            tmpImg.onload = function() {
                segImageCtx.drawImage(tmpImg, 0, 0);
            }
        }
    }
    //广告部分
    var adPushArray = new Array(); //保存广告canvas快照
    var adStep = -1;
    function adPush() {
        adStep++;
        if(adPushArray.length > adStep) {
            adPushArray.length = adStep;
        }
        adPushArray.push(nativeCanvas.toDataURL());
    }
    function adUndo() {
        if(adStep > 0) {
            adStep--;
            var tmpImg = new Image();
            tmpImg.src = adPushArray[adStep];
            tmpImg.onload = function() {
                nativeCanvas.getContext('2d').drawImage(tmpImg, 0, 0);
            }
        }
    }
    function adRedo() {
        if(adStep < adPushArray.length - 1) {
            adStep++;
            var tmpImg = new Image();
            tmpImg.src = adPushArray[adStep];
            tmpImg.onload = function() {
                nativeCanvas.getContext('2d').drawImage(tmpImg, 0, 0);
            }
        }
    }
    $('a#header-toolbar-undo').on('click', function(e) {
        if(isSelectSegmentation()) {
            segUndo();
        }else {
            adUndo();
        }
    });
    $('a#header-toolbar-redo').on('click', function(e) {
        if(isSelectSegmentation()) {
            segRedo();
        }else {
            adRedo();
        }        
    });
})