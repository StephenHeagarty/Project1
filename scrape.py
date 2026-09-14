import time
import requests
import pandas as pd

API_BASE = "https://logs.tf"
PAGE_SIZE = 50

# Number of qualifying games to scrape before stopping.
MAX_GAMES = 1000

# Delay between requests, in seconds.
REQUEST_DELAY = 0.1


CAPTURE_POINT_CSV = "spy_capture_point.csv"
PAYLOAD_CSV = "spy_payload.csv"

session = requests.Session()


def get_json(url: str):
    """Fetch JSON from a URL and return the decoded object."""
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_logs(offset: int, limit: int = PAGE_SIZE):
    """
    Retrieve one page of logs from the logs.tf API.
    """
    url = f"{API_BASE}/api/v1/log"
    params = {
        "limit": limit,
        "offset": offset,
    }

    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if not data.get("success"):
        raise RuntimeError(f"logs.tf API returned failure: {data}")

    return data


def process_game(log):
    """
    Download and process one game's detailed JSON.

    Returns:
        list of rows
    """

    log_id = log["id"]
    map_name = log.get("map", "")

    if map_name.startswith("cp"):
        game_type = "capture_point"
    elif map_name.startswith("pl"):
        game_type = "payload"
    else:
        return []

    print(f"Processing {log_id} | {game_type} | {map_name}")

    url = f"{API_BASE}/json/{log_id}"

    try:
        game_data = get_json(url)
    except requests.RequestException as e:
        print(f"  Failed to download {log_id}: {e}")
        return []

    rows = []

    players = game_data.get("players", {})

    for player_id, player_data in players.items():

        class_stats = player_data.get("class_stats", [])

        if not class_stats:
            continue

        for class_data in class_stats:

            # We only care about Spy
            if class_data.get("type") != "spy":
                continue

            deaths = class_data.get("deaths", 0)
            total_time = class_data.get("total_time", 0)

            weapons = class_data.get("weapon", {})

            for weapon_name, weapon_data in weapons.items():
                rows.append({
                    "game_id": log_id,
                    "map": map_name,
                    "game_type": game_type,
                    "player_id": player_id,
                    "weapon": weapon_name,
                    "kills": weapon_data.get("kills", 0),
                    "dmg": weapon_data.get("dmg", 0),
                    "avg_dmg": weapon_data.get("avg_dmg", 0),
                    "deaths": deaths,
                    "total_time": total_time,
                })

    return rows


def scrape(max_games=MAX_GAMES):
    capture_point_rows = []
    payload_rows = []

    offset = 0
    games_processed = 0

    while games_processed < max_games:

        print(f"\nFetching logs: offset={offset}")

        try:
            data = get_logs(offset)
        except requests.RequestException as e:
            print(f"Failed to fetch log page: {e}")
            break

        logs = data.get("logs", [])

        if not logs:
            print("No more logs returned.")
            break

        for log in logs:

            if games_processed >= max_games:
                break

            map_name = log.get("map", "")

            # Ignore maps that aren't CP or Payload
            if not (
                    map_name.startswith("cp")
                    or map_name.startswith("pl")
            ):
                continue

            rows = process_game(log)

            if map_name.startswith("cp"):
                capture_point_rows.extend(rows)
            elif map_name.startswith("pl"):
                payload_rows.extend(rows)

            games_processed += 1

            print(
                f"  Games processed: "
                f"{games_processed}/{max_games}"
            )

            time.sleep(REQUEST_DELAY)

        offset += PAGE_SIZE

    # Convert to DataFrames
    capture_point_df = pd.DataFrame(capture_point_rows)
    payload_df = pd.DataFrame(payload_rows)

    return capture_point_df, payload_df


if __name__ == "__main__":
    cp_df, pl_df = scrape(MAX_GAMES)

    print("\n=========================")
    print("Scraping complete")
    print("=========================")

    print(f"Capture Point rows: {len(cp_df)}")
    print(f"Payload rows:       {len(pl_df)}")

    cp_df.to_csv(CAPTURE_POINT_CSV, index=False)
    pl_df.to_csv(PAYLOAD_CSV, index=False)

    print(f"\nSaved: {CAPTURE_POINT_CSV}")
    print(f"Saved: {PAYLOAD_CSV}")
