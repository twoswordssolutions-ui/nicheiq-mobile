# NicheIQ Auto Research v2 — Android + GitHub Pages

**Built for** `twoswordssolutions-ui/nicheiq-mobile` and its published URL:
<https://twoswordssolutions-ui.github.io/nicheiq-mobile/>

## What changes

Instead of manually entering keywords and opportunities every week, register a research topic once using the **+ Register automatic niche** button in the Android website. The button opens a GitHub Issue template. Submitting the issue triggers one research run, and the system also refreshes open niches **Mondays at 15:17 UTC** (GitHub schedules are approximate). Reports appear under **Research**, and dated JSON snapshots are stored in `data/history/`.

You do **not** have to re-enter product ideas or research findings. You will still need to review important business decisions and validate products. Existing v1 records remain stored in your Android browser; they are not migrated or overwritten by the automated feed.

The implementation uses:
- A **GitHub Issue** as each niche registration. No GitHub personal access token is put in the browser.
- **GitHub Actions** to schedule runs, ask an AI model to research third-party public sources, write JSON reports and deploy Pages.
- **OpenAI Responses API with web search** for sourced research. Paid API usage is separate from ChatGPT subscriptions.
- Static **GitHub Pages** to display results on Android without a server or in-browser API secrets.

This does not scrape Etsy and does not access Etsy Marketplace Insights, seller account data, actual Etsy keyword search counts, Etsy sales, or private shop metrics. Those require separate authorized sources. The research priority numbers are **heuristic research triage** rather than sales predictions. Evidence level C means that the claim cites a public retrieved source; D means hypothesis or no citation.

## IMPORTANT: Deployment to your existing GitHub repo

**Do not create a second repository.** Upload the complete contents of this package (including the hidden `.github` folder) into the root of your existing `nicheiq-mobile` repository. Keep the ZIP as a backup, but do not upload the ZIP as your deployment.

**Before updating:** From your existing Android app, use `Backup` to export your local JSON records. This release retains the same local storage key but a backup is prudent.

### Easiest one-time upload through Termux on your Android phone

1. Download the ZIP into your phone's Download folder.
2. Open Termux and run:

```sh
pkg update
pkg install git gh unzip -y
termux-setup-storage
# Complete Android's storage permission dialog.
gh auth login
# Select GitHub.com -> HTTPS -> Login with a web browser.
gh auth setup-git
cd ~
git clone https://github.com/twoswordssolutions-ui/nicheiq-mobile.git
cd nicheiq-mobile
unzip -o ~/storage/downloads/NicheIQ_Auto_Research_v2_GitHub.zip -d .
git add -A
git commit -m "Add automatic niche research and mobile dashboard"
git push origin main
```

If you already cloned the repository, use `git pull --ff-only origin main` instead of cloning a second time. The ZIP path assumes your Android browser saved the download with that exact name; adjust if renamed. Use a verified owner account for `gh auth login`. Never paste GitHub tokens or API keys into ChatGPT or repository source files.

**Alternative desktop setup:** Clone the repository, extract the ZIP contents into the repository root, and run `git add -A && git commit -m "Add automated niche research" && git push`.

### REQUIRED: Turn on GitHub Actions publishing

Because commits created using `GITHUB_TOKEN` do **not** trigger Pages builds when published from a branch, this release uses one workflow for research **and** Pages deployment.

1. In your repository select **Settings → Pages → Build and deployment → Source: GitHub Actions**. This replaces the previous "Deploy from a branch" setting.
2. Go to **Settings → Secrets and variables → Actions → New repository secret**. Name it exactly `OPENAI_API_KEY`. Paste your OpenAI **API** key there. Use <https://platform.openai.com/api-keys>. This is separate from your ChatGPT login/subscription, with separate billing.
3. Ensure GitHub **Issues** and **Actions** are enabled. In repository Settings → Actions → General → Workflow permissions, ensure appropriate repository policies allow the workflow's requested write permissions to commit reports and deploy Pages. If org policy blocks it, an owner must adjust policy.
4. Visit **Actions → NicheIQ automated research → Run workflow** for the initial test, then open its logs. A successful deployment run creates/refreshes the website.
5. Return to <https://twoswordssolutions-ui.github.io/nicheiq-mobile/> and open **Research**.
6. Select **+ Register automatic niche**. Enter the title after `[Niche]` and optional buyer, region, budget and production constraints, then submit the GitHub issue. Only issues created by the repository owner are accepted for paid research runs, to prevent arbitrary public users spending your API balance.
7. The issue triggers the action. Once that run succeeds, open **Research → Refresh feed** to see research results. The phone automatically fetches refreshed reports when the dashboard launches, when online.

