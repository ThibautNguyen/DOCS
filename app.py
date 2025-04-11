# coding: utf-8
import streamlit as st

# Page configuration
st.set_page_config(
    page_title='Metadata Manager',
    page_icon='📊',
    layout='wide'
)

# Title and introduction
st.title('Metadata Management System')
st.write('This application allows you to manage metadata for your datasets.')
st.write('Test modification for Git tracking')

# Creating cards for different features
col1, col2 = st.columns(2)

with col1:
    st.info('### 📝 Metadata Entry')
    st.write('''
    Create and edit metadata records easily.
    
    Features:
    - Structured form
    - Automatic validation
    - JSON and TXT storage
    ''')
    # Will be implemented in the next step
    st.write('Entry form coming soon...')

with col2:
    st.info('### 🔍 Search')
    st.write('''
    Search quickly through existing metadata.
    
    Features:
    - Keyword search
    - Category filtering
    - Direct access to records
    ''')
    # Will be implemented in the next step
    st.write('Search functionality coming soon...')

# Footer
st.markdown('---')
st.write('© 2025 - Metadata Management System v1.0')
