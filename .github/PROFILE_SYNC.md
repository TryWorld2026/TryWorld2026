# Profile contribution sync

The profile checks public pull requests daily, scheduled for 08:17 Asia/Shanghai
(00:17 UTC). GitHub may delay scheduled runs. Changes to the generator, tests, or
profile README also trigger a refresh. You can run it immediately from
[Refresh contributions](https://github.com/TryWorld2026/TryWorld2026/actions/workflows/update-contributions.yml).

The homepage summarizes every public PR submitted to external repositories and
shows the eight most recently updated PRs. `CONTRIBUTIONS.md` contains the complete
public PR list, with PRs to your own repositories in a separate section. Issues,
reviews, and direct commits have links to their original GitHub records. These
PR totals have a different scope from GitHub's contribution calendar.

The generator follows the user's PR connection through every page, so it does
not depend on GitHub Search's first 1,000 results. It filters private repositories
before rendering. API errors, incomplete responses, invalid records, or missing
README markers stop the refresh and preserve the previous documents.

The workflow uses its built-in `GITHUB_TOKEN`. Only the refresh job on the original
repository's `main` branch has `contents: write`; pull-request runs only test the
generator. No personal access token or paid service is required. The bot stages
only `README.md`, `README.en.md`, and `CONTRIBUTIONS.md`.

When records do not change, there is no daily commit. The archive records its
verification month, producing one real verification update per month during quiet
periods. This provides regular repository activity for
[GitHub's scheduled-workflow inactivity rule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Keep the `CONTRIBUTIONS:START` and `CONTRIBUTIONS:END` markers in each README.
The text between them is generated; introductions, banners, navigation, technical
interests, and text outside the markers can be edited normally.

To check or refresh locally with Python 3.11+ and an authenticated GitHub CLI:

```sh
python -m unittest discover -s tests -v
python scripts/update_profile.py --user TryWorld2026
```
