import os
import json
import streamlit as st
from groq import Groq

# Streamlit page configuration
st.set_page_config(
    page_title="Amber Salon - ChatBot",
    page_icon="💇‍♀️",
    layout="centered"
)

# Inject custom JavaScript for sticky title and buttons, and scrolling behavior
st.markdown(
    """
    <style>
    #sticky {
        position: fixed;
        top: 0;
        width: 100%;
        background-color: white;
        z-index: 1000;
        border-bottom: 2px solid #f1f1f1;
        padding: 10px 0;
    }
    body {
        padding-top: 100px; /* Adjust based on sticky height */
    }
    </style>
    
    <script>
    function scrollToInput() {
        var inputBox = document.querySelector('[data-testid="stTextArea"]');
        if (inputBox) {
            inputBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
            inputBox.focus();
        }
    }
    </script>
    """,
    unsafe_allow_html=True
)

# Load API Key from config file
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Save the API key to environment variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize Groq client
client = Groq()

# Initialize the chat history as streamlit session state if not present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize `user_prompt` as None to avoid NameError
user_prompt = None

# Load salon details from a text file
salon_info_file = os.path.join(working_dir, "salon_info.txt")
with open(salon_info_file, "r") as f:
    salon_info = f.read()

# Sticky title and buttons container using JavaScript
st.markdown('<div id="sticky">', unsafe_allow_html=True)
st.title("💇‍♀️ Amber Salon - ChatBot")

# Add service suggestion buttons
col1, col2, col3, col4, col5 = st.columns(5)

# Button Presses with Automated Responses (independent `if` conditions)
if col1.button("Is anyone available to chat?"):
    user_prompt = "Is anyone available to chat?"
    assistant_response = "Yes! Welcome to Amber Salon. We are available to chat. How can we help you today?"
    st.markdown("<script>scrollToInput();</script>", unsafe_allow_html=True)

if col2.button("Book appointment for haircut"):
    user_prompt = "I want to book an appointment."
    assistant_response = "Sure! To book your haircut appointment, please visit our website at www.ambersalon.com and fill in your basic details along with your preferred date and time. We’ll take care of the rest!"
    st.markdown("<script>scrollToInput();</script>", unsafe_allow_html=True)

if col3.button("What type of services do you offer?"):
    user_prompt = "What type of services do you offer?"
    assistant_response = (
        "We offer a wide range of services, including:\n"
        "- Haircuts\n"
        "- Manicures\n"
        "- Pedicures\n"
        "- Facials\n"
        "- Hair Coloring\n"
        "- Hair Treatments\n"
        "- Waxing\n"
        "- Makeup Services\n"
        "- Bridal Packages\n"
        "- Massage Therapy\n"
        "Let us know which service you're interested in!"
    )
    st.markdown("<script>scrollToInput();</script>", unsafe_allow_html=True)

if col4.button("What are your salon working hours?"):
    user_prompt = "What are your salon working hours?"
    assistant_response = (
        "Our salon is open Monday to Saturday from 9 AM to 7 PM, and on Sundays from 10 AM to 4 PM."
    )
    st.markdown("<script>scrollToInput();</script>", unsafe_allow_html=True)

if col5.button("Where are your offices located?"):
    user_prompt = "Where is your salon located?"
    assistant_response = "We are located at 123 Amber Street, Kamloops, Canada. Come visit us anytime!"
    st.markdown("<script>scrollToInput();</script>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Append the user prompt and automated response to chat history if a button is pressed
if user_prompt:
    # Add user's question to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    # Add assistant's response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

# Display the updated chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user's message (if needed for custom queries)
user_prompt = st.chat_input("Ask a question...")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Check if user is asking about the salon (queries like "about your salon" or "tell me about your salon")
    if "about your salon" in user_prompt.lower() or "tell me about your salon" in user_prompt.lower():
        assistant_response = salon_info
    else:
        # Prepare the chat history for the model if it's not about the salon info
        messages = [
            {"role": "system", "content": "You are a helpful assistant at a salon."},
            *st.session_state.chat_history
        ]

        # Get the assistant's response using Groq API for custom questions
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )
            assistant_response = response.choices[0].message.content
        except Exception as e:
            assistant_response = "Sorry, something went wrong. Please try again."
            st.error(f"Error: {e}")

    # Append the assistant's response to the chat history
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

    # Display the assistant's response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
