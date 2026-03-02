# Auth service (login / register for external services)

This app can act as a central login/register service. External apps **redirect users** to the login/register pages and receive user data in the **redirect URL** as a GET parameter (encoded).

**Connecting from another HTML site?** See [docs/EXTERNAL_HTML_CLIENT.md](docs/EXTERNAL_HTML_CLIENT.md) for step-by-step integration and copy-paste examples.

---

## Using auth from an external source (browser redirect)

### Flow

1. **With redirect (external service)**  
   Send users to:
   - Login: `/accounts/login/?next=https://your-app.com/callback`
   - Register: `/accounts/register/?next=https://your-app.com/callback`  
   You can use `next` or `source` (same meaning).

2. **After success**  
   The user is redirected to your URL with user data in a **GET parameter** (`data=base64url-encoded-json`):
   ```
   https://your-app.com/callback?data=<base64url-encoded-json>
   ```
   Decode the `data` value (base64url) to get JSON like:
   ```json
   {
     "id": 1,
     "username": "jane",
     "email": "jane@example.com",
     "first_name": "",
     "last_name": "",
     "is_verified": false,
     "created_at": "2025-02-14T12:00:00Z",
     "picture": "https://lh3.googleusercontent.com/..."
   }
   ```
   When the user signed in with **Google**, the payload also includes `picture` (profile image URL). Your frontend can show it as an avatar.

3. **Without redirect**  
   If the user opens login/register with no `next`/`source`, after success they see a **user data page** that displays the same JSON (no redirect).

---

## API (login/register)

- **Register:** `POST /api/accounts/register/` — returns user + JWT tokens in the response body.
- **Login:** `POST /api/accounts/login/` — returns user + JWT tokens in the response body.

There is no server-to-server POST to an external URL; user data is only returned in the redirect GET param (web flow) or in the API response (API flow).

---

## Pages (web flow)

- **Login:** `/accounts/login/`  
  Form (username/password) + “Continue with Google”.
- **Register:** `/accounts/register/`  
  Form (username, email, password, confirm) + “Continue with Google”.
- **User data (no redirect):** `/accounts/complete/`  
  Shown after login/register when no `next`/`source` was given; shows the user JSON.

## Google OAuth

1. Install deps: `pip install -r requirements.txt` (includes `django-allauth`).
2. Create OAuth credentials: [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → Create OAuth 2.0 Client ID (Web application). Set authorized redirect URI to:
   - `http://127.0.0.1:8000/accounts/google/login/callback/` (dev)
   - or your production origin, e.g. `https://auth.otabekdushamov.uz/accounts/google/login/callback/`
3. In `.env`:
   ```env
   GOOGLE_OAUTH_CLIENT_ID=your-client-id
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   ```
4. Run migrations: `python manage.py migrate` (creates `Site` and allauth tables).

If Google env vars are missing, the “Continue with Google” button still appears; clicking it will error until the app is configured.
