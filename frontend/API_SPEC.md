# Peerex Peer API Specification (Draft)

This document outlines the required backend RESTful API endpoints for the Peerex Peer based on the frontend implementation.

## Base URL
`/api`

## Authentication (`/api/auth`)
*   `POST /login`
    *   **Body**: `{ username, password, role? }`
    *   **Response**: `{ token, user: { id, username, email, role, ... } }`
*   `POST /logout`
    *   **Headers**: `Authorization: Bearer <token>`
    *   **Response**: `{ success: true }`

## Users (`/api/users`)
*   `GET /current` - Get logged-in user profile
*   `GET /` - List all users (Admin)
*   `PUT /:id/role` - Update user role (Admin)
    *   **Body**: `{ role }`
*   `DELETE /:id` - Delete user (Admin)

## Manuscripts (`/api/manuscripts`)
*   `GET /` - List all manuscripts (Admin/Editor)
*   `GET /my` - List manuscripts submitted by the current user (Author)
*   `GET /:id` - Get manuscript details
*   `POST /` - Submit a new manuscript
    *   **Body**: `multipart/form-data` (files + JSON data)
*   `PUT /:id` - Update manuscript details/status
*   `DELETE /:id` - Delete manuscript
*   `POST /assign-editor` - Assign an editor to a manuscript
    *   **Body**: `{ manuscriptId, editorId }`

## Reviews (`/api/reviews`)
*   `GET /pending` - List manuscripts waiting for review by current user (Reviewer)
*   `GET /history` - List review history for current user (Reviewer)
*   `POST /:manuscriptId` - Submit a review
    *   **Body**: `{ comments, decision, rating, ... }`
*   `GET /statistics` - Get review statistics for current user

## System Administration (`/api/admin`)
*   `GET /statistics/system` - General system stats (user count, etc.)
*   `GET /statistics/trend` - Submission trend data for charts
*   `GET /statistics/modules` - Module distribution data for charts
*   `GET /statistics/status` - Status distribution data for charts

## Communications (`/api/messages`)
*   `GET /` - Get user messages
*   `POST /` - Send a message
*   `PUT /:id/read` - Mark message as read
*   `GET /unread-count` - Get unread message count

## System Configuration (`/api/config`)
*   `GET /announcements` - List active announcements
*   `POST /announcements` - Create announcement (Admin)
*   `PUT /announcements/:id` - Update announcement
*   `DELETE /announcements/:id` - Delete announcement

## Notes for Backend Implementation
1.  **Authentication**: The frontend expects a JWT or similar token-based authentication system. The token should be stored and sent in the `Authorization` header as `Bearer <token>`.
2.  **File Handling**: The submission endpoint (`POST /manuscripts`) must handle `multipart/form-data` correctly, saving files securely and storing their URLs/paths in the database.
3.  **Roles**: The system relies on strict role-based access control (RBAC). Ensure the backend validates roles (`author`, `reviewer`, `editor`, `admin`) before executing protected operations.