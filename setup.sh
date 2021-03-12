mkdir /app/downloads
pip install --upgrade pip
pip install -r requirements.txt
npm install
export CHROMEDRIVER_PATH = /app/.chromedriver/bin/chromedriver
export GOOGLE_CHROME_BIN = /app/.apt/usr/bin/google-chrome
export PORT=$PORT
node ./server.js