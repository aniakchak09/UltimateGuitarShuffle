import json
from html import unescape
from curl_cffi import requests


class UGClient:
    def __init__(self, cookie):
        if not cookie:
            raise ValueError("UG_COOKIE is not set in your .env file. Copy your cookie from browser DevTools and add it.")
        self.session = requests.Session(impersonate="chrome")
        self.session.headers.update({"Accept": "text/html"})
        for part in cookie.split(";"):
            part = part.strip()
            if "=" in part:
                name, _, value = part.partition("=")
                self.session.cookies.set(name.strip(), value.strip(), domain=".ultimate-guitar.com")

    def _extract_json(self, html):
        try:
            # Try double quotes first, then single quotes (UG changed their HTML)
            for quote in ('"', "'"):
                search_token = f"class=\"js-store\" data-content={quote}"
                start = html.find(search_token)
                if start != -1:
                    start += len(search_token)
                    end = html.find(f"{quote}>", start)
                    if end != -1:
                        raw_json = unescape(html[start:end])
                        return json.loads(raw_json)

            # Not found — print a snippet to help diagnose
            print(f"[DEBUG] 'js-store' not found in page. HTTP status check via snippet:")
            print(f"[DEBUG] First 500 chars of response:\n{html[:500]}")
            return None
        except Exception as e:
            print(f"[DEBUG] Exception in _extract_json: {e}")
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
        response = self.session.get(url)
        data = self._extract_json(response.text)
        try:
            raw_tabs = data['store']['page']['data']['list']['list']
            return [self._standardize_tab(t) for t in raw_tabs]
        except (KeyError, TypeError):
            return []

    def get_playlist(self, url):
        if not url.startswith('http'): url = f"https://{url}"
        response = self.session.get(url)
        data = self._extract_json(response.text)
        if not data:
            print("[DEBUG] Failed to extract JSON from page. Check your cookie or URL.")
            return []

        try:
            page_data = data['store']['page']['data']
            print(f"[DEBUG] page_data keys: {list(page_data.keys())}")

            raw_tabs = []
            if 'songbookTabs' in page_data:
                raw_tabs = page_data['songbookTabs']
            elif 'playlist' in page_data:
                raw_tabs = page_data['playlist'].get('tabs', [])
            elif 'list' in page_data:
                raw_tabs = page_data['list'].get('list', [])
            else:
                print(f"[DEBUG] No known tab key found. Full page_data:\n{json.dumps(page_data, indent=2)[:2000]}")

            print(f"[DEBUG] Found {len(raw_tabs)} raw tabs")
            return [self._standardize_tab(t) for t in raw_tabs if t]
        except Exception as e:
            print(f"Error parsing playlist: {e}")
            return []