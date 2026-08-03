# AstroOS — Google SSO + SEO setup

Live app: https://astroos-one.vercel.app  
API: https://astroos-api.vercel.app

## A. Google Sign-In (Auth.js)

### 1. Create Google OAuth credentials

1. Open [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create (or select) a project
3. Configure **OAuth consent screen** (External)
4. Create **OAuth client ID** → Application type **Web application**
5. Authorized JavaScript origins:
   - `http://localhost:3001`
   - `https://astroos-one.vercel.app`
6. Authorized redirect URIs:
   - `http://localhost:3001/api/auth/callback/google`
   - `https://astroos-one.vercel.app/api/auth/callback/google`

### 2. Vercel env (project **astroos**, not astroos-api)

```bash
cd frontend
npx vercel link --yes --project astroos --scope patus-projects

# Generate secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

npx vercel env add AUTH_SECRET production
npx vercel env add AUTH_GOOGLE_ID production
npx vercel env add AUTH_GOOGLE_SECRET production
npx vercel env add AUTH_URL production
# value: https://astroos-one.vercel.app

npx vercel env add NEXT_PUBLIC_SITE_URL production
# value: https://astroos-one.vercel.app

npx vercel --prod
```

### 3. Local `.env.local` (frontend/)

```env
AUTH_SECRET=your-long-random-string
AUTH_GOOGLE_ID=....apps.googleusercontent.com
AUTH_GOOGLE_SECRET=....
AUTH_URL=http://localhost:3001
NEXT_PUBLIC_SITE_URL=http://localhost:3001
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

Without Google env vars, the **Sign in with Google** button still shows but alerts that auth is not configured. Chart tools stay public.

## B. SEO / Google ranking

Already in the app:

- Rich metadata + Open Graph
- `/sitemap.xml`
- `/robots.txt`
- JSON-LD (`SoftwareApplication` + `FAQPage`)
- Indexable pages: `/`, `/about`, `/gun-milan`

### After deploy — do once

1. [Google Search Console](https://search.google.com/search-console) → Add property `https://astroos-one.vercel.app`
2. Submit sitemap: `https://astroos-one.vercel.app/sitemap.xml`
3. Optional: Google Analytics / Tag Manager

### Ranking tips

- Prefer a custom domain later (points to Vercel)
- Publish more MR/HI/EN guides over time
- Keep the astrology disclaimer visible
