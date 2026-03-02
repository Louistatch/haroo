# 🚀 Plateforme Agricole du Togo - Servers Running

## ✅ Both Servers Are Active

### Backend (Django API)
- **URL**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Base**: http://127.0.0.1:8000/api/v1/
- **Status**: ✅ RUNNING (Process ID: 21300)
- **Note**: Root URL (/) returns 404 - this is expected (API-only backend)

### Frontend (React/Vite)
- **URL**: http://localhost:3000
- **Status**: ✅ RUNNING (Process ID: 12580)
- **API Connection**: Configured to connect to http://localhost:8000/api

## 🔑 Test Users

| Username | Password | Role |
|----------|----------|------|
| admin_demo | Admin123! | Administrator |
| exploitant_demo | Demo123! | Farmer |
| agronome_demo | Demo123! | Agronomist |

## 📡 Available API Endpoints

### Authentication
- POST `/api/v1/auth/login/`
- POST `/api/v1/auth/logout/`
- POST `/api/v1/auth/register/`

### Agronomists
- GET `/api/v1/users/agronomists/` - Directory (filterable)
- GET `/api/v1/users/agronomists/{id}/` - Public detail
- POST `/api/v1/users/agronomists/register/` - Registration
- POST `/api/v1/users/agronomists/{id}/validate/` - Admin validation
- POST `/api/v1/users/agronomists/{id}/reject/` - Admin rejection
- GET `/api/v1/users/agronomists/pending/` - Pending validations
- GET `/api/v1/users/agronomists/me/` - Current user profile

### Missions
- GET `/api/v1/missions/` - List missions
- POST `/api/v1/missions/` - Create mission
- GET `/api/v1/missions/{id}/` - Mission detail
- POST `/api/v1/missions/{id}/accept/` - Accept mission
- POST `/api/v1/missions/{id}/complete/` - Complete mission
- POST `/api/v1/missions/{id}/validate/` - Validate completion
- POST `/api/v1/missions/{id}/cancel/` - Cancel mission

### Documents
- GET `/api/v1/documents/` - List documents
- POST `/api/v1/documents/purchase/` - Purchase document

### Payments
- POST `/api/v1/payments/initiate/` - Initiate payment
- GET `/api/v1/payments/verify/{transaction_id}/` - Verify payment

## 🎯 Next Steps

1. **Access Frontend**: Open http://localhost:3000 in your browser
2. **Test Login**: Use one of the test accounts above
3. **Explore Features**: 
   - Browse agronomist directory
   - View agronomist profiles
   - Create missions (as farmer)
   - Accept missions (as agronomist)
   - Test payment flow

## 📊 Implementation Progress

- **Completed Tasks**: 7/76 (9.2%)
- **Current Phase**: V1 - Recrutement et Notation
- **Next Task**: 15.1 - Farm verification system

## 🛠️ Development Commands

### Stop Servers
```bash
# Stop backend
# Find process and kill it

# Stop frontend
# Find process and kill it
```

### Restart Servers
```bash
# Backend
python manage.py runserver

# Frontend (in frontend/ directory)
npm run dev
```

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.missions
python manage.py test apps.users
```

## 📝 Notes

- Backend is API-only (no HTML templates)
- Frontend handles all UI rendering
- API uses token-based authentication
- All endpoints require authentication except public directory
- Escrow system integrated with mission payments
- Administrative data loaded (5 regions, 38 prefectures, 323 cantons)
