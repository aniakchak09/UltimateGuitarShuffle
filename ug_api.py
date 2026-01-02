import requests
import json
from html import unescape


class UGClient:
    def __init__(self, cookie):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": cookie,
            "Accept": "text/html"
        }

    def _extract_json(self, html):
        try:
            search_token = 'class="js-store" data-content="'
            start = html.find(search_token) + len(search_token)
            end = html.find('">', start)
            if start < len(search_token): return None
            raw_json = unescape(html[start:end])
            return json.loads(raw_json)
        except Exception:
            return None

    def _standardize_tab(self, tab):
        """Standardizes differences between Favorites and Playlist JSON keys."""
        return {
            'song_name': tab.get('song_name') or tab.get('name') or "Unknown Song",
            'band_name': tab.get('band_name') or tab.get('artist_name') or "Unknown Artist",
            'song_url': tab.get('song_url') or tab.get('tab_url'),
            'type': tab.get('type', 'Tab')
        }

    def get_favorites(self):
        url = "https://www.ultimate-guitar.com/user/favorite"
        response = requests.get(url, headers=self.headers)
        data = self._extract_json(response.text)
        try:
            raw_tabs = data['store']['page']['data']['list']['list']
            return [self._standardize_tab(t) for t in raw_tabs]
        except (KeyError, TypeError):
            return []

    def get_playlist(self, url):
        if not url.startswith('http'): url = f"https://{url}"
        response = requests.get(url, headers=self.headers)
        data = self._extract_json(response.text)
        if not data: return []

        try:
            page_data = data['store']['page']['data']

            # The key we found in your debug output!
            raw_tabs = []
            if 'songbookTabs' in page_data:
                raw_tabs = page_data['songbookTabs']
            elif 'playlist' in page_data:
                raw_tabs = page_data['playlist'].get('tabs', [])
            elif 'list' in page_data:
                raw_tabs = page_data['list'].get('list', [])

            # Standardize them so main.py always sees 'song_name' and 'band_name'
            return [self._standardize_tab(t) for t in raw_tabs if t]
        except Exception as e:
            print(f"Error parsing playlist: {e}")
            return []