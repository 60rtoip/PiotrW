
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageTk

def draw_rounded_gradient_border(canvas, width, height, radius=20, border_width=4):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color1 = (8, 199, 30)
    color2 = (251, 255, 0)
    for i in range(border_width):
        ratio = i / border_width
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.rounded_rectangle(
            [i, i, width - i - 1, height - i - 1],
            radius=radius,
            outline=(r, g, b),
            width=1
        )
    return ImageTk.PhotoImage(img)
