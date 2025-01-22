# Flight Recorder ("black box") of your AI Copiloting 

## Installation

### MacOS
Install [mitmproxy](https://mitmproxy.org)
```bash
brew install mitmproxy
sudo security add-trusted-cert -d -p ssl -p basic -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem
```
After completing a series of authorizations, you should be able to see "Mitmproxy Redirector" added in "Applications".

git clone this repo
```bash
cd flightrecorder
```

setup virtual environment in your favourite way with python 3.11 (as I'm using. modern versions of Python 3 should work as well)

```bash
pip install -r requirements.txt
```
