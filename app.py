import os
from flask import Flask, render_template, request
import main

app = Flask(__name__)

@app.route('/vystup', methods=['POST'])
def vystup():
    url = request.form['url']
    liga = request.form['liga']
    skratkaZostavy = False

    if 'checkbox' in request.form:
        if request.form['checkbox'] == 'skratka':
            skratkaZostavy = True

    return render_template('vystup.html', vystup = main.getStringVystup(url, liga, skratkaZostavy))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)