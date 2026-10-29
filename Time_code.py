
# Raspberry Pi Pico Alarm Clock
# Version 2 - Real Time Clock and Alarm System

from machine import Pin, RTC
from utime import sleep_ms, ticks_ms, ticks_diff

# --- Hardware Setup ---
led = Pin("LED", Pin.OUT)
rtc = RTC()

# --- Alarm Settings ---
# Change these to your desired alarm time (24-hour format)
alarm_hour = 0
alarm_minute = 5

alarm_enabled = True
alarm_ringing = False
last_alarm_date = None

# --- Clock Functions ---
def display_clock():
    year, month, day, weekday, hour, minute, second, subsecond = rtc.datetime()

    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12

    if display_hour == 0:
        display_hour = 12

    print("Current Time: {:02d}:{:02d}:{:02d} {}".format(
        display_hour, minute, second, period
    ))


# --- Alarm Functions ---
def check_alarm():
    global alarm_ringing, last_alarm_date

    year, month, day, weekday, hour, minute, second, subsecond = rtc.datetime()

    today = (year, month, day)

    if (alarm_enabled
            and not alarm_ringing
            and today != last_alarm_date
            and hour == alarm_hour
            and minute == alarm_minute):

        alarm_ringing = True
        last_alarm_date = today

        print("ALARM! WAKE UP!")


def dismiss_alarm():
    global alarm_ringing

    alarm_ringing = False
    led.off()
    print("Alarm dismissed.")


def update_alarm_led():
    if alarm_ringing:
        led.value((ticks_ms() // 250) % 2)
    else:
        led.off()


# --- Main Program ---
print("Raspberry Pi Pico Alarm Clock - Version 2")
print("Alarm set for {:02d}:{:02d}".format(
    alarm_hour, alarm_minute
))
print("Clock started!")

last_display = ticks_ms()

try:
    while True:
        now = ticks_ms()

        if ticks_diff(now, last_display) >= 1000:
            last_display = now

            display_clock()
            check_alarm()

        update_alarm_led()
        sleep_ms(20)

except KeyboardInterrupt:
    dismiss_alarm()
    print("Clock stopped.")
