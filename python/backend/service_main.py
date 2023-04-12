from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)


openai.api_key = 'api key'

@app.route('/')
def index():
    return send_file('../../index.html')

complete_models = set([
    'text-davinci-003',
    'text-davinci-002',
])

@app.route('/api/gpt3', methods=['POST'])
def generate_response():
    email = request.json['email']
    action = request.json['action']
    model = request.json['model']
    if model in complete_models:
        response = _call_complete(model, email, action)
    else:
        response = _call_chat(model, email, action)
    return jsonify({'response': response})


def _call_complete(model, email, action):
    prompt = f"""
I got an email:

{email}

What can I reply if I {action}?

"""

    options = {
        'temperature': 0.7,
        'max_tokens': 300,
        'n': 1,
    }
    print(prompt)
    input_text = f'Prompt: {prompt}\nResponse:'
    response = openai.Completion.create(
        engine=model,
        prompt=input_text,
        max_tokens=options['max_tokens'],
        n=options['n'],
        temperature=options['temperature']
    )
    print(response)
    return response.choices[0].text.strip()

def _call_chat(model, email, action):
    prompt = f"""
I got an email:

{email}

What can I reply if I {action}?

"""
    print(prompt)

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        print(response)
        return response.choices[0].message.content
    except Exception as e:
        # Handle other errors
        error_message = f"Unexpected error: {e}"
        print(error_message)
        return error_message
  

if __name__ == '__main__':
    app.run()
