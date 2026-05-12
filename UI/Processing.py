import os
import requests
import streamlit as st
import json
API_BASE_URL = os.getenv("API_URL", "http://api:8000")

def upload_and_process_ui(proj_id: str,user_name):
    def update_projects(proj_id: str, user_name: str,file_name):
        try:
            update_url = f"{API_BASE_URL}/users/{user_name}/projects"
            payload = {
                "project_id": proj_id,
                "file_name":file_name
            }
            response = requests.post(update_url, json=payload)
            if response.status_code == 200:
                st.success("User's related projects updated successfully!")
                return True
            else:
                st.error(f"Failed to update user's projects: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.ConnectionError as e:
            st.error(f"Connection Error during updating user's projects: {e}")
            return False
        except Exception as e:
            st.error(f"Unexpected error during updating user's projects: {str(e)}")
            return False

    st.header("Upload & Process Documents")
    st.write(f"**Target Project ID:** `{proj_id}`")
    uploaded_file = st.file_uploader("Choose a file (PDF)", type=["pdf"])
    with st.expander(" Advanced Processing Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.number_input("Chunk Size", value=512, step=64)
        with col2:
            overlap_size = st.number_input("Overlap Size", value=200, step=10)
        
        do_reset_check = st.checkbox("Reset Vector Database for this project?", value=False)
        do_reset = 1 if do_reset_check else 0
    if st.button("Upload & Process"):
        if not uploaded_file:
            st.error("Please upload a file first.")
            return
        upload_url = f"{API_BASE_URL}/api/v1/data/upload/{proj_id}?proj_ID={proj_id}"

        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
        }

        with st.spinner("Uploading document..."):
            try:
                upload_response = requests.post(upload_url, files=files)
                
                if upload_response.status_code != 200:
                    st.error(f"Upload Failed: {upload_response.status_code} - {upload_response.text}")
                    return
                upload_data = upload_response.json()
                saved_file_name = upload_response.json().get("File Name")
                st.toast("File uploaded! Starting processing...")
                
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection Error during upload: {e}")
                return
            except Exception as e:
                st.error(f"Unexpected error during upload: {str(e)}")
                return

        process_url = f"{API_BASE_URL}/api/v1/data/process/{proj_id}"
        process_payload = {
            "file_name": saved_file_name,
            "chunk_size": chunk_size,
            "overlap_size": overlap_size,
            "do_reset": do_reset
        }
        update_projects(proj_id, user_name, saved_file_name)
        
        with st.spinner("Processing & Vectorizing (This might take a few moments)..."):
            try:
                process_response = requests.post(process_url, json=process_payload)
                
                if process_response.status_code == 200:
                    st.success("Document successfully uploaded and processed!")
                    with st.expander("View Server Response"):
                        st.json(process_response.json())
                else:
                    st.error(f"Processing Failed: {process_response.status_code} - {process_response.text}")
                    
            except requests.exceptions.ConnectionError as e:
                st.error(f"Connection Error during processing: {e}")
            except Exception as e:
                st.error(f"Unexpected error during processing: {str(e)}")


def find_user_projects(prj_ids:list[str]):
        update_url = f"{API_BASE_URL}/user/specific"  
        response =  requests.post(update_url, json=prj_ids)
        st.sidebar.subheader("Your Projects")
        obj = response.json()
        for project in obj['Projects']:
            st.sidebar.write(f"- {project['project_name']} (ID: {project['project_id']})")
        return obj
    
