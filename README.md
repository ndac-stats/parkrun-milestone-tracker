# parkrun Milestone Tracker

A static website for GitHub Pages that displays the run milestones reached by a list of parkrunners. A weekly GitHub Actions workflow retrieves each athlete's public results history and writes a JSON snapshot. This app has been created using ChatGPT.

## Included features

- Track a configurable list of athlete IDs.
- Show current run count, achieved milestones and progress to the next milestone.
- Search by name or athlete ID.
- Filter to runners who have reached a milestone or are within five runs of one.
- Weekly refresh via GitHub Actions, plus a manual **Run workflow** option.

Milestones are configurable in `app.js` and `scripts/update_results.py`. The defaults are 10, 25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500 and 1,000 runs.

## Deploy to GitHub Pages

1. Edit `config/athletes.csv`. Replace the example IDs with the athlete IDs you want to track. Names are fallback labels; the scraper attempts to use the name shown on the parkrun page.
1. Open **Settings → Pages**.
1. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`, then save.
1. Open **Actions**, select **Update parkrun milestone data**, and click **Run workflow**.
1. Once the workflow succeeds, visit the GitHub Pages URL shown in Settings → Pages.

The scheduled refresh runs weekly on Sunday at 02:30 UTC. GitHub Actions cron schedules use UTC. You can change the schedule in `.github/workflows/update-results.yml`.

## Important notes about parkrun data access

- parkrun does not provide a public athlete-results API. This project reads the public athlete-history HTML page, so it may stop working if parkrun changes its page structure or blocks automated requests.
- The scraper is best-effort. If parkrun returns an anti-bot page, the workflow will report a failure. The website continues to show the last successful snapshot.

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
