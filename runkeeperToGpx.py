import argparse
import datetime
import gpxpy
import gpxpy.gpx
import json
import pandas as pd
import pytz
import xml.etree.ElementTree as etree

# Class to transform runkeeper point dictionary into object
class RunkeeperPoint:
    hr = None

    def __init__(self, **entries):
        self.__dict__.update(entries)
    
    def add_hr(self, hr):
        self.hr = hr
    
    def date_time(self, start_time):
        return start_time + datetime.timedelta(milliseconds=self.timestamp)

# Class to transform heart rate tuple into object
class HeartRatePoint:
    def __init__(self, time_seconds, hr):
        self.time_seconds, self.hr = time_seconds, hr


# Parsing command line arguments
parser = argparse.ArgumentParser(description='Convert Runkeeper JSON to GPX')

parser.add_argument('json_file', type=str, action='store', help='path of the json file downloaded from Runkeeper')
parser.add_argument('start_time', action='store', help='start time of the run', type=datetime.datetime.fromisoformat)
parser.add_argument('-hr', '--includeheartrate', action='store_true', help='include heart rate data in gpx')
parser.add_argument('-o', '--output', action='store', type=str, default='result.gpx', help='output file path')

args = parser.parse_args()

# open race json
with open(args.json_file, 'r') as r:
    raceJson = json.loads(r.read())

runkeeper_points = [RunkeeperPoint(**x) for x in raceJson['points']]

start_time = args.start_time

if args.includeheartrate:
    heartrate_points = [HeartRatePoint(x[0], x[1]) for x in raceJson['chartData']['series']['HEARTRATE']['data']]
    timeIndex = pd.DatetimeIndex([start_time + datetime.timedelta(seconds=x.time_seconds) for x in heartrate_points])
    timeSeries = pd.Series([x.hr for x in heartrate_points], index=timeIndex)

    # for each gps point, find the relevant HR
    for i, rp in enumerate(runkeeper_points):
        timestamp = rp.date_time(start_time)

        # find the last heart rate measurement at the time of the GPS recording
        hrPoint = timeSeries[timeSeries.index < timestamp].last_valid_index()
        
        if hrPoint:
            rp.add_hr(timeSeries[hrPoint])

# Used an example from the gpxpy library
gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

time_elem = etree.Element('time')
time_elem.text = str(start_time)

gpx.metadata_extensions.append(time_elem)

# Create points:
for rp in runkeeper_points:
    # altitude is measured in meters, converting to feet, although it seems Strava just uses its own elevation map
    track_point = gpxpy.gpx.GPXTrackPoint(latitude=rp.latitude, longitude=rp.longitude, elevation=rp.altitude * 3.28084, time=start_time + datetime.timedelta(milliseconds=rp.timestamp))

    if rp.hr:
        # create extension element
        extension_elem = etree.Element('gpxtpx:TrackPointExtension')
        hr_elem = etree.SubElement(extension_elem, 'gpxtpx:hr')
        hr_elem.text = str(rp.hr)

        track_point.extensions.append(extension_elem)

    gpx_segment.points.append(track_point)
    
with open(args.output, 'w') as w:
    w.write(gpx.to_xml())
