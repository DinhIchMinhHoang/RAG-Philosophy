# State Management

## Overview

The frontend uses a combination of:
- **Local component state**: DOM event handlers
- **LocalStorage**: User profile and authentication token
- **Server state**: RAG documents and chat history (in-memory on backend)

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

### Backend In-Memory State

```python
# backend/app/services/rag_service.py

class RAGService:
    _retriever = None           # MultiVectorRetriever or None
    _all_child_docs = []        # List[Document]
    _all_parent_docs = []       # List[Document]
    _source_files = []          # List of filenames
    _upload_dir = ""            # Temp directory path
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
Guest → Sign In → Authenticated User
     → Sign Up → Authenticated User
     → Logout → Guest
```

### Document Flow

```
No Documents → Upload PDF → Documents Ready
             → Reset → No Documents
```

### Scene Flow

```
Landing → Sign In → Dashboard → Chat
       → Sign Up ↗
       → Account ↗ (if authenticated)
```

## Persistence

| State | Storage | Persists Refresh |
|-------|---------|------------------|
| JWT Token | localStorage | Yes (until expiry) |
| User Profile | localStorage | Yes |
| Current Scene | Memory | No |
| RAG Documents | Backend Memory | No |

## Reset Actions

- **Logout**: Clears `accessToken` and `currentUser` from localStorage
<<<<<<< HEAD
- **Document Reset**: Clears backend RAGService state via `/documents/reset`
- **Page Refresh**: Restores from localStorage (auth), loses scene state
=======
- **Document Reset**: Removes document via `/api/documents/{document_id}`
- **Page Refresh**: Restores from localStorage (auth), loses scene state
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
