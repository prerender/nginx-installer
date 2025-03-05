# Portable Nginx CLI

## Version

Python 3.13.0

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/portable-nginx-cli.git
   cd portable-nginx-cli
   ```

2. Activate the virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip3 install -r requirements.txt
   ```

## Usage

To run the application, execute the following command in your terminal:
```
python src/main.py
```

For help, execute the following command in your terminal:
```
python3 src/main.py -h
```

## Testing with Docker

To test the application using Docker, execute the following commands in your terminal:

```
./run-docker-test.sh images/reverse-proxy-node images/reverse-proxy-node/nginx.conf
```

## PyInstaller

To create a standalone executable, execute the following command in your terminal:
```
pyinstaller src/main.py --onefile
```