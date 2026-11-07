import time
from pathlib import Path
from displayhatmini_lite import DisplayHATMini
from PIL import Image, ImageDraw, ImageFont, ImageText

FONT_DIR = Path(__file__).parent / "fonts"
FONT_TITLE_COLOUR = "#C3BCBC"
FONT_VALUE_COLOUR = "#FFFFFF"
FONT_VALUE_RED_COLOUR = "#FF0000"
FONT_VALUE_GREEN_COLOUR = "#00FF00"
FONT_VALUE_BLUE_COLOUR = "#0000FF"
FONT_VALUE_AMBER_COLOUR = "#FFBF00"
BACKGROUND_GRID_COLOUR = "#333333"
GRID_CONSUMPTION_THRESHOLD = 0.2
GRID_EXPORT_THRESHOLD = 0.2
BAT_DISCHARGE_THRESHOLD = 0.1
BAT_CHARGE_THRESHOLD = 0.1
SOLAR_THRESHOLD = 0.7
LED_GREEN_COLOUR = (0.0, 1.0, 0.0)
LED_RED_COLOUR = (1.0, 0.0, 0.0)
LED_AMBER_COLOUR = (1.0, 0.05, 0.0)
LED_OFF = (0.0, 0.0, 0.0)


class Dashboard:
    def __init__(self):
        self.display = DisplayHATMini()
        self.pv_power = 0
        self.bat_charge_power = 0
        self.bat_discharge_power = 0
        self.feedin_power = 0
        self.grid_consumption_power = 0
        self.soc = 0
        self.loads_power = 0

    def _get_self_use_percent(self):
        return ((self.pv_power + self.bat_discharge_power - self.feedin_power) / self.loads_power) * 100
        
    def _get_self_use_font_colour(self):
        self_use_percent = self._get_self_use_percent()
        if self_use_percent > 90:
            return FONT_VALUE_GREEN_COLOUR
        elif self_use_percent > 40:
            return FONT_VALUE_AMBER_COLOUR
        else:
            return FONT_VALUE_RED_COLOUR

    def _set_inverter_data(self, values):
        self.pv_power = values.get("pvPower")
        self.bat_charge_power = values.get("batChargePower")
        self.bat_discharge_power = values.get("batDischargePower")
        self.feedin_power = values.get("feedinPower")
        self.grid_consumption_power = values.get("gridConsumptionPower")
        self.soc = values.get("SoC")
        self.loads_power = values.get("loadsPower")

        print("Inverter data set:", values)
        print("Self-use percent:", self._get_self_use_percent())



    def _draw_background(self, draw):
        # draw cross to divide up the 4 quadrants
        draw.line((DisplayHATMini.WIDTH // 2, 0, DisplayHATMini.WIDTH // 2, DisplayHATMini.HEIGHT), fill=BACKGROUND_GRID_COLOUR)
        draw.line((0, DisplayHATMini.HEIGHT // 2, DisplayHATMini.WIDTH, DisplayHATMini.HEIGHT // 2), fill=BACKGROUND_GRID_COLOUR)

    def _set_led_colour(self):
        # Determine which LED color to display based on self-use percentage
        self_use_percent = self._get_self_use_percent()
        if self_use_percent > 90:
            self.display.set_led(*LED_GREEN_COLOUR) 
        elif self_use_percent > 10:
            self.display.set_led(*LED_AMBER_COLOUR)
        else:
            self.display.set_led(*LED_RED_COLOUR)

    def update_dashboard(self, inverter_data):

        values = {item["variable"]: item["value"] for item in inverter_data}
        self._set_inverter_data(values)
        self.display.set_backlight(1.0)

        image = Image.new("RGB", (DisplayHATMini.WIDTH, DisplayHATMini.HEIGHT), "black")
        draw = ImageDraw.Draw(image)
        number_font = ImageFont.truetype(str(FONT_DIR / "RobotoMono-VariableFont_wght.ttf"), 32)
        title_font = ImageFont.truetype(str(FONT_DIR / "RobotoMono-VariableFont_wght.ttf"), 24)
        mid_x = DisplayHATMini.WIDTH // 2

        self._draw_background(draw)  
        # blink the LED to indicate update
        self.display.set_led(*LED_OFF)   
        time.sleep(0.1)

        self._set_led_colour()
        value_font_colour = self._get_self_use_font_colour()

        # upper left quadrant show house load   
        draw.text((mid_x // 2, 13), "Home", font=title_font, fill=FONT_TITLE_COLOUR, anchor="mt")

        if self.loads_power < 1: 
            draw.text((mid_x // 2, 65), f"{self.loads_power*1000:.0f}w", font=number_font, fill=value_font_colour, anchor="mt")
        else:
            draw.text((mid_x // 2, 65), f"{self.loads_power:.2f}kw", font=number_font, fill=value_font_colour, anchor="mt")

        # upper right quadrant show solar power 
        draw.text((mid_x + mid_x // 2, 13), "Solar", font=title_font, fill=FONT_TITLE_COLOUR, anchor="mt")

        if self.pv_power < 1:
            draw.text((mid_x + mid_x // 2, 65), f"{self.pv_power*1000:.0f}w", font=number_font, fill=value_font_colour, anchor="mt")
        else:
            draw.text((mid_x + mid_x // 2, 65), f"{self.pv_power:.2f}kw", font=number_font, fill=value_font_colour, anchor="mt")

        # lower left quadrant show grid import or export power
        draw.text((mid_x // 2, DisplayHATMini.HEIGHT - 95), "Grid", font=title_font, fill=FONT_TITLE_COLOUR, anchor="mt")
    
        if self.grid_consumption_power < 1:
            draw.text((mid_x // 2, DisplayHATMini.HEIGHT - 50), f"{self.grid_consumption_power*1000:.0f}w", font=number_font, fill=value_font_colour, anchor="mt")
        else:
            draw.text((mid_x // 2, DisplayHATMini.HEIGHT - 50), f"{self.grid_consumption_power:.2f}kw", font=number_font, fill=value_font_colour, anchor="mt")
        
        # lower right quadrant show battery state of charge and charging/discharging status
        draw.text((mid_x + mid_x // 2, DisplayHATMini.HEIGHT - 95), "Battery", font=title_font, fill=FONT_TITLE_COLOUR , anchor="mt")
        draw.text((mid_x + mid_x // 2, DisplayHATMini.HEIGHT - 50), f"{self.soc:.0f}%", font=number_font, fill=value_font_colour, anchor="mt")

        # Send to display
        self.display.display(image)

