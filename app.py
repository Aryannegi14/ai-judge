from flask import Flask, render_template, request
from markupsafe import Markup
import requests
import re

app = Flask(__name__)

# ⛔ WARNING: Regenerate your API key after testing, don’t keep it public!
from dotenv import load_dotenv
import os

load_dotenv()  # load variables from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(problem, side_a, side_b):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a wise, neutral relationship counselor."},
            {"role": "user", "content": f"""
There's a relationship conflict:

Problem: {problem}

Boyfriend (BF) says: {side_a}
Girlfriend (GF) says: {side_b}


Please:
1. Analyze both POVs fairly (BF and GF).
2. Summarize the core issue neutrally.
3. Give a balanced decision.
4. Offer advice on how to improve communication and fix the relationship.
"""}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    json_data = response.json()

    # Debug output
    print("GROQ API Response:", json_data)

    if "choices" in json_data:
        return json_data["choices"][0]["message"]["content"]
    elif "error" in json_data:
        return f"⚠️ Error from GROQ API: {json_data['error']['message']}"
    else:
        return "⚠️ Unexpected response from GROQ API."

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    problem = request.form['problem']
    side_a = request.form['side_a']
    side_b = request.form['side_b']

    ai_response = ask_groq(problem, side_a, side_b)

    # ✨ Clean formatting: Convert Markdown to HTML
    ai_response = ai_response.replace("*", "")
    ai_response = re.sub(r"(Analysis of Both POVs|Core Issue.*?|Balanced Decision|Advice for Improvement)", r"<h3>\1</h3>", ai_response, flags=re.IGNORECASE)
    ai_response = ai_response.replace("\n", "<br>")

    return Markup(f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>AI Verdict - Relationship Judge</title>
      <link rel="stylesheet" href="/static/style.css">
      <style>
        .verdict-container {{
          background: rgba(255,255,255,0.05);
          backdrop-filter: blur(10px);
          padding: 30px;
          border-radius: 16px;
          box-shadow: 0 0 10px #00ffe0;
          color: #eee;
          font-family: 'Inter', sans-serif;
          line-height: 1.6;
        }}
        h3 {{
          margin-top: 25px;
          color: #00ffe0;
          font-size: 18px;
        }}
        a.button {{
          display: inline-block;
          margin-top: 20px;
          background: linear-gradient(to right, #00ffe0, #007cf0);
          padding: 10px 20px;
          color: #000;
          text-decoration: none;
          font-weight: bold;
          border-radius: 10px;
          box-shadow: 0 0 10px #00ffe0, 0 0 20px #007cf0;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🧠 AI Judge Verdict</h1>
        <div class="verdict-container">
          {ai_response}
        </div>
        <a href="/" class="button">🔁 Try Another Case</a>
      </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
