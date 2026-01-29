from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Server is running!"

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
