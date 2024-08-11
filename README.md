# Cistercian Numeral API

This FastAPI-based API generates images of numbers represented in the Cistercian numeral system. The Cistercian numeral system is a medieval number notation developed by the Cistercian monastic order in the early 13th century.

## Features

- Generate PNG images of Cistercian numerals for integers
- Support for numbers from -9,999,999,999,999,999 to 9,999,999,999,999,999
- Rate limiting to prevent abuse
- Simple web interface for API documentation and usage

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cistercian-numerals-api.git
   cd cistercian-numerals-api
   ```

2. Install the required packages:
   ```
   pip install fastapi uvicorn pillow slowapi
   ```

## Usage

1. Start the server:
   ```
   uvicorn main:app --port 8000 --reload
   ```
   This command runs the FastAPI application using Uvicorn, with automatic reloading enabled for development.

2. Open a web browser and navigate to `http://localhost:8000` to see the API documentation and usage instructions.

3. To generate a Cistercian numeral image, make a GET request to `/{number}`, where `{number}` is the integer you want to represent. For example:
   ```
   http://localhost:8000/42
   ```
   This will return a PNG image of the Cistercian numeral representation of 42.

## API Endpoints

- `GET /`: Returns the HTML documentation page
- `GET /{number}`: Generates and returns a PNG image of the Cistercian numeral representation of the given number

## Limitations

- Only integers are supported
- Numbers must be between -9,999,999,999,999,999 and 9,999,999,999,999,999
- Rate limited to 30 requests per minute for image generation
- Rate limited to 5 requests per minute for the documentation page

## Acknowledgements

- This project is based on the work of [Ákos Nikházy](https://akosnikhazy.github.io/cistercian-numerals/#about)
- Cistercian numeral system information from [Wikipedia](https://en.wikipedia.org/wiki/Cistercian_numerals)