from dotenv import load_dotenv
from pyresilience import resilient, RetryConfig, TimeoutConfig, CircuitBreakerConfig
from pyresilience import FallbackConfig, BulkheadConfig, RateLimiterConfig
import os
import hashlib
import time

import requests


FOXCLOUD_BASE_URL = 'https://www.foxesscloud.com'
DEVICE_REALTIME_PATH = '/op/v1/device/real/query'

class FoxcloudRequest:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.device_sn = os.getenv("DEVICE_SN")
        
    @resilient(
        retry=RetryConfig(max_attempts=3, delay=1.0, backoff_factor=2.0),
        timeout=TimeoutConfig(seconds=10),
        circuit_breaker=CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30),
        fallback=FallbackConfig(handler=lambda e: {"status": "degraded"}, fallback_on=[Exception]),
        bulkhead=BulkheadConfig(max_concurrent=10),
        rate_limiter=RateLimiterConfig(max_calls=100, period=60.0),
    )
    def _post(self, url, data=None, json=None, **kwargs):
        return requests.post(url, data=data, json=json, **kwargs)

    def _generate_signature(self, path, token, timestamp):
        return hashlib.md5(fr"{path}\r\n{token}\r\n{timestamp}".encode('UTF-8')).hexdigest()    

    def get_real_time_data(self):

        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(DEVICE_REALTIME_PATH, self.api_key, timestamp)

        headers = {
            'token': self.api_key,
            'timestamp': timestamp,
            'signature': signature,
            'lang': 'en',
            'Content-Type': 'application/json'   
        }
        payload = {
            'sns': [self.device_sn],
            'variables': ['pvPower', 'batChargePower', 'batDischargePower', 'feedinPower', 'gridConsumptionPower', 'SoC', 'loadsPower'] 
        }
        url = f"{FOXCLOUD_BASE_URL}{DEVICE_REALTIME_PATH}"

        response = self._post(url, json=payload, headers=headers)
        body = response.json()
        # print("FoxCloud API response body:", response.status_code, body)

        if body.get("errno") != 0:
            raise RuntimeError(f"FoxCloud API error: {body.get('msg')}")

        devices = body.get("result", [])
        return devices[0].get("datas", []) if devices else []