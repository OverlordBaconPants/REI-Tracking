# API Documentation

This document provides documentation for the REI-Tracker API endpoints.

## Base Routes

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### API Version

```
GET /api/version
```

Returns the API version information.

**Response**:
```json
{
  "version": "1.0.0",
  "name": "REI-Tracker API"
}
```

### Serve Upload

```
GET /uploads/<filename>
```

Serves an uploaded file.

**Parameters**:
- `filename`: The name of the file to serve

**Response**:
- The file content if found
- 404 Not Found if the file doesn't exist

## User Routes

### Register

```
POST /api/users/register
```

Registers a new user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:00:00.000Z"
  }
}
```

### Login

```
POST /api/users/login
```

Logs in a user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:00:00.000Z"
  }
}
```

### Logout

```
POST /api/users/logout
```

Logs out the current user.

**Response**:
```json
{
  "success": true
}
```

### Get Current User

```
GET /api/users/me
```

Gets the current user.

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:00:00.000Z"
  }
}
```

### Get User

```
GET /api/users/<user_id>
```

Gets a user by ID.

**Parameters**:
- `user_id`: The ID of the user to get

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:00:00.000Z"
  }
}
```

### Update User

```
PUT /api/users/<user_id>
```

Updates a user.

**Parameters**:
- `user_id`: The ID of the user to update

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "role": "admin"
}
```

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "role": "admin",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:00:00.000Z"
  }
}
```

### Delete User

```
DELETE /api/users/<user_id>
```

Deletes a user.

**Parameters**:
- `user_id`: The ID of the user to delete

**Response**:
```json
{
  "success": true
}
```

## Property Routes

*To be implemented*

## Transaction Routes

*To be implemented*

## Analysis Routes

*To be implemented*

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized

```json
{
  "success": false,
  "errors": {
    "_error": ["Not logged in"]
  }
}
```

### 403 Forbidden

```json
{
  "success": false,
  "errors": {
    "_error": ["Unauthorized"]
  }
}
```

### 404 Not Found

```json
{
  "error": {
    "code": 404,
    "message": "Not Found"
  }
}
```

### 500 Internal Server Error

```json
{
  "error": {
    "code": 500,
    "message": "Internal Server Error"
  }
}
