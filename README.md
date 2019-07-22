# Description

My test project playing with Sony Toio. See https://www.sony.net/SonyInfo/design/stories/toio/.

This runs on Linux with Python 3.6 or later. I am personally running this on Raspberry Pi 4 + Stretch.

# Getting Started

1. Install the package with `pip`. If you want to just try, `pip install -e .` at the root directory will be convenient.
2. Power on your Toio cubes, and run `./scan-cubes.sh`. It will scan the cubes and create `toio-cubes.txt` that includes their MAC addresses. Note that the scanning requires the root privilege and you may be asked the `sudo` password.
3. Run examples, e.g. `python examples/soccer.py`.
  * Stay in the same directory as `toio-cubes.txt`.
  * The Toio collection mat is required.

# Examples (under examples directory)

* simple.py: Just connects to cubes, identifies themselves with sounds and lights, then disconnects
* soundeffects.py: Beep the sound effects from #0 to #10
* notifications.py: Outputs the notifications (positions, button states, motions) to the console.
* rotate.py: Cube #1 rotates to the direction of cube #2
* symmetric.py: Cube #1 moves to the point-symmetric position of cube #2
* circle.py: Cube #1 moves circularly assuming cube #2 as the center
* gravity.py: Cube #1 and #2 moves around the mat with a gravity (and repulsion if they are too close) between each other
* soccer.py: Cube #1 plays soccer using cube #2 as the ball
