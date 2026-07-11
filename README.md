# 🥾 Trekking Management Application - V1

A simple **Flask-based Trekking Management Application** where users can book treks, staff can manage assigned treks, and admins can manage the entire system.

---

# 🚀 Features

## 🛠️ Admin Features

* Admin Dashboard
* Add new trek
* Edit trek
* Delete trek
* Upload trek images
* Manage trek staff
* Approve or reject staff
* Assign staff to treks
* View all users (staff and trekkers)
* View all bookings

---

## 🧑‍💼 Staff Features

* Register
* Login (Only when approved by admin!)
* View assigned treks
* View trek details
* Update available slots
* Change trek status
* View participants

---

## 👤 User (trekker) Features

* Register and Login
* View available treks
* Search and filter treks
* View trek details
* Book a trek
* Cancel booking
* View current bookings
* View booking history
* Update profile
* Change password

---

## ⚙️ Technologies Used

* Flask
* SQLite
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-Login
* Flask-WTF
* Werkzeug
* WTForms
* email_validator
* pytz
* python-dotenv
* HTML
* CSS
* Jinja2
* Bootstrap

---

# 📁 Project Structure

```
trekking-management-application-v1-MAD-1/

│── app/
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
|   |    └── admin/
|   |    └── staff/
|   |    └── trekker/
│   └── __init__.py
│   └── forms.py
│
│── config/
│── instance/
│   └── trekking.db
│
│── migrations/
│
│── .env
│── .gitignore
│── README.md
│── requirements.txt
│── run.py
```

---

# ⚙️ How to Run the Project

## Step 1 : Clone the Repository

```bash
git clone https://github.com/23f2005496/trekking-management-application-v1-MAD-1.git
```

Go inside the project folder.

```bash
cd trekking-management-application-v1-MAD-1
```

---

## Step 2 : Create Virtual Environment

*Windows*

```bash
python -m venv .venv
```

Activate it

```bash
.venv\Scripts\activate
```

*MacOs*

```bash
python3 -m venv .venv
```

Activate it

```bash
source .venv/bin/activate
```

---

## Step 3 : Install Required Packages

```bash
pip install -r requirements.txt
```

---

# Step 4 : 🗄️ Database

This project uses **SQLite** database.

*Database file:*
```
instance/trekking.db
```

If the database is already included, no setup is required. else,


If creating a new database:

```bash
flask db init
```
It will create a "instance" and "migrations" folders. then run,

---

```bash
flask create-db
```
It will create a new database with schema and tables and also add "admin" in database with credentials from ".env" file. then run,

---

```bash
flask seed-db
```
It will add "sample data" of all tables in database. then run,

---

"one special command"

```bash
flask reset-db
```
Use it wisely because it will "completely delete" your old database and "create a fresh" one from scratch with "admin".
It also asks for confirmation before excecute (y/n)

---

## Step 5 : Run the Project

```bash
python run.py
```
It will launch the app on http://127.0.0.1:5000/.


Open your browser and visit

```
http://127.0.0.1:5000
```

# 🔐 Login Credentials

## Admin

```
Email: admin@trek.com

Password: admin123
```
---

## Staff & Trekkers

See in config/seed.py file

---

# 📷 Application Screenshots

Add screenshots inside a folder named **screenshots**.

Example:

```
screenshots/

home.png
login.png
register.png
user_dashboard.png
trek_details.png
admin_dashboard.png
manage_treks.png
manage_staff.png
assigned_treks.png
my_bookings.png
```

Then add them like this:

### Home Page

![Home](screenshots/home.png)

### Login Page

![Login](screenshots/login.png)

### Admin Dashboard

![Admin Dashboard](screenshots/admin_dashboard.png)

### Trek Details

![Trek Details](screenshots/trek_details.png)

---

# 👨‍💻 Developed By

**Tushar Sharma** IIT Madras Student

---

# 📄 License

This project is developed for educational purposes as part of the **IIT Madras Diploma in Programming**.
