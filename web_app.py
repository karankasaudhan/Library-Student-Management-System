
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>Library Management System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                margin: 0;
                padding: 24px;
            }
            .card {
                max-width: 500px;
                margin: 30px auto;
                padding: 24px;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 15px #0001;
            }
            h1 { color: #1d4ed8; }
            p { line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📚 Library Management</h1>
            <p>Welcome! Your mobile web connection is working.</p>
            <p>Next, we will connect the book, student,
            and issue/return features.</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
