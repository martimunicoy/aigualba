# 🌊 Aigualba - Water Quality Monitoring System

A comprehensive water quality monitoring and management system for municipalities, providing real-time data visualization, citizen participation tools, and administrative oversight.

## ✨ Features

### 🔍 **Public Dashboard**
- Real-time water quality parameter visualization
- Interactive charts with historical data trends
- Location-based monitoring with multiple sampling points
- Threshold-based safety indicators
- Mobile-responsive design

### 📊 **Data Management**
- Sample submission interface for field operators
- Data validation and quality control
- CSV export functionality
- Parameter range verification with European standards
- Automated safety alerts

### 🔐 **Admin Panel**
- Secure authentication via Keycloak
- Sample validation and approval workflow  
- Bulk operations for data management
- Statistics dashboard with insights
- User role management (admin/user)

### 📈 **Analytics & Visualization**
- Interactive plotly charts
- Multi-parameter correlation analysis
- Time series trend visualization
- Location-based data filtering
- Real-time threshold monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     NGINX       │    │   PostgreSQL    │    │    Keycloak     │
│   (Proxy)       │    │   (Database)    │    │ (Auth Server)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   FastAPI       │◄─────────────┘
                        │   (Backend)     │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │      Dash       │
                        │   (Frontend)    │
                        └─────────────────┘
```

## 📁 Project Structure

```
aigualba/
├── nginx/                 # NGINX reverse proxy configuration
├── db/                    # PostgreSQL database scripts
│   ├── init.dev.sql      # Development database with sample data
│   ├── init.prod.sql     # Production database schema
│   └── migrations/       # Database migration scripts
├── backend/               # FastAPI backend application
│   ├── routers/          # API route definitions
│   │   ├── admin_router.py   # Admin-only endpoints
│   │   ├── samples_router.py # Sample management
│   │   └── parameters_router.py # Parameter definitions
│   └── main.py           # FastAPI application
├── frontend/              # Dash frontend application
│   ├── pages/            # Application pages
│   │   ├── home.py       # Landing page with latest data
│   │   ├── browse.py     # Sample browser with filters
│   │   ├── visualize.py  # Interactive data visualization
│   │   ├── submit.py     # Data submission form
│   │   ├── about.py      # Information page
│   │   └── admin.py      # Administrative dashboard
│   ├── components/       # Reusable UI components
│   │   ├── navbar.py     # Navigation bar
│   │   └── admin_dashboard.py # Admin interface components
│   ├── utils/            # Utility functions
│   │   ├── helpers.py    # Data processing utilities
│   │   ├── thresholds.py # Water quality thresholds
│   │   ├── auth.py       # Authentication utilities
│   │   └── admin.py      # Admin management functions
│   └── app.py            # Main Dash application
├── keycloak/              # Authentication server configuration
│   └── realm-import.json # Keycloak realm configuration
├── docker-compose.yml     # Production deployment
├── docker-compose.dev.yml # Development environment
└── setup-keycloak.sh     # Keycloak setup script
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/martimunicoy/aigualba.git
cd aigualba
```

#### 2. Start the Complete System (Development)
```bash
# Setup Keycloak authentication (first time only)
./setup-keycloak.sh

# Start all services including database, backend, frontend, and admin
docker-compose -f docker-compose.dev.yml up --build
```

#### 3. Access the Application
- **Public Dashboard**: http://localhost:8051
- **Admin Panel**: http://localhost:8051/admin  
- **Backend API**: http://localhost:8001
- **Keycloak Admin**: http://localhost:8080

#### 4. Admin Access
- **Username**: `admin`
- **Password**: `admin123`

### Production Deployment

#### 1. Production Setup
```bash
# Clone the repository
git clone https://github.com/martimunicoy/aigualba.git
cd aigualba

# Configure environment variables
cp .env.example .env
# Edit .env with your production values

# Deploy with the automated script
./deploy.sh
```

#### 2. Manual Production Deployment
```bash
# Start production services
docker-compose up -d

# Setup Keycloak (first time only)  
./setup-keycloak.sh

# Check service health
./health-check.sh
```

#### 3. Production URLs
- **Public Dashboard**: http://your-server (port 80)
- **Admin Panel**: http://your-server/admin
- **Backend API**: http://your-server/api
- **Keycloak Admin**: http://your-server:8080

For detailed production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 🔧 Development Setup

### Environment Configuration
The system uses different configurations for development and production:

#### Development Environment (`docker-compose.dev.yml`)
- **Database**: PostgreSQL on port `5433` with sample data
- **Backend**: FastAPI on port `8001` with hot reload
- **Frontend**: Dash on port `8051` with debug mode
- **NGINX**: Reverse proxy on port `8088`
- **Keycloak**: Authentication server on port `8080`

#### Key Development Features
- **Live Reload**: Frontend and backend update automatically
- **Debug Mode**: Detailed error messages and logging
- **Sample Data**: Pre-populated with realistic water quality samples
- **Test Users**: Admin and regular user accounts ready to use

### Local Development Workflow
1. **Make changes** to frontend/backend code
2. **Auto-reload** picks up changes instantly
3. **Test features** with sample data
4. **Access logs** via `docker-compose logs [service]`

## 🌐 Application Pages

### Public Pages
| Page | URL | Description |
|------|-----|-------------|
| **Home** | `/` | Latest water quality data and overview |
| **Browse** | `/browse` | Sample browser with filtering and pagination |
| **Visualize** | `/visualize` | Interactive charts and data analysis |
| **Submit** | `/submit` | Data submission form for field operators |
| **About** | `/about` | System information and methodology |

### Admin Pages  
| Page | URL | Description |
|------|-----|-------------|
| **Admin Dashboard** | `/admin` | Sample management and validation |
| **Sample Management** | `/admin#samples` | CRUD operations on water samples |
| **Statistics** | `/admin#stats` | System analytics and insights |
| **Configuration** | `/admin#config` | System settings and maintenance |

