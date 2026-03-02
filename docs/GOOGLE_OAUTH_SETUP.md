# How to set up Google OAuth for this app

This app uses **django-allauth** for “Continue with Google”. Follow these steps to enable it.

---

## 1. Open Google Cloud Console

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)** and sign in.
2. Create a **new project** or select an existing one (top bar: project dropdown → “New Project”).
3. Remember the **project name**; you’ll use it to find the credentials later.

---

## 2. Configure the OAuth consent screen

Google requires a “consent screen” before you can create OAuth credentials.

1. In the left menu go to **APIs & Services** → **OAuth consent screen**.
2. Choose **External** (so any Google account can sign in). Click **Create**.
3. Fill in:
   - **App name:** e.g. `Auth – otabekdushamov.uz`
   - **User support email:** your email
   - **Developer contact:** your email
4. Click **Save and Continue**.
5. **Scopes:** click **Add or Remove Scopes**. Add:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   (Or choose “See full list” and pick **email** and **profile** under Google APIs.)
6. Click **Save and Continue**.
7. **Test users** (if the app is in “Testing”): add your own Gmail address so you can sign in. Later you can publish the app so anyone can use it.
8. Click **Back to Dashboard**.

---

## 3. Create OAuth 2.0 credentials

1. Go to **APIs & Services** → **Credentials**.
2. Click **+ Create Credentials** → **OAuth client ID**.
3. **Application type:** **Web application**.
4. **Name:** e.g. `Auth web client`.
5. **Authorized JavaScript origins** (optional but recommended):
   - Local: `http://127.0.0.1:8000`
   - Production: `https://auth.otabekdushamov.uz`
6. **Authorized redirect URIs** — add **exactly** these (django-allauth expects this path):

   **Local development:**
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

   **Production (your auth domain):**
   ```
   https://auth.otabekdushamov.uz/accounts/google/login/callback/
   ```

   Important:
   - Use `https` in production, `http` for local.
   - Path must end with `/accounts/google/login/callback/`.
   - No typo in `callback` and no extra query string.

7. Click **Create**.
8. Copy the **Client ID** and **Client secret** (you can show the secret once; store it safely).

---

## 4. Configure this Django project

### Option A: Using `.env` (recommended)

In the project root (same folder as `manage.py`), create or edit `.env`:

```env
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

Replace with the values from the Google Cloud Console. No quotes needed.

### Option B: Environment variables on the server

On the server (e.g. in systemd, supervisor, or your hosting panel), set:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

Same values as above.

---

## 5. Django settings and Site (production)

This app already reads the credentials in `config/settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'FETCH_USERINFO': True,
        'APP': {
            'client_id': env('GOOGLE_OAUTH_CLIENT_ID', default=''),
            'secret': env('GOOGLE_OAUTH_CLIENT_SECRET', default=''),
        },
    }
}
```

For **production**, the **Django Site** must match your auth domain:

1. Run:
   ```bash
   python manage.py shell
   ```
2. In the shell:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'auth.otabekdushamov.uz'
   site.name = 'Auth otabekdushamov.uz'
   site.save()
   exit()
   ```
   Or in **Django Admin**: go to **Sites** → edit the site with id 1 and set **Domain name** to `auth.otabekdushamov.uz`.

---

## 6. Run migrations (if not done yet)

```bash
python manage.py migrate
```

This creates/updates allauth and Site tables.

---

## 7. Test

1. Start the server (e.g. `python manage.py runserver` for local).
2. Open the login page:
   - Local: `http://127.0.0.1:8000/accounts/login/`
   - Production: `https://auth.otabekdushamov.uz/accounts/login/`
3. Click **Continue with Google**.
4. You should see Google’s login/consent screen, then be redirected back to your app (or to the `next` URL, e.g. checkauth).

---

## Troubleshooting

| Problem | What to check |
|--------|----------------|
| “Redirect URI mismatch” | Redirect URI in Google Console must be **exactly** `https://auth.otabekdushamov.uz/accounts/google/login/callback/` (same protocol, domain, path, trailing slash). |
| “Access blocked: This app’s request is invalid” | OAuth consent screen must be configured and the correct scopes (email, profile) added. |
| “Continue with Google” does nothing or 500 | Ensure `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are set and the server was restarted after changing `.env`. |
| After Google login, wrong or blank page | In production, Site (id=1) `domain` must be `auth.otabekdushamov.uz`. |

---

## Summary checklist

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured (app name, email, scopes: email + profile)
- [ ] OAuth client ID created (Web application)
- [ ] Redirect URI added: `https://auth.otabekdushamov.uz/accounts/google/login/callback/`
- [ ] `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` set in `.env` or environment
- [ ] Django Site domain set to `auth.otabekdushamov.uz` for production
- [ ] Migrations run; “Continue with Google” tested on login page
