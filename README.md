# WebCrawler4People Extraction
You have a Domain and want to get the people information from it? Try our Service!!!

You have a company name and it has some employee organizational chart who are working in their company. You want this information and want to make an automate script which crawl this information for you.

This is a web crawler, which takes a URL as an input and provide people information to the user. Below are the details you can get.

***1. Person Name </ br>
2. Person Email Address
***
Using this service, you can extract most of the people names and email address if provided in the site.

When we got the domain, will search for only pages which will have the employee information like staff, leadership, team etc.. Based on it, by applying different NLP technoques and Spacy NLP language models will try to extract all the people information.

I tried to include all the possible cases to extract the above information, but still for some cases it may fail to extract all the details.

I have used Regex Patterns for removing all the unwanted characters and for identifying some key phrases like email addresses.

I have used NLTK for Sentence Tokenization, Parts of Speech Identification, Words Tokenization techniques and Spacy NLP language model **en_core_web_md (https://spacy.io/models/en)** to identify the people names.

One can develop any sort of extraction logic using above steps.
