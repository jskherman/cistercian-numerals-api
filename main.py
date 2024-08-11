import io
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from PIL import Image, ImageDraw
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
# Initialize the FastAPI application
app = FastAPI()


# Set an upper limit for the number, image generation
# This limit is chosen to be reasonable for a 256MB RAM 1xCPU server
MAX_NUMBER = 10**16 - 1  # 1 trillion - 1

# Initialize the rate limiter with a limit of 30 requests per minute
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middleware to add rate limit information to the response headers
@app.middleware("http")
async def add_rate_limit_header(request: Request, call_next):
    # Process the request
    response = await call_next(request)

    # Set rate limit headers (using available attributes from limiter or manually setting them)
    response.headers["X-RateLimit-Limit"] = str(app.state.limiter._default_limits)

    return response


# Exception handler for rate limit exceeded errors
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles the case when a client exceeds the rate limit.
    Returns a 429 status code with a message indicating the rate limit has been exceeded.
    """
    return HTMLResponse(
        content="Rate limit exceeded. Try again later.", status_code=429
    )


def draw_cistercian_digit(num, size=100):
    """
    Draws a single Cistercian digit on a square image.

    Parameters:
    num (int): The digit to be represented.
    size (int): The size (width and height) of the output image in pixels.

    Returns:
    Image: A PIL Image object representing the Cistercian digit.
    """
    # Create a blank white image
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)
    scale = size / 100  # Scale factor based on image size

    # Draw the central vertical line
    draw.line(
        [(50 * scale, 10 * scale), (50 * scale, 90 * scale)],
        fill="black",
        width=max(1, int(1.5 * scale)),
    )

    # Cistercian number line segments
    numbers = [
        # Ones
        [
            [(50, 10), (70, 10)],
            [(50, 30), (70, 30)],
            [(50, 10), (70, 30)],
            [(50, 30), (70, 10)],
            [(50, 10), (70, 10), (50, 30)],
            [(70, 10), (70, 30)],
            [(50, 10), (70, 10), (70, 30)],
            [(50, 30), (70, 30), (70, 10)],
            [(50, 10), (70, 10), (70, 30), (50, 30)],
        ],
        # Tens
        [
            [(50, 10), (30, 10)],
            [(50, 30), (30, 30)],
            [(50, 10), (30, 30)],
            [(50, 30), (30, 10)],
            [(50, 10), (30, 10), (50, 30)],
            [(30, 10), (30, 30)],
            [(50, 10), (30, 10), (30, 30)],
            [(50, 30), (30, 30), (30, 10)],
            [(50, 10), (30, 10), (30, 30), (50, 30)],
        ],
        # Hundreds
        [
            [(50, 90), (70, 90)],
            [(50, 70), (70, 70)],
            [(50, 90), (70, 70)],
            [(50, 70), (70, 90)],
            [(50, 90), (70, 90), (50, 70)],
            [(70, 90), (70, 70)],
            [(50, 90), (70, 90), (70, 70)],
            [(50, 70), (70, 70), (70, 90)],
            [(50, 90), (70, 90), (70, 70), (50, 70)],
        ],
        # Thousands
        [
            [(50, 90), (30, 90)],
            [(50, 70), (30, 70)],
            [(50, 90), (30, 70)],
            [(50, 70), (30, 90)],
            [(50, 90), (30, 90), (50, 70)],
            [(30, 90), (30, 70)],
            [(50, 90), (30, 90), (30, 70)],
            [(50, 70), (30, 70), (30, 90)],
            [(50, 90), (30, 90), (30, 70), (50, 70)],
        ],
    ]

    # Convert number to string and pad the number with zeros to 4 digits
    num_str = str(num).zfill(4)

    # Draw the negative line if the number is negative
    if num < 0:
        draw.line(
            [(30 * scale, 50 * scale), (70 * scale, 50 * scale)],
            fill="black",
            width=max(1, int(1.5 * scale)),
        )

    # Draw the appropriate lines for each digit
    for i in range(4):
        digit = int(num_str[3 - i])
        if digit == 0:
            continue
        lines = numbers[i][digit - 1]
        for j in range(len(lines) - 1):
            start = lines[j]
            end = lines[j + 1]
            draw.line(
                [
                    (start[0] * scale, start[1] * scale),
                    (end[0] * scale, end[1] * scale),
                ],
                fill="black",
                width=max(1, int(1.5 * scale)),
            )
    return img


def generate_cistercian_image(num, size=100):
    """
    Generates an image representing a number in the Cistercian numeral system.

    Parameters:
    num (int): The number to be represented.
    size (int): The size of each glyph in the generated image.

    Returns:
    Image: A PIL Image object representing the Cistercian number.

    Raises:
    ValueError: If the number exceeds the maximum allowable number.
    """
    if abs(num) > MAX_NUMBER:
        raise ValueError(f"Number exceeds maximum allowed value of +/- {MAX_NUMBER}")

    # Determine if the number is negative
    is_negative = num < 0
    # Convert the absolute value of the number to a list of digits
    digits = [int(d) for d in str(abs(num))]
    # Get the number of digits in the number
    num_digits = len(digits)
    # Calculate the number of glyphs needed to represent the number
    num_glyphs = (num_digits + 3) // 4

    # Create a new image with room for all the glyphs
    combined_img = Image.new("RGB", (size * num_glyphs, size), color="white")

    # Iterate over each glyph
    for i in range(num_glyphs):
        # Calculate the start and end indices for the current glyph
        start_index = max(0, num_digits - (i + 1) * 4)
        end_index = num_digits - i * 4
        # Get the digits for the current glyph
        glyph_digits = digits[start_index:end_index]
        # Convert the digits to a number
        glyph_num = int("".join(map(str, glyph_digits)))

        # Draw the current glyph onto the combined image
        glyph_img = draw_cistercian_digit(glyph_num, size)

        # If the number is negative, draw a negative sign onto the combined image
        if is_negative:
            draw = ImageDraw.Draw(glyph_img)
            scale = size / 100

            # Draw the negative line for all glyphs
            draw.line(
                [(30 * scale, 50 * scale), (70 * scale, 50 * scale)],
                fill="black",
                width=max(1, int(1.5 * scale)),
            )

        combined_img.paste(glyph_img, (size * (num_glyphs - i - 1), 0))

    # Return the combined image
    return combined_img


# Note: the route decorator must be above the limit decorator, not below it
@app.get("/{number}")
@limiter.limit("30/minute")
async def get_cistercian_number(number: int, request: Request, response: Response):
    try:
        img = generate_cistercian_image(number, size=200)
        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)
        return StreamingResponse(img_io, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/", response_class=HTMLResponse)
@limiter.limit("5/minute")
async def root(request: Request):
    html_content = """
    <html>
        <head>
            <title>Cistercian Numeral API</title>
            <link rel="icon" type="image/png" sizes="48x48" href="/favicon.ico">
            <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
            <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
            <link rel="manifest" href="/site.webmanifest">
            <link rel="stylesheet" href="https://unpkg.com/normalize.css">
            <link rel="stylesheet" href="https://unpkg.com/magick.css">
            <style>
            body {
                max-width: 70ch; /* Approximately 60 characters per line */
                padding: 0 20px;
                margin: auto;
                line-height: 1.6;
            }
            </style>
        </head>
        <body>
            <h1>Welcome to the Cistercian Numeral API</h1>
            <p>This API generates images of numbers represented in the
            <a
               href="https://en.wikipedia.org/wiki/Cistercian_numerals">
               Cistercian numeral system</a>. From Wikipedia:
            </p>
            <blockquote>
                <p>
                The medieval Cistercian numerals, or &quot;ciphers&quot; in
                nineteenth-century parlance, were developed by the Cistercian
                monastic order in the early thirteenth century at about the
                time that Arabic numerals were introduced to northwestern
                Europe. They are more compact than Arabic or Roman numerals,
                with a single glyph able to indicate any integer from 1 to
                9,999.
                </p>
            </blockquote>
            <h2>How to Use</h2>
            <p>
                To generate an image, append the desired number to the URL.
                For example:
            </p>
            <pre><code>GET /<span>999900</span></code></pre>
            <pre><code>curl /-1234 --output -1234.png</span></code></pre>
            <p><em>Limits</em>:</p>
            <ul>
                <li>Only integers are supported.</li>
                <li>Integers must not exceed ± (10<sup>16</sup> - 1).</li>
                <li>Negative integers are not historically accurate.</li>
            </ul>
            <p>This API is based on the
            <a
               href="https://akosnikhazy.github.io/cistercian-numerals/#about">
               generator by Ákos Nikházy</a>:
            </p>
            <blockquote>
                <p>
                While the original system only knew numbers 1-9999, I decided
                to enhance it and added negative numbers and zero. I found it
                logical to 0 be just a line and negative numbers to have a
                horizontal line in the middle. I do not express this at top at
                the generator because I do not want to give the wrong idea.
                Yet you can type negative numbers and 0 too. Try it!
                </p>
            </blockquote>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
