import subprocess

def get_current_track_info():
    script = '''
    tell application "Music"
        if it is running and player state is playing then
            set trackName to name of current track
            set artistName to artist of current track
            return trackName & "||" & artistName
        else
            return "||"
        end if
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip().split("||")

title, artist = get_current_track_info()
if title and artist:
    print(f"🎵 Now Playing: {title} - {artist}")
else:
    print("Apple Music is not playing.")
