from pageschema import PageSpec
import numpy as np
import pickle
import cv2
import os
class PAGESETUP:
    def __init__(self,PATH_WORDS_UNQ_ARABIC_WIKI,FOLDER_WORDS_PHOTO,cut_name="A4", font_pt=14, line_factor=1.5, direction="rtl"):

        self.PATH_WORDS_UNQ_ARABIC_WIKI = PATH_WORDS_UNQ_ARABIC_WIKI
        self.FOLDER_WORDS_PHOTO = FOLDER_WORDS_PHOTO

        with open(self.PATH_WORDS_UNQ_ARABIC_WIKI,'rb') as f:
            self.WORDS_UNQ = pickle.load(f)
        self.WORDS_UNQ_KEY={}
        for key in self.WORDS_UNQ.keys():
            self.WORDS_UNQ_KEY.update({self.WORDS_UNQ[key]:key})

       
        #if cut_name=="A4":
        pageconfig = PageSpec(cut_name=cut_name, font_pt=font_pt, line_factor=line_factor, direction=direction)

        self.PAGE_WIDTH      = pageconfig.page_width
        self.PAGE_HEIGHT     = pageconfig.page_height
        self.DISTANCE_LEFT   = pageconfig.margins["left"]
        self.DISTANCE_RIGHT  = pageconfig.margins["right"]
        self.DISTANCE_TOP    = pageconfig.margins["top"]
        self.DISTANCE_BOTTOM = pageconfig.margins["bottom"]
        self.DISTANCE_LINE   = pageconfig.line_spacing


        self.BG_PAGE = (np.ones((self.PAGE_HEIGHT,self.PAGE_WIDTH,3))*255).astype('uint8')
        self.preview_page()

    def preview_page(self):
        
        self.pagepreview = self.BG_PAGE.copy()
        self.point_top        = (self.PAGE_WIDTH//2,self.DISTANCE_TOP)
        self.point_bot        = (self.PAGE_WIDTH//2,self.PAGE_HEIGHT-self.DISTANCE_BOTTOM)
        point_left_top   = (self.PAGE_WIDTH-self.DISTANCE_LEFT,self.DISTANCE_TOP)
        point_left_bot   = (self.PAGE_WIDTH-self.DISTANCE_LEFT,self.PAGE_HEIGHT-self.DISTANCE_BOTTOM)
        point_right_top  = (self.DISTANCE_RIGHT,self.DISTANCE_TOP)
        point_right_bot  = (self.DISTANCE_RIGHT,self.PAGE_HEIGHT-self.DISTANCE_BOTTOM)

        self.pagepreview = self.draw_circle(self.pagepreview,self.point_top,color = (255, 0, 0))
        self.pagepreview = self.draw_circle(self.pagepreview,self.point_bot,color = (255, 0, 0))
        self.pagepreview = self.draw_circle(self.pagepreview,point_left_top,color = (255, 0, 0))
        self.pagepreview = self.draw_circle(self.pagepreview,point_left_bot,color = (255, 0, 0))
        self.pagepreview = self.draw_circle(self.pagepreview,point_right_top,color = (255, 0, 0))
        self.pagepreview = self.draw_circle(self.pagepreview,point_right_bot,color = (255, 0, 0))

        self.content_height = self.point_bot[1] - self.point_top[1]
        self.content_width = point_left_top[0] - point_right_top[0]
        self.Maximum_number_line   = int(np.ceil(self.content_height / self.DISTANCE_LINE))

        self.line_position = {}
        for line in range(0,self.Maximum_number_line):
            
            PY = self.DISTANCE_TOP + (self.DISTANCE_LINE*line)
            p_left   = (self.PAGE_WIDTH-self.DISTANCE_LEFT,PY)
            self.pagepreview = self.draw_circle(self.pagepreview,p_left,color = (255, 255, 0),radius=15)

            p_right   = (self.DISTANCE_RIGHT,PY)
            self.pagepreview = self.draw_circle(self.pagepreview,p_right,color = (255, 0, 255),radius=15)

            self.line_position.update({line+1:{'left':p_left,'right':p_right}})

        print('self.Maximum_number_line',self.Maximum_number_line)
        print(self.line_position)


    #def put_words_on_line(words_sequence):
        



    def pre_process(self,text):
        words = text.strip().split(" ")
        text_dict = {'text':text.strip(),'words':words}
        px=0;words_sequence={}
        for word in words:
            if word in self.WORDS_UNQ_KEY.keys():
                path = self.FOLDER_WORDS_PHOTO+'/'+str(self.WORDS_UNQ_KEY[word])+'.png'

                if os.path.exists(path)==True:
                    
                    iword_img = cv2.imread(path)
                    h,w,_ = iword_img.shape
                    tps = np.where(iword_img[:,:,0]<=30)
                    min_y = np.min(tps[0]); max_y = np.max(tps[0]);
                    min_x = np.min(tps[1]); max_x = np.max(tps[1]);
                    mean_y = int(np.mean(tps[0]))
                    mean_x = int(np.mean(tps[1]))
                    
                    words_sequence.update({px:{'path':path,'word':word,'key':self.WORDS_UNQ_KEY[word],'w':w,'h':h,'min_x':min_x,'min_y':min_y,'max_x':max_x,'max_y':max_y,'mean_x':mean_x,'mean_y':mean_y}})
                    px+=1;

        return words_sequence
        #print(words_sequence)


    def find_word_placement_on_line(self,words_sequence,resize_factor=0.05,minimum_words_distance=7):

        width_words = 0;words_on_line={};temp_words_on_line=[]
        ln=1;width_words_raw=0;
        for ipos in  words_sequence.keys():

            iword     = words_sequence[ipos]['word']
            ipath     = words_sequence[ipos]['path']
            w = words_sequence[ipos]['w']; h = words_sequence[ipos]['h']
            wq = w*resize_factor; hq = h*resize_factor;

            width_words_temp = width_words + wq + minimum_words_distance

            if self.content_width < width_words_temp:

                factor = (len(temp_words_on_line)-1)
                if factor!=0:
                    
                    space = int((self.content_width - width_words_raw) /factor)
                    if space<0:
                        space=0;
                
                words_on_line.update({ln:{'ipos':temp_words_on_line,'space':space}})
                temp_words_on_line=[];
                temp_words_on_line.append(ipos)
                width_words = wq+minimum_words_distance;width_words_raw=wq;
                ln=ln+1;
            else:
                width_words_raw = width_words_raw + wq
                temp_words_on_line.append(ipos)
                width_words = width_words + wq + minimum_words_distance
        if len(temp_words_on_line)>=1:
            words_on_line.update({ln:{'ipos':temp_words_on_line,'space':space}})
        return words_on_line

    def put_word_on_line(self,words_sequence,words_on_line,maximum_words_top=50,resize_factor=0.05):

        current_page = self.BG_PAGE.copy()
        allpage={};page_counter=0;pline=0;
        for line in words_on_line.keys():
            pos=0;
            pline = pline+1
            if (pline-1) >=self.Maximum_number_line:
                pline =1;
                allpage.update({page_counter:current_page})
                current_page = self.BG_PAGE.copy()
                page_counter+=1;
                #continue

            lf1 = self.line_position[pline]['left']
            lf2 = self.line_position[pline]['right']

            space = words_on_line[line]['space']
            ipos_lines = words_on_line[line]['ipos']
            for ipos in ipos_lines:
                
                iword     = words_sequence[ipos]['word']
                ipath     = words_sequence[ipos]['path']

                w = words_sequence[ipos]['w']; h = words_sequence[ipos]['h']
                iword_img  = cv2.imread(ipath)
                iword_imgr = cv2.resize(iword_img, None, fx=resize_factor, fy=resize_factor,interpolation=cv2.INTER_AREA)
                hq,wq,_ = iword_imgr.shape
                mean_y = int(words_sequence[ipos]['mean_y']*resize_factor)

                if pos==0:
                    

                    x1 = lf1[0]-wq; y1 = lf1[1]-hq; x2 = x1+wq;y2 = y1+hq
                    diffy = lf1[1]-maximum_words_top
                    yc = y1+ mean_y
                    diffz = ( yc - diffy)
                    y1 = y1 - ( diffz);
                    y2 = y2 - ( diffz);
                    yc = int((y1+y2)//2)
                else:
                    x1 = wq_last-wq; y1 = lf1[1]-hq; x2 = x1+wq;y2 = y1+hq
                    diffy = lf1[1]-maximum_words_top
                    yc = y1+ mean_y
                    diffz = ( yc - diffy)
                    y1 = y1 - ( diffz);
                    y2 = y2 - ( diffz);


                wq_last = x1-space;
                pos+=1;
                current_page[y1:y2,x1:x2] = iword_imgr

        allpage.update({page_counter:current_page})
        return allpage
    
    def draw_circle(self,image,center_point,color = (255, 0, 0),radius=25):
        center_point= (int(center_point[0]), int(center_point[1]))
        thickness = -1
        cv2.circle(image, center_point, radius, color, thickness)
        return image
