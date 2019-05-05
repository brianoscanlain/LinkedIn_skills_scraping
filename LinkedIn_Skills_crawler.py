# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 15:21:02 2019

@author: Administrator
"""
import pandas as pd
import requests, time
from bs4 import BeautifulSoup
import re

#Testing remnants:
PATH ='./'

#Creates an empty excel datafile so that we can append to:
def InitSkillList(PATH):
    print('Initialising a fresh database ...')
    # Create Empty Panda Frames:
    Skills = pd.DataFrame()
    RelatedSkills = pd.DataFrame()
    TopCompanies = pd.DataFrame()
    TopUniversities = pd.DataFrame()
    TopSkills = pd.DataFrame()
    #Read in the text file containing all the skills (previously compiled)
    FILE = ReadFILE(PATH)
    #Assign Data Frame columns:
    Skills['SkillName'] = pd.Series(FILE[0])
    Skills['URL'] = pd.Series(FILE[1])
    Skills['SkillIndex'] = pd.Series(list(range(len(FILE[0]))))
    Skills['SkillPopularity'] = pd.Series([0]*len(FILE[0]))
    #Write to excel file:
    Skills.to_excel('{}Skills.xlsx'.format(PATH))
    #
    RelatedSkills['ChildSkills'] = pd.Series()
    RelatedSkills['ParentSkillIndex'] = pd.Series()
    #Write to excel file:
    RelatedSkills.to_excel('{}RelatedSkills.xlsx'.format(PATH))
    #
    TopCompanies['CompanyName'] = pd.Series()
    TopCompanies['Count'] = pd.Series()
    TopCompanies['SkillParentIndex'] = pd.Series()
    #Write to excel file:
    TopCompanies.to_excel('{}TopCompanies.xlsx'.format(PATH))
    #
    TopUniversities['UniversityName'] = pd.Series()
    TopUniversities['Count'] = pd.Series()
    TopUniversities['SkillParentIndex'] = pd.Series()
    #Write to excel file:
    TopUniversities.to_excel('{}TopUniversities.xlsx'.format(PATH))
    #
    TopSkills['TopSkillName'] = pd.Series()
    TopSkills['Count'] = pd.Series()
    TopSkills['SkillParentIndex'] = pd.Series()
    #Write to excel file:
    TopSkills.to_excel('{}TopSkills.xlsx'.format(PATH))
    #Return the DataFrames!
    print('Initialising complete!')
    #return [Skills, RelatedSkills, TopCompanies, TopUniversities,TopSkills]
    
    
    
def ReadFILE(PATH):
    LIurl = 'https://www.linkedin.com/topic/'
    with open('{}skillsDB.txt'.format(PATH),'r',encoding='utf-16', errors='ignore') as f:
           skill = f.readlines()
    #Now let's strip the \n carriage return from the end of each line:
    skill = [x.rstrip('\n') for x in skill] 
    #next, let's compile a list of url's to each skill webpage:
    urlList = [LIurl + x for x in skill] 
    return [skill, urlList]


def SaveSkillDB(PATH, Skills, RelatedSkills, TopCompanies, TopUniversities,TopSkills):
    #Do a simple overwrite (we will make sure to load files into memory and then save!)
    Skills.to_excel('{}Skills.xlsx'.format(PATH))
    RelatedSkills.to_excel('{}RelatedSkills.xlsx'.format(PATH))
    TopCompanies.to_excel('{}TopCompanies.xlsx'.format(PATH))
    TopUniversities.to_excel('{}TopUniversities.xlsx'.format(PATH))
    TopSkills.to_excel('{}TopSkills.xlsx'.format(PATH))
    



def LoadSkillDB(PATH):
    Skills = pd.read_excel('{}Skills.xlsx'.format(PATH))
    RelatedSkills = pd.read_excel('{}RelatedSkills.xlsx'.format(PATH))
    TopCompanies = pd.read_excel('{}TopCompanies.xlsx'.format(PATH))
    TopUniversities = pd.read_excel('{}TopUniversities.xlsx'.format(PATH))
    TopSkills = pd.read_excel('{}TopSkills.xlsx'.format(PATH))
    return [Skills, RelatedSkills, TopCompanies, TopUniversities,TopSkills]




def SkillsCrawler(numScrapes = 224, PATH = './', specificStartIndex=None, FreshStart = False, waitTime = 1):
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    if FreshStart: InitSkillList(PATH)
    #Load already available data!
    [Skills, RelatedSkills, TopCompanies, TopUniversities,TopSkills] = LoadSkillDB(PATH)
    #Find out where we left off previously:
    if specificStartIndex != None: 
        strtIdx = specificStartIndex
    else:
        if len(RelatedSkills.ParentSkillIndex):
            strtIdx = RelatedSkills.ParentSkillIndex[-1] + 1
        else:
            strtIdx = 0 #if empty, let's start at 0
    #Let's pull out the url's of interest:
    urlList = list(Skills.URL[strtIdx:strtIdx+numScrapes])
    #Let's initiate client!
    client = requests.Session()
    #Let's define the header we want to use:
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    idx = strtIdx
    for url in urlList:
        time.sleep(waitTime)
        scrapedInfo = inScrape(url,header,client)
        if scrapedInfo != -1:
            #Save the scraped Info to the data columns!
            Skills.SkillIndex.append(idx)
            Skills.SkillName.append()
            Skills.SkillPopularity.append()
            #Same for the Related skills:
            RelatedSkills.ChildSkills.append()
            RelatedSkills.ParentSkillIndex.append(idx)
            #Companies:
            TopCompanies.CompanyName.append()
            TopCompanies.Count.append()
            TopCompanies.SkillParentIndex.append(idx)
        idx+=1
        

def inScrape(url,header,client):
    OUT = {'ChildSkills':[],'ChildSkillsParentIndex':[], \
           'ChildTopCompanies':[],'ChildTopCompaniesCount':[],\
           'ChildTopCompaniesParentIndex':[],'ChildTopUniversities':[], \
           'ChildTopUniversitiesCount':[],'ChildTopUniversitiesParentIndex':[],\
           'ChildTopSkills':[],'ChildTopSkillsCount':[],'ChildTopSkillsParentIndex':[]}
    try:
        html = client.get(url,headers=header).content
    except:
        print('HTML request error for ' + url)
        return -1
    ChildrenSoup = BeautifulSoup(html,"lxml")
    try:   #Try to obtain the number of people who have listed the skill
        OUT['SkillParentCount'].append(int(ChildrenSoup.findAll('span',{'class':'member-count'})[0].getText().split()[0].strip()))
    except:
        OUT['SkillParentCount'].append(None)
        pass
    #List out the additonal skills!
    skills = ChildrenSoup.findAll('li',{'class':'skill'})
    for skill in skills:
        #here I convert skill from a "bs4.element.tag" to a BeautifulSoup OBJ:
        skill = BeautifulSoup(str(skill))
        #Record the list of sub skills!
        OUT['ChildSkills'].append(str(skill.findAll('a')[0].getText()))
        print(' \"{}\" '.format(str(skill.findAll('a')[0].getText())))
    #Let's take a goosey gander at the pie charts (I hear that a piece of pie can be quite nice with a good cup of tea [good cup of tea emphasised here])    
    #Piies = ChildrenSoup.findAll('ol',{'class':'stats-text-list'}) #I cannot find the name of this Pie chart, so I am going one 
    Piies = ChildrenSoup.findAll('div',{'class':'stats-text-container'})
    for pie in Piies:
        print('\n')
        for slice in pie.findAll('li'):
            #for crumbs in pie.contents:
            #vals = re.split('\s-\s|-|\s-|-\s', crumbs.getText())
            #crumbs = re.split('\s-\s|-|\s-|-\s', slice.getText())   # fialed for the following Embry-Riddle Aeronautical University - 1,030  
            crumbs = re.split('\s-\s|\s-|-\s', slice.getText())
            #print('{} - {}'.format(crumbs[0],crumbs[1].replace(',','')))
            if pie.findAll('h3')[0].getText() == 'Top skills':
                try:
                    OUT['ChildTopSkills'].append(str(crumbs[0]))
                    OUT['ChildTopSkillsCount'].append(int(crumbs[-1].replace(',','')))
                except:
                    pass #Encountered error appending PieChart segment, skipping
            elif pie.findAll('h3')[0].getText() == 'Top companies':
                try:
                    OUT['ChildTopCompanies'].append(str(crumbs[0]))
                    OUT['ChildTopCompaniesCount'].append(int(crumbs[-1].replace(',','')))
                except:
                    pass #Encountered error appending PieChart segment, skipping
            elif pie.findAll('h3')[0].getText() == 'Top universities':
                    OUT['ChildTopUniversities'].append(str(crumbs[0]))
                    OUT['ChildTopUniversitiesCount'].append(int(crumbs[-1].replace(',','')))
            else:
                print('Cannot determine PieChart Name: {}'.format(pie.findAll('h3')[0].getText()))
    return OUT                    