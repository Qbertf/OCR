import json
import cv2
import glob
import numpy as np
import pickle
from tqdm import tqdm
from weasyprint import HTML
import random
from IPython.display import clear_output

def template_first_sols(colored_arabic_text,font1,font2,font3):
  html_template = f"""
  <html dir="rtl" lang="ar">
  <head>
  <meta charset="utf-8">
  <style>
  @font-face {{
      font-family: 'Amiri';
      src: url({font1});
  }}
  @font-face {{
      font-family: 'Amiri';
      src: url({font2});
  }}

  @font-face {{
      font-family: 'LTN';
      src: url({font3});
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
