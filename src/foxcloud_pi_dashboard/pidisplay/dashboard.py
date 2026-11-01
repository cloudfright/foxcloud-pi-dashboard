from pathlib import Path

from displayhatmini_lite import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont, ImageText

FONT_DIR = Path(__file__).parent / "fonts"

class Dashboard:
    def __init__(self):
        self.display = DisplayHATMini()

    def update_dashboard(self):
        
        # Turn on backlight
        self.display.set_backlight(1.0)
        
        self.display.set_led(0.0, 0.0, 1.0)
          
        monofont = ImageFont.truetype(str(FONT_DIR / "RobotoMono-VariableFont_wght.ttf"), 36)
        
        # Create image and draw text
        image = Image.new("RGB", (DisplayHATMini.WIDTH, DisplayHATMini.HEIGHT), "black")
        draw = ImageDraw.Draw(image)
        
        draw.text((10, 30), "6.5kw", font=monofont, fill="white")
        draw.text((10, 80), "0.5kw", font=monofont, fill="white")
        draw.text((10, 140), "0kw", font=monofont, fill="white")
        draw.text((10, 170), "78%", font=monofont, fill="white")
            
        # Send to display
        self.display.display(image)

