import json
import cv2
import glob
import numpy as np
import pickle
from tqdm import tqdm
from weasyprint import HTML
import random
from IPython.display import clear_output

def template_first(colored_arabic_text):
  html_template = f"""
  <html dir="rtl" lang="ar">
  <head>
  <meta charset="utf-8">
  <style>
  @font-face {{
      font-family: 'Amiri';
      src: url('/kaggle/working/B Lotus.ttf');
  }}
  @font-face {{
      font-family: 'Amiri';
      src: url('/kaggle/working/B Lotus Bold.ttf');
  }}

  @font-face {{
      font-family: 'LTN';
      src: url('/kaggle/working/MOVlts.ttf');
  }}


  body {{
      font-family: 'Amiri', serif;
      background: white;
      color: black;
      font-size: 18px;
      padding: 30px;
      line-height: 1.8;
      text-align: justify;
      margin: 0;
      word-spacing: 2px;
      width: 600px;
  }}
  p, span {{
      page-break-inside: avoid;
  }}
  @page {{
      size: A4;
      margin: 2cm;
  }}
  </style>
  </head>
  <body>
  {colored_arabic_text}
  </body>
  </html>
  """
  return html_template,168

def add_color_to_words(text):
    """اضافه کردن رنگ تصادفی به هر کلمه"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8',
        '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA', '#F1948A',
        '#D7BDE2', '#F9E79F', '#A9DFBF', '#F5B7B1', '#AED6F1', '#E8DAEF'
    ]

    colors = ['#000000']

    words = text.split()
    colored_words = []
    for word in words:
        color = random.choice(colors)
        colored_word = f'<span style="color:{color};">{word}</span>'
        colored_words.append(colored_word)
    return ' '.join(colored_words)


def put_text_on_segment(segment_content):
  text_putted = "";allwords=[]
  for key in segment_content.keys():
    title = segment_content[key]['title']

   # title = title.replace("(","").replace(")","").replace(")","").replace("(","").replace("-","_")
    title = title.replace("-","ـ")
    title = title.replace("_","ـ")

    for qw in title.split(" "):
      if qw.strip()!='':
        allwords.append(qw)

    #allwords = allwords + title.split(" ")
    text_putted = text_putted + '<strong>'+title+'</strong></br> '
    for pargraph in segment_content[key]['paragraph']:
      #pargraph = pargraph.replace("(","").replace(")","").replace(")","").replace("(","").replace("-","_")
      #pargraph = pargraph.replace("-","_")

      pargraph = pargraph.replace("-","ـ")
      pargraph = pargraph.replace("_","ـ")

      text_putted += ''+pargraph+'</br> '
      #allwords = allwords + pargraph.split(" ")
      for qw in pargraph.split(" "):
        if qw.strip()!='':
          allwords.append(qw)


    text_putted += '</br></br> '
  return text_putted,allwords

def save_binary_image_cv2(imagec, output_path):
    """
    تبدیل تصویر RGB به باینری (1-bit) و ذخیره با حداقل حجم
    """
    # 1. تبدیل به grayscale (اگر imagec سه کاناله باشد)
    if len(imagec.shape) == 3:
        gray = cv2.cvtColor(imagec, cv2.COLOR_BGR2GRAY)
    else:
        gray = imagec

    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    

    binary_pil = Image.fromarray(binary)
    binary_1bit = binary_pil.point(lambda x: 0 if x < 128 else 255, '1')
    binary_1bit.save(output_path, optimize=True)
    
    return binary
  
def export(html_template,segmentname,outpath='tempwords',outdataset=""):

  #!mkdir -p $outpath
  os.system('mkdir -p '+outpath)

  with open("arabic_text_colored.html", "w", encoding="utf-8") as f:
      f.write(html_template)

  path_pdf = outdataset+"/"+f"{segmentname}.pdf"

  HTML('arabic_text_colored.html').write_pdf(path_pdf)

  from pdf2image import convert_from_path

  images = convert_from_path(path_pdf, dpi=600)

  for i, img in enumerate(images):
      index_out = str(i+1).zfill(5)
      img.save(outpath+"/"+f"{segmentname}_page_{index_out}.png", "PNG")
      #break

  #!rm -rf arabic_text_colored.html
  os.system('rm -rf arabic_text_colored.html')
  #!rm -rf arabic_text_colored.pdf

import os


def has_number(text):

    # محدوده اعداد انگلیسی
    english_digits = '0123456789'

    # محدوده اعداد عربی-هندی (Arabic-Indic)
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'

    # محدوده اعداد فارسی-عربی (Eastern Arabic-Indic)
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'

    # ترکیب همه اعداد
    all_digits = english_digits + arabic_digits + persian_digits

    # بررسی وجود هر کاراکتر عددی در رشته
    for char in text:
        if char in all_digits:
            return True

    return False

def export_word_line(html_template,perfix,segmentname,outpath='tempwords',outdataset="",sizebigger=False):


  words = html_template.split(" ")[perfix:]

  perfixtag = html_template.split(" ")[:perfix]

  #perfixtag = " ".join(html_template)

  html_sample_mask = perfixtag.copy()
  html_sample = perfixtag.copy()

  for index,wrd in enumerate(words):

    wrdx = wrd.replace('<strong>','').replace('</strong>','').replace('</br>','')
    if wrdx.strip()!='':

      if has_number(wrdx)==False:
        colored_word = f'<span style="font-family: LTN;">{wrd}</span>'
        #colored_word = f'<u style="text-decoration: none; border-bottom: 4px solid red; padding-bottom: 2px;">{colored_word}</u>'
        colored_word_mask = f'<u style="text-decoration: none; border-bottom: 4px solid red; padding-bottom: 4px;">{colored_word}</u>'

        #colored_word_mask = f'<span style="background-color: red; color: red;">{wrd}</span>'


      else:
        
        if sizebigger==True:
            colored_word = f'<span style="font-size: 21px;">{wrd}</span>'
        else:
            colored_word = wrd
          
        colored_word_mask = f'<u style="text-decoration: none; border-bottom: 4px solid red; padding-bottom: 4px;">{colored_word}</u>'
        #colored_word_mask = f'<span style="background-color: red; color: red;">{wrd}</span>'

    else:
        colored_word = wrd
        colored_word_mask=wrd

    #html_sample.append(colored_word)
    html_sample_mask.append(colored_word_mask)



  #html_sample = " ".join(html_sample)
  html_sample_mask = " ".join(html_sample_mask)

  #export(html_sample,outpath)
  export(html_sample_mask,segmentname,outpath+"_mask",outdataset)


def sort_words(points):
  #points = a_xy
  line_threshold = 40

  points_sorted_y = sorted(points, key=lambda p: p[1])

  lines = []
  current_line = [points_sorted_y[0]]

  for p in points_sorted_y[1:]:
      if abs(p[1] - np.mean([q[1] for q in current_line])) < line_threshold:
          current_line.append(p)
      else:
          lines.append(current_line)
          current_line = [p]
  lines.append(current_line)

  final_sorted = []
  for line in lines:
      final_sorted.extend(sorted(line, key=lambda p: -p[0]))

  return final_sorted

def create_mask(image):

  # خواندن تصویر
  #image = cv2.imread('/kaggle/working/tempwords_mask/example_page_1.png')

  # تبدیل از BGR به HSV (برای شناسایی بهتر رنگ)
  hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  # محدوده رنگ قرمز در HSV
  # قرمز در HSV دو محدوده دارد (به دلیل چرخه رنگ)
  lower_red1 = np.array([0, 120, 70])
  upper_red1 = np.array([10, 255, 255])
  lower_red2 = np.array([170, 120, 70])
  upper_red2 = np.array([180, 255, 255])

  # ایجاد ماسک برای رنگ قرمز
  mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
  mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
  red_mask = mask1 + mask2

  # اعمال ماسک روی تصویر اصلی
  red_regions = cv2.bitwise_and(image, image, mask=red_mask)

  # پیدا کردن کانتورهای نواحی قرمز
  contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  px=0;allsize=[]
  a_xy=[]
  # رسم مستطیل دور نواحی قرمز
  for contour in contours:
      # فیلتر کردن کانتورهای کوچک
      if cv2.contourArea(contour) > 40:  # حداقل مساحت
          x, y, w, h = cv2.boundingRect(contour)
          if (w*h)>=40:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # مستطیل سبز
            a_xy.append((x,y,w,h))
            px+=1;

  return a_xy
'''
def export_word(html_template,perfix,outpath='tempwords'):

  !mkdir -p $outpath
  words = html_template.split(" ")[perfix:]

  perfixtag = html_template.split(" ")[:perfix]

  #perfixtag = " ".join(html_template)

  for index1,wrd1 in enumerate(words):

    html_sample = perfixtag.copy()
    for index2,wrd2 in enumerate(words):
      if index1==index2:
        wrdx = wrd2.replace('<strong>','').replace('</strong>','').replace('</br>','')
        if wrdx.strip()!='':
          color = '#000000'
          colored_word = f'<span style="color:{color};">{wrd2}</span>'
          html_sample.append(colored_word)

      else:
          color = '#FFFFFF'
          colored_word = f'<span style="color:{color};">{wrd2}</span>'
          html_sample.append(colored_word)


    html_sample = " ".join(html_sample)

    export(html_sample,outpath)
    #break


  return html_sample
'''
def get_info_mask(allwords):

  count_number=0;info_mask={}
  for path in tqdm(np.sort(glob.glob('/kaggle/working/tempwords_mask/*.png'))):
    image = cv2.imread(path)
    a_xy = create_mask(image)
    if len(a_xy)>=1:
      final_sorted = sort_words(a_xy)
      count_number = count_number + len(a_xy)
      info_mask.update({path:final_sorted})

  if len(allwords)==count_number:
    print('\nok')
    flag=1;

  else:
    print('danger!')
    flag=0;

  return info_mask,flag


def replace_english_digits_with_arabic(text: str) -> str:
    """
    جایگزینی اعداد انگلیسی (0-9) با معادل عربی شرقی (٠-٩) در رشتهٔ ورودی
    """
    translation_map = {
        '0': '٠',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩',
    }

    for eng, arb in translation_map.items():
        text = text.replace(eng, arb)

    return text
  
def export_dataset(segmentname,info_mask,allwords,outdataset="dataset",types="O"):

  px=0;outpage=[]
  for key in info_mask.keys():
    coords_list = info_mask[key]
    image = cv2.imread(key)
    imagec = image.copy()

    page_data={};wx=0;
    fulltext=''
    for coords in coords_list:
      x, y, w, h = coords
      imagec[y-5:y-5+h+10,x-5:x-5+w+10]=(255,255,255)

      y = y - 170; h = 170
      x = x-5; w = w + 25
      #cv2.rectangle(imagec, (x, y), (x + w, y + h), (0, 255, 0), 2)  # مستطیل سبز

      word = allwords[px]
      word = replace_english_digits_with_arabic(word)

      page_data.update({wx:{'word':word,'location':{'x':x,'y':y,'w':w,'h':h}}})

      fulltext = fulltext + word + ' '
      wx+=1;

      if px==0:
        title = "temp/"+segmentname+"_F_"+word+".png"
        cv2.imwrite(title, imagec[y:y+h,x:x+w])

      if px==len(allwords)-1:
        title = "temp/"+segmentname+"_L_"+word+".png"
        cv2.imwrite(title, imagec[y:y+h,x:x+w])

      px+=1;
    #break

    output_path_image = key.replace('tempwords_mask',outdataset+"/images")

    if types=='O':
      cv2.imwrite(output_path_image, imagec)
    else:
      save_binary_image_cv2(imagec[:,:,0],output_path_image)
    
    output_path_label = output_path_image.replace('images','labels').replace('.png','.json')

    with open(output_path_label, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, ensure_ascii=False, indent=2)


    with open(output_path_image.replace('images','texts').replace('.png','.txt'),'w', encoding='utf-8') as f:
        f.write(fulltext.strip())
      
    outpage.append(output_path_image)

  return outpage

from PIL import Image
import os

def png_list_to_pdf(png_paths, output_pdf_path, dpi=600, resize_factor=None):
    """
    لیستی از مسیرهای PNG را به PDF تبدیل می‌کند

    Parameters:
    png_paths (list): لیست مسیرهای فایل‌های PNG
    output_pdf_path (str): مسیر فایل PDF خروجی
    dpi (int): کیفیت خروجی
    resize_factor (float): فاکتور تغییر سایز (مثلاً 0.5 برای نصف کردن)
    """
    try:
        images = []
        for i, png_path in enumerate(png_paths):
            if not os.path.exists(png_path):
                print(f"اخطار: فایل {png_path} یافت نشد")
                continue

            img = Image.open(png_path)

            # تبدیل به RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # تغییر سایز اگر لازم باشد
            if resize_factor:
                new_width = int(img.width * resize_factor)
                new_height = int(img.height * resize_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            images.append(img)
            print(f"صفحه {i+1} پردازش شد: {png_path}")

        if not images:
            print("هیچ عکس معتبری برای تبدیل یافت نشد")
            return False

        # ذخیره PDF
        images[0].save(
            output_pdf_path,
            save_all=True,
            append_images=images[1:],
            dpi=(dpi, dpi)
        )

        print(f"✅ PDF با موفقیت ساخته شد: {output_pdf_path}")
        print(f"📄 تعداد صفحات: {len(images)}")
        print(f"🎯 کیفیت: {dpi} DPI")
        return True

    except Exception as e:
        print(f"❌ خطا در تبدیل به PDF: {e}")
        return False
