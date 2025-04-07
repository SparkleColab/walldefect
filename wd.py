import streamlit as st
from google import genai
from PIL import Image
import io
import os

# --- Configuration ---
# Set page configuration (optional but good practice)
st.set_page_config(
    page_title="VauntCo Image Analyzer",
    page_icon="✨",
    layout="centered",
)

# --- API Key Handling ---
# Preferred method: Use Streamlit secrets
try:
    # Attempt to get the API key from Streamlit secrets
   GOOGLE_API_KEY = os.getenv("Google_API_KEY")
except KeyError:
    st.error("Error: GOOGLE_API_KEY not found in environment secrets.")
    st.info("Please add your Google API Key to the environment secrets configuration.")
    st.stop() # Stop execution if the key isn't found

# Configure the Generative AI SDK
try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error configuring Google AI SDK: {e}")
    st.stop()


# --- Model Selection ---
# Use the VauntAI 1.5 Pro model (which handles images)
# Or use 'gemini-1.5-flash-latest' for potentially faster responses
MODEL_NAME = "gemini-1.5-flash-latest"

# --- Streamlit App UI ---
#st.set_page_config(page_title="Image Analyzer with VauntAI", layout="wide")
st.title("🖼️ Image Analyzer for Wall Defects")
st.write("Upload an image to identify wall defects. ")

# --- Image Upload ---
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# --- Processing and Display ---
if uploaded_file is not None:
    try:
        # Read the uploaded image file
        image_bytes = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(image_bytes))

        # Display the uploaded image
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("") # Add some space

        # Prepare the prompt for VauntAI (Image + Text)
        # You can customize the text prompt
        prompt_parts = [
            "Describe visible defects on the wall, identify any root causes and recommend any suggested remedies",
            image, # Send the PIL Image object directly
        ]

        # --- Call VauntAI API ---
        st.write(f"Sending image to VauntAI ({MODEL_NAME})...")
        response = None # Initialize response variable
        gemini_response_received = False # Flag to track if we got *any* response object

        try:
            # Generate content
            response = client.models.generate_content(model=MODEL_NAME, contents = [image, "Describe visible defects on the wall, identify any root causes and recommend any suggested remedies"])
            gemini_response_received = True # Set flag as we got a response object

        # --- Confirmation ---
        # *Crucially*, print confirmation immediately after the call returns,
        # regardless of whether response.text access works later.
        finally:
            if gemini_response_received:
                st.success("✅ Confirmation: Received a response object from VauntAI.")
            else:
                # This part might not be reached if generate_content raises an error before returning
                st.warning("⚠️ Confirmation: Did not receive a response object from VauntAI (API call might have failed).")

        # --- Display VauntAI Response ---
        if response and gemini_response_received:
            try:
                st.write("---")
                st.subheader("VauntAI's Response:")
                # Accessing response.text can sometimes fail if the response was blocked etc.
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error accessing or displaying the text from VauntAI's response: {e}")
                st.info("Even though displaying failed, a response object *was* received.")
                st.write("Raw Response Object (for debugging):")
                st.json(str(response)) # Show the raw response structure if text access fails
        elif gemini_response_received:
             st.warning("Received a response object from VauntAI, but it appears empty or unusable.")
             st.write("Raw Response Object (for debugging):")
             st.json(str(response)) # Show the raw response structure

    except genai.types.BlockedPromptException as bpe:
        st.error("❌ VauntAI API Error: The request was blocked. This might be due to safety settings or harmful content.")
        st.error(f"Details: {bpe}")
    except Exception as e:
        st.error(f"An unexpected error occurred during processing: {e}")
else:
    st.info("Please upload an image file to analyze.")






