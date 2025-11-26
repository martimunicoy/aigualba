# Aigualba Backend

## Project Structure

The backend is organized following FastAPI best practices with a clean separation of concerns:

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── models/                # Pydantic models for data validation
│   ├── __init__.py
│   └── sample.py          # MostreData model
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── parameters.py      # Parameters endpoints
│   └── samples.py         # Sample data endpoints
└── database.py            # Database operations and connections
```

## Architecture

### 1. **main.py**
- FastAPI application setup
- CORS middleware configuration
- Router registration
- Health check endpoint

### 2. **models/**
- **sample.py**: Contains `MostreData` Pydantic model for water sample validation
- Includes field validation, type checking, and business logic validation
- Custom validator for chlorine balance validation

### 3. **routers/**
- **parameters.py**: Handles `/api/parameters` endpoints for basic water quality parameters
- **samples.py**: Handles `/api/mostres` endpoints for water sample management
- Each router is properly tagged and documented for automatic OpenAPI generation

### 4. **database.py**
- Database connection management
- CRUD operations for parameters and samples
- Clean separation between business logic and database operations

## API Endpoints

### Parameters
- `GET /api/parameters/` - Get all water quality parameters

### Samples  
- `GET /api/mostres/` - Get all water samples
- `POST /api/mostres/` - Create a new water sample

### Health
- `GET /api/health` - Health check endpoint

## Data Models

### MostreData
Water sample model with comprehensive validation:
- **Required fields**: `data` (date), `punt_mostreig` (sampling point)
- **Optional fields**: All water quality parameters with appropriate validation ranges
- **Custom validation**: Chlorine balance validation (combined = total - free)

## Key Features

1. **Type Safety**: Full Pydantic model validation
2. **Error Handling**: Comprehensive exception handling with appropriate HTTP status codes
3. **Documentation**: Automatic OpenAPI/Swagger documentation
4. **Modular Design**: Clean separation of concerns
5. **Database Safety**: Parameterized queries to prevent SQL injection

## Development

### Running the Application
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Adding New Endpoints
1. Create appropriate Pydantic models in `models/`
2. Add database operations in `database.py`
3. Create router with endpoints in `routers/`
4. Register router in `main.py`

## Dependencies

- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings management
- **psycopg2-binary**: PostgreSQL adapter
- **uvicorn**: ASGI server implementation