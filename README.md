# Volunteer Management System

A Flask-based web application for managing volunteer activities and registrations. This system allows organizations to create and manage volunteer activities, while volunteers can register for activities and track their registration status.

## Features

### For Volunteers
- View available activities with detailed information
- Register for activities
- Track registration status (Pending, Approved, Rejected)
- View activity details including date, time, location, and maximum volunteers
- Register again if previous registration was rejected

### For Administrators
- Create and manage volunteer activities
- Approve or reject volunteer registrations
- View all registrations and their status
- Manage activity details (title, description, date, time, location, max volunteers)

### Security Features
- Secure user authentication
- Admin-only access to management features
- Prevention of duplicate registrations
- Status tracking for all registrations

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   python app.py
   ```

## Accessing the Platform

The application will be available at:
- Main URL: `http://127.0.0.1:5000`
- Alternative URL: `http://localhost:5000`

## Default Admin Account
- Email: admin@example.com
- Password: admin123

## Usage

### For Volunteers
1. Browse available activities on the home page
2. Click "Register" to sign up for an activity
3. View your registration status:
   - Yellow badge: Registration Pending
   - Green badge: Registration Approved
   - Red badge: Registration Rejected
4. If rejected, you can register again

### For Administrators
1. Log in with admin credentials
2. Access the admin panel to:
   - Create new activities
   - Manage existing activities
   - Approve or reject registrations
   - View all volunteer registrations

## Technology Stack
- Python 3.x
- Flask
- SQLite
- Bootstrap 5
- Flask-Login
- Flask-SQLAlchemy

## Contributing
Feel free to submit issues and enhancement requests.

## License
This project is licensed under the MIT License.

## Project Structure
```
volunteer_manager/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Homepage
│   ├── register.html  # Registration form
│   ├── login.html     # Login form
│   ├── signup.html    # Sign-up form
│   ├── admin.html     # Admin panel
│   └── new_activity.html  # Activity creation form
└── static/            # Static files (CSS, JS, images)
``` 