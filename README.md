# Runkeeper Apple Watch recording to GPX

This python script takes the Runkeeper json point information and converts it to a standard gpx file that can be uploaded to a different service, such as Strava.

## Motivation
I ran a virtual race that required the Runkeeper app, so I recorded the run on my Apple Watch Runkeeper app hoping that I can both post to Runkeeper to get credit for the race and also upload the results to my personal Strava account. Turns out, Runkeeper lets you export GPX files from your runs using their phone app, but not when using the standalone Apple Watch app. Thankfully, *most* of the information necessary to create a GPX file is available from Runkeeper, so I got ahold of that data, extracted the neccessary information and wrote this script to generate a gpx file

## Python requirements
This script is written for python 3.8, and requires the following python libraries:
- `pandas`
- `gpxpy`
- `pytz`

You can install these by running `pip install <lib>`

## Directions
1. Go to your Runkeeper activity
2. Using Chrome Inspection tools (or alternatives on other browsers), look at the network requests made from the site
3. You will see a request to fetch a json point data file, download this file
4. The json contains points + heart rate data (if you recorded HR), but not the start time of the run, so you would have to grab that separately
5. run `python runkeeperToGpx.py <path_to_downloaded_json> <run_start_time>`
    - if you want heart rate data to be included, add an "-hr" flag
    - the gpx file exported will be called "result.gpx", you can provide your own path via the "-o" flag
    - ex. `python runkeeperToGpx.py race.json "2020-10-03 15:16:49" -hr -o raceResult.gpx`

## Caveats
This was mostly a quick script to solve my own issue, so I'm sure it doesn't fit all cases, feel free to open up an issue/PR to add more functionality to this script