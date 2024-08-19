import os
import datetime
import pyperclip
import threading
from tzlocal import get_localzone
import customtkinter as ctk
from tkinter import filedialog
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import tkinter as tk
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GCalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Calendar Event Uploader")

        # Set the default size of the window
        window_width = 900
        window_height = 600

        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the position to center the window
        position_top = int((screen_height / 2) - (window_height / 2))
        position_right = int((screen_width / 2) - (window_width / 2))

        # Set the geometry of the window
        self.root.geometry(
            f"{window_width}x{window_height}+{position_right}+{position_top}"
        )
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.creds = None
        self.credentials_path = None
        self.current_date = datetime.date.today()
        self.events = []

        self.check_credentials()

    def check_credentials(self):
        if os.path.exists("credentials_path.txt"):
            with open("credentials_path.txt", "r") as file:
                self.credentials_path = file.read().strip()

        if not self.credentials_path or not os.path.exists(self.credentials_path):
            self.show_upload_instructions()
        else:
            self.create_widgets()
            self.authenticate()

    def show_upload_instructions(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configure the root grid to center the content
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the instructions and button
        instruction_frame = ctk.CTkFrame(self.root)
        instruction_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Center the frame's content
        instruction_frame.grid_rowconfigure(0, weight=1)
        instruction_frame.grid_columnconfigure(0, weight=1)

        # Instruction label
        instruction_label = ctk.CTkLabel(
            instruction_frame,
            text="First time setup: Please upload your Google Calendar API credentials file (credentials.json).",
            wraplength=300,
        )
        instruction_label.grid(row=0, column=0, padx=10, pady=(0, 0), sticky="nsew")

        # Upload button
        upload_button = ctk.CTkButton(
            instruction_frame, text="Upload File", command=self.upload_credentials_file
        )
        upload_button.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="nsew")

    def upload_credentials_file(self):
        self.credentials_path = filedialog.askopenfilename(
            title="Select credentials.json file", filetypes=[("JSON files", "*.json")]
        )
        if self.credentials_path:
            with open("credentials_path.txt", "w") as file:
                file.write(self.credentials_path)
            self.create_widgets()
            self.authenticate()

    def create_widgets(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame to contain all widgets
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configure rows and columns in the main frame to handle resizing
        main_frame.grid_rowconfigure(0, weight=1)  # Row for date navigation and events
        main_frame.grid_rowconfigure(1, weight=0)  # Row for add event button
        main_frame.grid_columnconfigure(0, weight=1)

        # Frame to hold date navigation and event list
        center_frame = ctk.CTkFrame(main_frame)
        center_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure rows and columns in the center frame
        center_frame.grid_rowconfigure(0, weight=0)  # Row for date navigation
        center_frame.grid_rowconfigure(1, weight=1)  # Row for events
        center_frame.grid_columnconfigure(0, weight=1)

        # Frame for date navigation
        date_frame = ctk.CTkFrame(center_frame)
        date_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        prev_day_button = ctk.CTkButton(date_frame, text="<", command=self.previous_day)
        prev_day_button.pack(side="left", padx=5, expand=True)

        self.date_label = ctk.CTkLabel(
            date_frame,
            text=self.current_date.strftime("%Y-%m-%d"),
            font=("Arial", 16),
        )
        self.date_label.pack(side="left", padx=10)

        next_day_button = ctk.CTkButton(date_frame, text=">", command=self.next_day)
        next_day_button.pack(side="left", padx=5, expand=True)

        # Scrollable frame for events
        scrollable_frame = ctk.CTkScrollableFrame(center_frame)
        scrollable_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Display events in the scrollable frame
        self.display_events(scrollable_frame)

        # Frame for buttons at the bottom
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="sew")

        # Configure the button frame to handle the buttons side by side
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        button_frame.grid_columnconfigure(4, weight=0)

        # Add event button
        add_event_button = ctk.CTkButton(
            button_frame,
            text="Add Event",
            command=self.open_add_event_window,
        )
        add_event_button.grid(row=0, column=0, padx=5, pady=5)

        # Paste Events from ChatGPT button
        gpt_button = ctk.CTkButton(
            button_frame,
            text="Paste Events from ChatGPT",
            command=self.open_paste_events_window,
        )
        gpt_button.grid(row=0, column=1, padx=5, pady=5)

        # Upload to Google Calendar button
        upload_button = ctk.CTkButton(
            button_frame,
            text="Upload to Google Calendar",
            command=self.upload_events_to_calendar,
        )
        upload_button.grid(row=0, column=2, padx=5, pady=5)

        # Clear All Events button
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear All Events",
            command=self.clear_all_events,
        )
        clear_button.grid(row=0, column=3, padx=5, pady=5)

        # Create the exit button
        exit_button = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.root.quit,  # Close the application
        )
        exit_button.grid(row=0, column=4, padx=5, pady=5)

        # Configure the root to resize properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def clear_all_events(self):
        self.events.clear()
        self.create_widgets()  # Refresh the UI to reflect the cleared events

    def previous_day(self):
        self.current_date -= datetime.timedelta(days=1)
        self.update_date_label()

    def next_day(self):
        self.current_date += datetime.timedelta(days=1)
        self.update_date_label()

    def update_date_label(self):
        self.date_label.configure(text=self.current_date.strftime("%Y-%m-%d"))
        self.create_widgets()  # Recreate widgets to refresh the event list

    def create_option_menu(self, parent, variable, options, height, font_size, width):
        return ctk.CTkOptionMenu(
            parent,
            variable=variable,
            values=options,
            height=height,
            font=("Arial", font_size),
            width=width,
        )

    def upload_events_to_calendar(self):
        # Create the loading bar window
        loading_window = ctk.CTkToplevel(self.root)
        loading_window.title("Uploading Events")
        loading_window.geometry("400x150")
        loading_window.resizable(False, False)

        # Get the screen width and height
        screen_width = loading_window.winfo_screenwidth()
        screen_height = loading_window.winfo_screenheight()

        # Get the window width and height
        window_width = 400
        window_height = 150

        # Calculate the x and y position
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Set the position of the loading window
        loading_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make sure the loading window appears above the main interface
        loading_window.lift()  # Bring the window to the top
        loading_window.attributes("-topmost", True)  # Keep the window on top

        # Create and place the loading bar
        progress = ctk.CTkProgressBar(loading_window, mode="determinate", width=300)
        progress.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

        # Create and place the status label
        status_label = ctk.CTkLabel(loading_window, text="", font=("Arial", 12))
        status_label.grid(row=1, column=0, padx=20, pady=5, columnspan=2)

        # Function to upload events
        def upload_events():
            total_events = len(self.events)
            service = build("calendar", "v3", credentials=self.creds)
            calendar_id = "primary"
            local_timezone = get_localzone()
            local_timezone_str = str(local_timezone)

            for i, event in enumerate(self.events):
                try:
                    # Update status label with current event being processed
                    status_label.configure(text=f"Uploading event: {event['name']}")
                    loading_window.update()

                    # Parse start and end times
                    def parse_time(time_str):
                        try:
                            return datetime.datetime.strptime(
                                time_str, "%I:%M %p"
                            ).time()
                        except ValueError as e:
                            status_label.configure(text=f"Time format error: {e}")
                            return None

                    start_time_obj = parse_time(event["start_time"])
                    end_time_obj = parse_time(event["end_time"])

                    if not start_time_obj or not end_time_obj:
                        status_label.configure(
                            text="Invalid time format encountered, skipping event."
                        )
                        continue

                    # Combine date and time
                    start_datetime = datetime.datetime.combine(
                        self.current_date, start_time_obj
                    )
                    end_datetime = datetime.datetime.combine(
                        self.current_date, end_time_obj
                    )

                    # Set timezone
                    start_datetime = start_datetime.replace(tzinfo=local_timezone)
                    end_datetime = end_datetime.replace(tzinfo=local_timezone)

                    # Format start and end times in ISO format
                    start_time_iso = start_datetime.isoformat()
                    end_time_iso = end_datetime.isoformat()

                    event_body = {
                        "summary": event["name"],
                        "start": {
                            "dateTime": start_time_iso,
                            "timeZone": local_timezone_str,
                        },
                        "end": {
                            "dateTime": end_time_iso,
                            "timeZone": local_timezone_str,
                        },
                        "colorId": event["color_id"],
                    }

                    # Upload event
                    service.events().insert(
                        calendarId=calendar_id, body=event_body
                    ).execute()
                    status_label.configure(
                        text=f"Event uploaded successfully: {event['name']}"
                    )

                except HttpError as error:
                    status_label.configure(text=f"An error occurred: {error}")

                # Update progress bar
                progress.set((i + 1) / total_events)
                loading_window.update()

            # Final status update and closing the window
            status_label.configure(text="All events uploaded successfully!")
            progress.set(1.0)
            loading_window.update()

            # Close the loading window after a short delay
            loading_window.after(2000, loading_window.destroy)

        # Run the upload process in a separate thread
        threading.Thread(target=upload_events, daemon=True).start()

    def open_paste_events_window(self):
        # Create a Toplevel window
        paste_event_window = ctk.CTkToplevel(self.root)
        paste_event_window.title("Paste Events")

        # Set the size and make the window non-resizable
        window_width = 600
        window_height = 400
        paste_event_window.geometry(f"{window_width}x{window_height}")
        paste_event_window.resizable(False, False)
        paste_event_window.attributes("-topmost", True)

        # Center the window relative to the main window
        main_window_x = self.root.winfo_rootx()
        main_window_y = self.root.winfo_rooty()
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()

        position_top = int(
            (main_window_y + (main_window_height / 2)) - (window_height / 2)
        )
        position_right = int(
            (main_window_x + (main_window_width / 2)) - (window_width / 2)
        )
        paste_event_window.geometry(
            f"{window_width}x{window_height}+{position_right}+{position_top}"
        )

        # Instruction label
        instruction_label = ctk.CTkLabel(
            paste_event_window,
            text="Paste the formatted events here:",
        )
        instruction_label.pack(pady=10)

        # Textbox for pasting events
        text_box = ctk.CTkTextbox(paste_event_window, width=550, height=250)
        text_box.pack(pady=10)

        # Tooltip to copy the prompt to clipboard
        prompt = (
            "Please format the events exactly as follows without any alterations or special formatting:\n"
            "Event Name\n"
            "Start Time (e.g., 02:00 PM)\n"
            "End Time (e.g., 03:00 PM)\n"
            "Color ID (1-11 for different colors)\n\n"
            "Example:\n"
            "Meeting with Team\n"
            "02:00 PM\n"
            "03:00 PM\n"
            "4\n\n"
            "Ensure each event is separated by a blank line. Do not add any lines, bold text, or other formatting. Ensure there are no extra spaces or characters, such as a space after the times."
        )

        tooltip_button = ctk.CTkButton(
            paste_event_window,
            text="Copy Format Instructions to Clipboard",
            command=lambda: pyperclip.copy(prompt),
        )
        tooltip_button.pack(pady=10)

        # Save events button
        save_button = ctk.CTkButton(
            paste_event_window,
            text="Save Events",
            command=lambda: self.save_pasted_events(text_box.get("1.0", tk.END)),
        )
        save_button.pack(pady=10)

    def save_pasted_events(self, event_data):
        events = event_data.strip().split("\n\n")
        for event_text in events:
            lines = event_text.strip().split("\n")
            if len(lines) < 4:
                continue

            event_name = lines[0].strip()
            start_time = lines[1].strip()
            end_time = lines[2].strip()
            color_id = lines[3].strip()

            self.events.append(
                {
                    "name": event_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "color_id": color_id,
                }
            )

        self.create_widgets()  # Refresh event list

    def open_add_event_window(
        self,
        event_name="",
        start_time="12:00 AM",
        end_time="01:00 AM",
        color_id="1",
        save_callback=None,
    ):
        # Create a Toplevel window
        add_event_window = ctk.CTkToplevel(self.root)
        add_event_window.title("Add New Event")

        # Set the size and make the window non-resizable
        window_width = 600
        window_height = 350
        add_event_window.geometry(f"{window_width}x{window_height}")
        add_event_window.resizable(False, False)
        add_event_window.attributes("-topmost", True)

        # Center the window relative to the main window
        main_window_x = self.root.winfo_rootx()
        main_window_y = self.root.winfo_rooty()
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()

        position_top = int(
            (main_window_y + (main_window_height / 2)) - (window_height / 2)
        )
        position_right = int(
            (main_window_x + (main_window_width / 2)) - (window_width / 2)
        )
        add_event_window.geometry(
            f"{window_width}x{window_height}+{position_right}+{position_top}"
        )

        def validate_time_format(time_str):
            try:
                datetime.datetime.strptime(time_str, "%I:%M%p")
                return True
            except ValueError:
                return False

        def update_end_time(*args):
            start_time_str = (
                entry_start_hour.get()
                + ":"
                + entry_start_minute.get()
                + entry_start_am_pm.get()
            )
            if validate_time_format(start_time_str):
                start_time = datetime.datetime.strptime(start_time_str, "%I:%M%p")
                end_time = start_time + datetime.timedelta(hours=1)
                entry_end_hour.set(end_time.strftime("%I"))
                entry_end_minute.set(end_time.strftime("%M"))
                entry_end_am_pm.set(end_time.strftime("%p"))
            validate_save_button()

        def validate_save_button(*args):
            # Get the event name and times
            event_name = entry_event_name.get().strip()
            start_time_str = (
                entry_start_hour.get()
                + ":"
                + entry_start_minute.get()
                + entry_start_am_pm.get()
            )
            end_time_str = (
                entry_end_hour.get()
                + ":"
                + entry_end_minute.get()
                + entry_end_am_pm.get()
            )

            # Clear error messages
            lbl_error_name.configure(text="")
            lbl_error_time.configure(text="")

            # Enable/disable the save button based on conditions
            if not event_name:
                lbl_error_name.configure(text="Please enter a name", text_color="red")
                btn_save_event.configure(state="disabled")
            elif not validate_time_format(start_time_str) or not validate_time_format(
                end_time_str
            ):
                lbl_error_time.configure(
                    text="Please enter valid times", text_color="red"
                )
                btn_save_event.configure(state="disabled")
            else:
                start_time = datetime.datetime.strptime(start_time_str, "%I:%M%p")
                end_time = datetime.datetime.strptime(end_time_str, "%I:%M%p")
                if end_time <= start_time:
                    lbl_error_time.configure(
                        text="Ensure the event time ends after it starts",
                        text_color="red",
                    )
                    btn_save_event.configure(state="disabled")
                else:
                    btn_save_event.configure(state="normal")

        def update_color_box(*args):
            color_id = get_color_id()
            color_code = self.get_color_from_id(color_id)
            color_box.configure(fg_color=color_code)

        # Event Name
        lbl_event_name = ctk.CTkLabel(add_event_window, text="Event Name:")
        lbl_event_name.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        entry_event_name = ctk.CTkEntry(add_event_window, width=300)
        entry_event_name.grid(
            row=0, column=1, padx=10, pady=10, columnspan=3, sticky="w"
        )
        entry_event_name.insert(0, event_name)
        entry_event_name.bind("<KeyRelease>", validate_save_button)

        # Start Time
        lbl_start_time = ctk.CTkLabel(add_event_window, text="Start Time:")
        lbl_start_time.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        hours = [f"{h:02}" for h in range(1, 13)]
        minutes = [f"{m:02}" for m in range(0, 60)]
        am_pm = ["AM", "PM"]

        start_time_parts = start_time.split(" ")
        entry_start_hour = ctk.StringVar(value=start_time_parts[0].split(":")[0])
        entry_start_minute = ctk.StringVar(value=start_time_parts[0].split(":")[1])
        entry_start_am_pm = ctk.StringVar(
            value=start_time_parts[1] if len(start_time_parts) > 1 else "AM"
        )

        start_hour_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=entry_start_hour, values=hours
        )
        start_minute_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=entry_start_minute, values=minutes
        )
        start_am_pm_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=entry_start_am_pm, values=am_pm
        )

        start_hour_dropdown.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        start_minute_dropdown.grid(row=1, column=2, padx=5, pady=10, sticky="w")
        start_am_pm_dropdown.grid(row=1, column=3, padx=5, pady=10, sticky="w")

        entry_start_hour.trace_add("write", update_end_time)
        entry_start_minute.trace_add("write", update_end_time)
        entry_start_am_pm.trace_add("write", update_end_time)

        # End Time
        lbl_end_time = ctk.CTkLabel(add_event_window, text="End Time:")
        lbl_end_time.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        end_time_parts = end_time.split(" ")
        entry_end_hour = ctk.StringVar(value=end_time_parts[0].split(":")[0])
        entry_end_minute = ctk.StringVar(value=end_time_parts[0].split(":")[1])
        entry_end_am_pm = ctk.StringVar(
            value=end_time_parts[1] if len(end_time_parts) > 1 else "AM"
        )

        end_hour_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=entry_end_hour, values=hours
        )
        end_minute_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=entry_end_minute, values=minutes
        )
        end_am_pm_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=entry_end_am_pm, values=am_pm
        )

        end_hour_dropdown.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        end_minute_dropdown.grid(row=2, column=2, padx=5, pady=10, sticky="w")
        end_am_pm_dropdown.grid(row=2, column=3, padx=5, pady=10, sticky="w")

        entry_end_hour.trace_add("write", validate_save_button)
        entry_end_minute.trace_add("write", validate_save_button)
        entry_end_am_pm.trace_add("write", validate_save_button)

        # Color
        lbl_color = ctk.CTkLabel(add_event_window, text="Color:")
        lbl_color.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        color_options = {
            "Lavender": "1",
            "Sage": "2",
            "Grape": "3",
            "Flamingo": "4",
            "Banana": "5",
            "Tangerine": "6",
            "Peacock": "7",
            "Graphite": "8",
            "Blueberry": "9",
            "Basil": "10",
            "Tomato": "11",
        }

        color_var = ctk.StringVar(
            value=[key for key, value in color_options.items() if value == color_id][0]
        )

        color_dropdown = ctk.CTkOptionMenu(
            add_event_window, variable=color_var, values=list(color_options.keys())
        )
        color_dropdown.grid(row=3, column=1, padx=5, pady=10, sticky="w")

        def get_color_id():
            selected_color = color_var.get()
            return color_options.get(
                selected_color, "1"
            )  # Default to color ID "1" if not found

        # Color Box
        color_box = ctk.CTkFrame(
            add_event_window,
            width=30,
            height=30,
            corner_radius=5,
            fg_color=self.get_color_from_id(color_id),
        )
        color_box.grid(row=3, column=2, padx=10, pady=10, sticky="w")

        def get_color_id():
            selected_color = color_var.get()
            for key, value in color_options.items():
                if selected_color == key:
                    return value
            return "1"  # Default color ID if invalid

        # Update color box when color dropdown value changes
        color_var.trace_add("write", update_color_box)

        # Save Event Button
        btn_save_event = ctk.CTkButton(
            add_event_window,
            text="Save Event",
            command=lambda: (
                save_callback(
                    entry_event_name.get(),
                    f"{entry_start_hour.get()}:{entry_start_minute.get()} {entry_start_am_pm.get()}",
                    f"{entry_end_hour.get()}:{entry_end_minute.get()} {entry_end_am_pm.get()}",
                    get_color_id(),
                )
                if save_callback
                else self.save_event(
                    entry_event_name.get(),
                    f"{entry_start_hour.get()}:{entry_start_minute.get()} {entry_start_am_pm.get()}",
                    f"{entry_end_hour.get()}:{entry_end_minute.get()} {entry_end_am_pm.get()}",
                    get_color_id(),
                )
            ),
            state="disabled",
        )
        btn_save_event.grid(
            row=4, column=0, padx=10, pady=10, columnspan=4, sticky="nsew"
        )

        # Error Messages
        lbl_error_name = ctk.CTkLabel(add_event_window, text="", text_color="red")
        lbl_error_name.grid(row=5, column=0, padx=10, pady=5, columnspan=4, sticky="w")

        lbl_error_time = ctk.CTkLabel(add_event_window, text="", text_color="red")
        lbl_error_time.grid(row=6, column=0, padx=10, pady=5, columnspan=4, sticky="w")

        # Update Save Button state initially
        validate_save_button()

        # Start the event loop for the Toplevel window
        add_event_window.mainloop()

    def open_edit_event_window(self, event_index):
        event = self.events[event_index]

        # Open the add/edit event window with the event's current details pre-filled
        self.open_add_event_window(
            event_name=event["name"],
            start_time=event["start_time"],
            end_time=event["end_time"],
            color_id=event.get("color_id", "1"),  # Default color if not specified
            save_callback=lambda name, start, end, color: self.save_edited_event(
                event_index, name, start, end, color
            ),
        )

    def save_edited_event(self, event_index, name, start_time, end_time, color_id):
        self.events[event_index] = {
            "name": name,
            "start_time": start_time,
            "end_time": end_time,
            "color_id": color_id,
        }
        self.refresh_events()

    def refresh_events(self):
        self.create_widgets()  # Refresh the event list

    def save_event(self, name, start_time, end_time, color_id):
        event = {
            "name": name,
            "start_time": start_time,
            "end_time": end_time,
            "color_id": color_id,
        }
        self.events.append(event)
        self.create_widgets()  # Refresh event list

    def display_events(self, events_frame):
        # Clear existing event widgets
        for widget in events_frame.winfo_children():
            widget.destroy()

        if not self.events:
            no_event_label = ctk.CTkLabel(events_frame, text="No events for today.")
            no_event_label.pack(pady=10)
            return

        # Helper function to convert event start time to datetime object
        def parse_time(event):
            try:
                return datetime.datetime.strptime(event["start_time"], "%I:%M %p")
            except ValueError:
                # Handle cases where the time format might be incorrect
                return datetime.datetime.max

        # Sort events by start time
        sorted_events = sorted(self.events, key=parse_time)

        for i, event in enumerate(sorted_events):
            event_frame = ctk.CTkFrame(events_frame, corner_radius=10)
            event_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

            # Configure columns in the event frame to align the edit and delete buttons to the right
            event_frame.grid_columnconfigure(0, weight=1)  # Event name
            event_frame.grid_columnconfigure(1, weight=0)  # Event time
            event_frame.grid_columnconfigure(2, weight=0)  # Edit button
            event_frame.grid_columnconfigure(3, weight=0)  # Delete button

            # Get event text color if available
            event_text_color = self.get_color_from_id(event.get("color_id", ""))

            # Event name label with color
            event_name_label = ctk.CTkLabel(
                event_frame,
                text=event["name"],
                font=("Arial", 14),
                text_color=event_text_color,
            )
            event_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            # Event time label with color
            event_time_label = ctk.CTkLabel(
                event_frame,
                text=f"{event['start_time']} - {event['end_time']}",
                font=("Arial", 12),
                text_color=event_text_color,
            )
            event_time_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Edit button for each event
            edit_button = ctk.CTkButton(
                event_frame,
                text="Edit",
                command=lambda i=i: self.open_edit_event_window(i),
            )
            edit_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")

            # Delete button for each event
            delete_button = ctk.CTkButton(
                event_frame, text="Delete", command=lambda i=i: self.delete_event(i)
            )
            delete_button.grid(row=0, column=3, padx=10, pady=5, sticky="e")

    def get_color_from_id(self, color_id):
        # Example color mapping based on colorId
        color_map = {
            "1": "#a4bdfc",  # Light blue
            "2": "#7ae7bf",  # Light green
            "3": "#dbadff",  # Light purple
            "4": "#ff887c",  # Light red
            "5": "#fbd75b",  # Light yellow
            "6": "#ffb878",  # Light orange
            "7": "#46d6db",  # Light turquoise
            "8": "#e1e1e1",  # Light gray
            "9": "#5484ed",  # Blue
            "10": "#51b749",  # Green
            "11": "#dc2127",  # Red
        }
        return color_map.get(
            color_id, "#000000"
        )  # Default to black if colorId not found

    def delete_event(self, event_index):
        # Delete the event at the specified index
        del self.events[event_index]
        self.create_widgets()  # Refresh the display

    def authenticate(self):
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())


if __name__ == "__main__":
    root = ctk.CTk()
    app = GCalApp(root)
    root.mainloop()
