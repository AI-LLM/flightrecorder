# Flight Recorder ("black box") of your AI Copiloting 

## Usage

### MacOS
Install [mitmproxy](https://mitmproxy.org)
```bash
brew install mitmproxy
sudo security add-trusted-cert -d -p ssl -p basic -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem
```
After completing a series of authorizations, you should be able to see "Mitmproxy Redirector" added in "Applications".

git clone this repo.
```bash
cd flightrecorder
```

setup virtual environment in your favourite way with python 3.11 (as I'm using. modern versions of Python 3 should work as well) and install the dependencies.

```bash
pip install -r requirements.txt
```

[Zed](https://zed.dev) is used in the example, you can replace **mitmproxy --mode local:"Zed"** in script *run.sh* with the name of your Editor or IDE. When you run it, any file operations in the working directory, as well as AI API calls made by the Editor/IDE, will be recorded in its *.flightrecorder* subdirectory.
```bash
./run.sh <path of working dir>
```
