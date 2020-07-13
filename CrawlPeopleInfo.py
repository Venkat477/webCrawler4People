# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 02:20:31 2020
@author: Venkata N Divi
"""

import sys,re,streamlit as st
from webCrawlerExtractor1 import ExtractInfo
from spacy import load
from nltk.corpus import stopwords

stop = [word for word in set(stopwords.words('english')) if len(word)>1]

def domainValidity(domain):
    regex = '^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
    if re.match(regex, domain):
        return True
    else:
        return False
    
def extractData(domainName_):
    nlp = load("en_core_web_md")
    result,dInfo = {},ExtractInfo()
    try:
        url = dInfo.getURL(domainName_)
        url = 'http://'+domainName_ if url is None else url
        print('url',url)
        soup,textHTML = dInfo.scrapeLink(url)
        if soup and textHTML:
            filterLinks,emails = dInfo.processLinks(soup,url,domainName_)
            mainLinks = [links.strip()[:-1] if links.strip()[-1] == '/' else links.strip() for links in filterLinks]
            mainLinks = [links.split('?')[0] for links in mainLinks if links.count('/')<=5]
            if len(mainLinks)==0:
                mainLinks.append(url)
                
            filterLinks = list(set(mainLinks))
            result = dInfo.startProcessLinksForPeople(filterLinks,domainName_,nlp,emails,stop)
            return result
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
        pass
                       
def processCrawling():
    st.subheader("**Try the Crawler**")
    domainName_ = st.text_input("Domain Name/URL")
    st.info('**Ex:domain.com or www.domain.com or https://www.domain.com**')
    if st.button('Extract'):
        domName_ = domainName_.replace('https://','').replace('http://','').split('/')[0]
        if len(domName_)<5 or '.' not in domName_ or not domainValidity(domName_):
            st.warning('Please try to enter proper Domain name!!!')
        else:     
            st.success('Crawling '+domainName_+', Please wait!!!')
            result = extractData(domName_)
            st.write(result)
            
def selectOptions():
    try:
        st.write("You have a company name and it has some employee organizational chart who are working in their company. You want this information and want to make an automate script which crawl this information for you.")
        st.write("This is a web crawler, which takes a URL as an input and provide people information to the user. Below are the details you can get.")
        st.write("""
        - **Person Name**
        - **Person Email Address**""")
        st.write("""Using this service, you can extract most of the people names and email address if provided in the site. """)
        st.write("""When we got the domain, will search for only pages which will have the employee information like staff, leadership, team etc..
        Based on it, by applying different NLP technoques and Spacy NLP language models will try to extract all the people information.""")
        st.write("""I tried to include all the possible cases to extract the above information, but still for some cases it may fail to extract all the details.""")
        st.write("""I have used Regex Patterns for removing all the unwanted characters and for identifying 
        some key phrases like email addresses.""")
        st.write("""I have used NLTK for Sentence Tokenization, Parts of Speech Identification, Words Tokenization techniques and Spacy NLP language model 
        **en_core_web_md (https://spacy.io/models/en)** to identify the people names.""")
        st.write("""One can develop any sort of extraction logic using above steps.""")
        st.subheader('**Use the Left Side Options to test the Service**')
    except Exception as e:
        print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
        
def main():
    st.sidebar.title("Web Crawler for Extracting People")
    st.sidebar.markdown("Try our Service!!!")
    st.sidebar.subheader("Choose")
    activities=["Select","Web Crawler"]
    choice = st.sidebar.selectbox("",activities)
    if choice == 'Select':
        selectOptions()
    elif choice == 'Web Crawler':
        processCrawling()
    
if __name__ == '__main__':
    st.write('<!DOCTYPE html><html lang="en">   <head>      <meta charset="UTF-8">      <meta name="viewport" content="width=device-width, initial-scale=1.0">      <meta http-equiv="X-UA-Compatible" content="ie=edge">      <title>Responsive Navigation Bar - W3jar.Com</title>      <style>*,*::before,*::after {  box-sizing: border-box;  -webkit-box-sizing: border-box;}body {  font-family: sans-serif;  margin: 0;  padding: 0;}.container {  height: 80px;  background-color: #052252;  display: -webkit-box;  display: -ms-flexbox;  display: flex;  -ms-flex-wrap: wrap;  flex-wrap: wrap;  -webkit-box-align: center;  -ms-flex-align: center;  align-items: center;  overflow: hidden;}.container .logo {  max-width: 250px;  padding: 0 10px;  overflow: hidden;}.container .logo a {  display: -webkit-box;  display: -ms-flexbox;  display: flex;  -ms-flex-wrap: wrap;  flex-wrap: wrap;  -webkit-box-align: center;  -ms-flex-align: center;  align-items: center;  height: 60px;}.container .logo a img {  max-width: 100%;  max-height: 60px;}@media only screen and (max-width: 650px) {  .container {    -webkit-box-pack: justify;    -ms-flex-pack: justify;    justify-content: space-between;  }  .container .logo {    -webkit-box-flex: 1;    -ms-flex: 1;    flex: 1;  }}.body {  max-width: 700px;  margin: 0 auto;  padding: 10px;} .h1 { color:#FEFEFE; position: center; top: 10px; font-size:135px;font-family:verdana;    margin-top:0px;    margin:0px; line-height:50px; }</style>   </head>   <body>      <div class="container">      <div class="logo">    <a href="#"><img src="https://image.flaticon.com/icons/svg/2344/2344464.svg" alt="logo"></a>    </div> </body></html>', unsafe_allow_html=True)
    st.title("Web Crawler")
    st.markdown("You have a Domain and want to get the people information from it? **Try our Service!!!**")
    main()