# Demo Play Sound

QML-only demo: play audio from a URL using QtMultimedia (`MediaPlayer`), with transport controls (play, pause, stop), a volume slider, playback position, and an on-screen debug log. On startup it checks whether `QtMultimedia 5.15` can be imported and logs the result.

No LispBM script and no native code are included.

## Usage

Install the package from the VESC Package store and open its UI. Enter an audio source in the **URL** field—either a remote URL (`https://…`) or a local path (`file:///…`, for example `file:///sdcard/Music/test.mp3`). A sample HTTPS stream is filled in by default. Use **Play**, **Pause**, and **Stop** as needed; adjust volume with the slider. Status and errors appear in the debug log at the bottom.
