# Ngrok Setup Guide for M-Pesa Callback

## Quick Steps:

1. **Download ngrok**: https://ngrok.com/download
   - Extract `ngrok.exe` to a folder (e.g., `C:\ngrok`)

2. **Sign up for free ngrok account** (REQUIRED):
   - Go to: https://dashboard.ngrok.com/signup
   - Create a free account and verify your email

3. **Get your authtoken**:
   - After signing in, go to: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your authtoken (long string)

4. **Configure ngrok with your authtoken**:
   ```powershell
   cd "path\to\your\ngrok\folder"
   .\ngrok.exe config add-authtoken YOUR_AUTHTOKEN_HERE
   ```
   Replace `YOUR_AUTHTOKEN_HERE` with the token you copied.

5. **Start your Flask app**:
   ```bash
   python app.py
   ```
   Your app will run on `http://localhost:5000`

6. **In a NEW terminal, start ngrok**:
   ```bash
   cd C:\ngrok  # or wherever you put ngrok.exe
   ngrok http 5000
   ```

7. **Copy the HTTPS URL** from ngrok output:
   ```
   Forwarding    https://abc123xyz.ngrok-free.app -> http://localhost:5000
   ```
   Copy: `https://abc123xyz.ngrok-free.app`

8. **Update your `.env` file**:
   ```
   MPESA_CALLBACK_URL=https://abc123xyz.ngrok-free.app/mpesa_callback
   ```
   (Replace `abc123xyz.ngrok-free.app` with YOUR actual ngrok URL)

9. **Restart your Flask app** to load the new callback URL

## Important:
- Keep ngrok running while testing M-Pesa payments
- If you restart ngrok, you'll get a new URL - update `.env` and restart Flask
- You only need to configure the authtoken once - ngrok will remember it

## Testing:
- Use test phone: `254708374149`
- Use small amount (e.g., 1 or 10)
- Check ngrok terminal for incoming callback requests from Safaricom

