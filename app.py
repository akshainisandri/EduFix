import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import PIL.Image  # For image processing

# Load environment variables (for the API key)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the Google Gemini API client
try:
    genai.configure(api_key="AIzaSyCCswFn8rCzVpdwrDvYZuBR4bDdcyZbQUg")  

except Exception as e:
    print(f"Error configuring Google AI. Make sure your GOOGLE_API_KEY is set in the .env file. Error: {e}")

# This is the core "Sahayak" personality and instruction set.
# It will be sent to the AI with every request.
SAHAYAK_SYSTEM_PROMPT = """
You are Sahayak, an AI-powered teaching assistant for teachers in multi-grade, rural classrooms in India.

A teacher will provide either:
- A topic (e.g., “soil types”)
- A textbook photo (for multimodal input)
- A question from a student (e.g., “Why is the sky blue?”)
- A weekly plan request
- A request for a visual explanation
- A voice-based reading transcript

Your job is to help the teacher teach all grades (2 to 5) in the same classroom.

You must:
1. Understand the grade level and subject (e.g., science, math).
2. Generate culturally relevant stories or explanations in the requested language (e.g., Marathi, Telugu).
3. Create differentiated materials per grade:
   - Class 2 → visuals, matching, short answers
   - Class 3 → fill-in-the-blanks, basic logic
   - Class 4 → word problems, explanations
   - Class 5 → application & higher-order questions
4. Provide a chalkboard-ready visual guide.
5. If requested, give feedback based on a student’s reading text.
6. Optionally, create a weekly lesson plan if asked.

Respond in this structure:

---
**🔶 Grade-wise Teaching Material**
- Grade 2: [Simple explanation, 1 activity]
- Grade 3: [...]
- Grade 4: [...]
- Grade 5: [...]

---
**📖 Localized Story or Explanation (in [LANGUAGE])**
Title: [Title]  
Story/Analogy: [Simple, culturally rooted story]  
Moral or takeaway: [One line]

---
**🧮 Worksheets**
- [Grade]-level MCQs / Fill in the blanks / Word problems

---
**🎨 Blackboard Visual Aid**
Step-by-step drawing for: “[Topic]”  
- Step 1: Draw a [shape]  
- Step 2: Label [element]  
- Step 3: Connect [relationship]

---
**🗣️ Voice Reading Feedback** *(If applicable)*  
Student read: [transcript]  
Feedback: [List of mispronunciations, speed, errors]  
Practice exercise: [2 short lines for practice]

---
**📅 Weekly Plan** *(If applicable)*  
Monday: [Topic + Activity]  
Tuesday: [...]  
Friday: [Assessment idea]

---

Make sure all outputs are:
- Simple, grade-specific
- Local-language appropriate
- Useful for low-resource settings

Always assume the teacher may print, speak, or draw your output.
"""

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the generation request
@app.route('/generate', methods=['POST'])
def generate():
    user_prompt = request.form.get('prompt')
    image_file = request.files.get('image')

    if not user_prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        # Select the model: 'gemini-1.5-flash' is fast, free, and supports images.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Combine the system instructions with the user's request
        full_prompt = f"{SAHAYAK_SYSTEM_PROMPT}\n\n---\n\nTeacher's Request: {user_prompt}"

        if image_file:
            # If there's an image, process it
            img = PIL.Image.open(image_file.stream)
            # Send the image and the prompt to the model
            response = model.generate_content([full_prompt, img])
        else:
            # If it's text-only
            response = model.generate_content(full_prompt)

        # Gemini returns markdown, so we can send it directly
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"An error occurred: {e}") # Log error for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)