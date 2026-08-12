# Deployment — GitHub → Vercel

The published site is `outputs/interactive/`, committed to the repository so Vercel serves
it as a static site with no build step.

**Repository:** https://github.com/ankurxbatta/cnv-gis-analysis

There are two ways to get "push to main → live site". **Pick one, not both**, or every push
deploys twice.

---

## Option A — Vercel Git Integration (simplest, recommended)

No secrets, no workflow. Vercel watches the repo itself.

1. Go to **https://vercel.com/new**
2. **Continue with GitHub** and authorise Vercel if prompted
3. Find **`ankurxbatta/cnv-gis-analysis`** → **Import**
   - Not listed? Click **Adjust GitHub App Permissions** and grant access to the repo
4. **Change nothing** on the configure screen — `vercel.json` already declares:
   - Framework preset: **Other**
   - Build command: **none**
   - Output directory: **`outputs/interactive`**
5. **Deploy**

Done. Every push to `main` redeploys; pull requests get preview URLs.

If you use this option, disable the workflow so it does not deploy a second time:
Actions tab → **Deploy to Vercel** → **⋯** → **Disable workflow**.
(Its validation job is still useful, so you may prefer to keep it and simply not add the
Vercel secrets — the deploy job then skips itself automatically.)

---

## Option B — GitHub Actions (`.github/workflows/deploy.yml`)

Use this if you want CI to gate the deploy, or you would rather not give Vercel access to
your GitHub account.

### 1. Create the Vercel project once

```bash
npm i -g vercel
vercel login
cd /path/to/cnv-gis-analysis
vercel link          # answer: create a new project, name it cnv-gis-analysis
```

This writes `.vercel/project.json` containing `orgId` and `projectId`.

```bash
cat .vercel/project.json
```

### 2. Create a Vercel access token

https://vercel.com/account/tokens → **Create Token** → copy it.

### 3. Add three repository secrets

GitHub → repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|---|---|
| `VERCEL_TOKEN` | the token from step 2 |
| `VERCEL_ORG_ID` | `orgId` from `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | `projectId` from `.vercel/project.json` |

Or from the command line:

```bash
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID     --body "$(jq -r .orgId    .vercel/project.json)"
gh secret set VERCEL_PROJECT_ID --body "$(jq -r .projectId .vercel/project.json)"
```

`.vercel/` is gitignored, so those IDs never enter the repository.

### 4. Push

The workflow runs on every push to `main`, on pull requests, and on demand from the
Actions tab. Until the secrets exist it validates the site and **skips the deploy step
cleanly** rather than failing.

---

## What the workflow checks before deploying

- all three pages exist (`index`, `review`, `recommendations`)
- every GeoJSON/JSON layer parses
- the pages still carry the **proxy** caveat and the **"no political variable"** statement
- the pages still carry the required **OpenStreetMap / CARTO attribution**

A push that strips those caveats fails CI instead of quietly publishing a
misrepresentative map.

---

## Publishing an update

```bash
./publish.sh                          # rebuild site, run QA, commit, push
./publish.sh "Refresh transit data"   # with a custom message
```

To refresh the underlying data first:

```bash
python run_pipeline.py --download --force
python run_pipeline.py --process --maps --report
./publish.sh "Refresh from upstream sources"
```

---

## What gets served

| Path | Contents |
|---|---|
| `/` | Civic Geography Explorer |
| `/recommendations` | Highest-exposure public locations, with reasoning |
| `/review` | Data review — excluded and flagged data |
| `/data/*.geojson` | Map layers |
| `/tables/*.csv` | Downloadable tables |

Roughly 2.4 MB total, well inside Vercel's free tier.

## What is not deployed

`data/raw/` (~1.2 GB of source downloads) and `data/processed/*.gpkg` are gitignored, and
are reproducible with `python run_pipeline.py --download --process`. The `.meta.json`
provenance sidecars **are** committed, so each source's URL, licence, SHA256 and retrieval
date survives in the repo without the payloads.

## Custom domain

Vercel project → **Settings → Domains → Add**. HTTPS is issued automatically.