**A successful Pages publish is not proof that research ran.** Inspect the *research* job separately. The first run without a niche will publish the empty dashboard; research requires an open `[Niche] ...` issue and `OPENAI_API_KEY`.

### Example niche

GitHub Issue title: `[Niche] Hand-tooled leather hat patches`

- Target buyer: Western-wear enthusiasts and personalized gift buyers
- Region: United States
- Production constraints: Vegetable-tanned leather, hand tooling, small-batch production; avoid machinery-intensive work
- Testing budget: 150

### Operating model

- **Adding** a niche: New issue via the app, with title `[Niche] ...`.
- **Changing** a niche: Edit its issue, which triggers fresh research.
- **Stopping** a niche: Close its issue. It disappears from active reports after a successful run; existing `data/history/` remains.
- **Refreshing** an existing niche: Automatic weekly run, or **Actions → Run workflow** manually.
- **Research volume control:** Up to eight niches per weekly run by default. If more exist, batches rotate weekly; change `NICHEIQ_MAX_WEEKLY_NICHES` in `.github/workflows/nicheiq-research.yml`. A newly opened/edited owner issue triggers a single-niche refresh. These calls can incur API costs.
- **Historical results:** `data/history/<issue-number>/<UTC timestamp>.json` and latest dashboard summary in `data/latest.json`.
- **Data backup:** Your manual local records still need JSON backup. Automated research data lives in GitHub history and is public to viewers of a public repo.

### Research safety and evidence limits

- Automated research requests **public third-party sources**, explicitly not automated access to Etsy.com, and never bypasses Etsy restrictions. The model can propose differentiated products, search phrases to investigate, and market hypotheses. It cannot verify exact Etsy searches, sales, or inventory from these sources.
- Citations on findings are accepted only when the source URL was returned as a model web-search result or citation. Missing citations mean evidence level D and research priority capped at 65/100.
- Scores are *research priorities*, not production-ready product validation or expected revenue.
- The GitHub Issue contents and report JSON in a public repository are publicly visible. Never input private business plans, customer data, or credentials there.
- GitHub Pages hosts only the static app shell and sanitized latest research JSON; API keys remain in GitHub Actions secrets.
- Do not replace reports with arbitrary sales numbers; validate actual measurements independently.

### Costs

GitHub Pages is usually free for public repositories on GitHub Free. GitHub Actions has its own usage policies. OpenAI web search and model tokens cost money, and prices can change: <https://platform.openai.com/pricing>. Consider an OpenAI project budget and usage alerts, and keep the weekly per-run niche cap small to start.

### Testing and troubleshooting

Run the included backend tests locally:

```sh
python -m unittest discover -s tests -v
node --check service-worker.js
```

- Research section empty: first open issue may not yet have been processed; inspect Actions run and whether `OPENAI_API_KEY` is set.
- New GitHub niche button opens an error: enable Issues and verify `.github/ISSUE_TEMPLATE/niche.yml` exists after upload.
- Pages site doesn't update: ensure source is **GitHub Actions** rather than "Deploy from a branch" and inspect `deploy` job.
- Research has no citations: model did not return traceable web sources. It is correctly labeled as a hypothesis, not verified.
- Some niches skipped: weekly maximum is 8 and rotates; use `Run workflow` for another batch or increase the cap cautiously.
- Cached/old data: reconnect to internet, tap **Refresh feed**, review the report timestamp; clear PWA cache only if necessary, preserving a JSON backup first.

**Readiness:** The repo package and static code are built. Backend tests and static JavaScript syntax checks can be run locally. The live OpenAI API, GitHub Actions, and a real Android device must be tested *after* the secret is connected and the repository is updated.
