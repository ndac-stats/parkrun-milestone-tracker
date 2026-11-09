# parkrun Milestone Tracker

A static website for GitHub Pages that displays the run milestones reached by a list of parkrunners. A weekly GitHub Actions workflow retrieves each athlete's public results history and writes a JSON snapshot. GitHub Pages serves the site and snapshot; no server or database is required.

## Included features

- Track a configurable list of athlete IDs.
- Show current run count, achieved milestones and progress to the next milestone.
- Search by name or athlete ID.
- Filter to runners who have reached a milestone or are within five runs of one.
- Weekly refresh via GitHub Actions, plus a manual **Run workflow** option.
- Mobile-friendly layout.

Milestones are configurable in `app.js` and `scripts/update_results.py`. The defaults are 10, 25, 50, 100, 250, 500 and 1,000 runs. The 10-run milestone is the junior milestone; confirm which milestone categories your group wants to display.

## Deploy to GitHub Pages

1. Create a new GitHub repository and upload the contents of this folder to its root.
2. Edit `config/athletes.csv`. Replace the example IDs with the athlete IDs you want to track. Keep the header row `athlete_id,name`. Names are fallback labels; the scraper attempts to use the name shown on the parkrun page.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`, then save.
5. Open **Actions**, select **Update parkrun milestone data**, and click **Run workflow**.
6. Once the workflow succeeds, visit the GitHub Pages URL shown in Settings → Pages.

The scheduled refresh runs weekly on Sunday at 02:30 UTC. GitHub Actions cron schedules use UTC. You can change the schedule in `.github/workflows/update-results.yml`.

## Important notes about parkrun data access

- parkrun does not provide a public athlete-results API. This project reads the public athlete-history HTML page, so it may stop working if parkrun changes its page structure or blocks automated requests.
- Keep requests infrequent. The workflow runs weekly and pauses three seconds between athlete requests. Do not run it repeatedly or use it for high-volume collection.
- Check parkrun's current website terms and any applicable data-use requirements before deploying. This is an unofficial community project and is not affiliated with parkrun.
- The scraper is best-effort. If parkrun returns an anti-bot page, the workflow will report a failure. The website continues to show the last successful snapshot.
- Athlete IDs and result totals are public-facing data. Only include people you have a legitimate reason to track, and consider whether they are comfortable being listed.

## Local preview

You can preview the frontend with any static web server from the project root, for example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`. The sample JSON is deliberately included so the page renders before the first live scrape.

## Customising milestones

Edit both milestone arrays:
- `MILESTONES` in `app.js`
- `MILESTONES` in `scripts/update_results.py`

Keep the two lists in sync. The current implementation tracks **run milestones**, not volunteer milestones.
