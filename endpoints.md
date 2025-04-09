# for auth 
POST /auth/login
POST /auth/register
GET /auth/me 

---

# for teams // in case we implement this 
GET /teams/            # list of users team 
POST /teams/           # create team
GET /teams/{id}        # team info + members
POST /teams/{id}/invite # create team invitation 

--- 
# for the sessions 

GET /sessions/         # list user sessions
POST /sessions/        # create new debug session
GET /sessions/{id}     # live session info (logs, screen, suggestions)
POST /sessions/{id}/end   # end session

---
# for the chat during the session 
GET /sessions/{id}/chat
POST /sessions/{id}/chat  # send message

---

# logs and suggestions  /// for report generation 

POST /sessions/{id}/logs      # upload OCR/log entry
POST /sessions/{id}/suggest   # upload Groq suggestions
GET /sessions/{id}/feed       # full timeline for frontend

# report generation 
GET /sessions/{id}/report  # return Markdown or PDF



