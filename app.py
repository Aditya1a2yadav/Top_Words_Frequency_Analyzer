from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import re
import requests
import plotly.graph_objects as go
import plotly.io as pio
import json
from requests.exceptions import RequestException, InvalidURL
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

app = Flask(__name__)

# Home route to render the input form
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle the form submission
@app.route('/get-top-words', methods=['POST'])
def get_top_words():
    url = request.form.get('url')
    top_n = int(request.form.get('n', 10))

    # Check if the URL is valid
    if not url.startswith('http://') and not url.startswith('https://'):
        return render_template('index.html', top_words=None, error="Invalid URL format. Please include 'http://' or 'https://'.", graph_html=None)

    try:
        
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            text = re.sub(r'\s+', ' ', text).lower()
            
            # Remove punctuation and split text into words
            words = re.findall(r'\b\w+\b', text)

            stpw=stopwords.words('english')
            # print(stpw)

            # for word in text:
            #     if word in stpw:
            #         text=text.replace(word,'')
            # Count word frequencies
            freq = {}
            for word in words:
                if (word in stpw) or (word[0]<'a' or word[0]>'z') or (len(word)==1):
                    continue
                freq[word] = freq.get(word, 0) + 1

            # Get the top `n` words
            top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

            # Sum the frequencies of less frequent words as "Other Words"
            remaining_words = list(freq.items())[top_n:]
            other_words_freq = sum([count for word, count in remaining_words])

            # Prepare data for pie chart (Top N words + Other Words)
            pie_data = top_words
            if other_words_freq > 0:
                pie_data.append(('Other Words', other_words_freq))

            # Generate pie chart
            labels = [word for word, _ in pie_data]
            values = [count for _, count in pie_data]
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            graph_html = pio.to_html(fig, full_html=False)

            return render_template('index.html', top_words=top_words, error=None, graph_html=graph_html)
        else:
            return render_template('index.html', top_words=None, error="Failed to retrieve the URL (status code: {})".format(response.status_code), graph_html=None)
    
    except InvalidURL:
        return render_template('index.html', top_words=None, error="The URL is not valid. Please provide a valid URL.", graph_html=None)
    except RequestException as e:
        return render_template('index.html', top_words=None, error="Error occurred while retrieving the URL: {}".format(str(e)), graph_html=None)

if __name__ == '__main__':
    app.run(debug=True)
