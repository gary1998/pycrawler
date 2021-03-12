wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# apt-get -y update
# apt-get install -y python3 python-pip
# apt-get install -y google-chrome-stable
# apt-get install -yqq unzip
wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
curl -sL https://deb.nodesource.com/setup_15.x | bash -
# apt install -y nodejs
pip install --upgrade pip
pip install -r requirements.txt
npm install
export PORT=$PORT
node ./server.js