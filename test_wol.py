# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 09:38:34 2024

@author: AxelBaillet
"""
import win32evtlog
from datetime import datetime, timedelta

def get_recent_wake_events(minutes=5):
    server = 'localhost'
    logtype = 'System'
    hand = win32evtlog.OpenEventLog(server, logtype)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    events = []
    cutoff_time = datetime.now() - timedelta(minutes=minutes)

    while True:
        events_list = win32evtlog.ReadEventLog(hand, flags, 0)
        if events_list:
            for event in events_list:
                if event.TimeGenerated < cutoff_time:
                    return events  # Stop reading if the event is older than the cutoff time
                if event.EventID == 1 and event.SourceName == "Power-Troubleshooter":
                    events.append(event)
        else:
            break
    return events

def analyze_wake_event(event):
    strings = event.StringInserts
    if strings and any("Wake Source: " in s for s in strings):
        for s in strings:
            if "Wake Source: " in s:
                return s
    return None

# Example usage
def main():
    print('awake?')
    recent_events = get_recent_wake_events(minutes=5)
    for event in recent_events:
        wake_source = analyze_wake_event(event)
        if wake_source:
            print(f"Wake event detected: {wake_source}")
            if "Wake Source: 3" in wake_source:
                print("Detected Wake-on-LAN event.")
            else:
                print("Detected user-initiated wake event.")
            break
        
main()