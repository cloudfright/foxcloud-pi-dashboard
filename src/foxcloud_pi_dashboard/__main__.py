from email.mime import image
from tkinter import font
import time

from foxcloud_pi_dashboard.foxcloudapi.request import FoxcloudRequest
from foxcloud_pi_dashboard.pidisplay.dashboard import Dashboard

def main() -> None:

    pi_display = Dashboard()

    # reead API inverter data every 5m     
    foxcloud_request = FoxcloudRequest()
    while True:
        inverter_data = foxcloud_request.get_real_time_data()
        pi_display.update_dashboard(inverter_data)
        time.sleep(300)

if __name__ == "__main__":
    main()