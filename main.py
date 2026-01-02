import os
import random
import webbrowser
from dotenv import load_dotenv, set_key  # Added set_key
from ug_api import UGClient

# Path to your .env file
ENV_PATH = '.env'
load_dotenv(ENV_PATH)


def get_saved_playlists():
    raw = os.getenv("PLAYLISTS", "")
    if not raw: return {}
    # Handles empty strings or trailing commas
    parts = [item for item in raw.split(",") if ":" in item]
    return dict(item.split(":") for item in parts)


def save_playlist_to_env(p_id, p_name):
    """Adds a new playlist to the .env file permanently."""
    current_playlists = os.getenv("PLAYLISTS", "")
    new_entry = f"{p_id}:{p_name}"

    if not current_playlists:
        updated_value = new_entry
    elif p_id in current_playlists:
        print(f"Playlist {p_id} is already in your list.")
        return
    else:
        updated_value = f"{current_playlists},{new_entry}"

    # This writes directly back to your .env file
    set_key(ENV_PATH, "PLAYLISTS", updated_value)
    print(f"Successfully saved '{p_name}' to .env!")


def main():
    cookie = os.getenv("UG_COOKIE")
    client = UGClient(cookie)

    while True:
        saved_playlists = get_saved_playlists()
        print("\n--- UG SHUFFLER PRO ---")
        print("0. My Favorites")

        # Display saved playlists
        playlist_ids = list(saved_playlists.keys())
        for i, p_id in enumerate(playlist_ids, 1):
            print(f"{i}. Playlist: {saved_playlists[p_id]} ({p_id})")

        last_num = len(playlist_ids) + 1
        print(f"{last_num}. Paste a new URL/ID")
        print("q. Quit")

        choice = input("\nSelect a source: ").lower()

        if choice == 'q': break

        tabs = []
        if choice == '0':
            tabs = client.get_favorites()
        elif choice.isdigit() and int(choice) < last_num:
            p_id = playlist_ids[int(choice) - 1]
            url = f"https://www.ultimate-guitar.com/user/playlist/view?id={p_id}"
            tabs = client.get_playlist(url)
        elif choice.isdigit() and int(choice) == last_num:
            url_input = input("Paste URL or ID: ")

            # Extract ID from URL if necessary
            p_id = url_input.split("id=")[-1] if "id=" in url_input else url_input

            tabs = client.get_playlist(url_input)

            if tabs:
                save_q = input(f"Found {len(tabs)} songs. Save this playlist to .env? (y/n): ").lower()
                if save_q == 'y':
                    p_name = input("Enter a nickname for this playlist: ").replace(":", "").replace(",", "")
                    save_playlist_to_env(p_id, p_name)
                    # Reload env variables after saving
                    load_dotenv(ENV_PATH, override=True)
        else:
            continue

        if not tabs:
            print("No tabs found. Check your session or URL.")
            continue

        # Shuffle Loop
        while True:
            song = random.choice(tabs)
            print(f"\n🎸 PICKED: {song['song_name']} - {song['band_name']}")
            cmd = input("[Enter] Open | [s] Skip | [b] Back to Menu: ").lower()
            if cmd == '':
                webbrowser.open(song['song_url'])
            elif cmd == 'b':
                break


if __name__ == "__main__":
    main()