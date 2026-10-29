
# Raspberry Pi Pico Alarm Clock
# main.py - Version 2.2
# Continuous clock with alarm controls and settings menu.

from machine import Pin, RTC
from utime import ticks_ms, ticks_diff, ticks_add, sleep_ms
import sys
import select
import settings


# --- Hardware Setup ---
led = Pin("LED", Pin.OUT)
rtc = RTC()


# --- Load Saved Settings ---
config = settings.load_settings()


# --- Alarm State ---
alarm_ringing = False
snooze_until = None
last_alarm_date = None


# --- Menu State ---
menu_mode = "main"
setting_hour = None


# --- Time Formatting ---
def format_time(hour, minute, second=None):
    period = "AM" if hour < 12 else "PM"

    display_hour = hour % 12

    if display_hour == 0:
        display_hour = 12

    if second is None:
        return "{:02d}:{:02d} {}".format(
            display_hour, minute, period
        )

    return "{:02d}:{:02d}:{:02d} {}".format(
        display_hour, minute, second, period
    )


# --- RTC Validation ---
def rtc_valid():
    now = rtc.datetime()

    year, month, day = now[0], now[1], now[2]
    hour, minute, second = now[4], now[5], now[6]

    return (
        year >= 2026
        and 1 <= month <= 12
        and 1 <= day <= 31
        and 0 <= hour <= 23
        and 0 <= minute <= 59
        and 0 <= second <= 59
    )


# --- Display Clock ---
def display_clock():
    now = rtc.datetime()

    print()
    print("====== ALARM CLOCK ======")

    if rtc_valid():
        print(
            "Current Time:",
            format_time(now[4], now[5], now[6])
        )
    else:
        print("Current Time: NOT SYNCHRONIZED")

    print(
        "Alarm Time:",
        format_time(
            config["alarm_hour"],
            config["alarm_minute"]
        )
    )

    print("Alarm Enabled:", config["alarm_enabled"])

    print(
        "Snooze Duration:",
        config["snooze_minutes"],
        "minutes"
    )

    if alarm_ringing:
        print("Status: RINGING!")
    elif snooze_until is not None:
        print("Status: SNOOZED")
    else:
        print("Status: READY")

    print("=========================")


# --- Save Alarm Configuration ---
def change_setting(key, value):
    return settings.update_settings(config, key, value)


# --- Reset Daily Alarm Tracking ---
def reset_alarm_tracking():
    global last_alarm_date

    last_alarm_date = None


# --- Check Alarm ---
def check_alarm():
    global alarm_ringing, snooze_until
    global last_alarm_date

    # Check whether snooze has ended.
    if snooze_until is not None:
        if ticks_diff(ticks_ms(), snooze_until) >= 0:
            snooze_until = None

            if config["alarm_enabled"]:
                alarm_ringing = True
                print("\nSNOOZE ENDED! WAKE UP!")

        return

    if not config["alarm_enabled"]:
        return

    if not rtc_valid():
        return

    now = rtc.datetime()

    today = (now[0], now[1], now[2])

    hour = now[4]
    minute = now[5]

    alarm_time = (
        config["alarm_hour"],
        config["alarm_minute"]
    )

    if (
        not alarm_ringing
        and today != last_alarm_date
        and (hour, minute) == alarm_time
    ):
        alarm_ringing = True
        last_alarm_date = today

        print("\nALARM! WAKE UP!")


