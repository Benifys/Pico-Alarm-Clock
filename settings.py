
# Raspberry Pi Pico Alarm Clock
# settings.py - Version 1
# Save and load alarm settings using JSON.

import json

# --- Default Settings ---
DEFAULT_SETTINGS = {
    "alarm_hour": 8,
    "alarm_minute": 0,
    "alarm_enabled": True,
    "snooze_minutes": 5
}

SETTINGS_FILE = "alarm_settings.json"


# --- Validate Settings ---
def validate_settings(settings):
    if not isinstance(settings, dict):
        return False

    try:
        hour = settings["alarm_hour"]
        minute = settings["alarm_minute"]
        enabled = settings["alarm_enabled"]
        snooze = settings["snooze_minutes"]

        if type(hour) is not int or not 0 <= hour <= 23:
            return False

        if type(minute) is not int or not 0 <= minute <= 59:
            return False

        if type(enabled) is not bool:
            return False

        if type(snooze) is not int or not 1 <= snooze <= 60:
            return False

        return True

    except (KeyError, TypeError):
        return False


# --- Save Settings ---
def save_settings(settings):
    if not validate_settings(settings):
        print("Invalid settings. Nothing saved.")
        return False

    try:
        with open(SETTINGS_FILE, "w") as file:
            json.dump(settings, file)

        print("Settings saved successfully!")
        return True

    except OSError as error:
        print("Error saving settings:", error)
        return False


# --- Load Settings ---
def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)

        if validate_settings(settings):
            print("Saved settings loaded!")
            return settings

        print("Invalid saved settings. Using defaults.")

    except (OSError, ValueError, TypeError):
        print("No valid settings file. Using defaults.")

    return DEFAULT_SETTINGS.copy()


# --- Update Settings ---
def update_settings(settings, key, value):
    if key not in DEFAULT_SETTINGS:
        print("Unknown setting:", key)
        return False

    updated = settings.copy()
    updated[key] = value

    if not validate_settings(updated):
        print("Invalid value for:", key)
        return False

    if save_settings(updated):
        settings.update(updated)
        return True

    return False



# --- Main Test Program ---
def main():
    print("Alarm Settings Configuration")

    settings = load_settings()

    print("Current Alarm: {:02d}:{:02d}".format(
        settings["alarm_hour"],
        settings["alarm_minute"]
    ))

    try:
        hour = int(input("Enter alarm hour (0-23): "))
        minute = int(input("Enter alarm minute (0-59): "))

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            settings["alarm_hour"] = hour
            settings["alarm_minute"] = minute

            if save_settings(settings):
                print("Alarm updated successfully!")
                print("New Alarm: {:02d}:{:02d}".format(
                    hour, minute
                ))
        else:
            print("Invalid alarm time.")

    except ValueError:
        print("Please enter valid numbers.")


if __name__ == "__main__":
    main()
