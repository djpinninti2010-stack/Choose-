import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

# Core dependencies
import requests
import cv2
import speech_recognition as sr
import pyttsx3
from google import genai

class CruiseAIApp(App):
    def build(self):
        self.title = "Cruise AI"
        
        # Initialize Google GenAI Client
        # Set your API key in environment variables or pass directly: genai.Client(api_key="YOUR_KEY")
        api_key = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
        self.ai_client = genai.Client(api_key=api_key) if api_key != "YOUR_GEMINI_API_KEY_HERE" else None

        # Main Layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title Label
        title_label = Label(
            text="🚀 Cruise AI Assistant", 
            size_hint_y=None, 
            height=40, 
            font_size='20sp', 
            bold=True
        )
        layout.add_widget(title_label)

        # Output / Log Area
        self.scroll_view = ScrollView(size_hint=(1, 0.6))
        self.output_label = Label(
            text="Welcome to Cruise AI!\nType a prompt or tap Voice Command to begin.", 
            size_hint_y=None, 
            text_size=(None, None), 
            halign='left', 
            valign='top'
        )
        self.output_label.bind(texture_size=self.output_label.setter('size'))
        self.scroll_view.add_widget(self.output_label)
        layout.add_widget(self.scroll_view)

        # Text Input Area
        self.user_input = TextInput(
            hint_text="Ask Cruise AI something...", 
            multiline=False, 
            size_hint_y=None, 
            height=50
        )
        layout.add_widget(self.user_input)

        # Buttons Grid
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        send_btn = Button(text="Send Prompt", on_press=self.send_text_prompt)
        voice_btn = Button(text="🎙 Voice Input", on_press=self.start_voice_thread)
        camera_btn = Button(text="📷 Camera Test", on_press=self.test_camera)
        
        btn_layout.add_widget(send_btn)
        btn_layout.add_widget(voice_btn)
        btn_layout.add_widget(camera_btn)
        
        layout.add_widget(btn_layout)

        return layout

    def update_output(self, text):
        """Update the output UI safely from any thread."""
        Clock.schedule_once(lambda dt: self._append_text(text))

    def _append_text(self, text):
        self.output_label.text += f"\n\n{text}"

    def speak_text(self, text):
        """Text-to-Speech execution."""
        def tts_task():
            try:
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                self.update_output(f"[TTS Error]: {e}")
        
        threading.Thread(target=tts_task, daemon=True).start()

    def send_text_prompt(self, instance):
        prompt = self.user_input.text.strip()
        if not prompt:
            return
        
        self.user_input.text = ""
        self.update_output(f"You: {prompt}")

        def ai_task():
            if not self.ai_client:
                self.update_output("Cruise AI: Please set your GEMINI_API_KEY inside main.py.")
                return

            try:
                response = self.ai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                answer = response.text
                self.update_output(f"Cruise AI: {answer}")
                self.speak_text(answer)
            except Exception as e:
                self.update_output(f"[AI Error]: {e}")

        threading.Thread(target=ai_task, daemon=True).start()

    def start_voice_thread(self, instance):
        self.update_output("Listening for voice input...")
        threading.Thread(target=self.listen_voice, daemon=True).start()

    def listen_voice(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                self.update_output(f"Heard: {text}")
                
                # Auto-send recognized voice text to AI
                Clock.schedule_once(lambda dt: self._trigger_ai_from_voice(text))
        except sr.WaitTimeoutError:
            self.update_output("[Voice]: Listening timed out.")
        except sr.UnknownValueError:
            self.update_output("[Voice]: Could not understand audio.")
        except Exception as e:
            self.update_output(f"[Voice Error]: {e}")

    def _trigger_ai_from_voice(self, text):
        self.user_input.text = text
        self.send_text_prompt(None)

    def test_camera(self, instance):
        def camera_task():
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    self.update_output("[Camera]: Unable to open camera unit.")
                    return
                
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    self.update_output(f"[Camera]: Captured frame successfully! Size: {frame.shape[1]}x{frame.shape[0]}")
                else:
                    self.update_output("[Camera]: Failed to capture image frame.")
            except Exception as e:
                self.update_output(f"[Camera Error]: {e}")

        threading.Thread(target=camera_task, daemon=True).start()

if __name__ == '__main__':
    CruiseAIApp().run()
