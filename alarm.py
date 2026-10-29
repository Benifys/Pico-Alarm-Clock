
# Raspberry Pi Pico Alarm Clock
# alarm.py - Version 1
# Alarm management, snooze, dismissal, and daily reset.

from machine import Pin, RTC
from utime import ticks_ms, ticks_diff, sleep_ms

# --- Hardware Setup ---
led = Pin("LED", Pin.OUT)
rtc = RTC()


# --- Alarm Settings ---
alarm_hour = 0
alarm_minute = 5

alarm_enabled = True
alarm_ringing = False

snooze_minutes = 5
snooze_until = None

last_alarm_date = None


# --- Alarm Configuration ---
def set_alarm(hour, minute):
    global alarm_hour, alarm_minute
    global last_alarm_date, snooze_until

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        print("Invalid alarm time.")
        return

    alarm_hour = hour
    alarm_minute = minute

    last_alarm_date = None
    snooze_until = None

    print("Alarm set for {:02d}:{:02d}".format(
        alarm_hour, alarm_minute
    ))


def enable_alarm():
    global alarm_enabled

    alarm_enabled = True
    print("Alarm enabled.")


def disable_alarm():
    global alarm_enabled, alarm_ringing, snooze_until

    alarm_enabled = False
    alarm_ringing = False
    snooze_until = None

    led.off()
    print("Alarm disabled.")


# --- Alarm Control ---
def dismiss_alarm():
    global alarm_ringing, snooze_until

    alarm_ringing = False
    snooze_until = None

    led.off()
    print("Alarm dismissed.")


def snooze_alarm(minutes=5):
    global alarm_ringing, snooze_until

    if not alarm_ringing:
        print("No active alarm to snooze.")
        return

    now = rtc.datetime()
    current_minutes = now[4] * 60 + now[5]

    snooze_until = (current_minutes + minutes) % 1440

    alarm_ringing = False
    led.off()

    print("Alarm snoozed for {} minutes.".format(minutes))


# --- Alarm Detection ---
def check_alarm():
    global alarm_ringing, last_alarm_date, snooze_until

    now = rtc.datetime()

    year, month, day = now[0], now[1], now[2]
    hour, minute = now[4], now[5]

    today = (year, month, day)
    current_minutes = hour * 60 + minute

    if not alarm_enabled:
        return

    # Check whether snooze has expired
    if snooze_until is not None:
        if current_minutes == snooze_until:
            alarm_ringing = True
            snooze_until = None
            print("SNOOZE ENDED! WAKE UP!")
        return

    # Check regular alarm
    if (not alarm_ringing
            and today != last_alarm_date
            and hour == alarm_hour
            and minute == alarm_minute):

        alarm_ringing = True
        last_alarm_date = today

        print("ALARM! WAKE UP!")


# --- LED Alarm ---
def update_alarm_led():
    if alarm_ringing:
        led.value((ticks_ms() // 250) % 2)
    else:
        led.off()


# --- Main Test Program ---
def main():
    print("Alarm system started!")
    print("Alarm set for {:02d}:{:02d}".format(
        alarm_hour, alarm_minute
    ))

    last_check = ticks_ms()

    try:
        while True:
            now = ticks_ms()

            if ticks_diff(now, last_check) >= 1000:
                last_check = now
                check_alarm()

            update_alarm_led()
            sleep_ms(20)

    except KeyboardInterrupt:
        led.off()
        print("Alarm test stopped.")


if __name__ == "__main__":
    main()
