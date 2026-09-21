# Approved DreamRec profile sync

The repository includes a GitHub Actions workflow that runs approximately every five minutes and processes up to 100 approved public profile URLs per run.

## Add profiles

Edit [`profiles.txt`](profiles.txt) and add one URL per line:

```text
https://recroom.network/user/Example/
```

The synchronizer accepts only HTTPS URLs on `recroom.network` or `www.recroom.network` whose path matches `/user/<name>/`. It does not generate random names, probe arbitrary accounts, or attempt to log in.

## What each run does

The workflow fetches the next 100 URLs that have not already succeeded, verifies that each response is not an obvious 404, saves the profile HTML under `user/<name>/index.html`, applies the DreamRec theme and local DreamRec logo, updates the all-links directory, and records the result in `profile-sync-manifest.json` and `profile-sync-results.md`.

A one-second delay is used between requests. The five-minute schedule is approximate because GitHub Actions scheduled jobs can be delayed during periods of high GitHub load. The workflow also has a manual **Run workflow** button.

## Important limits

Only add profile URLs that you are authorized to mirror. The workflow does not bypass authentication, solve CAPTCHAs, enumerate usernames, or download private account data. If the source changes its page structure or blocks automated requests, failed URLs are recorded rather than retried indefinitely.
