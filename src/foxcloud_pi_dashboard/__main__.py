import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from foxcloud_pi_dashboard.foxcloudapi.request import FoxcloudRequest
from foxcloud_pi_dashboard.pidisplay.dashboard import Dashboard

REFRESH_INTERVAL = 5
STANDBY_PAUSE_HOUR = 22
STANDBY_PAUSE_MINUTE = 00
STANDBY_RESUME_HOUR = 5
STANDBY_RESUME_MINUTE = 00


def main() -> None:
    pi_display = Dashboard()
    foxcloud_request = FoxcloudRequest()

    scheduler = BackgroundScheduler()

    def update_task():
        inverter_data = foxcloud_request.get_real_time_data()
        pi_display.update_dashboard(inverter_data)

    # Run immediately on startup
    update_task()

    # Then schedule recurring updates every 5 minutes
    scheduler.add_job(
        update_task,
        "interval",
        minutes=REFRESH_INTERVAL,
        id="api_update",
    )

    # Pause during standby hours
    scheduler.add_job(
        lambda: (pi_display.standby(), scheduler.pause_job("api_update")),
        CronTrigger(hour=STANDBY_PAUSE_HOUR, minute=STANDBY_PAUSE_MINUTE),
        id="pause_job",
    )

    # Resume after standby
    scheduler.add_job(
        lambda: (update_task(), scheduler.resume_job("api_update")),
        CronTrigger(hour=STANDBY_RESUME_HOUR, minute=STANDBY_RESUME_MINUTE),
        id="resume_job",
    )

    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    main()