# --- Update Alarm LED ---
def update_led():
    if alarm_ringing:
        led.value((ticks_ms() // 250) % 2)
    else:
        led.off()


# --- Increase Alarm Hour ---
def increase_hour():
    global alarm_ringing, snooze_until

    new_hour = (config["alarm_hour"] + 1) % 24

    if change_setting("alarm_hour", new_hour):
        reset_alarm_tracking()

        alarm_ringing = False
        snooze_until = None

        led.off()

        print(
            "Alarm updated:",
            format_time(
                config["alarm_hour"],
                config["alarm_minute"]
            )
        )


# --- Increase Alarm Minute ---
def increase_minute():
    global alarm_ringing, snooze_until

    new_minute = (config["alarm_minute"] + 1) % 60

    if change_setting("alarm_minute", new_minute):
        reset_alarm_tracking()

        alarm_ringing = False
        snooze_until = None

        led.off()

        print(
            "Alarm updated:",
            format_time(
                config["alarm_hour"],
                config["alarm_minute"]
            )
        )


# --- Toggle Alarm ---
def toggle_alarm():
    global alarm_ringing, snooze_until

    enabled = not config["alarm_enabled"]

    if change_setting("alarm_enabled", enabled):
        if not enabled:
            alarm_ringing = False
            snooze_until = None

            led.off()

        print("Alarm enabled:", enabled)


# --- Trigger Alarm Manually ---
def trigger_alarm():
    global alarm_ringing, snooze_until

    if config["alarm_enabled"]:
        snooze_until = None
        alarm_ringing = True

        print("\nALARM! WAKE UP!")
    else:
        print("Alarm is disabled.")


# --- Dismiss Alarm ---
def dismiss_alarm():
    global alarm_ringing, snooze_until

    if alarm_ringing:
        alarm_ringing = False
        snooze_until = None

        led.off()

        print("Alarm dismissed.")
    else:
        print("No active alarm to dismiss.")


# --- Snooze Alarm ---
def snooze_alarm():
    global alarm_ringing, snooze_until

    if alarm_ringing:
        delay_ms = config["snooze_minutes"] * 60000

        snooze_until = ticks_add(
            ticks_ms(),
            delay_ms
        )

        alarm_ringing = False
        led.off()

        print(
            "Alarm snoozed for",
            config["snooze_minutes"],
            "minutes."
        )
    else:
        print("No active alarm to snooze.")


# --- Main and Settings Menus ---
def show_menu():
    print()

    if menu_mode == "main":
        print("====== MAIN MENU ======")
        print("1 - Increase alarm hour")
        print("2 - Increase alarm minute")
        print("3 - Enable/Disable alarm")
        print("4 - Trigger alarm (test)")
        print("5 - Dismiss alarm")
        print("6 - Snooze alarm")
        print("7 - Show clock")
        print("8 - Settings Menu")
        print("9 - Exit")
        print("=======================")

    elif menu_mode == "settings":
        print("====== SETTINGS MENU ======")
        print("1 - Set exact alarm time")
        print("2 - Set snooze duration")
        print("3 - Enable/Disable alarm")
        print("4 - View current settings")
        print("5 - Return to main menu")
        print("===========================")

    elif menu_mode == "set_hour":
        print("Enter alarm hour (0-23):")

    elif menu_mode == "set_minute":
        print("Enter alarm minute (0-59):")

    elif menu_mode == "set_snooze":
        print("Enter snooze duration (1-60 minutes):")

    print()


# --- Process Terminal Commands ---
def process_command(choice):
    global menu_mode, setting_hour
    global alarm_ringing, snooze_until

    # Main Menu
    if menu_mode == "main":

        if choice == "1":
            increase_hour()

        elif choice == "2":
            increase_minute()

        elif choice == "3":
            toggle_alarm()

        elif choice == "4":
            trigger_alarm()

        elif choice == "5":
            dismiss_alarm()

        elif choice == "6":
            snooze_alarm()

        elif choice == "7":
            display_clock()

        elif choice == "8":
            menu_mode = "settings"

        elif choice == "9":
            print("Alarm clock stopped.")
            return False

        else:
            print("Invalid choice.")

    # Settings Menu
    elif menu_mode == "settings":

        if choice == "1":
            menu_mode = "set_hour"

        elif choice == "2":
            menu_mode = "set_snooze"

        elif choice == "3":
            toggle_alarm()

        elif choice == "4":
            display_clock()

        elif choice == "5":
            menu_mode = "main"

        else:
            print("Invalid choice.")

    # Set Exact Alarm Hour
    elif menu_mode == "set_hour":

        try:
            hour = int(choice)

            if 0 <= hour <= 23:
                setting_hour = hour
                menu_mode = "set_minute"

            else:
                print("Hour must be between 0 and 23.")

        except ValueError:
            print("Enter a valid number.")

    # Set Exact Alarm Minute
    elif menu_mode == "set_minute":

        try:
            minute = int(choice)

            if 0 <= minute <= 59:

                updated = config.copy()

                updated["alarm_hour"] = setting_hour
                updated["alarm_minute"] = minute

                if settings.save_settings(updated):
                    config.update(updated)

                    reset_alarm_tracking()

                    alarm_ringing = False
                    snooze_until = None

                    led.off()

                    print(
                        "Alarm set to",
                        format_time(setting_hour, minute)
                    )

                setting_hour = None
                menu_mode = "settings"

            else:
                print("Minute must be between 0 and 59.")

        except ValueError:
            print("Enter a valid number.")

    # Set Snooze Duration
    elif menu_mode == "set_snooze":

        try:
            minutes = int(choice)

            if 1 <= minutes <= 60:

                if change_setting(
                    "snooze_minutes",
                    minutes
                ):
                    print(
                        "Snooze duration set to",
                        minutes,
                        "minutes."
                    )

                menu_mode = "settings"

            else:
                print("Snooze must be between 1 and 60 minutes.")

        except ValueError:
            print("Enter a valid number.")

    return True


# --- Main Program ---
def main():
    global menu_mode

    print("Raspberry Pi Pico Alarm Clock - Version 2.2")
    print("Continuous alarm system started!")

    if not rtc_valid():
        print("WARNING: RTC may not be synchronized!")
        print("Synchronize time before relying on the alarm.")

    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    last_check = ticks_ms()
    last_display = ticks_ms()

    command_buffer = ""
    running = True

    menu_mode = "main"

    show_menu()

    try:
        check_alarm()

        while running:
            now = ticks_ms()

            # Check scheduled alarm every second.
            if ticks_diff(now, last_check) >= 1000:
                last_check = now
                check_alarm()

            # Keep LED blinking during alarm.
            update_led()

            # Display clock every 10 seconds.
            if ticks_diff(now, last_display) >= 10000:
                last_display = now
                display_clock()

            # Non-blocking terminal commands.
            if poller.poll(0):

                char = sys.stdin.read(1)

                if char == "\n" or char == "\r":

                    choice = command_buffer.strip()
                    command_buffer = ""

                    if choice:
                        running = process_command(choice)

                        if running:
                            show_menu()

                elif char == "\x08" or char == "\x7f":
                    command_buffer = command_buffer[:-1]

                elif char:
                    if len(command_buffer) < 16:
                        command_buffer += char

            sleep_ms(20)

    except KeyboardInterrupt:
        print("\nAlarm clock interrupted.")

    finally:
        led.off()
        print("System stopped.")


if __name__ == "__main__":
    main()
