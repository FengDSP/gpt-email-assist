
import sys
import time

from absl import flags
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai

flags.DEFINE_string('openai_api_key', None, 'Your OpenAI API key')


app = Flask(__name__)
CORS(app)


complete_models = set([
    'text-davinci-003',
    'text-davinci-002',
])

@app.route('/api/email-auto-reply', methods=['POST'])
def generate_response():
    email = request.json['email']
    action = request.json['action']
    model = request.json['model']

    start_time = time.perf_counter()
    if model in complete_models:
        response = _call_complete(model, email, action)
    else:
        response = _call_chat(model, email, action)
    end_time = time.perf_counter()

    return jsonify({
        'response': response,
        'latency_sec': end_time - start_time,
    })


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
    flags.FLAGS(sys.argv)
    if not flags.FLAGS.openai_api_key:
        raise ValueError("Missing required argument: --openai_api_key")
    openai.api_key = flags.FLAGS.openai_api_key
    app.run()
