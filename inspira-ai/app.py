import google.generativeai as genai
import random
import gradio as gr
import os 

# --- Configuration ---
# Load the API key from an environment variable
ENV_VAR_NAME = "GOOGLE_API_KEY_INSPI" # Define your chosen environment variable name once
GOOGLE_API_KEY = os.getenv(ENV_VAR_NAME)

# Check if the environment variable was successfully loaded
if not GOOGLE_API_KEY:
    print(f"CRITICAL ERROR: The {ENV_VAR_NAME} environment variable is not set.")
    print("The application cannot run without it. Please set it in your deployment environment (e.g., Hugging Face Spaces secrets).")
    # For local testing, you might have a different message or fallback,
    # but for code going to GitHub/deployment, exiting is usually safest.
    exit() # Stop the script if the key isn't found

# Configure the Google AI SDK with the loaded key
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Google AI SDK configured successfully.")
except Exception as e:
    print(f"Error configuring Google AI SDK with the provided key: {e}")
    print("Please ensure the API key in the environment variable is correct and valid.")
    exit()

# ... rest of your script (MODEL_NAME, functions, Gradio Blocks, etc.)

MODEL_NAME = "gemini-1.5-flash"

def generate_quote_for_ui(topic):
    if not topic or topic.strip() == "":
        return "Please enter a topic to get a quote."
    # ... (rest of your generation logic remains the same) ...
    generation_config = {
        "temperature": 0.7,
        "max_output_tokens": 80,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        prompt_templates = [
            f"Generate a short, insightful, and original quote about '{topic}'. The quote should be a single sentence.",
            f"Craft a profound and inspiring one-sentence quote on the subject of {topic}.",
            f"What is a wise and memorable saying about {topic}? Keep it to one sentence.",
            f"Compose a unique, concise quote that captures the essence of {topic}.",
            f"Give me an original aphorism or maxim related to {topic}, as a single sentence."
        ]
        prompt = random.choice(prompt_templates)
        print(f"Generating quote for topic: '{topic}' with prompt: '{prompt}'")
        response = model.generate_content(prompt)
        if response.candidates:
            quote = response.text.strip()
        else:
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                print(f"Prompt blocked for topic '{topic}': {response.prompt_feedback.block_reason_message}")
                return "Sorry, your request was blocked. Please try a different topic."
            quote = ""
        if quote.startswith('"') and quote.endswith('"'): quote = quote[1:-1]
        if quote.startswith("'") and quote.endswith("'"): quote = quote[1:-1]
        if not quote: return f"Could not generate a specific quote for '{topic}'. Try rephrasing."
        return f'"{quote}" - InspiraAI'
    except Exception as e:
        print(f"Error during Google AI generation for topic '{topic}': {e}")
        if "API key not valid" in str(e).lower() or "permission_denied" in str(e).lower() or "authentication" in str(e).lower():
            return "Error: Your Google API key seems invalid..."
        return "Sorry, there was an error communicating with the AI. Please try again."

# --- Gradio Interface Definition using gr.Blocks ---
with gr.Blocks(theme=gr.themes.Soft()) as iface: # Using a theme for a slightly different look
    gr.Markdown(
        """
        # ✨ InspiraAI Quote Generator ✨
        Get an AI-generated quote on any topic you can think of! Powered by INSIPRA-AI.
        """
    )
    with gr.Row():
        # The `scale` parameter in Blocks can influence width distribution.
        # A higher scale value relative to other elements in the same row makes it wider.
        # Since these are in their own rows effectively, we can try to make them wide.
        topic_input = gr.Textbox(
            label="Enter a topic or phrase for your quote:",
            placeholder="e.g., the beauty of silence, overcoming challenges...",
            # scale=4 # Experiment with scale if you have multiple items in a row
            elem_id="topic_input_textbox" # Adding an ID for potential CSS
        )

    with gr.Row():
        generate_button = gr.Button("Generate Quote", variant="primary") # Added a button

    with gr.Row():
        quote_output = gr.Textbox(
            label="InspiraAI Says:",
            lines=5, # Increased lines for more space
            interactive=False, # Output textbox shouldn't be editable by user
            # scale=4
            elem_id="quote_output_textbox" # Adding an ID for potential CSS
        )

    gr.Examples(
        examples=[
            ["the power of dreams"],
            ["finding joy in small things"],
            ["the future of artificial intelligence"],
            ["a rainy sunday morning"]
        ],
        inputs=topic_input, # Link examples to the input textbox
        # outputs=quote_output, # Not strictly needed if button triggers update
        # fn=generate_quote_for_ui, # Not needed here if button has the action
        # cache_examples=False # Depending on if you want to cache example runs
    )

    # Define the action for the button
    generate_button.click(fn=generate_quote_for_ui, inputs=topic_input, outputs=quote_output)

# --- Main Application Launch ---
# ... (all your other imports, GOOGLE_API_KEY loading, genai.configure,
#      your generate_quote_for_ui function, and your gr.Blocks UI definition
#      should be above this block) ...
if __name__ == "__main__":
    print("Preparing to launch InspiraAI Quote Generator...")

    ENV_VAR_NAME = "GOOGLE_API_KEY_INSPI"
    GOOGLE_API_KEY = os.getenv(ENV_VAR_NAME)
    if not GOOGLE_API_KEY:
        print(f"CRITICAL ERROR: The {ENV_VAR_NAME} environment variable is not set.")
        exit()
    try:
        # genai.configure(api_key=GOOGLE_API_KEY) # This should already be done
        pass # Assuming genai is configured earlier
    except Exception as e:
        print(f"Error related to Google AI SDK configuration: {e}")
        exit()

    # Get PORT from environment variable provided by deployment platforms like Render.
    # Default to 7860 if PORT is not set (for easy local running).
    default_port_for_local_dev = 7860
    port_str = os.environ.get("PORT") # os.environ.get returns a string or None

    if port_str is not None:
        try:
            port = int(port_str)
        except ValueError:
            print(f"Warning: PORT environment variable '{port_str}' is not a valid integer. Using default port {default_port_for_local_dev}.")
            port = default_port_for_local_dev
    else:
        print(f"Info: PORT environment variable not set. Using default port {default_port_for_local_dev} for local development.")
        port = default_port_for_local_dev

    print(f"INFO: Launching Gradio app on 0.0.0.0:{port}")

    
    iface.launch(server_name="0.0.0.0", server_port=port, share=False)