# Auth service (login / register for external services)

This app can act as a central login/register service. External apps redirect users here; after successful auth you get user data (e.g. in JSON or in the redirect URL).

## Flow

1. **With redirect (external service)**  
   Send users to:
   - Login: `/accounts/login/?next=https://your-app.com/callback`
   - Register: `/accounts/register/?next=https://your-app.com/callback`  
   You can use `next` or `source` (same meaning).

2. **After success**  
   The user is redirected to your URL with user data in the **hash fragment**:
   ```
   https://your-app.com/callback#data=<base64url-encoded-json>
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
     "created_at": "2025-02-14T12:00:00Z"
   }
   ```
   Your frontend can read `window.location.hash` and parse `data` to get the user.

3. **Without redirect**  
   If the user opens login/register with no `next`/`source`, after success they see a **user data page** that displays the same JSON (no redirect).

## Pages

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
   - or your production origin, e.g. `https://yourdomain.com/accounts/google/login/callback/`
3. In `.env`:
   ```env
   GOOGLE_OAUTH_CLIENT_ID=your-client-id
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   ```
4. Run migrations: `python manage.py migrate` (creates `Site` and allauth tables).

If Google env vars are missing, the “Continue with Google” button still appears; clicking it will error until the app is configured.
