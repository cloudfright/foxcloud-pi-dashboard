from email.mime import image
from tkinter import font

from foxcloud_pi_dashboard.foxcloudapi.request import FoxcloudRequest
from foxcloud_pi_dashboard.pidisplay.dashboard import Dashboard

def main() -> None:

    pi_display = Dashboard()

    foxcloud_request = FoxcloudRequest()
    real_time_data = foxcloud_request.get_real_time_data()
    print(real_time_data)
    pi_display.update_dashboard()

if __name__ == "__main__":
    main()