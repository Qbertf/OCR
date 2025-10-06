from Operation import Operation as Ope
import numpy as np
import pickle
import glob
import re
import os

class arabicwiki:
    def __init__(self,forlderpath,outputpath):

        self.forlderpath = forlderpath
        self.outputpath  = outputpath
        self.Ope = Ope('outwords')
        if os.path.exists(self.outputpath)==False:
            os.mkdir(self.outputpath)

    def parse_wiki_sections_from_file(self,path, exclude=("المراجع", "انظر أيضا", "جستارها")):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = {}
        section_pattern = re.compile(r"(==+\s*(.*?)\s*==+)")
        matches = list(section_pattern.finditer(text))

        # اگر سکشنی نبود → کل متن مقدمه
        if not matches:
            return {"مقدمة": text.strip()}

        # متن قبل از اولین سکشن → مقدمه
        first_match = matches[0]
        intro_text = text[:first_match.start()].strip()
        if intro_text:
            sections["مقدمة"] = intro_text

        # بقیه سکشن‌ها
        for i, match in enumerate(matches):
            title = match.group(2).strip()
            if title in exclude:
                continue

            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)
            content = text[start:end].strip()
            sections[title] = content

        return sections

    def has_english(self,text: str) -> int:
        return 1 if re.search(r"[A-Za-z]", text) else 0
    
    def has_arabic(self,text: str) -> int:
        return 1 if re.search(r"[\u0600-\u06FF]", text) else 0

    def lightrun(self):
        words_unq=set()
        for path in glob.glob(self.forlderpath+'/*.txt'):
            path = path.replace('\\','/')
            sections_dict = self.parse_wiki_sections_from_file(path)          
            for title, content in sections_dict.items():
                information={}
                if self.has_english(content)==0 and self.has_arabic(content)==1:
                    if self.has_english(title)==0 and self.has_arabic(title)==1:

                        wordsdict_title   = self.Ope.getwords(title)
                        wordsdict_content = self.Ope.getwords(content)

                        #words_unq = list(words_unq) + [wordsdict_content[w] for w in wordsdict_content.keys()]
                        #words_unq = words_unq + [wordsdict_title[w] for w in wordsdict_title.keys()]
                        #words_unq = set(words_unq)


                        information={'title':title,'content':content,'wordsdict_title':wordsdict_title,'wordsdict_content':wordsdict_content}
                        outpath = self.outputpath+'/'+path.split('/')[-1].replace('.txt','.pkl')
                        with open(outpath,'w') as f:
                            f.write(str(information))


        #outpath = self.outputpath+'/UNIQUE_WORDS.pkl'
        #tmpw={};p=0;
        #for w in words_unq:
        #    tmpw.update({p:w});p+=1;
        #with open(outpath,'wb') as f:
            #pickle.dump(tmpw,f)
            
    def run(self):
        words_unq=set()
        for path in glob.glob(self.forlderpath+'/*.txt'):
            path = path.replace('\\','/')
            sections_dict = self.parse_wiki_sections_from_file(path)          
            for title, content in sections_dict.items():
                information={}
                if self.has_english(content)==0 and self.has_arabic(content)==1:
                    if self.has_english(title)==0 and self.has_arabic(title)==1:

                        wordsdict_title   = self.Ope.getwords(title)
                        wordsdict_content = self.Ope.getwords(content)

                        words_unq = list(words_unq) + [wordsdict_content[w] for w in wordsdict_content.keys()]
                        words_unq = words_unq + [wordsdict_title[w] for w in wordsdict_title.keys()]
                        words_unq = set(words_unq)


                        information={'title':title,'content':content,'wordsdict_title':wordsdict_title,'wordsdict_content':wordsdict_content}
                        outpath = self.outputpath+'/'+path.split('/')[-1].replace('.txt','.pkl')
                        with open(outpath,'wb') as f:
                            pickle.dump(information,f)


        outpath = self.outputpath+'/UNIQUE_WORDS.pkl'
        tmpw={};p=0;
        for w in words_unq:
            tmpw.update({p:w});p+=1;
        with open(outpath,'wb') as f:

            pickle.dump(tmpw,f)

