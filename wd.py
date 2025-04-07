import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# --- Configuration ---
# Set page configuration (optional but good practice)
st.set_page_config(
    page_title="Gemini Image Analyzer",
    page_icon="✨",
    layout="centered",
)

# --- API Key Handling ---
# Preferred method: Use Streamlit secrets
try:
    # Attempt to get the API key from Streamlit secrets
    api_key = os.getenv("GOOGLE_API_KEY")
except KeyError:
    st.error("Error: GOOGLE_API_KEY not found in environment secrets.")
    st.info("Please add your Google API Key to the environment secrets configuration.")
    st.stop() # Stop execution if the key isn't found

# Configure the Generative AI SDK
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring Google AI SDK: {e}")
    st.stop()

# --- Model Initialization ---
# Initialize the Gemini Pro Vision model
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error initializing Gemini model: {e}")
    st.info("Check your API key and network connection.")
    st.stop()

# --- Helper Function ---
def get_gemini_response(image: Image.Image, prompt: str):
    """
    Sends the image and prompt to Gemini Pro Vision and returns the response.

    Args:
        image (PIL.Image.Image): The image to analyze.
        prompt (str): The text prompt to accompany the image.

    Returns:
        str: The text response from Gemini, or an error message.
    """
    if image is None:
        return "Error: No image provided."

    try:
        # Prepare the content payload
        # The API expects a list containing the prompt and the image
        content = [prompt, image]

        # Generate content
        response = model.generate_content(content, stream=False) # Use stream=False for simpler handling

        # Handle potential safety blocks or empty responses
        if not response.parts:
             # Check prompt feedback for blocking reasons
            try:
                feedback = response.prompt_feedback
                block_reason = feedback.block_reason.name if feedback.block_reason else "Unknown"
                return f"❌ Response blocked. Reason: {block_reason}"
            except (ValueError, AttributeError):
                 return "❌ Response was empty or blocked for an unknown reason."

        return response.text

    except Exception as e:
        return f"An error occurred: {e}"

# --- Streamlit UI ---
st.title("✨ Gemini Image Analyzer")
st.write("Upload an image and ask Gemini about it!")

# User prompt input
user_prompt = st.text_input("What do you want to ask about the image?", "Describe this image in detail.")

# Image uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

image_to_display = None
image_for_gemini = None

if uploaded_file is not None:
    # Read the file content into bytes
    image_bytes = uploaded_file.getvalue()

    try:
        # Open the image using PIL
        image_for_gemini = Image.open(io.BytesIO(image_bytes))
        # Display the uploaded image
        st.image(image_for_gemini, caption='Uploaded Image.', use_column_width=True)
        image_to_display = True # Flag that image is ready
    except Exception as e:
        st.error(f"Error loading image: {e}")
        uploaded_file = None # Reset uploader if image is invalid

# Analyze button
if image_to_display: # Only show button if image is successfully loaded
    if st.button("Analyze Image"):
        if image_for_gemini and user_prompt:
            with st.spinner("Gemini is thinking... 🤔"):
                response_text = get_gemini_response(image_for_gemini, user_prompt)
            st.subheader("Gemini's Response:")
            st.markdown(response_text) # Use markdown for better formatting
        elif not user_prompt:
            st.warning("Please enter a prompt.")
        else:
            st.warning("Please upload a valid image first.")

st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.info(
    "This app uses the Google Gemini Pro Vision model "
    "via the Google Generative AI SDK to analyze uploaded images based on your prompt."
)
