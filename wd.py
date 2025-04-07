import google.generativeai as genai  
from PIL import Image  
import streamlit as st  
import os  
import requests
from IPython.display import display, Markdown

# Set the initial configuration for the Streamlit app
st.set_page_config(page_title="Wall Defect App", initial_sidebar_state="expanded", layout="wide") 
st.title("Wall Defect Detection") 

# Fetch the Google API key from environment variables
google_genai_key = os.getenv("GOOGLE_API_KEY")



with st.sidebar:
    st.title("Select an image")  # Sidebar title
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])  
    if uploaded_file:
        image = Image.open(uploaded_file)  
        st.image(image, caption='Uploaded Image') 

if image:
    # Choose a model that supports vision input
    # Examples: 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro-vision' (older)
    Model_Name = "gemini-1.5-flash-latest" # Or another vision model
    # Define your text prompt
    #prompt_text = "Describe this image in detail."#@param: {type: "string"}
    '''
    # Combine the text prompt and the PIL image object in a list
    prompt_parts = [
        prompt_text,
        image, # Pass the PIL Image object directly
    ]
    '''
    print("\nSending prompt to Gemini...")
    try:
        # Generate content
        
        response = client.models.generate_content(
            model=Model_Name,
            contents=[
                image,
                "Please describe the surface defects visible on the wall, identify root causes and suggest possible corrections"
            ]
        )

        st.display(image)
        st.Markdown(response.text)

        # Print the response
        print("\n--- Gemini Response ---")
        print(response.text)
        print("-----------------------")

    except Exception as e:
        print(f"\nAn error occurred calling the Gemini API: {e}")
        # You might want to inspect response.prompt_feedback here too for safety ratings etc.
        # try:
        #    print(response.prompt_feedback)
        # except:
        #    pass
