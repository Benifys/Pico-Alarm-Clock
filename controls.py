
# Raspberry Pi Pico Alarm Clock
# controls.py - Version 1
# Simulate alarm clock buttons using the terminal.

from machine import Pin
from utime import sleep_ms

# --- Hardware Setup ---
led = Pin("LED", Pin.OUT)

# --- Default Settings ---
alarm_hour = 7
alarm_minute = 30
alarm_enabled = True
alarm_ringing = False
snooze_minutes = 5


# --- Display Current Settings ---
def show_status():
    print()
    print("--- Alarm Clock Status ---")
    print("Alarm Time: {:02d}:{:02d}".format(
        alarm_hour, alarm_minute))
    print("Alarm Enabled:", alarm_enabled)
    print("Alarm Ringing:", alarm_ringing)
    print("Snooze Duration:", snooze_minutes, "minutes")
    print("--------------------------")


# --- Change Alarm Hour ---
def increase_hour():
    global alarm_hour

    alarm_hour = (alarm_hour + 1) % 24
    print("Alarm hour changed to:", alarm_hour)


# --- Change Alarm Minute ---
def increase_minute():
    global alarm_minute

    alarm_minute = (alarm_minute + 1) % 60
    print("Alarm minute changed to:", alarm_minute)


# --- Toggle Alarm ---
def toggle_alarm():
    global alarm_enabled, alarm_ringing

    alarm_enabled = not alarm_enabled

    if not alarm_enabled:
        alarm_ringing = False
        led.off()

    print("Alarm enabled:", alarm_enabled)


# --- Simulate Alarm ---
def trigger_alarm():
    global alarm_ringing

    if alarm_enabled:
        alarm_ringing = True
        led.on()
        print("ALARM! WAKE UP!")
    else:
        print("Cannot trigger: Alarm is disabled.")


# --- Dismiss Alarm ---
def dismiss_alarm():
    global alarm_ringing

    if alarm_ringing:
        alarm_ringing = False
        led.off()
        print("Alarm dismissed.")
    else:
        print("No active alarm to dismiss.")


# --- Snooze Alarm ---
def snooze_alarm():
    global alarm_ringing

    if alarm_ringing:
        alarm_ringing = False
        led.off()
        print("Alarm snoozed for", snooze_minutes, "minutes.")
    else:
        print("No active alarm to snooze.")


# --- Simulated Button Menu ---
def main():
    print("Raspberry Pi Pico Alarm Controls Test")

    while True:
        show_status()

        print()
        print("Select a button:")
        print("1 - Increase alarm hour")
        print("2 - Increase alarm minute")
        print("3 - Enable/Disable alarm")
        print("4 - Trigger alarm (test)")
        print("5 - Dismiss alarm")
        print("6 - Snooze alarm")
        print("7 - Exit")

        try:
            choice = input("Enter choice (1-7): ").strip()

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
                led.off()
                print("Controls test stopped.")
                break

            else:
                print("Invalid choice. Try again.")

            sleep_ms(100)

        except KeyboardInterrupt:
            led.off()
            print()
            print("Controls test interrupted.")
            break


if __name__ == "__main__":
    main()
