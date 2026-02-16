from app import app
app.config['SECRET_KEY'] = 'this-is-a-secret-key'

if __name__=="__main__":
    # Run on port 5000 (default Flask port)
    # Make sure this port matches what you use in ngrok
    app.run(debug=True, port=5000)