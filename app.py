import os
from flask import Flask, render_template, request
import main

app = Flask(__name__)

@app.route('/vystup', methods=['POST'])
def vystup():
    url = liga = ''
    skratky = False

    f = request.form
    for key in f.keys():
        for value in f.getlist(key):
            if key == 'url':
                url = value
            if key == 'liga':
                liga = value
            if key == 'checkbox':
                skratky = True

    return render_template('vystup.html', vystup = main.getStringVystup(url, liga, skratky))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)