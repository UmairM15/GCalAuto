# GCalAuto

**GCalAuto** is a desktop application built with Python and `customtkinter` that provides a user-friendly interface for managing your Google Calendar events. This app allows you to easily add, edit, and upload events to your Google Calendar from schedules made using ChatGPT.

## Features

- **Add and Edit Events:** Simple forms to create and modify events.
- **Upload to Google Calendar:** Directly upload events to your Google Calendar.
- **Paste Events from ChatGPT:** Import event lists formatted for easy paste.
- **Clear All Events:** Remove all events from the current view.
- **Progress and Status Updates:** Visual progress bar and status updates during event uploads.
- **Intuitive Date Navigation:** Navigate between days to manage events.

## Getting Started

### Download the Executable

1. Visit the [releases page](https://github.com/UmairM15/GCalAuto/releases/) to download the latest version of the application executable.
2. Double-click the downloaded `.exe` file to run the application. The executable is a standalone file and does not require Python to be installed on the system.

### Create Google Calendar API Credentials

To use the application, you'll need to set up credentials for the Google Calendar API. Follow these steps to create your credentials file:

1. **Create a Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Sign in with your Google account.
   - On the top left, click on the project drop-down menu and select "New Project."
   - Enter a project name (e.g., "Google Calendar Event Manager") and click "Create."

2. **Enable the Google Calendar API:**
   - In the Google Cloud Console, navigate to the [API Library](https://console.cloud.google.com/apis/library).
   - Search for "Google Calendar API" and click on it.
   - Click the "Enable" button to enable the API for your project.

3. **Set Up OAuth 2.0 Credentials:**
   - Go to the [Credentials page](https://console.cloud.google.com/apis/credentials).
   - Click "Create Credentials" and select "OAuth 2.0 Client ID."
   - You may be prompted to configure the OAuth consent screen. Click "Configure Consent Screen," select "External," and fill in the required fields, then click "Save and Continue" until you reach the "Summary" page, and click "Back to Dashboard."
   - On the "Create OAuth 2.0 Client ID" page, select "Desktop app" as the application type.
   - Enter a name for your OAuth 2.0 client (e.g., "Google Calendar Event Manager Client").
   - Click "Create" and then "Download" to download the credentials file (`credentials.json`).

4. **Save the Credentials File:**
   - Save the downloaded `credentials.json` file in the same directory as the application executable.

### Run the Application

1. Launch the application from the downloaded `.exe` file.

2. Manage Events:
   - Click on "Add Event" to create new events or use "Paste Events from ChatGPT" to import pre-formatted event lists.

3. Upload Events:
   - Use the "Upload to Google Calendar" button to sync events with your Google Calendar.

4. Navigate Dates:
   - Use the date navigation buttons to view and manage events for different days.

## Contributing

Contributions are welcome! To contribute to the project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/YourFeature`).
6. Open a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please contact [Umair Mulla](mailto:umairmulla315@example.com).
