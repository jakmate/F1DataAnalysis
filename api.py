import json
import requests
import time
from typing import Dict, Any, Optional
from functools import lru_cache

class JolpicaF1API:
    BASE_URL = "http://api.jolpi.ca/ergast/f1"

    def __init__(self, rate_limit_wait: bool = True):
        """
        Initialize the Jolpica-F1 API connection.
        
        :param rate_limit_wait: Whether to automatically handle rate limiting
        """
        self.rate_limit_wait = rate_limit_wait
        self.session = requests.Session()
        self._sustained_limit = 500  # requests per hour
        self._burst_limit = 4        # requests per second
        self.request_log = []  # Changed to instance variable

    def _manage_rate_limits(self):
        """Manage both burst and sustained rate limits"""
        now = time.time()
        
        # Clean up request log - keep only requests from the last hour
        self.request_log = [t for t in self.request_log if now - t < 3600]
    
        # Check sustained hourly limit (500 requests/hour)
        if len(self.request_log) >= self._sustained_limit:
            oldest_request_time = self.request_log[0]
            wait_time = 3600 - (now - oldest_request_time)
            print(f"Hourly limit reached. Waiting {wait_time:.1f} seconds")
            time.sleep(wait_time + 1)
            return

        # Check burst limit (4 requests/second)
        recent_requests = [t for t in self.request_log if now - t < 1]
        if len(recent_requests) >= self._burst_limit:
            time_since_oldest = now - recent_requests[0]
            wait_time = 1 - time_since_oldest
            print(f"Burst limit reached. Waiting {wait_time:.1f} seconds")
            time.sleep(wait_time + 0.1)
            return

    def _create_cache_key(self, params: Optional[Dict]) -> tuple:
        """Convert parameters to a cache-safe format"""
        return tuple(sorted((params or {}).items()))

    @lru_cache(maxsize=128)
    def _make_request(self, endpoint: str, cache_params: tuple) -> Dict[str, Any]:
        """
        Make a request to the Jolpica-F1 API with caching.
        This is the actual cached method that does the work.
        """
        endpoint = endpoint.strip('/')
        params = dict(cache_params)
        params.setdefault('limit', 100)
        params.setdefault('offset', 0)

        retries = 0
        max_retries = 5
        
        while retries < max_retries:
            self._manage_rate_limits()
            
            try:
                response = self.session.get(
                    f"{self.BASE_URL}/{endpoint}",
                    params=params,
                    timeout=10
                )
                self.request_log.append(time.time())

                if response.status_code == 429:
                    retry_after = self._handle_rate_limit_error(response)
                    time.sleep(retry_after)
                    retries += 1
                    continue

                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                print(f"Request failed: {str(e)}")
                retries += 1
                if retries >= max_retries:
                    raise Exception(f"Failed after {max_retries} retries: {str(e)}")
                time.sleep(2 ** retries)

            except json.JSONDecodeError:
                print("Invalid JSON response")
                return {}

        return {}

    def getQualifyingResults(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        """Public method with caching wrapper"""
        cache_key = self._create_cache_key({'season': season, 'round': round})
        return self._make_request(f'{season}/{round}/qualifying', cache_key)
    
    def getLaps(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        """Public method with caching wrapper"""
        cache_key = self._create_cache_key({'season': season, 'round': round})
        return self._make_request(f'{season}/{round}/laps', cache_key)
    
    def getDrivers(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        """Public method with caching wrapper"""
        cache_key = self._create_cache_key({'season': season, 'round': round})
        return self._make_request(f'{season}/{round}/driverstandings', cache_key)
    
    def getPitstops(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        """Public method with caching wrapper"""
        cache_key = self._create_cache_key({'season': season, 'round': round})
        return self._make_request(f'{season}/{round}/pitstops', cache_key)

    def _handle_rate_limit_error(self, response: requests.Response) -> float:
        """Extract retry time from headers"""
        if self.rate_limit_wait:
            retry_after = min(
                int(response.headers.get("Retry-After", 1)),
                300  # Max 5 minute wait
            )
            print(f"Rate limit hit. Waiting {retry_after}s")
            return retry_after
        raise Exception("Rate limit exceeded")