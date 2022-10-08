from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
import requests
import chalk

username = inquirer.text(message="Lastfm username:").execute()
sessionid = inquirer.text(message="Lastfm 'sessionId' cookie:").execute()
playlist_length = int(
    inquirer.number(
        message="Playlist length:", min_allowed=1, validate=EmptyInputValidator()
    ).execute()
)

mix_type = inquirer.select(
    message="Mix type",
    choices=["User library", "User mix", "User recommended", "Track mix", "Artist mix"],
    multiselect=True,
).execute()

output = []  # Spotify track URIs list


def get_user_mix(
    lastfm_username: str = username,
    num_songs: int = playlist_length + 1,
    session_id=sessionid,
    page_num: int = 1,
    song_num: int = 1,
    output_lst: list[str] = output,
    mix_type: str = "mix",
) -> str:
    if mix_type == "library":
        url = f"https://www.last.fm/player/station/user/{lastfm_username}/library?page={page_num}&ajax=1"
    elif mix_type == "mix":
        url = f"https://www.last.fm/player/station/user/{lastfm_username}/mix?page={page_num}&ajax=1"
    elif mix_type == "recommended":
        url = f"https://www.last.fm/player/station/user/{lastfm_username}/recommended?page={page_num}&ajax=1"

    r = requests.get(url, cookies={"sessionid": session_id})

    # Traverse datastructure to get spotify track ids and convert to spotify compatible URIs
    output = []
    nl = "\n"

    for track in r.json()["playlist"]:
        track_name = track["_name"]
        track_artist = track["artists"][0]["_name"]
        playlink_type = track["_playlinks"][0]["affiliate"]

        if playlink_type == "spotify":
            track_id = track["_playlinks"][0]["id"]
            spotify_uri = f"spotify:track:{track_id}"
            output_lst.append(spotify_uri)
            song_num += 1
            print(
                chalk.green(
                    f"({song_num}/{num_songs-1}) ✅ {track_artist} - {track_name}"
                )
            )
        elif playlink_type == "youtube":
            return chalk.red(
                "❌ ERROR: This sesionid cookie is NOT from a spotify enabled lastfm account!"
            )
        else:
            print(
                chalk.red(
                    f"({song_num}/{num_songs}) ❌ Track not found: {track_artist} - {track_name}"
                )
            )
            song_num += 1

        if song_num == num_songs:
            "We have reached the user requested # of songs on the first page. Exit"
            return (
                f"Create a new playlist and paste the next line\n{nl.join(output_lst)}"
            )

    # Check if we have reached the required num of songs at the end of the page
    if song_num == num_songs:
        "We have reached the user requested # or songs. Exit"
        return f"{type}: Create a new playlist and paste the next line\n{nl.join(output_lst)}"
    else:
        "Query for next page"
        return get_user_mix(
            page_num=page_num + 1,
            lastfm_username=lastfm_username,
            num_songs=num_songs,
            song_num=song_num,
            session_id=session_id,
            mix_type=mix_type,
        )


# def similar_mix(
#     lastfm_username: str = username,
#     num_songs: int = playlist_length + 1,
#     session_id=sessionid,
#     page_num: int = 1,
#     song_num: int = 1,
#     output_lst: list[str] = output,
#     mix_type: str = "artist",
# ):
#     if mix_type == "artist":
#         # https://www.last.fm/user/{username}/playlists/create/from-artist
#         # POST DATA: {"artist": artist name}
#     elif mix_type == "track":
#         # https://www.last.fm/user/{username}/playlists/create/from-track
#         # POST DATA: {"track": song name, "artist": artist name}


#     r = requests.get(url, cookies={"sessionid": session_id})


for selection in mix_type:
    if selection == "User library":
        print(get_user_mix(mix_type="library"))
    elif selection == "User mix":
        print(get_user_mix())
    elif selection == "User recommended":
        print(get_user_mix(mix_type="recommended"))
    elif selection == "Track mix":
        pass
    elif selection == "Artist mix":
        pass
