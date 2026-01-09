import json
import requests
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class JolpicaF1API:
    BASE_URL = "http://api.jolpi.ca/ergast/f1"

    def __init__(self, rate_limit_wait: bool = True, cache_dir: str = ".f1_cache", cache_ttl_hours: int = 24):
        """
        Initialize the Jolpica-F1 API connection.
        
        :param rate_limit_wait: Whether to automatically handle rate limiting
        :param cache_dir: Directory to store cached responses
        :param cache_ttl_hours: Hours before cache expires (use None for no expiry)
        """
        self.rate_limit_wait = rate_limit_wait
        self.session = requests.Session()
        self._sustained_limit = 500
        self._burst_limit = 4
        self.request_log = []
        
        # Cache setup
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours) if cache_ttl_hours else None

    def _get_cache_path(self, endpoint: str, params: Dict) -> Path:
        """Generate cache file path from endpoint and params"""
        cache_key = f"{endpoint}_{json.dumps(params, sort_keys=True)}"
        hash_key = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"

    def _read_cache(self, cache_path: Path) -> Optional[Dict[str, Any]]:
        """Read from cache if valid"""
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check TTL if set
            if self.cache_ttl:
                cache_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cache_time > self.cache_ttl:
                    return None
            
            return cached['data']
        except (KeyError, ValueError):
            return None

    def _write_cache(self, cache_path: Path, data: Dict[str, Any]):
        """Write response to cache"""
        try:
            cache_obj = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_obj, f)
        except Exception as e:
            print(f"Cache write failed: {e}")

    def _manage_rate_limits(self):
        """Manage both burst and sustained rate limits"""
        now = time.time()
        self.request_log = [t for t in self.request_log if now - t < 3600]
    
        if len(self.request_log) >= self._sustained_limit:
            oldest_request_time = self.request_log[0]
            wait_time = 3600 - (now - oldest_request_time)
            print(f"Hourly limit reached. Waiting {wait_time:.1f} seconds")
            time.sleep(wait_time + 1)
            return

        recent_requests = [t for t in self.request_log if now - t < 1]
        if len(recent_requests) >= self._burst_limit:
            time_since_oldest = now - recent_requests[0]
            wait_time = 1 - time_since_oldest
            time.sleep(wait_time + 0.2)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the API with file-based caching"""
        endpoint = endpoint.strip('/')
        params = params or {}
        params.setdefault('limit', 100)
        params.setdefault('offset', 0)

        # Check cache first
        cache_path = self._get_cache_path(endpoint, params)
        cached_data = self._read_cache(cache_path)
        if cached_data:
            return cached_data

        # Make actual request
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
                
                if response.status_code == 429:
                    retry_after = self._handle_rate_limit_error(response)
                    time.sleep(retry_after + 1)
                    retries += 1
                    continue

                response.raise_for_status()
                self.request_log.append(time.time())
                
                data = response.json()
                
                if not data or 'MRData' not in data:
                    print(f"Warning: Invalid response structure from {endpoint}")
                    retries += 1
                    if retries >= max_retries:
                        raise Exception(f"Invalid response after {max_retries} retries")
                    time.sleep(2 ** retries)
                    continue
                
                # Cache successful response
                self._write_cache(cache_path, data)
                return data

            except requests.RequestException as e:
                print(f"Request failed: {str(e)}")
                retries += 1
                if retries >= max_retries:
                    raise Exception(f"Failed after {max_retries} retries: {str(e)}")
                time.sleep(2 ** retries)

            except json.JSONDecodeError as e:
                print(f"Invalid JSON response: {str(e)}")
                retries += 1
                if retries >= max_retries:
                    raise Exception(f"Invalid JSON after {max_retries} retries")
                time.sleep(2 ** retries)

        raise Exception(f"Failed to get valid response after {max_retries} retries")

    def clear_cache(self):
        """Clear all cached responses"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        print(f"Cleared cache directory: {self.cache_dir}")

    def get_qualifying_results(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        return self._make_request(f'{season}/{round}/qualifying', {'season': season, 'round': round})
    
    def get_race_results(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        return self._make_request(f'{season}/{round}/results', {'season': season, 'round': round})
    
    def get_laps(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        """Get all laps with progress tracking"""
        all_laps = []
        offset = 0
        limit = 100
        num_drivers = 20
        total_unique_laps = 0

        init_response = self._make_request(
            f'{season}/{round}/laps',
            {'season': season, 'round': round, 'offset': 0, 'limit': 1}
        )
        
        try:
            race_data = init_response['MRData']['RaceTable']['Races'][0]
            total_driver_entries = int(init_response['MRData']['total'])
            num_drivers = len(race_data['Laps'][0]['Timings']) if race_data['Laps'] else 20
            total_unique_laps = (total_driver_entries + num_drivers - 1) // num_drivers
        except (KeyError, IndexError):
            return init_response

        laps_per_page = limit // num_drivers
        total_pages = (total_unique_laps + laps_per_page - 1) // laps_per_page
        
        print(f"Fetching {total_unique_laps} race laps over {total_pages} pages")

        while len(all_laps) < total_unique_laps:
            page_num = (offset // limit) + 1
            print(f"Page {page_num}/{total_pages}...", end='\r')
            
            response = self._make_request(
                f'{season}/{round}/laps',
                {'season': season, 'round': round, 'offset': offset, 'limit': limit}
            )

            try:
                new_laps = response['MRData']['RaceTable']['Races'][0]['Laps']
            except (KeyError, IndexError):
                break

            if not new_laps:
                break

            all_laps.extend(new_laps)
            offset += limit
            time.sleep(0.1)

        final_laps = all_laps[:total_unique_laps]
        print(f"Successfully fetched {len(final_laps)} race laps")
        
        return {
            'MRData': {
                **init_response['MRData'],
                'total': str(len(final_laps) * num_drivers),
                'RaceTable': {
                    'Races': [{
                        **race_data,
                        'Laps': final_laps
                    }]
                }
            }
        }
    
    def get_driver_standings(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        if round > 0:
            return self._make_request(f'{season}/{round}/driverstandings', {'season': season, 'round': round})
        else:
            return self._make_request(f'{season}/driverstandings', {'season': season})
    
    def get_constructor_standings(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        if round > 0:
            return self._make_request(f'{season}/{round}/constructorstandings', {'season': season, 'round': round})
        else:
            return self._make_request(f'{season}/constructorstandings', {'season': season})

    def get_drivers(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        return self._make_request(f'{season}/{round}/driverstandings', {'season': season, 'round': round})
    
    def get_pitstops(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        return self._make_request(f'{season}/{round}/pitstops', {'season': season, 'round': round})
    
    def get_race_info(self, season: str = 'current', round: int = 0) -> Dict[str, Any]:
        if round > 0:
            return self._make_request(f'{season}/{round}/races', {'season': season, 'round': round})
        else:
            return self._make_request(f'{season}/races', {'season': season})

    def _handle_rate_limit_error(self, response: requests.Response) -> float:
        if self.rate_limit_wait:
            retry_after = min(
                int(response.headers.get("Retry-After", 1)),
                300
            )
            print(f"Rate limit hit. Waiting {retry_after}s")
            return retry_after
        raise Exception("Rate limit exceeded")