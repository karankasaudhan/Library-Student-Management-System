# 📚 Library & Student Management System

A Python and MySQL-based desktop application designed to simplify library operations and student record management through a graphical user interface (GUI).

**Developed by:** Karan Kasaudhan

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation and Setup](#-installation-and-setup)
- [Environment Configuration](#-environment-configuration)
- [Run the Application](#-run-the-application)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Future Improvements](#-future-improvements)
- [Author](#-author)
- [License](#-license)

## 💡 About the Project

The Library & Student Management System is a desktop application built using Python and MySQL to organize library-related activities and student records in one place.

The project includes a graphical interface, centralized database connectivity, and separate modules for managing books, students, and book issue/return operations.

The goal is to make everyday library management more organized, efficient, and easier to use.

## ✨ Features

- 🖥️ **Graphical User Interface:** Interact with the application through a desktop interface.
- 🔐 **Admin Login:** Administrator authentication functionality, according to the current implementation.
- 📚 **Book Management:** Dedicated module for book-related operations.
- 🎓 **Student Management:** Dedicated module for maintaining student records.
- 🔄 **Issue and Return Management:** Module for library lending and returns.
- 📊 **Library Reports:** Report-related functionality.
- 🗄️ **MySQL Database:** Store and manage application data in a relational database.
- 🔌 **Centralized Database Connection:** Shared configuration through `connection.py`.
- 🔒 **Environment-Based Configuration:** Keep local database credentials in a `.env` file.
- 🧩 **Modular Code Structure:** Separate files for different application responsibilities.

*Note: The available operations depend on the current implementation of each module.*

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| MySQL | Database management |
| MySQL Connector/Python | Python-to-MySQL connectivity |
| python-dotenv | Load environment variables |
| Tkinter or the GUI framework used in the project | Desktop interface |
| Git | Version control |
| GitHub | Source code hosting |

## 📁 Project Structure

```text
Library-Student-Management-System/
│
├── main.py
├── gui_app.py
├── connection.py
├── db_config.py
├── book_management.py
├── students_management.py
├── issue_return.py
├── library report.py
├── sql tables.py
├── requirements.txt
├── .env.example
├── .gitignore                 
```

### File Descriptions

- `main.py` — Application entry point.
- `gui_app.py` — Desktop graphical interface.
- `connection.py` — Centralized MySQL connection.
- `db_config.py` — Compatibility/configuration support.
- `book_management.py` — Book management operations.
- `students_management.py` — Student record operations.
- `issue_return.py` — Book issue and return operations.
- `library report.py` — Library report functionality.
- `sql tables.py` — SQL and table setup scripts.
- `requirements.txt` — Python dependencies.
- `.env.example` — Example environment configuration.
- `.gitignore` — Files and folders Git should ignore.

## 📋 Prerequisites

Before running the project, make sure you have:

1. Python installed on your computer.
2. MySQL Server installed and running.
3. A MySQL database configured for the application.
4. The required Python packages installed.
5. The database tables created according to the project's SQL setup.

## 🚀 Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/karankasaudhan/Library-Student-Management-System.git
```

Move into the project directory:

```bash
cd Library-Student-Management-System
```

Alternatively, download the repository ZIP from GitHub and extract it.

### Step 2: Install dependencies

Run this command in the project directory:

```bash
python -m pip install -r requirements.txt
```

### Step 3: Configure MySQL

1. Start your MySQL Server.
2. Create or select the database required by the application.
3. Review `sql tables.py` and the existing SQL setup instructions.
4. Create the required tables and relationships before running the application.

**Important:** Back up existing data before running any SQL script that deletes, resets, or recreates tables.

## 🔐 Environment Configuration

The project uses environment variables to separate database credentials from the application code.

### Step 1: Create `.env`

Copy `.env.example` to a new file named `.env` in the project root.

### Step 2: Configure the variables

Use the following format as an example. Replace the placeholder values with your local settings and use the exact variable names expected by `connection.py`.

```dotenv
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
```

If your application uses additional environment variables for initial administrator setup, configure those according to the existing implementation.

### Step 3: Keep credentials private

- Never upload `.env` to GitHub.
- Keep `.env` listed in `.gitignore`.
- Only put placeholder values in `.env.example`.
- Never publish real database passwords or administrator credentials.

## ▶️ Run the Application

From the project root, execute:

```bash
python main.py
```

The application should start using the configured database connection, provided that the database, dependencies, and required tables are ready.

If the GUI does not open, check the terminal output and confirm the correct entry point in `main.py`.

## 🛡️ Security

Security is important when working with database-backed applications.

- Store local credentials in `.env`.
- Do not hard-code real passwords in Python files.
- Use a dedicated MySQL user with only the permissions the application requires.
- Avoid using the MySQL `root` account for routine application access.
- Never publish real student records or personal information.
- If credentials were previously pushed to a public repository, change those credentials. Adding `.gitignore` does not erase secrets from previous commits.

## 🧰 Troubleshooting

| Issue | Suggested solution |
|---|---|
| MySQL connection error | Check that MySQL Server is running and `.env` contains correct values. |
| Missing Python module | Run `python -m pip install -r requirements.txt`. |
| Database not found | Confirm that the database exists and its name matches `DB_NAME`. |
| Tables are missing | Review the SQL setup scripts and create the required tables. |
| GUI does not launch | Check the error in the terminal and inspect `main.py`. |
| Admin login fails | Check the configured administrator setup and required database records. Do not assume default credentials. |
| `.env` appears in Git | Check `.gitignore` and whether `.env` was previously tracked. |

## 🔮 Future Improvements

Potential ideas for future versions include:

- Automated tests for database operations.
- Database backup and restore tools.
- More detailed reports and dashboards.
- Improved role-based access control.
- A demonstration GIF and screenshots in the repository.
- Setup documentation for a fresh database.

These are possible improvements, not claims that they are already implemented.

## 👨‍💻 Author

**Karan Kasaudhan**

Aspiring Software Engineer | Student | Technology Enthusiast

GitHub: [@karankasaudhan](https://github.com/karankasaudhan)
LinkedIn: [@karankasaudhan](https://www.linkedin.com/in/karan-kasaudhan)

## 📄 License

## 📄 License

This project is licensed under the [MIT License](LICENSE).

You are free to use, copy, modify, and distribute this software, including for commercial purposes, subject to the terms and conditions of the MIT License.

See the [LICENSE](LICENSE) file for details.