
# Raspberry Pi Pico Alarm Clock
# display.py - Version 1
# Simulates the alarm clock display using the terminal.
# Future support for an OLED display.

from machine import RTC
from utime import sleep

# --- Hardware Setup ---
rtc = RTC()

# --- Test Settings ---
alarm_hour = 8
alarm_minute = 0
alarm_enabled = True
alarm_ringing = False


# --- Time Formatting ---
def format_time(hour, minute, second=None):
    # Convert 24-hour time to 12-hour format
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12

    if display_hour == 0:
        display_hour = 12

    # Display seconds for current time
    if second is not None:
        return "{:02d}:{:02d}:{:02d} {}".format(
            display_hour, minute, second, period
        )

    # Display hours and minutes for alarm time
    return "{:02d}:{:02d} {}".format(
        display_hour, minute, period
    )


# --- Display Functions ---
def display_screen(hour, minute, second,
                   alarm_hour, alarm_minute,
                   alarm_enabled, alarm_ringing):

    current_time = format_time(hour, minute, second)
    alarm_time = format_time(alarm_hour, alarm_minute)

    # Determine alarm status
    if alarm_ringing:
        status = "RINGING!"
    elif alarm_enabled:
        status = "ON"
    else:
        status = "OFF"

    # Simulated OLED display
    print("------------------------")
    print("     PICO ALARM CLOCK")
    print("------------------------")
    print("Time:  " + current_time)
    print("Alarm: " + alarm_time)
    print("Status: " + status)
    print("------------------------")


# --- Main Test Program ---
def main():
    print("Display test started!")

    try:
        while True:
            year, month, day, weekday, hour, minute, second, subsecond = rtc.datetime()

            display_screen(
                hour, minute, second,
                alarm_hour, alarm_minute,
                alarm_enabled, alarm_ringing
            )

            sleep(1)

    except KeyboardInterrupt:
        print("Display test stopped.")


if __name__ == "__main__":
    main()
