(function(global) {

    'use strict';
  
    var fabric  = global.fabric || (global.fabric = { }),
        filters = fabric.Image.filters,
        createClass = fabric.util.createClass;
  
    /**
     * Threshold filter class
     * @class fabric.Image.filters.Threshold
     * @memberOf fabric.Image.filters
     * @extends fabric.Image.filters.BaseFilter
     * @see {@link fabric.Image.filters.Threshold#initialize} for constructor definition
     * @see {@link http://fabricjs.com/image-filters|ImageFilters demo}
     * @example
     * var filter = new fabric.Image.filters.Threshold({
     *   add here an example of how to use your filter
     * });
     * object.filters.push(filter);
     * object.applyFilters();
     */
    filters.Threshold = createClass(filters.BaseFilter, /** @lends fabric.Image.filters.Threshold.prototype */ {
  
      /**
       * Filter type
       * @param {String} type
       * @default
       */
      type: 'Threshold',
  
      /**
       * Fragment source for the myParameter program
       */
      fragmentSource: 'precision highp float;\n' +
        'uniform sampler2D uTexture;\n' +
        'uniform float uMyParameter;\n' +
        'varying vec2 vTexCoord;\n' +
        'void main() {\n' +
          'vec4 color = texture2D(uTexture, vTexCoord);\n' +
          // add your gl code here
          'float v = 0.21 * color.r + 0.72 * color.g + 0.07 * color.b;\n' +
          'v = v > uMyParameter ? 1.0 : 0.0;\n' +
          'gl_FragColor = vec4(v, v, v, color.a);\n' +
        '}',
  
      /**
       * Threshold value, from -1 to 1.
       * translated to -255 to 255 for 2d
       * 0.0039215686 is the part of 1 that get translated to 1 in 2d
       * @param {Number} myParameter
       * @default
       */
      myParameter: 0.6,
  
      /**
       * Describe the property that is the filter parameter
       * @param {String} m
       * @default
       */
      mainParameter: 'myParameter',
  
      /**
      * Apply the Threshold operation to a Uint8ClampedArray representing the pixels of an image.
      *
      * @param {Object} options
      * @param {ImageData} options.imageData The Uint8ClampedArray to be filtered.
      */
      applyTo2d: function(options) {
        if (this.myParameter === 0) {
          // early return if the parameter value has a neutral value
          return;
        }
        var imageData = options.imageData,
            data = imageData.data, i, len = data.length;
        for (i = 0; i < len; i += 4) {
          // insert here your code to modify data[i]
            var r = data[i];
            var g = data[i+1];
            var b = data[i+2];
            var v = (0.2126*r + 0.7152*g + 0.0722*b >= myParameter) ? 255 : 0;
            data[i] = data[i+1] = data[i+2] = v;          
        }
      },
  
      /**
       * Return WebGL uniform locations for this filter's shader.
       *
       * @param {WebGLRenderingContext} gl The GL canvas context used to compile this filter's shader.
       * @param {WebGLShaderProgram} program This filter's compiled shader program.
       */
      getUniformLocations: function(gl, program) {
        return {
          uMyParameter: gl.getUniformLocation(program, 'uMyParameter'),
        };
      },
  
      /**
       * Send data from this filter to its shader program's uniforms.
       *
       * @param {WebGLRenderingContext} gl The GL canvas context used to compile this filter's shader.
       * @param {Object} uniformLocations A map of string uniform names to WebGLUniformLocation objects
       */
      sendUniformData: function(gl, uniformLocations) {
        gl.uniform1f(uniformLocations.uMyParameter, this.myParameter);
      },
    });
  
    /**
     * Returns filter instance from an object representation
     * @static
     * @param {Object} object Object to create an instance from
     * @param {function} [callback] to be invoked after filter creation
     * @return {fabric.Image.filters.Threshold} Instance of fabric.Image.filters.Threshold
     */
    fabric.Image.filters.Threshold.fromObject = fabric.Image.filters.BaseFilter.fromObject;
  
  })(typeof exports !== 'undefined' ? exports : this);

//   (function(global) {

//     'use strict';
  
