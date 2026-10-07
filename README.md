# kaop-demo-checkout

A throwaway demo service for testing Komodor AgentOps. It is created and torn
down by `kaop-scenarios/gcp-code-change` in
[komodorio/sa-tools](https://github.com/komodorio/sa-tools). Don't put anything
here you want to keep.

Every push to `main` builds the image and deploys it to Cloud Run
(`.github/workflows/deploy.yml`), authenticating to Google Cloud with Workload
Identity Federation. There are no secrets in this repo; the deploy settings
are repository variables.

Each deployed revision carries the commit it was built from:

- image tag `checkout:<sha>`
- revision label `commit-sha=<sha>` and revision name `<service>-<sha7>-<run>-<attempt>`
- env var `GIT_SHA`, written on every log line (`jsonPayload.git_sha`, `labels.git_sha`)
