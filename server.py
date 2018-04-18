#import these items for webservice
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen

import json
#import sys
import os
import time
import uuid
import dispatch1

import dispatch1_seg

#listeing http port. default 8000
from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)


# def base64_2_img(_str):
#     img = base64.decodestring(_str)
#     return img

cur_path = os.path.dirname(__file__)
__MODELS__ = os.path.join(cur_path,'./Models/')
#__PAGES__  = os.path.join(cur_path,'./index/') 
__PAGES__  = os.path.join(cur_path,'./index/') 
__IMAGES__ = os.path.join(cur_path,'./images/')

main_poster, user_image_names = [], []
id_list = {"id_list": ["1.id", "2.id", "3.id", "4.id"]}   
id_list = {"id_list": ["1.id"]}   

poster_height = 400
poster_buffer = ['Models/buffer/' + str(uuid.uuid4()) + '.png', poster_height] #[output_path, height]
image_name = []
debug_info = ["", 0]

# classes for smart Ads begin.
class getCurrentPosterHandler(tornado.web.RequestHandler):
    def get(self):        
        global main_poster            
        ret = json.dumps(main_poster, ensure_ascii=False)
        self.write(ret)


class getListHandler(tornado.web.RequestHandler):
    def get(self):
        print 'getListHandler'          
        global id_list    
        ret = json.dumps(id_list, ensure_ascii=False)
        
        self.write(ret)


class getPosterImageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):        
        print 'getPosterImageHandler'
        global poster_buffer, main_poster    
        poster_name = yield tornado.gen.Task(dispatch1.generate_poster, main_poster, poster_buffer)
       
        self.write(poster_name)


class getUserImageHandler(tornado.web.RequestHandler):
    def get(self):
        print 'getUserImageHandler'        
         
        global user_image_names
        user_image_list = {"user_image_list": range(len(user_image_names))}
        
        ret = json.dumps(user_image_list, ensure_ascii=False)
        self.write(ret)


class insertLayerHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print 'insertLayerHandler'
        _user_image_id = self.get_argument('user_image_id')
        _user_layer_index = None

        if self.request.arguments.has_key('layer'):
            _user_layer_index = self.request.arguments['layer'][0]
           
        global main_poster   
        _user_image_name = user_image_names[int(_user_image_id)]
        main_poster = yield tornado.gen.Task(dispatch1.insert_layer, main_poster, _user_image_name, _user_layer_index)
         
        ret = json.dumps(main_poster, ensure_ascii=False)
        self.write(ret)


class loadPosterHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print 'loadPosterHandler'
        _id = self.get_argument('id')

        print self.request
        json_str = yield tornado.gen.Task(dispatch1.load_poster, _id)         
         
        global main_poster
        main_poster = json_str
         
        ret = json.dumps(json_str, ensure_ascii=False)
        self.write(ret)


class modifyLayerHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print 'modifyLayerHandler'
        
        _args = self.request.arguments
        _params = dict([[x, self.get_argument(x)] for x in _args])
           
        global main_poster   
        main_poster = yield tornado.gen.Task(dispatch1.modify_layer, main_poster, _params)
         
        ret = json.dumps(main_poster, ensure_ascii=False)
        self.write(ret)
        
        
class uploadImageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print 'uploadImageHandler'

        if self.request.files.has_key('image'):
            _user_img = self.request.files.get('image')[0]
        else:
            raise NameError('error key words!')

        ret = yield tornado.gen.Task(dispatch1.upload_image, _user_img)
        
        global user_image_names
        user_image_names.append(ret)

        add_image_name = {"add_image_name": ret}
        ret = json.dumps(add_image_name, ensure_ascii=False)
        print ret
        self.write(ret)
# classes for smart Ads end.        

