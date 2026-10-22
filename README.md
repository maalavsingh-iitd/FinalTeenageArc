# Final Teenage Arc

A local-first personal command centre for countdown motivation, daily tasks, weekly planning, long-term goals, focus sessions, memories, and retrospectives.

## Project source

The repository includes `final-teenage-arc-final.zip`, the complete React + Vite source bundle, and a GitHub Actions workflow to build and publish the site to GitHub Pages.

## Run locally

1. Extract the project archive.
2. Open the `final-teenage-arc-v2` directory.
3. Run `npm install`, then `npm run dev`.
4. Run `npm run build` for a production build.

## Storage and privacy

The app is local-first and stores data in the browser's localStorage. Data is not synced between devices, so export backups regularly. Do not commit personal backups or private media to this repository.

## Deployment

GitHub Actions builds the Vite app from the source archive and deploys the `dist` folder to GitHub Pages. In repository Settings → Pages, choose **GitHub Actions** as the build and deployment source if it is not already configured.
