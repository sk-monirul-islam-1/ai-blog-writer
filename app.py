import streamlit as st
import google.generativeai as genai
from apikey import google_gemini_key
from gradio_client import Client
import os
import shutil

# Configure API key for generative AI
genai.configure(api_key=google_gemini_key)

# Generation configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}

# Model setup
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

# Image directory
save_dir = r"C:\doc\textImg"

# Create directory if it doesn't exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Initialize the client
client = Client("black-forest-labs/FLUX.1-schnell")

# Layout of the page
st.set_page_config(layout="wide")
# Title of app
st.title("Quick Blogger")
# Subheader of app
st.subheader("Write more in less time with your AI Partner")

# Sidebar input
with st.sidebar:
    st.title("Input Your Blog Details Master")
    st.subheader("Master please Enter Details of the Blog You want to Generate")
    # Title input box
    blog_title = st.text_input("Blog Title")
    # Keyword input box
    keywords = st.text_input("Keywords [comma-separated]")
    # Blog length
    num_words = st.slider("Length of Blog", min_value=200, max_value=1000, step=100)
    # Number of images
    num_images = st.number_input("Number of Images", min_value=1, max_value=6, step=1)
    
    # Blog generation prompt
    blog_prompt = (
        f'Generate a comprehensive, engaging blog post relevant to the given title \"{blog_title}\" and keywords \"{keywords}\". '
        f'Make sure to incorporate the keywords in the blog post. The blog should be approximately {num_words} words.'
    )

    # Submit button
    submit_button = st.button("Generate Blog")

# Generate blog and images when the button is clicked
if submit_button:
    with st.spinner("Generating your blog and images..."):
        # Generate the blog content
        blog_response = model.generate_content([blog_prompt])
        blog_content = blog_response.text.strip()
        
        # Display generated blog
        st.subheader("Generated Blog Content")
        st.write(blog_content)
        
        # Display word count for blog content only
        word_count = len(blog_content.split())
        st.write(f"Word Count: {word_count}")

        # Generate and display the specified number of images
        st.subheader("Generated Images")
        for i in range(num_images):
            try:
                # Generate an image description prompt using Gemini
                image_prompt_response = model.generate_content(
                    [f'Create a unique image description for a blog titled "{blog_title}". Ensure diversity across prompts.']
                )
                image_prompt = image_prompt_response.text.strip()
                
                # Generate the image using Gradio client
                result = client.predict(
                    prompt=image_prompt,
                    seed=i,  # Different seed for each image
                    randomize_seed=True,
                    width=1024,
                    height=1024,
                    num_inference_steps=4,
                    api_name="/infer"
                )

                # Extract the file path from the result tuple
                image_path = result[0]  # This is the path to the generated image

                # Define the destination path where you want to save the image
                save_path = os.path.join(save_dir, f"generated_image_{i + 1}.webp")

                # Move the image from the temporary location to the desired directory
                shutil.move(image_path, save_path)

                # Display the image in Streamlit with reduced size
                st.image(save_path, caption=f"Generated Image {i + 1}", width=400)

            except Exception as e:
                st.error(f"Error generating image {i + 1}: {e}")

    # Remove spinner after completion
    st.success("Blog and images generation complete!")