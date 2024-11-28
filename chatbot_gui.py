import tkinter as tk
from tkinter import ttk, scrolledtext
from model import MedicalChatbot
from datetime import datetime

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Chatbot Assistant")
        self.root.geometry("800x600")
        self.chatbot = MedicalChatbot()
        self.current_symptoms = []
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('ChatFrame.TFrame', background='#f0f0f0')
        self.style.configure('Input.TFrame', background='white')
        
        self.setup_gui()
        self.start_chat()

    def setup_gui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Chat display area
        self.chat_frame = ttk.Frame(main_container, style='ChatFrame.TFrame')
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create scrolled text widget for chat
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 10),
            background='#ffffff',
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Input area
        input_frame = ttk.Frame(main_container, style='Input.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 5))

        # Text input
        self.input_field = ttk.Entry(
            input_frame,
            font=("Helvetica", 10)
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message())

        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message
        )
        send_button.pack(side=tk.RIGHT)

        # Current symptoms display
        self.symptoms_label = ttk.Label(
            main_container,
            text="Current Symptoms: None",
            font=("Helvetica", 9),
            wraplength=780
        )
        self.symptoms_label.pack(fill=tk.X, pady=5)

    def start_chat(self):
        welcome_message = (
            "👋 Hello! I'm your Medical Assistant.\n\n"
            "I can help you identify possible medical conditions based on your symptoms.\n"
            "Please tell me what symptoms you're experiencing, one at a time.\n"
            "Type 'done' when you've finished listing your symptoms."
        )
        self.display_bot_message(welcome_message)

    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.display_user_message(message)
            self.process_message(message)

    def process_message(self, message):
        message = message.lower().strip()
        
        # Handle greetings
        if self.is_greeting(message):
            self.display_bot_message("Hello! I'm Dr. Bot. Please tell me what symptoms you're experiencing.")
            return
            
        # Handle goodbyes
        if self.is_goodbye(message):
            self.display_bot_message("Take care! Remember to consult a real doctor if symptoms persist. Goodbye!")
            return

        # Extract symptoms from natural language
        if self.contains_symptoms(message):
            # Clean the message
            message = self.clean_message(message)
            
            # Extract symptoms
            extracted_symptoms = self.chatbot.extract_symptoms_from_text(message)
            
            if extracted_symptoms:
                # Add new symptoms to current list
                new_symptoms = []
                for symptom in extracted_symptoms:
                    if symptom not in self.current_symptoms:
                        self.current_symptoms.append(symptom)
                        new_symptoms.append(symptom)
                
                # Construct natural response
                if new_symptoms:
                    response = f"I understand that you're experiencing {self.format_symptom_list(new_symptoms)}. "
                    
                    # Show all current symptoms
                    if len(self.current_symptoms) > len(new_symptoms):
                        response += f"\nSo far, you've told me about: {self.format_symptom_list(self.current_symptoms)}. "
                    
                    response += "\nAre you experiencing any other symptoms?"
                    self.display_bot_message(response)
                else:
                    self.display_bot_message("I've already noted those symptoms. Are you experiencing anything else?")
            else:
                self.display_bot_message("I'm not sure I understood your symptoms. Could you describe them differently?")
            return

        # Handle "no more symptoms"
        if self.is_no_more_symptoms(message):
            if self.current_symptoms:
                self.display_bot_message("Let me analyze your symptoms and provide a possible diagnosis...")
                self.make_prediction()
            else:
                self.display_bot_message("I haven't noted any symptoms yet. Could you tell me what's bothering you?")
            return

    def is_greeting(self, message):
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in message for greeting in greetings)

    def is_goodbye(self, message):
        goodbyes = ['bye', 'goodbye', 'see you', 'thanks', 'thank you']
        return any(goodbye in message for goodbye in goodbyes)

    def contains_symptoms(self, message):
        symptom_indicators = [
            'i have', 'i am', "i'm", 'suffering', 'experiencing',
            'feeling', 'got', 'having', 'with', 'feel'
        ]
        return any(indicator in message for indicator in symptom_indicators)

    def is_no_more_symptoms(self, message):
        no_more = ['no', 'none', 'nothing', 'that\'s all', 'thats all', 'done']
        return any(phrase in message for phrase in no_more)

    def clean_message(self, message):
        # Remove common phrases that aren't symptoms
        phrases_to_remove = [
            'i am', 'i have', 'i\'m', 'suffering from', 'experiencing',
            'feeling', 'with', 'got', 'having'
        ]
        for phrase in phrases_to_remove:
            message = message.replace(phrase, '')
        return message

    def format_symptom_list(self, symptoms):
        """Format symptoms list in a natural way"""
        symptoms = [s.replace('_', ' ') for s in symptoms]
        if len(symptoms) == 1:
            return symptoms[0]
        elif len(symptoms) == 2:
            return f"{symptoms[0]} and {symptoms[1]}"
        else:
            return ', '.join(symptoms[:-1]) + f", and {symptoms[-1]}"

    def make_prediction(self):
        predictions = self.chatbot.predict_condition(self.current_symptoms)
        
        # Get the top prediction (first in the list)
        main_condition, main_confidence = predictions[0]
        
        # Format the prediction message
        result = "\nPrediction Results:\n"
        result += "=" * 40 + "\n\n"
        
        # Show top 3 predictions with confidence
        result += "Top 3 possible conditions:\n"
        for condition, confidence in predictions:
            result += f"• {condition} (Confidence: {confidence:.1f}%)\n"
        
        result += "\n" + "=" * 40 + "\n"
        
        # If confidence is too low, add a warning
        if main_confidence < 50:
            result += "\n⚠️ Warning: Low confidence prediction. Please provide more symptoms for a more accurate diagnosis.\n\n"
        
        # Get description and precautions for the top prediction
        description = self.chatbot.get_description(main_condition)
        precautions = self.chatbot.get_precautions(main_condition)
        
        result += f"\nDetailed information for top prediction: {main_condition}\n"
        result += f"\nDescription:\n{description}\n"
        result += "\nPrecautions:\n"
        for i, precaution in enumerate(precautions, 1):
            result += f"{i}. {precaution}\n"
        
        self.display_bot_message(result)
        
        # If confidence is low, prompt for more symptoms
        if main_confidence < 30:
            self.display_bot_message("\nWould you like to add more symptoms for a more accurate diagnosis? (Type 'yes' to continue or 'done' to finish)")
        else:
            self.display_bot_message("\nWould you like to check for other symptoms? (Type 'yes' to start over)")
        
        self.current_symptoms = []
        self.update_symptoms_display()

    def display_bot_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"\n🤖 Bot [{timestamp}]:\n", "bot_prefix")
        self.chat_display.insert(tk.END, f"{message}\n", "bot_message")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags
        self.chat_display.tag_configure("bot_prefix", foreground="#007AFF")
        self.chat_display.tag_configure("bot_message", foreground="#000000")

    def display_user_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"\nYou [{timestamp}]:\n", "user_prefix")
        self.chat_display.insert(tk.END, f"{message}\n", "user_message")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags
        self.chat_display.tag_configure("user_prefix", foreground="#28a745")
        self.chat_display.tag_configure("user_message", foreground="#000000")

    def update_symptoms_display(self):
        if self.current_symptoms:
            symptoms_text = "Current Symptoms: " + ", ".join(self.current_symptoms)
        else:
            symptoms_text = "Current Symptoms: None"
        self.symptoms_label.config(text=symptoms_text)

def main():
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 