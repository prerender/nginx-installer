# Portable Nginx CLI

This project is a command line application designed to search and modify Nginx configurations using the Crossplane library for configuration manipulation.

## Features

- Automatically detects the default Nginx configuration file location.
- Allows users to specify a custom configuration file location.
- Parses and displays the contents of the Nginx configuration file.
- Provides functionality to modify the configuration using Crossplane.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/portable-nginx-cli.git
   cd portable-nginx-cli
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command in your terminal:
```
python src/main.py
```

The application will prompt you to use the default Nginx configuration file location or specify a custom path. After selecting the location, it will parse the configuration and display the results.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.