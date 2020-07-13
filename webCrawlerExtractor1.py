# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 02:20:31 2020
@author: Venkata N Divi
"""
from bs4 import BeautifulSoup
from operator import itemgetter
from re import sub,match,finditer
from html.parser import HTMLParser
import re,sys,requests,urllib.parse,warnings
from nltk import sent_tokenize,ne_chunk,pos_tag,word_tokenize
warnings.filterwarnings("ignore")

stoppers = ['learn','team','more','get','amp']
peopleStops = ['staff','people','hall','contact','employee','leadership','team','directory','about','dept','our','management']
types = ['.png','.jpg','.jpeg','.pdf','.doc','.txt','.docx','.xml','.json','/search/','/comments/','/archive','/node/','.mp','/files/','/checkout/','/white-paper-pdf/','/downloads/','/user/','/category/','/alphabet']

junkcName = ['floor','block','plot','road','house','site','lobby','broadband','internet','net','cable','wireless','infocom','infonet','pool'
             'netsol','isp','comnet','lan','building','town','ave','avenue','highway','marg','lane','telecom','telecommun','sec','network','unit',
             'ave','avenue','street','st','road','rd','way','boulevard','lane','ln','drive','dr','terrace','place','court','square','plaza','blvd',
             'pl','bay','crescent','trail','highway','motorway']

impTitles = ["chairman","chair","co-owner","co-publisher","co-chairman","co-chair","co-chief","co-president",
          "co-founder","founder","president","chief","chiefexecutiveofficer","cmo","cpo","cfo","cro","cto",
          "c.f.o","ceo","c.e.o","coo","c.o.o","cmo","c.m.o","cco","cdo","cio","cno","coo","cpo","cro","csc",
          "cso","cuo","cvo","cwo","cxo","czo","avp","mvp","svp","evp","vice","vp","v.p","vice-president",
          "v.p.","vicepresident","v-p","vp.","director","dir.","diectors","md","m.d","owner","board","dir",
          "manager","man.","managers","publisher","lead","head","architect","consultant","scientist","assistant",
          "analyst","officer","associate","engineer","developer","programmer","programming","support",
          "technical","database","dba","dbadmin","engineering","technology","information","computer",
          "administrator","software","testing",'executive']

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"

class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        matchTaggers = ['p','h1','h2','h3','h4','h5','h6','a','br','label','div']
        if tag in matchTaggers:
            self.__text.append('\n\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')
    
    def text(self):
        return ''.join(self.__text).strip()

class ExtractInfo():
    def __init__(self):
        print ("init") 
        
    def dehtml(self,text):
        try:
            parser = _DeHTMLParser()
            parser.feed(text)
            parser.close()
            return parser.text()
        except:
            return text
        
    def scrapeLink(self,url):
        try:
            response = requests.get(url, headers={'User-Agent': user_agent}, verify=False, timeout=(15, 20))
            soup = BeautifulSoup(response.text,'html5lib')
            for script in soup(["script", "style"]):
                script.extract()    
                
            textHTML = self.dehtml(str(soup))
            if 'html>' in textHTML or '>' in textHTML or '<' in textHTML:
                textHTML = soup.find_all(text=True)
                textHTML = ' '.join(text for text in textHTML)
                
            return soup,textHTML
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return None,None
        
    def processLinks(self,soup,url,domain):
        try:
            if soup:
                links = soup.find_all('a', href=True)
                emails = [link['href'].replace('mail:','').replace('mailto:','').replace('?',' ') for link in links if '@' in link['href'] and len(link['href'])<100 and len(link['href'])>2 and '.' in link['href']]
                        
                links = [urllib.parse.urljoin(url, link['href']) for link in links]
                domainLinks = list(set([link for link in links if (domain in link or url in link) and 'http' in link and not any(type1 in link for type1 in types)]))
                domainLinks = [link[:-1] if link.strip()[-1] == '/' else link for link in domainLinks ]
                filterLinks = [link for link in domainLinks if any(linkwords in peopleStops for linkwords in re.split("[^a-zA-Z0-9\s]",link.split('/')[-1]))]
                
                return list(set(filterLinks)),emails
            else:
                return [url],[]
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return [url],[]
        
    def processEmails(self,soup):
        try:
            if soup:
                links = soup.find_all('a', href=True)
                emails = [link['href'].replace('mail:','').replace('mailto:','').split('?')[0] for link in links if '@' in link['href'] and len(link['href'])<100 and len(link['href'])>2 and '.' in link['href']]
                return emails
            else:
                return []
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return []
        
    def getURL(self,domain):
        url = 'http://'+domain
        try:
            response = requests.get(url, headers={'User-Agent': user_agent}, verify=False ,timeout=(15, 20))
            if response and response.history:
                redirectURL = response.url
                url = urllib.parse.urljoin(redirectURL, '/')
                return url
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return url
    
    def processWordTags(self,text,titles):
        results = []
        try:
            for txt in text.split('\n'):
                for chunk in ne_chunk(pos_tag(word_tokenize(txt))):
                    tag = ' '.join(c[0] for c in chunk)
                    if hasattr(chunk, 'label'):
                        if chunk.label() == 'PERSON' and not bool(re.search(r'\d', tag)) and not '-' in tag:
                            results.append((tag,chunk.label()))
                        elif chunk.label() == 'ORGANIZATION' and tag.lower() in titles and tag.lower() not in stoppers and len(tag)>1:
                            results.append((tag,'TITLE'))
                        elif chunk.label() == 'ORGANIZATION' and tag not in titles and len(tag)>1:
                            results.append((tag,chunk.label()))
                        elif tag.lower() in titles and tag.lower() not in stoppers and len(tag)>1:
                            results.append((tag,'TITLE'))   
                        elif len(tag)>1 and tag.lower() not in stoppers:
                            results.append((tag,chunk.label())) 
            return results
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return results
    
    def processorStage2(self,results):
        person1,org1,mainTit,person,Org,Tit = [],[],[],'','',''
        try:
            for tag,chunk in results:
                if chunk == 'PERSON':
                    person = person+tag+' '
                    org1.append(Org) if (len(Org)>1 and Org not in org1) else None
                    mainTit.append(Tit) if (len(Tit)>1 and Tit not in mainTit) else None
                    Org,Tit = '',''
                elif chunk == 'ORGANIZATION':
                    Org = Org+tag+' '
                    person1.append(person) if (len(person)>1 and person not in person1) else None
                    mainTit.append(Tit) if (len(Tit)>1 and Tit not in mainTit) else None
                    person,Tit = '',''
                elif chunk == 'TITLE':
                    Tit = Tit+tag+' '
                    org1.append(Org) if (len(Org)>1 and Org not in org1) else None
                    person1.append(person) if (len(person)>1 and person not in person1) else None
                    person,Org = '',''
                elif tag !=',':
                    org1.append(Org) if (len(Org)>1 and Org not in org1) else None
                    person1.append(person) if (len(person)>1 and person not in person1) else None
                    mainTit.append(Tit) if (len(Tit)>1 and Tit not in mainTit) else None
                    person,Org,Tit = '','',''
    
            person1 = [person.strip() for person in person1]
            org1 = [org.strip() for org in org1]
    
            return person1
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return person1
    
    def checkforTitles(self,formatWords,master_collection1,stop):
        newTitles = []
        try:
            titles = master_collection1.distinct('Title',{'Title':{'$in':formatWords}})
            newTitles = [tit for tit in titles if tit.split()[0] not in stop and tit.split()[-1] not in stop]
    
            return newTitles
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return newTitles
    
    def checktitleinName1(self,person,master_collection1,stop):
        actPersons = []
        try:
            perTitles = [ p1[:-1] if p1[-1] == 's' and len(p1)>2 else p1 for per in person for p1 in per.lower().split() ]
            matchedTitles = master_collection1.distinct('Title',{'Title':{'$in':perTitles}})
            
            for per in person:
                match = 0
                for p1 in per.lower().split():
                    if (p1 in matchedTitles or p1[0:-1] in matchedTitles) or (p1 in stop):
                        match = 1
                        break
                    
                if match == 0 and ' ' in per:
                    actPersons.append(per)
            
            return actPersons
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return actPersons
        
    def getSpacyResults(self,text,nlp):
        try:
            doc = nlp(text)
            set1 = [X.text.strip() for X in doc.ents if X.label_ == 'PERSON' and '.' not in X.text ]
            return list(set(set1))
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return []
    
    def getEmail(self,inputString): 
        emails = []
        try:
            sentences = sent_tokenize(inputString)
            pattern = re.compile(r'\S*@\S*')
            for sen in sentences:
                sen = ' '.join(sen.split())
                sen = sen.replace('mailto:','').replace('mail:','').replace('?',' ')
                sen = '#'.join([sss if '@' in sss else '' for sss in sen.split()])
                matches = pattern.findall(str(sen))
                for match in matches:
                    for mm in match.split('#'):
                        if len(mm)>1 and mm and mm not in emails and len(mm)>1 and len(mm.split('@')[0])>1 and len(mm.split('@')[1])>1 and '.' in mm:
                            emails.append(mm.split('?')[0])
            return emails
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return emails
    
    def processText1(self,finalProcessedNames,text):
        names1,text,dumNames1 = {},' '.join(text.split()),[]
        try:
            for name in finalProcessedNames:
                if len(name.split())<=3:
                    nameIndex = [m.start() for m in re.finditer(name, text)]
                    for index in nameIndex:
                        names1[name] = int(index+len(name))
                        dumNames1.append((name,int(index+len(name))))
                    
            return dumNames1
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return names1
            
    def processText2(self,newTitles,text,stop):
        titles1,titleSet,text = {},[],text.lower()
        try:
            for title in newTitles:
                if text.find(title)>0:
                    for ind1 in [m.start() for m in finditer(title, text)]:
                        ind1 = int(ind1)
                        if ind1 in titles1:
                            ttt = titles1.get(ind1)
                            if title not in stop and title not in ttt:
                                ttt.append(title)
                                titles1[ind1] = ttt
                        else:
                            if title not in stop:
                                dummy = []
                                dummy.append(title)
                                titles1[ind1] = dummy
    
                        if ind1 not in titleSet:
                            titleSet.append(ind1)        
    
            titleSet = sorted(titleSet)
            return titleSet,titles1
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return titleSet,titles1
            
    def getNamesTitles(self,names1,titleSet,titles1):
        result = {}
        try:
            peronIndexes = [val for key,val in names1]
            for key,value in names1:
                start,end = value,value+50
                limit = [per for per in peronIndexes if (per >= start and per <end)]
                if len(limit)>1:
                    end = limit[1]-1
                
                j2 = [tit for tit in titleSet if tit > start and tit<=end]
                for jj in j2:
                    matchTitle = [item[1] for item in titles1 if item[0] == jj][0]
                    if key in result:
                        perTitle = result[key]
                        perTitle = perTitle+' '+matchTitle[0].title()
                        result[key] = perTitle
                    else:
                        result[key] = matchTitle[0].title()
            
            return result
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return result
        
    def checkEmailNameMatch(self,name,email1):
        try:
            email1 = re.sub('[^A-Za-z.@_-]+', '', email1)
            stat = 0
            for nm in name.lower().split():
                if len(email1)<2:
                    if nm[0] in email1:
                        email1,stat = email1.replace(nm[0],''),1
                elif nm in email1:
                    email1,stat = email1.replace(nm,''),1
                    
                if len(email1)<2 and len(email1)>0 and stat == 1 : return 1
            return 0
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return 0
                
    def mapEmailswithNames(self,names,emails):
        emailMatch = {}
        try:
            for email in emails:
                email = email.lower()
                email1 = email.split('@')[0].strip()
                for name in names:
                    print(name)
                    match = self.checkEmailNameMatch(name[0],email1)
                    if match == 1:
                        email = re.sub('[^A-Za-z0-9.@_-]+', '', email)
                        emailMatch[name[0]] = email.strip()
                        break
            return emailMatch
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return emailMatch
        
    def finalNLTKProcess(self,txt):
        people = []
        try:
            for chunk in ne_chunk(pos_tag(word_tokenize(txt))):
                tag = ' '.join(c[0] for c in chunk)
                if hasattr(chunk, 'label'):
                    if chunk.label() == 'PERSON' and not bool(re.search(r'\d', tag)) and not '-' in tag:
                        people.append(tag)
            return people
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return people
        
    def processText(self,text1,nlp):
        finalNames,titles = [],[]
        try:
            PeopleSet = self.getSpacyResults(text1,nlp)
            results = self.processWordTags(text1,titles)
            person1 = self.processorStage2(results)
            person = list(set(person1+PeopleSet))
            #person11 = self.checktitleinName1(person,master_collection1,stop)
            finalNames = list(set(person))
            
            return finalNames
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return finalNames
            
    def startProcessLinksForPeople(self,links,domain,nlp,emails1,stop):
        regex1,peopleData,emails,finalText = re.compile('^[a-zA-Z .]*$'),[],[],''
        for link in links:
            try:
                soup,text = self.scrapeLink(link)
                if soup:
                    emails2,finalText =  self.processEmails(soup),''
                    if text:
                        for splitter in text.split('\n'):
                            if len(splitter)>0:
                                processText11 = ' '.join(word for word in splitter.split() if word.lower() not in stop)
                                if ' nbsp' in processText11.strip():
                                    finalText = finalText+processText11.strip().replace(' nbsp','')+' '
                                else:
                                    finalText = finalText+processText11.strip()+'\n'
                                processText11,soup = '',None
                                
                        emails += self.getEmail(finalText) 
                        emails = list(set(emails+emails1+emails2))
                        emails = [email for email in emails if re.search('[a-zA-Z]', email.split('@')[0])]
                        inpText = ' '.join(text.replace('\n',' ').replace(' nbsp',' ').replace('/',' ').split())
                        
                        finalProcessedNames = self.processText(finalText,nlp)
                        finalProcessedNames1,finalText = [],''
                        for name in finalProcessedNames:
                            if(regex1.search(name) != None): 
                                isName = self.getSpacyResults(name,nlp)
                                if len(isName)>0:
                                    finalProcessedNames1.append(isName[0])
                        
                        finalProcessedNames1 = self.processText1(finalProcessedNames1,inpText)
                        finalProcessedNames1 = sorted(finalProcessedNames1,key=itemgetter(1))
                        emailMatch,inpText = self.mapEmailswithNames(finalProcessedNames1,emails),''
                        
                        for key in finalProcessedNames1:
                            mainResult = {}
                            key = key[0]
                            if len(key.split())>1 and not any(nm in junkcName for nm in key.lower().split()):
                                mainResult['Name'],mainResult['Email'] = key.title(),emailMatch[key] if key in emailMatch else ''
                                mainResult['Domain'] = domain
                                peopleData.append(mainResult)
                                
                        return peopleData
                    else:
                        return peopleData
                else:
                    return peopleData
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
                return peopleData
        
        return peopleData