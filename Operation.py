from pdf2image import convert_from_path
from weasyprint import HTML, CSS
from tqdm import tqdm
from PIL import Image
import numpy as np
import warnings
import pickle
import cv2
import io
import os

warnings.filterwarnings('ignore')

class Operation:
    def __init__(self,outwordpath):

        self.outwordpath = outwordpath
        if os.path.exists(self.outwordpath)==False:
            os.mkdir(self.outwordpath)

        self.padcrop=10;
        self.html_template = f"""
            <html dir="rtl" lang="ar">
            <head>
            <meta charset="utf-8">
            <style>
                @font-face {{
                    font-family: 'Amiri';
                    src: url('FONT_URL');
                }}
                body {{
                    font-family: 'Amiri', serif;
                    background: white;
                    color: black;
                    font-size: FONT_SIZEpx;
                    padding: 10px;
                    width: auto;
                    line-height: 1.8;
                    text-align: justify;
                    margin: 0;
                }}
            </style>
            </head>
            <body>
            WORD_LOCATION
            </body>
            </html>
        """


    def getwords(self,RawText):
        wordsdict={}
        for index,word in enumerate(RawText.split(' ')):
            wordsdict.update({index:word})
        return wordsdict

    def crop(self,image):
        image = np.asarray(image)[:,:,0]
        tps = np.where(image<=30)
        min_x = np.min(tps[0])-self.padcrop; max_x = np.max(tps[0])+self.padcrop;
        min_y = np.min(tps[1])-self.padcrop; max_y = np.max(tps[1])+self.padcrop;
        image_crop = Image.fromarray(image[min_x:max_x,min_y:max_y])
        return image_crop
    
    def takephoto(self,word,id,fontsize,fonturl):
        html_template = self.html_template.replace('WORD_LOCATION',word)
        html_template = html_template.replace('FONT_SIZE',str(fontsize))
        html_template = html_template.replace('FONT_URL',str(fonturl))

        with open("temp.html", "w", encoding="utf-8") as f:
            f.write(html_template )
        #HTML('temp.html').write_pdf('temp.pdf')
        #HTML('temp.html').write_pdf('temp.pdf', stylesheets=[CSS(string='@page { size: A4 landscape; margin: 1cm; }')])
        HTML('temp.html').write_pdf('temp.pdf', stylesheets=[CSS(string='@page { size: 420mm 400mm; margin: 1cm; }')])
        
        pages = convert_from_path("temp.pdf", dpi=300)
        
        image_crop = self.crop(pages[0])
        #outpath = os.path.join(self.outwordpath,str(id),'.png')
        outpath = os.path.join(self.outwordpath, f"{id}.png")
        image_crop.save(outpath, "PNG")

        return outpath

    def gen2img(self,wordsdict,fontsize,fonturl='fonts/arabic_font/122-H_Esfahan.TTF'):
        UniqueWords={}
        id=0;
        for key in wordsdict.keys():
            if wordsdict[key] not in UniqueWords.keys():
                outpath = self.takephoto(wordsdict[key],id,fontsize,fonturl)
                UniqueWords.update({wordsdict[key]:outpath})
                id+=1;
        
    def runphoto(self,file_unqwords,fontsize,fonturl='fonts/arabic_font/122-H_Esfahan.TTF'):
        with open(file_unqwords,'rb') as f:
            words_unq = pickle.load(f)
         
        for key in tqdm(words_unq.keys()):
            outpath = self.takephoto(words_unq[key],key,fontsize,fonturl)

            #break
            #UniqueWords.update({wordsdict[key]:outpath})
