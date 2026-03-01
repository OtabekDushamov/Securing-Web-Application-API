# Connecting from another HTML app

This guide explains how to connect **your own HTML site** (on another domain or the same server) to this auth app. Users click “Login” or “Register” on your page, are sent to the auth app to sign in or sign up, then are sent back to your page with user data in a **GET parameter** (encoded). Your HTML decodes the parameter to get the user.

---

## Overview

1. **Your HTML** has “Login” and “Register” links that redirect to the **auth app** with a `next` parameter pointing back to your callback page.
2. User signs in or signs up on the auth app.
3. The auth app **redirects** the user to your callback URL with user data in a **GET parameter** (`?data=...`, base64url-encoded JSON).
4. **Your callback page** reads the query string, decodes the `data` parameter, and uses the user (e.g. show name, protect content).

---

## 1. Auth server base URL

Use the base URL where this Django app is running:

| Environment | Base URL |
|-------------|----------|
| Local dev   | `http://127.0.0.1:8000` |
| Production  | `https://your-auth-domain.com` |

In the examples below this is written as `AUTH_BASE`. Replace it with your actual base URL.

---

## 2. Login and register URLs

Send users to these paths on the auth server, with `next` (or `source`) set to **your** callback URL (the page that should open after login/register). The callback URL must be **URL-encoded**.

```
GET {AUTH_BASE}/accounts/login/?next={YOUR_CALLBACK_URL}
GET {AUTH_BASE}/accounts/register/?next={YOUR_CALLBACK_URL}
```

**Example**

- Auth server: `http://127.0.0.1:8000`
- Your callback page: `http://localhost:5500/callback.html` (or `https://myapp.com/callback.html`)

Then:

- **Login:**  
  `http://127.0.0.1:8000/accounts/login/?next=http%3A%2F%2Flocalhost%3A5500%2Fcallback.html`
- **Register:**  
  `http://127.0.0.1:8000/accounts/register/?next=http%3A%2F%2Flocalhost%3A5500%2Fcallback.html`

Use `encodeURIComponent('http://localhost:5500/callback.html')` in JavaScript to build the `next` value.

---

## 3. Callback URL (your page)

After a successful login or register, the user is redirected to the URL you passed as `next`, with user data in a **GET parameter**:

```
{YOUR_CALLBACK_URL}?data={base64url-encoded-json}
```

Example:

```
http://localhost:5500/callback.html?data=eyJpZCI6MSwidXNlcm5hbWUiOiJqYW5lIiwiZW1haWwiOiJqYW5lQGV4YW1wbGUuY29tIn0
```

Your page must read `window.location.search` and decode the `data` parameter (base64url → JSON).

---

## 4. Parsing the GET parameter in JavaScript

On your callback page, on load:

1. Read `window.location.search` (e.g. `?data=eyJpZCI6...`).
2. Parse the `data` query parameter.
3. Decode the value from **base64url** (base64 with URL-safe chars, no padding).
4. Parse the decoded string as JSON.

**Base64url in browser:** standard `atob()` expects standard base64. For base64url you add padding and replace `-`/`_` with `+`/`/`, or use the helper below.

### Decode helper

```javascript
function parseAuthDataFromGetParam() {
  const params = new URLSearchParams(window.location.search);
  const encoded = params.get('data');
  if (!encoded) return null;

  let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
  const pad = base64.length % 4;
  if (pad) base64 += '===='.slice(0, 4 - pad);

  try {
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    return JSON.parse(json);
  } catch (e) {
    console.error('Failed to decode auth data:', e);
    return null;
  }
}
```

### User object shape

The decoded JSON is an object like:

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

Use this to show the user’s name, email, or to gate content on “logged in” (e.g. `if (user) { ... }`).

---

## 5. Full example: two-page setup

### Your site (any host, e.g. `http://localhost:5500`)

**index.html** – landing page with Login and Register links:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App - Sign in</title>
</head>
<body>
  <h1>Welcome</h1>
  <p>Sign in or create an account using the auth server.</p>

  <script>
    const AUTH_BASE = 'http://127.0.0.1:8000';
    const CALLBACK_URL = window.location.origin + window.location.pathname.replace(/index\.html$/, '') + 'callback.html';
    const nextParam = encodeURIComponent(CALLBACK_URL);

    document.body.innerHTML += `
      <p>
        <a href="${AUTH_BASE}/accounts/login/?next=${nextParam}">Log in</a>
        &nbsp;|&nbsp;
        <a href="${AUTH_BASE}/accounts/register/?next=${nextParam}">Register</a>
      </p>
    `;
  </script>
