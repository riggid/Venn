# Setting Up Social Compass with Ngrok

## Step 1: Start Streamlit Locally

First, make sure Streamlit is running on your local machine:

```bash
streamlit run main.py
```

This will start the app on `http://localhost:8501`

## Step 2: Set Up Ngrok Tunnel

### Install Ngrok (if not already installed)

```bash
# Download from https://ngrok.com/download
# Or use package manager:
# Ubuntu/Debian:
sudo apt install ngrok
# Or download binary and add to PATH
```

### Create Ngrok Tunnel

In a **new terminal window**, run:

```bash
ngrok http 8501
```

This will create a tunnel and give you a public URL like:
```
https://ethical-quietly-hornet.ngrok-free.app
```

## Step 3: Configure Streamlit for External Access

If you need to allow external connections, you can set:

```bash
streamlit run main.py --server.address 0.0.0.0 --server.port 8501
```

## Step 4: Access Your App

1. Copy the ngrok URL (the `https://` one)
2. Open it in your browser
3. You may need to click through ngrok's warning page

## Troubleshooting

### Blank Page Issues

1. **Check if Streamlit is running:**
   ```bash
   ps aux | grep streamlit
   ```

2. **Check the terminal where Streamlit is running** for error messages

3. **Verify ngrok is pointing to the right port:**
   - Make sure ngrok is tunneling to port 8501 (or whatever port Streamlit is using)
   - Check ngrok dashboard: http://localhost:4040

4. **Check browser console** (F12) for JavaScript errors

5. **Try accessing localhost directly:**
   ```
   http://localhost:8501
   ```
   If this works, the issue is with ngrok configuration

### Common Issues

- **"This site can't be reached"**: Streamlit isn't running
- **Blank page**: Check Streamlit terminal for errors
- **Connection refused**: Port mismatch between Streamlit and ngrok
- **Ngrok warning page**: Click "Visit Site" button

## Alternative: Run Without Ngrok

For local development, you don't need ngrok:

```bash
streamlit run main.py
```

Then access at: `http://localhost:8501`

