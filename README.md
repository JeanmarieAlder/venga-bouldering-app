# Venga App - Bouldering Management App for Users and Setters

**An open-source bouldering gym management application.**

Venga App is a web application built with Flask to help bouldering gyms manage their boulders, setters, and climbers.

> **Project status:** In development. Features and setup instructions may change.

## Features

- Browse active boulders and view their details.
- Create, edit, archive, and restore boulders.
- User authentication and session management.
- Role-based permissions for climbers, setters, and administrators.
- Admin tools for managing user roles.

## Tech Stack

- **Backend:** Python, Flask
- **Authentication:** Flask-Login
- **Forms and CSRF protection:** Flask-WTF
- **Data storage:** JSON files (current implementation)
- **Templating:** Jinja2

## Getting Started (development setup)

### Prerequisites

- Python 3.10 or later
- Git.

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>
```

Replace the placeholders with your repository URL and directory name.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Linux / macOS**
```bash
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

The project has a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create an `api.env` based on the `example.api.env` file available in the root directory.

At minimum, configure a strong, unique Flask secret key:

```dotenv
SECRET_KEY=replace-with-a-secure-random-secret
```

Generate a secret using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit `api.env` or expose your secret key publicly.

### 5. Run the application

```bash
python run.py
```

Open the local address shown in your terminal, typically:

http://127.0.0.1:5000

Follow the application's registration and login flow to create an account.

## User Roles

| Role | Permissions |
|---|---|
| Climber | Browse boulders and view details |
| Setter | Climber features, plus boulder management |
| Admin | All application features, plus user role management |

Administrator accounts should be created through a secure administrative process. Public registration must not allow users to assign themselves elevated roles.

At the moment, the admin should manually create an account for himself, then change the JSON file to set his role to "admin" instead of "setter" or "climber".

## Project Structure

```text
venga/
├── run.py
├── api.env                 # Local configuration; do not commit
├── requirements.txt
├── LICENSE
├── README.md
└── venga_app/
    ├── __init__.py
    ├── config.py
    ├── extensions.py
    ├── models.py
    ├── user_store.py
    ├── boulder_store.py
    ├── permissions.py
    ├── blueprints/
    │   ├── auth/
    │   ├── main/
    │   ├── boulder/
    │   └── admin/
    └── templates/
```

## Data Storage

The current implementation uses JSON files for user and boulder records.

For local development, ensure the application's data directory is writable and back up important data. JSON storage is intended for the current prototype; production deployments may benefit from a database.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a branch for your change.
3. Make and test your changes.
4. Submit a pull request describing the changes.

Please open an issue first for major changes so the proposed approach can be discussed.

## Security

Please do not publish secrets, passwords, session keys, or private user data in issues or pull requests.

If you discover a security vulnerability, report it privately to the maintainer rather than publicly disclosing exploit details.

## License

Venga is released under the MIT License. See the [LICENSE](LICENSE) file for details.