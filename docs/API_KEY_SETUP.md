# How to Get HashKey API Key

Based on the official HashKey API documentation.

---

## Use sandbox without API key (public data only)

You can use the **HashKey Global sandbox** for public data **without any API key**:

| Endpoint | Auth | Description |
|----------|------|--------------|
| `GET https://api-glb.sim.hashkeydev.com/api/v1/ping` | **None** | Test connectivity |
| `GET https://api-glb.sim.hashkeydev.com/api/v1/time` | **None** | Server time |
| `GET https://api-glb.sim.hashkeydev.com/api/v1/exchangeInfo` | **None** | Trading pairs (symbols) |
| `GET https://api-glb.sim.hashkeydev.com/quote/v1/ticker/24hr` | **None** | 24h ticker (prices) |
| `GET https://api-glb.sim.hashkeydev.com/quote/v1/ticker/price` | **None** | Latest price |

ChainMind uses these when no `HSP_API_KEY` is set: dashboard shows “Sandbox OK (no API key)” and trading signals can use live sandbox ticker data.

**Account balance and transactions:** To show your **exchange account balance** and **recent trades** on the dashboard from the sandbox, set both `HSP_API_KEY` and `HSP_SECRET` in `.env` (from the same sandbox account → API Management → Create API). The dashboard will then use `GET /api/v1/account` and `GET /api/v1/account/trades` instead of chain/mock data.

---

## Sandbox (testing)

Use this to get API keys for development and demos.

### 1. Get a sandbox account

- **Email:** [global-api@hashkey.com](mailto:global-api@hashkey.com)  
- Request a sandbox account so you can use the test environment.

### 2. Open the sandbox site

- **URL:** https://global.sim.hashkeydev.com  

### 3. Log in

- Use the credentials you receive.
- **Sandbox only:** All 2FA / SMS / Email codes are **`123456`**.

### 4. Create an API key

1. Click **User Settings** (top right).
2. Open **API Management**.
3. Click **Create API**.
4. Fill in:
   - **Account** and **API Key name**
   - **Read** and/or **Write** permission
   - **IP address** (optional; leave blank or add your IP for testing)
5. Accept the agreement and click **Confirm**.

You will get:

- **Access Key** → use as `HSP_API_KEY` (or `X-HK-APIKEY` in requests).
- **Secret Key** → keep private; used for **HMAC SHA256** signatures on private endpoints.

---

## Production

On the main HashKey site (after you have a live account):

1. Go to **Settings → API Management → Create API**.
2. Enter **API Key name**, set **API permission**, and **IP Access Restriction** (if required).
3. Use the issued **Access Key** in the `X-HK-APIKEY` header; use the **Secret Key** only for signing, never in the header or in docs.

---

## Using the key in ChainMind

In your `.env`:

```env
HSP_API_KEY=your_access_key_here
```

For **signed** (private) endpoints, the docs require:

- Header: **`X-HK-APIKEY`** = your Access Key.
- **timestamp** (milliseconds) in query or body.
- **signature** = HMAC SHA256 of the request string using your **Secret Key**.

So for full private API use you need both Access Key and Secret Key; store the secret in `.env` only and never commit it.

---

## References

- **Authentication:** https://hashkeyglobal-apidoc.readme.io/reference/authentication-1  
- **Sandbox:** https://hashkeyglobal-apidoc.readme.io/reference/test-our-sandbox  
- **HashKey docs:** https://docs.hashkey.com  
