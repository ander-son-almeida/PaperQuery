# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 12:48:59 2023

@author: Anderson Almeida
"""

import arxiv
import requests
import io
import streamlit as st
import zipfile
import pandas as pd
from streamlit_tags import st_tags_sidebar


st.set_page_config(page_title="PaperQuery",layout='wide', page_icon='🔬')

st.subheader('PaperQuery')
st.sidebar.image('img/arxiv_logo.png', use_column_width=True)

st.write('''
         arXiv is a project by the Cornell University Library 
         that provides open access to 1,000,000+ articles in Physics, 
         Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, 
         and Statistics.
         
         In order to optimize bibliographic reviews using the library, this app
         was developed. With it you enter at least 4 keywords - in order of importance for the query.
         
         Thanks and credits to **[arXiv API](https://info.arxiv.org/help/api/basics.html#about)** contributors 
                                             and Lukas Schwab for adapting 
                                             a **[Python version](https://github.com/lukasschwab/arxiv.py)** of this API.
         
         ''')

###############################################################################
# keywords interface
keywords = st_tags_sidebar(
    label='# Enter Keywords:',
    text='Press enter to add more',
    value=['open clusters', 'mass function', 'slope'],
    suggestions=['milky way', 'spiral arms', 'solar mass', 
                 'eight'],
    maxtags = 4,
    key='2')

###############################################################################
# Order list
order_list = 'lastUpdatedDate', 'relevance', 'submittedDate'
criterion = st.sidebar.selectbox(
    "Sort Criterion:",
    list(order_list))

###############################################################################
# Query
def build_query(keywords):
    query = f'all:"{keywords[0]}"'
    if len(keywords) > 1:
        query += " AND " + " AND ".join(["all:" + word for word in keywords[1:]])
    return query

paper_numbers = st.sidebar.slider('Number of papers for download:', 1, 50, 5)

query_words = build_query(keywords)

search = arxiv.Search(
  query = query_words,
  max_results = paper_numbers,
  sort_by = arxiv.SortCriterion(criterion)
)

###############################################################################
# dataframe results
df = pd.DataFrame(columns=['Title', 'Autors', 'Published'])
empty_slot = st.empty()

buffer = io.BytesIO()
if st.sidebar.button("Scan papers 🔍"):
    
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for result in search.results():
            
            # update dataframe
            # df = df.append({'Title': result.title, 
            #                 'Autors': (result.authors)[0], 
            #                 'Published': result.published}, ignore_index=True)
            
            df_update = pd.DataFrame({'Title': result.title, 
                                      'Autors': (result.authors)[0], 
                                      'Published': result.published}, ignore_index=True)
            
            df = pd.concat([df, df_update], ignore_index=True)
            
            empty_slot.dataframe(df)
            
            # download pdf
            pdf_url = result.pdf_url    
            file_name = result.title + '.pdf'
            response = requests.get(pdf_url)
            
            # save in object BytesIO
            zip_file.writestr(file_name, response.content)
        

    # streamlit download button 
    btn = st.download_button("Download papers", 
                             data=buffer.getvalue(), 
                             file_name="Papers-{}.zip".format(criterion))
            

st.sidebar.write('Developed by Anderson Almeida, for more information visit the GitHub of this application.')














