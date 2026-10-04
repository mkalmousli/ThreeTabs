<p align="center"><img src="docs/assets/logo.svg" width="96" alt="ThreeTabs logo"></p>

# ThreeTabs

**Only three tabs. Total focus.** A free, open-source browser extension that limits you to 3 tabs (adjustable) and blocks new ones once you hit the limit.

🌐 Website: https://mkalmousli.github.io/ThreeTabs/

## Features
- Tab limit of 3 by default, adjustable from 1 to 50
- Blocks new tabs and windows when the limit is reached
- Optional redirect: open the blocked link in the tab you came from
- Count across all windows or per window
- Quiet by design: no numbers on the toolbar icon. A popup shows your slots and a blocked-tabs counter
- Settings always open, even when you're over the limit
- Never closes existing tabs, no tracking, no network requests
- Works on Chrome, Edge, Brave, Opera, Vivaldi and Firefox (Manifest V3)

## Install (from source)
**Chrome / Edge / Brave:** open `chrome://extensions`, enable *Developer mode*, click *Load unpacked*, and select the `extension` folder.

**Firefox (121+):** open `about:debugging#/runtime/this-firefox`, click *Load Temporary Add-on…*, and select `extension/manifest.json`.

To build a ZIP: `./scripts/package.sh` (outputs `dist/threetabs.zip`).

## Permissions
- `tabs`: count tabs and close the extra one
- `storage`: save your settings locally

## License
[MIT](LICENSE)
