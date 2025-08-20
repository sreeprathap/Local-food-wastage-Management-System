import streamlit as st

st.set_page_config(page_title="Home",layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: green;'><u>Local Food Wastage Management System (LFWMS)</u></h1>",
    unsafe_allow_html=True
)
col1, col2, col3 = st.columns([1,2,1])  # middle column is wider
with col2:
    st.image("images/food.jpg", caption="Food Waste Management", use_container_width=True)

# Only link files from inside /pages
st.sidebar.page_link("pages/LFWMS.py", label="Food data Entry")
st.sidebar.page_link("pages/FoodWastageQuery.py", label="Basic Query")

st.write(f'''Welcome to the Local Food Wastage Management System (LFWMS). 
This platform is designed to connect restaurants and individuals with surplus 
food to those in need, helping reduce food waste and address food insecurity in 
your community. By leveraging technology, geolocation, and data analysis, LFWMS 
makes it easy to list, find, and claim surplus food while promoting responsible 
food management and social good. Join us in building a more sustainable and 
compassionate future—one meal at a time.''')
