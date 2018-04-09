// fabric.Image.filters.threshold = fabric.util.createClass({

//     type: 'threshold',
  
//     /**
//      * Fragment source for the threshold program
//      */
//     fragmentSource: 'precision highp float;\n' +
//       'uniform sampler2D uTexture;\n' +
//       'varying vec2 vTexCoord;\n' +
//       'void main() {\n' +
//         'vec4 color = texture2D(uTexture, vTexCoord);\n' +
//         'color.g = 0;\n' +
//         'color.b = 0;\n' +
//         'gl_FragColor = color;\n' +
//       '}',
  
//     applyTo: function(options) {
//       var imageData = options.imageData,
//           data = imageData.data, i, len = data.length;
  
//       for (i = 0; i < len; i += 4) {
//         data[i + 1] = 0;
//         data[i + 2] = 0;
//         var r = data[i];
//         var g = data[i+1];
//         var b = data[i+2];
//         var v = (0.2126*r + 0.7152*g + 0.0722*b >= 180) ? 255 : 0;
//         data[i] = data[i+1] = data[i+2] = v;
//       }
  
//     }

//   });
  
//   fabric.Image.filters.threshold.fromObject = fabric.Image.filters.BaseFilter.fromObject;

// (function(global) {

//     'use strict';
  
//     var fabric  = global.fabric || (global.fabric = { }),
//         filters = fabric.Image.filters,
//         createClass = fabric.util.createClass;
  
//     /**
//      * threshold filter class
//      * @class fabric.Image.filters.threshold
//      * @memberOf fabric.Image.filters
//      * @extends fabric.Image.filters.BaseFilter
//      * @see {@link fabric.Image.filters.threshold#initialize} for constructor definition
//      * @see {@link http://fabricjs.com/image-filters|ImageFilters demo}
//      * @example
//      * var filter = new fabric.Image.filters.threshold({
//      *   add here an example of how to use your filter
//      * });
//      * object.filters.push(filter);
//      * object.applyFilters();
//      */
//     filters.threshold = createClass(filters.BaseFilter, /** @lends fabric.Image.filters.threshold.prototype */ {
  
//       /**
//        * Filter type
//        * @param {String} type
//        * @default
//        */
//       type: 'threshold',
  
//       /**
//        * Fragment source for the myParameter program
//        */
//       fragmentSource: 'precision highp float;\n' +
//         'uniform sampler2D uTexture;\n' +
//         'uniform float uMyParameter;\n' +
//         'varying vec2 vTexCoord;\n' +
//         'void main() {\n' +
//           'vec4 color = texture2D(uTexture, vTexCoord);\n' +
//           // add your gl code here
//           'gl_FragColor = color;\n' +
//         '}',
  
//       /**
//        * threshold value, from -1 to 1.
//        * translated to -255 to 255 for 2d
//        * 0.0039215686 is the part of 1 that get translated to 1 in 2d
//        * @param {Number} myParameter
//        * @default
//        */
//       myParameter: 0,
  
//       /**
//        * Describe the property that is the filter parameter
//        * @param {String} m
//        * @default
//        */
//       mainParameter: 'myParameter',
  
//       /**
//       * Apply the threshold operation to a Uint8ClampedArray representing the pixels of an image.
//       *
//       * @param {Object} options
//       * @param {ImageData} options.imageData The Uint8ClampedArray to be filtered.
//       */
//       applyTo2d: function(options) {
//         if (this.myParameter === 0) {
//           // early return if the parameter value has a neutral value
//           return;
//         }
//         var imageData = options.imageData,
//             data = imageData.data, i, len = data.length;
//         for (i = 0; i < len; i += 4) {
//           // insert here your code to modify data[i]
//             var r = data[i];
//             var g = data[i+1];
//             var b = data[i+2];
//             var v = (0.2126*r + 0.7152*g + 0.0722*b >= 180) ? 255 : 0;
//             data[i] = data[i+1] = data[i+2] = v;          
//         }
//       },
  
//       /**
//        * Return WebGL uniform locations for this filter's shader.
//        *
//        * @param {WebGLRenderingContext} gl The GL canvas context used to compile this filter's shader.
//        * @param {WebGLShaderProgram} program This filter's compiled shader program.
//        */
//       getUniformLocations: function(gl, program) {
//         return {
//           uMyParameter: gl.getUniformLocation(program, 'uMyParameter'),
//         };
//       },
  
//       /**
//        * Send data from this filter to its shader program's uniforms.
//        *
//        * @param {WebGLRenderingContext} gl The GL canvas context used to compile this filter's shader.
//        * @param {Object} uniformLocations A map of string uniform names to WebGLUniformLocation objects
//        */
//       sendUniformData: function(gl, uniformLocations) {
//         gl.uniform1f(uniformLocations.uMyParameter, this.myParameter);
//       },
//     });
  
//     /**
//      * Returns filter instance from an object representation
//      * @static
//      * @param {Object} object Object to create an instance from
//      * @param {function} [callback] to be invoked after filter creation
//      * @return {fabric.Image.filters.threshold} Instance of fabric.Image.filters.threshold
//      */
//     fabric.Image.filters.threshold.fromObject = fabric.Image.filters.BaseFilter.fromObject;
  
//   })(typeof exports !== 'undefined' ? exports : this);