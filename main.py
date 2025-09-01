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
import argparse
import sys

warnings.filterwarnings('ignore')

class Operation:
    def __init__(self, outwordpath):
        self.outwordpath = outwordpath
        if not os.path.exists(self.outwordpath):
            os.makedirs(self.outwordpath, exist_ok=True)

        self.padcrop = 10
        self.html_template = """
            <html dir="rtl" lang="ar">
            <head>
            <meta charset="utf-8">
            <style>
                @font-face {{
                    font-family: 'Amiri';
                    src: url('{font_url}');
                }}
                body {{
                    font-family: 'Amiri', serif;
                    background: white;
                    color: black;
                    font-size: {font_size}px;
                    padding: 10px;
                    width: auto;
                    line-height: 1.8;
                    text-align: justify;
                    margin: 0;
                }}
            </style>
            </head>
            <body>
            {word_location}
            </body>
            </html>
        """

    def getwords(self, RawText):
        wordsdict = {}
        for index, word in enumerate(RawText.split(' ')):
            wordsdict.update({index: word})
        return wordsdict

    def crop(self, image):
        image = np.asarray(image)[:, :, 0]
        tps = np.where(image <= 30)
    
        # اگر چیزی پیدا نشد → همون تصویر خام رو برگردون یا None بده
        if tps[0].size == 0 or tps[1].size == 0:
            # انتخاب: یا برگردون کل تصویر، یا None
            return Image.fromarray(image)  
    
        min_x = np.min(tps[0]) - self.padcrop
        max_x = np.max(tps[0]) + self.padcrop
        min_y = np.min(tps[1]) - self.padcrop
        max_y = np.max(tps[1]) + self.padcrop
    
        # Ensure indices are within bounds
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(image.shape[0], max_x)
        max_y = min(image.shape[1], max_y)
    
        image_crop = Image.fromarray(image[min_x:max_x, min_y:max_y])
        return image_crop


    def takephoto(self, word, id, fontsize, fonturl):
        html_content = self.html_template.format(
            font_url=fonturl,
            font_size=fontsize,
            word_location=word
        )

        with open("temp.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        HTML('temp.html').write_pdf('temp.pdf', 
            stylesheets=[CSS(string='@page { size: 420mm 400mm; margin: 1cm; }')])
        
        pages = convert_from_path("temp.pdf", dpi=300)
        
        if pages:
            image_crop = self.crop(pages[0])
            outpath = os.path.join(self.outwordpath, f"{id}.png")
            image_crop.save(outpath, "PNG")
            
            # Clean up temporary files
            if os.path.exists("temp.html"):
                os.remove("temp.html")
            if os.path.exists("temp.pdf"):
                os.remove("temp.pdf")
                
            return outpath
        return None

    def gen2img(self, wordsdict, fontsize, fonturl='fonts/arabic_font/122-H_Esfahan.TTF'):
        UniqueWords = {}
        id = 0
        for key in wordsdict.keys():
            if wordsdict[key] not in UniqueWords.keys():
                outpath = self.takephoto(wordsdict[key], id, fontsize, fonturl)
                if outpath:
                    UniqueWords.update({wordsdict[key]: outpath})
                id += 1
        return UniqueWords

    def runphoto(self, file_unqwords, fontsize, fonturl='fonts/arabic_font/122-H_Esfahan.TTF'):
        if not os.path.exists(file_unqwords):
            print(f"Error: File {file_unqwords} not found!")
            return
        
        try:
            with open(file_unqwords, 'rb') as f:
                words_unq = pickle.load(f)
        except Exception as e:
            print(f"Error loading pickle file: {e}")
            return
        
        for key in tqdm(words_unq.keys()):
            outpath = self.takephoto(words_unq[key], key, fontsize, fonturl)
            if not outpath:
                print(f"Failed to process word {key}: {words_unq[key]}")

def main():
    parser = argparse.ArgumentParser(description='Process Arabic text to images')
    
    # Define command line arguments
    parser.add_argument('--takephoto', action='store_true', 
                       help='Take photo of Arabic word')
    parser.add_argument('--word', type=str, 
                       help='Arabic word to process')
    parser.add_argument('--id', type=str, 
                       help='ID for the output image')
    parser.add_argument('--outpath', type=str, default='output',
                       help='Output directory path')
    parser.add_argument('--fontsize', type=int, default=24,
                       help='Font size for the text')
    parser.add_argument('--fonturl', type=str, 
                       default='fonts/arabic_font/122-H_Esfahan.TTF',
                       help='URL or path to the font file')
    
    args = parser.parse_args()
    
    # Create operation instance
    op = Operation(args.outpath)
    
    # Process based on arguments
    if args.takephoto:
        if not args.word or not args.id:
            print("Error: --word and --id are required when using --takephoto")
            sys.exit(1)
        
        #print(f"Processing word: {args.word}")
        #print(f"Output ID: {args.id}")
        #print(f"Font size: {args.fontsize}")
        #print(f"Font URL: {args.fonturl}")
        #print(f"Output path: {args.outpath}")
        
        result_path = op.takephoto(args.word, args.id, args.fontsize, args.fonturl)
        
        #if result_path:
            #print(f"Success! Image saved to: {result_path}")
        #else:
            #print("Failed to create image")
    else:
        print("No operation specified. Use --takephoto to process a word.")

if __name__ == "__main__":

    main()

