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
            //canvas预览图片，进行抠图操作
            segImage.width = imgWidth * scale;
            segImage.height = imgHeight * scale;
            segImageCtx.drawImage(imgElement, 0, 0, segImage.width, segImage.height);
            
        } else {
            //点击之后添加到中间canvas画布
            //居中功能 tbd.
            var imgInstance = new fabric.Image(imgElement, {
                left: 100,
                top: 100,
            });
            imgInstance.scale(0.3);
            canvas.add(imgInstance); 
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
        var imgFile = this.files[0];
        var fileReader = new FileReader();
        fileReader.readAsDataURL(imgFile);
        fileReader.onload = function(e) {
            var imgSrc = e.target.result;
            //右侧预览区域显示
            var previewHtml = [
                '<div class="upload-item">',
                    '<div class="upload-item-img">',
                        '<img src="' + imgSrc + '" width="100%">',
                        '<img src="' + imgSrc + '" style="display:none">',
                    '</div>',
                    '<div class="upload-item-cover"><div class="upload-item-delete"></div></div>',
                '</div>'
            ].join('');                  
            $('div.upload-list').append(previewHtml);
            // imagesAddEvents();
        }
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

    //抠图的框选功能
    var flag = false;
    var startX = 0;
    var startY = 0;
    var endX = 0;
    var endY = 0;
    segImage.addEventListener('mousedown', function(e) {
        // console.log('startX:', e.offsetX);
        // console.log('startY:', e.offsetY);
        switch(segStatus) {
            case 'region':
                flag = true;
                startX = e.offsetX;
                startY = e.offsetY;
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
                break;
            default:
                break;
        }
    });

    //智能抠图
    $('a#smartSegmentation').on('click', function(e) {
        console.log('startX:', startX);
        console.log('startY:', startY);
        console.log('endX:', endX);
        console.log('endY:', endY);
    });

})