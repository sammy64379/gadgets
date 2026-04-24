from app import app


if __name__=="__main__":
    # Run on port 5000 (default Flask port)
    # Make sure this port matches what you use in ngrok
    app.run(debug=True, port=5000)