# classes for smart segmentation begin.
class uploadImageHandlerForSeg(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print 'uploadImageHandler'
        print self.request
        if self.request.files.has_key('image'):
            _user_img = self.request.files.get('image')[0]
        else:
            raise NameError('error key words!')
  
        global image_name
        image_name = yield tornado.gen.Task(dispatch1_seg.upload_image, _user_img)     
        
        if image_name :
            add_image_name = {"add_image_name": 'images/user/' + image_name}
            ret = json.dumps(add_image_name, ensure_ascii=False)     
        else:            
            ret = json.dumps({"add_image_name": False}, ensure_ascii=False)
            
        self.write(ret)
        
class sendInteractionHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        print 'sendInteractionHandler'
        print self.request.arguments

        _position = [json.loads(self.get_argument('pos_rect')), json.loads(self.get_argument('pos_m_brush')), \
                     json.loads(self.get_argument('pos_p_brush'))] 
        
        algo_status = self.get_argument('algo_status')      
        
        global debug_info
        if ('init' == algo_status):            
            debug_info = [str(uuid.uuid4()), 0]    
        else:
            debug_info[1] += 1                       
            
        _data_names = [algo_status, self.get_argument('origin_url'), self.get_argument('pkl_name')]     
        ret = yield tornado.gen.Task(dispatch1_seg.send_interaction, _position, _data_names, debug_info)
        print ret
        if ret[0]:
            ret = json.dumps({"status": True, "algo_status": "continue", "rect_out": ret[2], \
                   "show_url": 'images/user/'+ret[1]+'.png', "mask_url": 'images/user/'+ret[1]+'_mask.png', \
                   "pkl_name": 'images/user/'+ret[1]+'_mask.pkl', "sub_masks": ret[3]}, ensure_ascii=False)
        else:
            ret = json.dumps({"status": False ,  "msg": ret[1], 'algo_status': algo_status}, ensure_ascii=False)
         
        print ret  
        self.write(ret)
# classes for smart segmentation end.




#main function
if __name__ == "__main__":
    tornado.options.parse_command_line()
    #app = tornado.web.Application(handlers=[(r"/", IndexHandler)])#create Applicaiton instance
    print 'parse_command_line OK'
    app = tornado.web.Application(
        handlers=[
            (r"/getList",getListHandler),
            (r"/loadPoster", loadPosterHandler),
            (r"/uploadImage", uploadImageHandler),
            (r"/uploadImageForSeg", uploadImageHandlerForSeg), 
            (r"/api/uploadImageForSeg", uploadImageHandlerForSeg),                         
            (r"/getUserImage", getUserImageHandler),   
            (r"/insertLayer", insertLayerHandler),  
            (r"/getCurrentPoster", getCurrentPosterHandler),   
            (r"/getPosterImage", getPosterImageHandler), 
            (r"/modifyLayer", modifyLayerHandler), 
            (r"/uploadImage", uploadImageHandler), 
            (r"/sendInteraction", sendInteractionHandler), 
            (r"/api/sendInteraction", sendInteractionHandler),                         
            (r"/Models/(.*)", tornado.web.StaticFileHandler, {'path': __MODELS__}), #output dir
            (r"/images/(.*)", tornado.web.StaticFileHandler, {'path': __IMAGES__}), #output dir            
            (r"/(.*)",tornado.web.StaticFileHandler,{'path':__PAGES__}),
            # (r"/(.*)",tornado.web.StaticFileHandler,{'path':__PAGES__})            
        ]
    )
    print 'Application OK'

      
    sockets = tornado.netutil.bind_sockets(options.port)
    
  #  sockets.setsockopt(sockets.SOL_SOCKET,sockets.SO_REUSEADDR,1)
    print 'bind_sockets OK'
    #fork it on product
    #tornado.process.fork_processes(0)
    
    http_server = tornado.httpserver.HTTPServer(app)
    print 'HTTPServer OK'
    http_server.add_sockets(sockets)
    print 'add_sockets OK'
    tornado.ioloop.IOLoop.instance().start()
