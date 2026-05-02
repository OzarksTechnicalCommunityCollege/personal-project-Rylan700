# Student Engagement Platform

A Django-based platform to manage student engagement, clubs, events, attendance, and gamification through a points system.

## Features

- User authentication (students, club admins, staff)
- Club creation and management
- Event creation and registration
- check-in system for attendance
- Points system with transaction ledger
- Badges and rewards system
- Shop / voucher redemption system

## Tech Stack

- Python
- Django
- SQLite (can be swapped for PostgreSQL)
- HTML / CSS / JavaScript

## Project Structure

- `users/` - User accounts, roles, and profiles
- `events/` - Event creation, registration, and attendance
- `points/` - Points ledger and transactions
- `shop/` - Rewards and voucher system

## How It Works

1. Students register
2. Clubs create events
3. Students register and check in
4. Attendance triggers point rewards
5. Points can be spent in the shop for rewards or vouchers

## Setup Instructions

# Clone the repo
git clone <your-repo-url>

# Move into project
cd your-project

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate


Install dependencies
pip install -r requirements.txt

Run migrations
python manage.py migrate

Start server
python manage.py runserver

#Notes
Make sure AUTH_USER_MODEL is set correctly in settings.py
Run migrations after any model changes
QR check-in
Future Improvements
Mobile app support
Real-time notifications
Analytics dashboard for clubs
Improved gamification system