</body>
</html>
```

**callback.html** – page the user returns to after login/register; reads user from GET param:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome back</title>
</head>
<body>
  <div id="message">Checking authentication...</div>
  <p><a href="index.html" id="logout">Back to home</a></p>

  <script>
    function parseAuthDataFromGetParam() {
      const params = new URLSearchParams(window.location.search);
      const encoded = params.get('data');
      if (!encoded) return null;
      let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
      const pad = base64.length % 4;
      if (pad) base64 += '===='.slice(0, 4 - pad);
      try {
        const json = decodeURIComponent(
          atob(base64)
            .split('')
            .map(function (c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            })
            .join('')
        );
        return JSON.parse(json);
      } catch (e) {
        return null;
      }
    }

    const user = parseAuthDataFromGetParam();
    const el = document.getElementById('message');

    if (user) {
      el.textContent = 'Hello, ' + (user.username || user.email) + '! You are signed in.';
    } else {
      el.textContent = 'No user data in URL. Please sign in from the home page.';
      document.getElementById('logout').textContent = 'Go to login';
      document.getElementById('logout').href = 'index.html';
    }
  </script>
</body>
</html>
```

---

## 6. Single-page example (same page as callback)

If you want the same page to show “Login / Register” when logged out and “Hello, user” when logged in (using the GET param):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
</head>
<body>
  <div id="app"></div>

  <script>
    const AUTH_BASE = 'http://127.0.0.1:8000';
    const CALLBACK_URL = window.location.origin + (window.location.pathname || '/');
    const nextParam = encodeURIComponent(CALLBACK_URL);

    function parseAuthDataFromGetParam() {
      const params = new URLSearchParams(window.location.search);
      const encoded = params.get('data');
      if (!encoded) return null;
      let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
      if (base64.length % 4) base64 += '===='.slice(0, 4 - base64.length % 4);
      try {
        const json = decodeURIComponent(
          atob(base64)
            .split('')
            .map(function (c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            })
            .join('')
        );
        return JSON.parse(json);
      } catch (e) {
        return null;
      }
    }

    function render() {
      const user = parseAuthDataFromGetParam();
      const app = document.getElementById('app');

      if (user) {
        app.innerHTML = '<p>Hello, <strong>' + (user.username || user.email) + '</strong>! You are signed in.</p>';
      } else {
        app.innerHTML = '<p><a href="' + AUTH_BASE + '/accounts/login/?next=' + nextParam + '">Log in</a> | ' +
          '<a href="' + AUTH_BASE + '/accounts/register/?next=' + nextParam + '">Register</a></p>';
      }
    }

    render();
  </script>
</body>
</html>
```

---

## 7. CORS (if you call the API from JavaScript)

The flow above uses **redirects only**; the browser never sends a cross-origin request from your HTML to the auth server, so **CORS is not required** for that flow.

If you also call the **REST API** from your HTML (e.g. `fetch(AUTH_BASE + '/api/accounts/login/', { method: 'POST', ... })`), the auth server must allow your origin. Add your site’s origin to the Django settings:

**.env** (or `config/settings.py`):

```env
CORS_ALLOWED_ORIGINS=http://localhost:5500,https://myapp.com
```

So: for “another HTML that comes here” and then goes back with user in the GET param, you only need the redirect flow and the query parsing above; CORS is only needed if you use the API from the browser.

---

## 8. Checklist

- [ ] Set `AUTH_BASE` to your auth server URL (e.g. `http://127.0.0.1:8000`).
- [ ] Set `CALLBACK_URL` to the full URL of the page that should receive the user (e.g. `http://localhost:5500/callback.html`).
- [ ] Use `encodeURIComponent(CALLBACK_URL)` as the `next` (or `source`) query parameter in login/register links.
- [ ] On the callback page, parse `window.location.search` and the `data` parameter (base64url → JSON).
- [ ] If you call the API from JS, add your HTML origin to `CORS_ALLOWED_ORIGINS`.

After that, your HTML can “connect” to this app by redirecting users to login/register and reading the user from the `data` GET parameter on the callback page.
