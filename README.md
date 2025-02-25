# Portable Nginx CLI

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/portable-nginx-cli.git
   cd portable-nginx-cli
   ```

2. Activate the virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command in your terminal:
```
python src/main.py
```

## PyInstaller

To create a standalone executable, execute the following command in your terminal:
```
pyinstaller src/main.py --onefile
```

## Testing with Docker

To test the application using Docker, execute the following commands in your terminal:

```
./run-test.sh images/reverse-proxy-node images/reverse-proxy-node/nginx.conf
```