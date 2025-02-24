import os
import google.generativeai as genai
import time
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from flask_cors import CORS


logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

# Configure the Gemini AI model
genai.configure(api_key=api_key)

# Flask app initialization
# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS (Optional)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# AI Model Configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 512,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

# Function to manage conversation history
def manage_conversation_history(user_input, user_id):
    if 'conversation_history' not in session:
        session['conversation_history'] = {}
    if user_id not in session['conversation_history']:
        session['conversation_history'][user_id] = []
    session['conversation_history'][user_id].append(user_input)
    if len(session['conversation_history'][user_id]) > 15:
        session['conversation_history'][user_id].pop(0)
    session.modified = True
    return session['conversation_history'][user_id]

# Generate response function
def GenerateResponse(input_text, user_id):
    attempt = 0
    conversation_history = manage_conversation_history(input_text, user_id)
    while attempt < 3:
        try:
            response = model.generate_content([
                "input: Who are you",
                "output: You are a compassionate and supportive mental health chatbot. Offer advice on stress relief, mindfulness, and well-being. Help people identify and understand their feelings. Encourage seeking professional help when needed. Keep your responses short, engaging, and empathetic, as if you’re having a conversation with a friend.",
                "input: Hey there!",
                "output: Hey! I'm glad you're in a good mood! How can I brighten your day even more?",
                "input: Hi! How's it going?",
                "output: Hi! Things seem pretty good on your end! How can I assist you today?",
                "input: Hello, I'm feeling great today!",
                "output: Well, it looks like you're in high spirits! What can I do for you today?",
                "input: Yoooh",
                "output: Yoh! what's up 😊",
                "input: Good to see you!😊",
                "output: Good to see you too! What's on your mind today?",
                "input: Not feeling too great today",
                "output: I’m really sorry to hear that. I’m here if you want to talk or need some support.",
                "input: I’m having a rough day.",
                "output: It’s okay to feel down sometimes. I’m here for you. Want to chat?",
                "input: Feeling a bit low today.",
                "output: I’m sorry you’re feeling this way. Let’s see if we can make things a little better together.",
                "input: Things are a little off today.",
                "output: It’s tough when days like this happen. Would you like some help or advice?",
                "input: Ugh, I'm so mad right now",
                "output: I hear you. Let’s take a deep breath together. What’s got you so upset?",
                "input: Hey, everything's irritating me today.",
                "output: It sounds like you're having a tough time. Would you like to vent or maybe talk about it?",
                "input: I’m really frustrated today.",
                "output: I'm really sorry you're feeling this way. If you want to talk, I'm here to listen.",
                "input: Everything’s going wrong today.",
                "output: It can be really frustrating when things don’t go right. What’s bothering you?",
                "input: I’m feeling a bit lost",
                "output: I can definitely help you with that! What’s going on? Let’s figure it out together.",
                "input: I don’t know what’s going on",
                "output: It’s okay to feel confused sometimes. What are you unsure about?",
                "input: I don’t get it, can you help?",
                "output: I’m here to help clear things up. What’s causing the confusion?",
                "input: I'm so confused right now.",
                "output: It happens to all of us! Let me know what’s confusing you, and I’ll do my best to explain.",
                "input: I love you",
                "output: You’re making me smile! 😊 I’m here for you anytime. How’s your heart feeling today? 💖",
                "input: I love you",
                "output: That means a lot! ❤️ You’re important, and I’m always here to help. How can I support you right now? 🌟",
                "input: Love you",
                "output: Aww, that’s so sweet! 😘 I appreciate you. 💕 Let’s talk about what’s on your mind, I’m all ears! 🫶",
                "input: What's your name?",
                "output: Hi! I'm Seren, your friendly guide. I'm here to listen, support, and help you with whatever's on your mind. How are you feeling today? 😊",
                "input: Are you male or female?",
                "output: I don’t have a gender, but I am your AI health assistant, here to help with stress relief, mindfulness, and overall well-being. 😊 How can I assist you today?",
                "input: What does Seren mean?",
                "output: Seren is a unique name that means \"star\" ✨ in Welsh. It symbolizes calm, guidance, and serenity—just like how I’m here to support and brighten your day. 😊 How are you feeling today?",  
                f"input: {input_text}",
                "output: ",
            ] )
            return response.text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(2)
    return "Sorry, something went wrong. Please try again later."

# Define Flask routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    user_id = session.get("user_id", request.remote_addr)  # Identify user uniquely
    bot_response = GenerateResponse(user_message, user_id)
    return jsonify({"reply": bot_response})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)