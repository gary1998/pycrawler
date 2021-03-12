apt-get install -y chromium-browser
mkdir /app/downloads
pip install --upgrade pip
pip install -r requirements.txt
npm install
export PORT=$PORT
node ./server.js