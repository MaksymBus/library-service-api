# Library service API

## Project Description
A web-based application for managing books, users, borrowings, 
and sending notifications. The system allows users to borrow books, 
track active borrowings, and receive Telegram notifications on borrowing creation.

## Features
- JWT authentication for secure API access.
- Manage books, users, and borrowing records.
- Permissions system:
  -  Admins can create, update, and delete books.
  -  All users (even unauthenticated) can list books.
  -  Borrowings are restricted to authenticated users.
- Borrowing system with inventory validation.
- Telegram notifications for new borrowings.
- API documentation available at `/api/schema/swagger-ui/` (Swagger UI)

## Technologies Used
- **Backend:** Django Framework, Django REST Framework
- **Authentication:** JWT (via djangorestframework-simplejwt)
- **Database:** PostgreSQL
- **Notifications:** Telegram API
- **Containerization:** Docker, Docker Compose

## Installation
### Python 3 must be installed

1. Clone the repository:
   ```sh
   git clone https://github.com/MaksymBus/library-service-api.git
   cd library_service_api
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate
   venv\Scripts\activate (on Windows)
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the root directory and add the following variables:
   ```
   # Django
    SECRET_KEY=<your-secret-key>
    DEBUG=True/False
    
    # DB
    POSTGRES_USER=<db_user>
    POSTGRES_PASSWORD=<db_password>
    POSTGRES_DB=<db_name>
    POSTGRES_HOST=<db_host>
    POSTGRES_PORT=<db_port>
    PGDATA=/var/lib/postgresql/data
   
    # Telegram
    TELEGRAM_CHAT_ID=<your_telegram_chat_id>
    TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
   
10. **Create and Configure a Telegram Bot:**

- Open Telegram and search for `@BotFather`.
- Start a chat with BotFather and send the command `/newbot`.
- Follow the instructions to choose a name and a username for your bot.
- After creation, BotFather will provide you with a bot token.
- Store this token in your `.env` file as TELEGRAM_BOT_TOKEN.
- To obtain the chat ID (where notifications will be sent):
  - Add your bot to a Telegram group or create a chat.
  - Open a browser and navigate to `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates`
  - The response will contain a `chat.id` - copy this value and add this to `.env` as TELEGRAM_CHAT_ID

## Running with Docker
1. Build and start the services:
   ```sh
   docker-compose up --build
   ```
2. The application will be accessible at `http://127.0.0.1:8000/api/`.

## Optionally

#### Loading Initial Data:
To load sample data:
```sh
docker exec -it <your_container_name> sh
python manage.py loaddata library_data.json
```

#### Creating a Superuser:
To access the admin panel, create a superuser:
```sh
docker exec -it <your_container_name> sh
python manage.py createsuperuser
```
Use the following credentials when prompted:
- Email: `test@user.com`
- Password: `test_12345`

## Usage
### Authentication
The API uses JWT for authentication. You can obtain a token by sending a POST request to:
```sh
POST /api/user/token/
```

You will receive access and refresh tokens to authenticate API requests.

## API Endpoints


- `/api/books/` - List all books or create (admin only)
- `/api/books/{id}/` - Retrieve/update/delete book (admin only)


- `/api/borrowings/` - List borrowings (filtered by user, active status for admin) or create (requires authentication)
- `/api/borrowings/{id}/` - Retrieve borrowing detail info
- `/api/borrowings/{id}/return/` - Return a borrowed book


- `/api/user/register/` - Register new user
- `/api/user/token/` - Get token for user
- `/api/user/me/` - Manage user data