## 🎯 Key Features in Detail

### Water Quality Monitoring
- **Parameters Tracked**: pH, Temperature, Chlorine (free/total), Turbidity, E.coli, Enterococci, Haloacetic acids
- **Threshold Monitoring**: European water quality standards compliance
- **Visual Indicators**: Color-coded safety status (green/yellow/red)
- **Calculated Parameters**: Combined chlorine, sum of 5 haloacetic acids

### Data Validation System  
- **Two-Stage Process**: Submission → Admin Review → Public Display
- **Quality Control**: Parameter range validation and anomaly detection
- **Bulk Operations**: Batch processing for efficient management
- **Audit Trail**: Complete history of data changes

### Interactive Visualizations
- **Time Series**: Historical trends with customizable date ranges
- **Multi-Location**: Compare data across sampling points
- **Parameter Correlation**: Identify relationships between measurements
- **Threshold Lines**: Visual compliance indicators
- **Export Functionality**: CSV download for further analysis

## 🔐 Security & Authentication

### Authentication System (Keycloak)
- **OAuth2/OpenID Connect**: Industry-standard authentication
- **Role-Based Access**: Admin vs regular user permissions  
- **Session Management**: Secure token-based authentication
- **User Management**: Centralized user administration

### Security Features
- **Protected Routes**: Admin-only access to management functions
- **JWT Tokens**: Secure API authentication
- **CORS Configuration**: Controlled cross-origin requests
- **Input Validation**: Comprehensive data sanitization

## 📊 Database Schema

### Core Tables
- **`mostres_aigua`**: Water quality samples with all parameters
- **`parameters`**: System configuration and thresholds
- **Validation columns**: `validated` (boolean), `created_at` (timestamp)

### Supported Parameters
- **Physical**: Temperature, pH, Conductivity, Turbidity, Color, Odor, Taste
- **Chemical**: Free/Total Chlorine, Haloacetic acids (5 types)
- **Biological**: E.coli, Enterococci, Aerobic microorganisms, Total coliforms

## 🛠️ API Documentation

### Public Endpoints
```
GET  /api/mostres          # Get all validated samples
GET  /api/mostres/{id}     # Get specific sample
POST /api/mostres          # Submit new sample
GET  /api/parameters       # Get parameter definitions
```

### Admin Endpoints (Requires Authentication)
```
GET    /api/admin/samples           # Get all samples (including unvalidated)
PATCH  /api/admin/samples/{id}/validate  # Validate/unvalidate sample
PUT    /api/admin/samples/{id}      # Update sample data
DELETE /api/admin/samples/{id}      # Delete sample
POST   /api/admin/samples/bulk-validate  # Bulk validation
GET    /api/admin/statistics        # System statistics
```

## 🔧 Configuration & Customization

### Environment Variables
```bash
# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=aigualba
DB_USER=aigualba_user
DB_PASSWORD=aigualba_pass

# Keycloak Configuration  
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=aigualba
KEYCLOAK_CLIENT_ID=aigualba-frontend
KEYCLOAK_CLIENT_SECRET=aigualba-frontend-secret-123

# Application Configuration
BACKEND_URL=http://localhost:8001
DASH_DEBUG=1
```

### Customization Options
- **Thresholds**: Modify water quality limits in `utils/thresholds.py`
- **Parameters**: Add new monitoring parameters via database schema
- **Styling**: Update CSS in `frontend/assets/style.css`
- **Charts**: Customize visualizations in `pages/visualize.py`
- **Validation Rules**: Enhance data validation in `utils/helpers.py`

## 🛠️ Production Management

### Backup and Recovery
```bash
# Create backup
./backup.sh

# Restore database from backup  
docker-compose exec -T db psql -U aigualba_user aigualba < backup-20241129.sql
```

### Monitoring
```bash
# Check system health
./health-check.sh

# View service logs
docker-compose logs -f [service_name]

# Monitor resource usage
docker stats
```

### Updates
```bash
# Update to latest version
git pull origin main
docker-compose down
docker-compose up --build -d
```

### Maintenance Scripts
- **`deploy.sh`**: Automated production deployment
- **`health-check.sh`**: System health monitoring
- **`backup.sh`**: Database and application backup
- **`setup-keycloak.sh`**: Keycloak authentication setup

## 📋 Troubleshooting

### Common Issues
1. **Keycloak not starting**: Wait 30-60 seconds for full initialization
2. **Database connection errors**: Ensure PostgreSQL container is healthy
3. **Admin login fails**: Verify Keycloak realm import was successful
4. **Charts not loading**: Check if plotly dependencies are installed

### Debugging Commands
```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs [service_name]

# Restart specific service
docker-compose -f docker-compose.dev.yml restart [service_name]

# Reset everything
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- European water quality standards and regulations
- Open-source technologies: PostgreSQL, FastAPI, Dash, Keycloak
- Water quality monitoring best practices and methodologies

---

For detailed admin setup instructions, see [ADMIN_SETUP.md](ADMIN_SETUP.md).
