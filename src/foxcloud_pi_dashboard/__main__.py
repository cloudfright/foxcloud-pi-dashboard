from foxcloud_pi_dashboard.foxcloudapi.request import FoxcloudRequest

def main() -> None:
    foxcloud_request = FoxcloudRequest()
    real_time_data = foxcloud_request.get_real_time_data()
    print(real_time_data)

if __name__ == "__main__":
    main()