import math
from PIL import Image, ImageDraw


def draw_cistercian_number(num, size=100):
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)

    # Scale factor for different image sizes
    scale = size / 100

    # Draw the middle line
    draw.line(
        [(50 * scale, 10 * scale), (50 * scale, 90 * scale)],
        fill="black",
        width=max(1, int(1.5 * scale)),
    )

    # Define the number patterns
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

    # Handle negative numbers
    if num < 0:
        draw.line(
            [(30 * scale, 50 * scale), (70 * scale, 50 * scale)],
            fill="black",
            width=max(1, int(1.5 * scale)),
        )
        num = abs(num)

    # Convert number to string and pad with zeros
    num_str = str(num).zfill(4)

    # Draw the number
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


def generate_cistercian_pngs(
    start=0, end=99999, size=100, output_dir="cistercian_numerals"
):
    import os

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for num in range(start, end + 1):
        if num <= 9999:
            img = draw_cistercian_number(num, size)
            img.save(f"{output_dir}/cistercian_{num:05d}.png")
        else:
            # For numbers > 9999, use two glyphs side by side
            left_num = num // 10000
            right_num = num % 10000

            left_img = draw_cistercian_number(left_num, size)
            right_img = draw_cistercian_number(right_num, size)

            combined_img = Image.new("RGB", (size * 2, size), color="white")
            combined_img.paste(left_img, (0, 0))
            combined_img.paste(right_img, (size, 0))

            combined_img.save(f"{output_dir}/cistercian_{num:05d}.png")

        if num % 1000 == 0:
            print(f"Generated {num} images...")

    print(f"Finished generating {end - start + 1} images.")


if __name__ == "__main__":
    # Usage example
    generate_cistercian_pngs(
        start=0, end=99999, size=200, output_dir="cistercian_numerals"
    )
