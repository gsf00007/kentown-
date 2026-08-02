# Kentown Mini Mart

This project is a grocery delivery storefront with an admin panel for managing products.

## Product updates without editing HTML manually
If you change a product's price, unit, category, or image link from the admin panel, the change is saved to the shared state files so it is reflected in the site source rather than only in your local browser session.

How it works:
- Product edits are saved through the admin panel.
- The app writes the updated state to the shared source file [admin-state.json](admin-state.json).
- When the local server is running, the same update is also written back into the page source so the site can be reloaded from the repository without hand-editing the HTML.

## Run locally
```bash
python3 server.py
```
Then open http://127.0.0.1:8000/.

## Admin access
Use the admin button in the storefront and enter the password:
```text
kentown123
```
