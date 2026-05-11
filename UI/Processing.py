import streamlit as st
def Upload_and_Process():
    st.title("Upload and Process")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        st.write(f"File '{uploaded_file.name}' uploaded successfully!")
        st.success("File processed successfully!")