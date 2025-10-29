from openai import OpenAI
import pyttsx3
import speech_recognition as sr
import threading

# ----------------- Setup -----------------
# Initialize OpenAI client
client = OpenAI(
    base_url="https://url.api",
    api_key="openai-apikey",
)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# ----------------- Functions -----------------
def speak_text(text):
    """Speak text safely in a separate thread"""
    def run_speech():
        # Create a NEW engine instance each time to avoid resource locks
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
        engine.stop()  # Explicitly stop the engine
    
    t = threading.Thread(target=run_speech)
    t.start()
    t.join()  # Wait for TTS to finish

def listen():
    """Listen from microphone and return recognized text"""
    try:
        with sr.Microphone() as source:
            print("\n🎙️ Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
        
        print("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"✅ You said: {text}")
        return text
    
    except sr.WaitTimeoutError:
        print("⏱️ No speech detected. Please try again.")
        return None
    except sr.UnknownValueError:
        print("❌ Could not understand audio. Try again.")
        return None
    except sr.RequestError as e:
        print(f"❌ Recognition error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# ----------------- Conversation -----------------
conversation = [
    {"role": "system", "content": "You are Jarvis — an intelligent, witty, and loyal AI assistant. Be concise, clear, and slightly humorous."}
]

print("🤖 Jarvis is online! Speak to chat with Jarvis.")
print("Say 'goodbye' or 'please quit' to exit.\n")

speak_text("Hello! Jarvis is online and ready to assist you.")

while True:
    user_input = listen()
    
    if not user_input:
        continue  # If recognition failed, try again

    # Check for exit commands
    if any(keyword in user_input.lower() for keyword in ["goodbye", "please quit", "exit"]):
        speak_text("Goodbye, boss! Until next time.")
        print("Jarvis: Goodbye, boss! 🫡")
        break

    # Add user message
    conversation.append({"role": "user", "content": user_input})

    try:
        # Get Jarvis response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0,
            max_tokens=max,
        )

        reply = response.choices[0].message.content.strip()
        print(f"\n🤖 Jarvis: {reply}")

        # Speak reply
        speak_text(reply)

        # Add to conversation
        conversation.append({"role": "assistant", "content": reply})
    
    except Exception as e:
        error_msg = "I encountered an error processing your request."
        print(f"❌ Error: {e}")
        speak_text(error_msg)