//     var fabric  = global.fabric || (global.fabric = { }),
//         filters = fabric.Image.filters,
//         createClass = fabric.util.createClass;
  
//     filters.Sobel = createClass(filters.BaseFilter, /** @lends fabric.Image.filters.Threshold.prototype */ {
  
//       type: 'Sobel',
  
//       /**
//        * Fragment source for the myParameter program
//        */
//       fragmentSource: 
//         'precision mediump float;\n' +
//         '#define KERNEL_SIZE 3\n' +
//         'uniform sampler2D u_image;\n' +
//         'uniform vec2 u_textureSize;\n' +
//         // 'uniform float u_kernel[KERNEL_SIZE];\n' +
//         'vec3 u_kernel = vec3(1.0,2.0,1.0);\n' +
//         '#define M_PI 3.1415926535897932384626433832795\n' +
//         '#define GET_PIXEL(_x, _y) (texture2D(u_image, textCoord + onePixel*vec2(_x, _y)))\n' +

//         'void main() {\n' +
//             'vec2 onePixel = vec2(1.0, 1.0) / u_textureSize;\n' +
//             'vec2 textCoord = gl_FragCoord.xy / u_textureSize;\n' +
//             'float dx = (length(GET_PIXEL(-1, -1)*u_kernel[0] + GET_PIXEL(-1,  0)*u_kernel[1] + GET_PIXEL(-1, +1)*u_kernel[2]) - length(GET_PIXEL(+1, -1)*u_kernel[0] + GET_PIXEL(+1,  0)*u_kernel[1] + GET_PIXEL(+1, +1)*u_kernel[2]));\n' +
//             'float dy = (length(GET_PIXEL(-1, -1)*u_kernel[0] + GET_PIXEL(0, -1)*u_kernel[1] + GET_PIXEL(+1, -1)*u_kernel[2]) - length(GET_PIXEL(-1, +1)*u_kernel[0] + GET_PIXEL(0, +1)*u_kernel[1] + GET_PIXEL(+1, +1)*u_kernel[2]));\n' +
//             'float theta = (atan(dy, dx) + M_PI) / (2.0*M_PI);\n' +
//             'gl_FragColor = vec4(length(vec2(dx, dy)), theta, 0.0, 1.0);\n' +
//         '}',
//       myParameter: [1.0, 2.0, 1.0],
  
//       mainParameter: 'myParameter',
  
//       applyTo2d: function(options) {
//         // if (this.myParameter === 0) {
//         //   // early return if the parameter value has a neutral value
//         //   return;
//         // }
//         // var imageData = options.imageData,
//         //     data = imageData.data, i, len = data.length;
//         // for (i = 0; i < len; i += 4) {
//         //   // insert here your code to modify data[i]
//         //     var r = data[i];
//         //     var g = data[i+1];
//         //     var b = data[i+2];
//         //     var v = (0.2126*r + 0.7152*g + 0.0722*b >= myParameter) ? 255 : 0;
//         //     data[i] = data[i+1] = data[i+2] = v;          
//         // }
//       },
  
//       /**
//        * Return WebGL uniform locations for this filter's shader.
//        *
//        * @param {WebGLRenderingContext} gl The GL canvas context used to compile this filter's shader.
//        * @param {WebGLShaderProgram} program This filter's compiled shader program.
//        */
//       getUniformLocations: function(gl, program) {
//         return {
//             u_kernel: gl.getUniformLocation(program, 'u_kernel[0]'),
//         };
//       },
  
//       /**
//        * Send data from this filter to its shader program's uniforms.
//        *
//        * @param {WebGLRenderingContext} gl The GL canvas context used to compile this filter's shader.
//        * @param {Object} uniformLocations A map of string uniform names to WebGLUniformLocation objects
//        */
//       sendUniformData: function(gl, uniformLocations) {
//         gl.uniform1f(uniformLocations.u_kernel, this.myParameter);
//       },
//     });
  
//     fabric.Image.filters.Sobel.fromObject = fabric.Image.filters.BaseFilter.fromObject;
  
//   })(typeof exports !== 'undefined' ? exports : this);

