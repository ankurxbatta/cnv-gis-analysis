# Deployment — GitHub → Vercel

The published site is `outputs/interactive/`, committed to the repository so Vercel can
serve it as a static site with no build step.

**Repository:** https://github.com/ankurxbatta/cnv-gis-analysis

---

## One-time Vercel setup

1. Go to **https://vercel.com/new**
2. Choose **Import Git Repository** and pick `ankurxbatta/cnv-gis-analysis`
   (authorise Vercel for the repo if prompted)
3. Leave every build setting **as-is** — `vercel.json` already declares:
   - Framework preset: *Other*
   - Build command: *none*
   - Output directory: `outputs/interactive`
4. Click **Deploy**

That's it. Vercel's Git integration is now connected.

## After that, updates are automatic

Every push to `main` triggers a redeploy. Pull requests get their own preview URL.

```bash
./publish.sh                      # rebuild site, run QA, commit, push
./publish.sh "Refresh transit"    # with a custom message
```

Or manually:

```bash
python run_pipeline.py --maps     # regenerate the site from processed data
git add -A && git commit -m "Update" && git push
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
| `/` | Civic Geography Explorer (main map) |
| `/review` | Data review map — excluded and flagged data |
| `/data/*.geojson` | 19 map layers |
| `/tables/*.csv` | 19 downloadable tables |

Total payload ≈ 2.4 MB, comfortably inside Vercel's free tier.

## What is *not* deployed

`data/raw/` (~1.2 GB of source downloads) and `data/processed/*.gpkg` are gitignored.
They are fully reproducible with `python run_pipeline.py --download --process`.
The `.meta.json` provenance sidecars **are** committed, so every source's URL, licence,
SHA256 and retrieval date survives in the repository without the payloads.

## Custom domain

Vercel project → **Settings → Domains → Add**. HTTPS is issued automatically.
