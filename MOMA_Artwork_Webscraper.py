# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 20:35:37 2022

@author: jogoz
"""

#MOMA Webscraper


#Packages Used
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


#MOMA stores their artworks under their collections/works section meaning it's 
#Actually really easy to just scrape everything by scraping through random numbers
#and then just discarding links that don't work


#WARNING: This will visit 500k websites. This will obv take a while to run 
og_combs = []
for j in range(0,5):
    URL = f'https://www.moma.org/collection/works/{j}'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #This section here checks if the website is blank
    oof_check = soup.find(class_='main layout/anchor-offset')
    word= "Error 404"
    oof_check = str(oof_check)
    if word in oof_check:
        continue
    
    #Actual extraction of data from the website
    art_datas = soup.find_all('main', class_='main layout/anchor-offset')
    combs1= []
    for art_data in art_datas:
        description = art_data.find('div', class_='main-content')
        view_status = art_data.find('li', class_='tags__item') 
        year = art_data.find('div', class_='work__short-caption') 
        location = art_data.find('span', class_='locations__item__text balance-text') 
        art_details = art_data.find('dl', class_='work__caption')
        description= description.text.strip()
        view_status = view_status.text.strip()
        year = year.text.strip()
        art_details = art_details.text.strip()
        art_id = URL
        
        if location is not None:
            location = location.text.strip()
            combs1.append((description, view_status, art_details, year, art_id, location))
        else: 
            combs1.append((description, view_status, art_details, year, art_id, location))

        
        df2 = pd.DataFrame(combs1)
    df2 = pd.DataFrame(combs1)
    og_combs.append(df2)

#Bring all the loop dataframes together now
og_combs = pd.concat(og_combs)

#Change column names
og_combs.columns = ['Description', 'View_Status', 'Art_Details', 'Year', 'Art_id', 'Location']
#Reset Index
og_combs = og_combs.reset_index(drop=True)

#Split the year column up to get the artist and title info as well
year = og_combs['Year'].str.split("(\s{2,})",expand = True)
og_combs['Year'] = year[[4]]
og_combs['Artist'] = year[[0]]
og_combs['Title'] = year[[2]]



#Break up the art details box to extract all the different misc info for the 
#Arwork such as copyright, credit, dimension, department, and medium
art_details_df = pd.DataFrame()
columns_to_get = ['Medium', 'Dimensions','Copyright', 'Credit', 'Department']
for i in range(len(columns_to_get)): 
    word_2_search = columns_to_get[i]
    test = og_combs['Art_Details'].str.split(f'{word_2_search}(.*)',expand = True)
    if word_2_search == 'Copyright': 
        test = test.iloc[:, 2].str.split("(\s{4,})",expand = True)
        test = test.replace(r'^\s*$', np.nan, regex=True)
        #Drop columns that are only NA
        test = test.dropna(axis=1, how ='all')
        new_col_names = []
        for j in range(test.shape[1]):
            new_col_names.append(f'column_{j}')
        test.columns = new_col_names
        art_details_df[f'column_{i}'] = test['column_1']
    else:
        test = test.iloc[:, 2].str.split("(\s{2,})",expand = True)
        test = test.replace(r'^\s*$', np.nan, regex=True)
        #Drop columns that are only NA
        test = test.dropna(axis=1, how ='all')
        new_col_names = []
        for j in range(test.shape[1]):
            new_col_names.append(f'column_{j}')
        test.columns = new_col_names
        art_details_df[f'column_{i}'] = test['column_0']


#Clean up the copyright column
art_details_df.columns = columns_to_get
art_details_df['Copyright'] = np.where(art_details_df['Copyright'].str.contains('©'),
                                       art_details_df['Copyright'],
                                       None)

#Join art data back in
og_combs = og_combs.join(art_details_df)

#Select for clean column names we want
og_combs = og_combs[['Artist', 'Title', 'Medium', 'Year', 'View_Status', 'Location', 'Description', 'Dimensions', 
                     'Credit','Copyright', 'Department', 'Art_id']]


#We have our most basic MOMA data here, now to get the image hpyerlink
MOMA_data = og_combs

#Now we're only visitng valid URl's to get the photo
hyperlinks = list('https://www.moma.org/collection/works/' + MOMA_data['Art_id'])
og_combs = []
for i in range(len(hyperlinks)):
    combs1 = []
    URL = hyperlinks[i]
    print(URL)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    images = soup.findAll('img')
    if images:
        example = images[0]
        example = example.attrs['src']
        combs1.append((URL, example))
        df2 = pd.DataFrame(combs1)
        og_combs.append(df2)
    else: 
        continue

og_combs = pd.concat(og_combs)


#Combine the image data to our MOMA data
og_combs.columns = ['URL', 'Image_Hyperlink']
og_combs['Art_id'] = og_combs['URL'].str.replace('https://www.moma.org/collection/works/', '')
#og_combs['Art_id'] = og_combs['Art_id']
og_combs['Image_Hyperlink'] = 'https://www.moma.org' + og_combs['Image_Hyperlink']
og_combs = og_combs.drop(['URL'], axis= 1)

og_combs['Art_id'] = og_combs['Art_id'].astype(str)

MOMA_data = pd.merge(MOMA_data, og_combs, 
                     how= "left", 
                     on= 'Art_id')

#Split up the location column to make it usable
location = MOMA_data['Location'].str.split(",",expand = True)
if location.shape[1] > 1: 
    location.columns = ['MOMA', 'Floor', 'Room']
    location = location.drop(['MOMA'], axis= 1)
    MOMA_data = MOMA_data.join(location)

