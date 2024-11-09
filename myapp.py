from flask import Flask, render_template, request
from openai import OpenAI
from ntscraper import Nitter
from pprint import pprint

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key="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"
)

# Initialize Nitter scraper
scraper = Nitter(log_level=1, skip_instance_check=False)

@app.route('/')
def home():
    return render_template('myapp.html')

@app.route('/translate', methods=['POST'])
def translate():
    # Get text input for translation
    user_input = request.form['user_input']

    messages = [
        {
            "role": "user",
            "content": f"{user_input}"
        }
    ]

    try:
        # Translate text
        stream = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=messages,
            max_tokens=500,
            stream=True
        )

        # Gather the translation response
        translated_text = ""
        for chunk in stream:
            translated_text += chunk.choices[0].delta.content

        return render_template('myapp.html', translated_text=translated_text, user_input=user_input)

    except Exception as e:
        return render_template('myapp.html', translated_text=f"Error: {str(e)}", user_input=user_input)

@app.route('/describe_image', methods=['POST'])
def describe_image():
    # Get image URL from the form
    image_url = request.form['image_url']

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in 1 sentence."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ]

    try:
        # Generate image description
        stream = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages=messages,
            max_tokens=500,
            stream=True
        )

        # Gather the description response
        image_description = ""
        for chunk in stream:
            image_description += chunk.choices[0].delta.content

        return render_template('myapp.html', image_description=image_description, image_url=image_url)

    except Exception as e:
        return render_template('myapp.html', image_description=f"Error: {str(e)}", image_url=image_url)

# New route to scrape tweets using Nitter
@app.route('/scrape_tweets', methods=['POST'])
def scrape_tweets():
    # Get Twitter username input
    username = request.form['username']
    
    try:
        # Scrape tweets using Nitter
        tweets = scraper.get_tweets(username, mode='user', number=5)['tweets'][3]
        
        # Format tweets for display
        formatted_tweets = [f"{tweets['date']} - {tweets['text']}"]

        return render_template('myapp.html', tweets=formatted_tweets, username=username)

    except Exception as e:
        return render_template('myapp.html', tweets=[f"Error: {str(e)}"], username=username)

if __name__ == "__main__":
    app.run(debug=True)
