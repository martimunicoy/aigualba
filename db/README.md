# Database Setup

This guide provides instructions to set up the database for the Aigualba water quality monitoring project.

## Database Initialization Files

The database setup includes multiple initialization files for different environments:

### 🟢 Production: `init.prod.sql`
- **Use for**: Production deployments
- **Contains**: Clean database schema, indexes, and essential system parameters
- **No dummy data**: Starts with empty tables ready for real water quality samples
- **Optimized**: Includes performance indexes and table documentation

### 🟡 Development: `init.dev.sql` 
- **Use for**: Development and testing
- **Contains**: Database schema + 5 sample water quality records
- **Dummy data**: Pre-populated with realistic test samples from different locations
- **Testing ready**: Allows immediate testing of browse/detail functionality

### 🔴 Legacy: `init.sql`
- **Status**: Current default (contains test data)
- **Recommendation**: Replace with appropriate environment-specific file

## Prerequisites

Ensure you have the following installed:
- **Python 3.8+**
- **pip** (Python package manager)
- **Docker** (if using Docker for the database)

## Environment Setup

1. **Navigate to the `db` Directory**:
   Open a terminal and navigate to the `db` folder:
   ```bash
   cd /Users/martimunicoy/repos/aigualba/db
   ```

2. **Set Up a Virtual Environment** (Optional but Recommended):
   Create and activate a Python virtual environment to isolate dependencies:
   ```bash
   python3 -m venv envs/aigualba_db
   source envs/aigualba_db/bin/activate
   ```

3. **Install Python Dependencies**:
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Setting Up the Database

1. **Ensure the .env File is Configured**:
   Verify that the `.env` file in the project root contains the correct database credentials. For example:
   ```properties
   DEV_POSTGRES_USER=devuser
   DEV_POSTGRES_PASSWORD=devpass
   DEV_POSTGRES_DB=aigualba_db
   ```

2. **Start the Database Service**:
   If you are using Docker, start the database container:
   ```bash
   docker-compose up -d db
   ```

3. **Run the Database Setup Script**:
   Execute the `setup_database.py` script to create the database, user, and grant privileges:
   ```bash
   python setup_database.py
   ```

   If successful, you should see output similar to:
   ```
   Database 'aigualba_db' created successfully.
   User 'devuser' created successfully.
   Granted all privileges on database 'aigualba_db' to user 'devuser'.
   ```

## Troubleshooting

- **Error: `connection to server at "db" failed`**:
  Ensure the database container is running and accessible. Check the Docker logs:
  ```bash
  docker-compose logs db
  ```

- **Error: `FATAL: password authentication failed`**:
  Verify that the credentials in the `.env` file match the database configuration.

- **Recreate the Database**:
  If you need to reset the database, you can drop and recreate it manually:
  ```bash
  docker-compose down
  docker-compose up -d db
  python setup_database.py
  ```

## Additional Notes

- The `setup_database.py` script is located in the `db` folder.
- The database schema is initialized using the `init.sql` file.
- For development, the database runs on the `db` hostname within the Docker network.

---
