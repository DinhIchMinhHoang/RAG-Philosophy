# State Management

## Overview

The frontend uses a combination of:
- **Local component state**: DOM event handlers
- **LocalStorage**: user profile and authentication token
- **Server state**: documents, ingest jobs, chat history, and indexed chunks on the backend

## Client State

### User Profile (LocalStorage)

```javascript
// Stored key: 'currentUser'
{
    username: "johndoe",
    email: "johndoe@gmail.com",
    displayName: "John Doe",
    bio: "Philosophy student"
}
```

### Authentication Token (LocalStorage)

```javascript
// Stored key: 'accessToken'
// Value: JWT string
```

### Current Scene

```javascript
// transitions.js - TransitionManager
this.currentScene = 'landing';  // current scene name
this.isTransitioning = false;    // prevents double transitions
```

## Server State

### Backend Persistent State

```python
# backend/app/models.py

class DocumentRecord(Base):
    ...

class IngestJob(Base):
    ...

class ChatMessage(Base):
    ...
```

### SQLite User Database

```python
# backend/app/models.py

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
```

## State Transitions

### Authentication Flow

```
Guest -> Sign In -> Authenticated User
     -> Sign Up -> Authenticated User
     -> Logout -> Guest
```

### Document Flow

```
No Documents -> Upload supported source -> Documents Ready
             -> Reset -> No Documents
```

### Scene Flow

```
Landing -> Sign In -> Dashboard -> Chat
       -> Sign Up ->
       -> Account -> (if authenticated)
```

## Persistence

| State | Storage | Persists Refresh |
|-------|---------|------------------|
| JWT Token | localStorage | Yes (until expiry) |
| User Profile | localStorage | Yes |
| Current Scene | Memory | No |
| Documents / Jobs | Backend DB + object storage | Yes |
| Chat History | Backend DB | Yes |
| Vectors / Chunks | Qdrant + backend DB | Yes |
| Latest notebook conversation snapshot | localStorage cache | Yes, until UI TTL expires |
| Saved notes / pinned messages | Backend DB (`saved_notebook_items`) | Yes |

## Notebook Chat Cache

The backend database is the source of truth for chat history. The frontend only caches the latest visible conversation per notebook for fast switching.

- Cache key: `notebook:{notebook_id}:conversation:last`
- TTL: 24 hours
- Expired cache is ignored and removed from localStorage
- Cache expiration never deletes DB conversations or messages
- On notebook switch, the UI shows cache first, then syncs from `GET /api/notebooks/{notebook_id}/conversations/latest`
- New notebooks with no DB history render the empty welcome state

Saved notes and pinned messages are stored separately from normal chat messages, so future DB cleanup jobs can archive/delete inactive chat without deleting user-selected long-term content.

## Reset Actions

- **Logout**: Clears `accessToken` and `currentUser` from localStorage
- **Document Reset**: Removes document via `/api/documents/{document_id}`
- **Page Refresh**: Restores from localStorage (auth), loses scene state
- **Job Polling**: Ingest progress survives refresh because the backend persists job state and the UI can reload it from `/api/jobs/{job_id}` or the document list
