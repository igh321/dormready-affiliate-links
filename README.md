# DormReady Affiliate Links CDN

This repository hosts affiliate link configurations for the DormReady iOS app.

## Structure

```
v1/
├── bedding_sleep.json          # Bedding & Sleep category
├── bath_personal_care.json     # Bath & Personal Care category
├── electronics_tech.json       # Electronics & Tech category
├── kitchen_dining.json         # Kitchen & Dining category
├── clothing_laundry.json       # Clothing & Laundry category
├── school_supplies.json        # School Supplies category
├── decor_storage.json          # Decor & Storage category
├── health_safety.json          # Health & Safety category
└── other_essentials.json       # Other Essentials category
```

## Version History

- **v1** (2025-12-01): Initial release with 9 categories

## Usage

Files are served via GitHub Pages at:
```
https://[username].github.io/dormready-affiliate-links/v1/{category}.json
```

## Format

Each JSON file follows this structure:

```json
{
  "categoryId": "bedding_sleep",
  "version": 3,
  "lastUpdated": "2025-11-21",
  "items": {
    "item-id": {
      "itemVersion": 1,
      "links": [
        {
          "retailer": "amazon",
          "url": "https://amazon.com/...",
          "displayName": "Product Name",
          "affiliateTag": "dormready-20",
          "priority": 1,
          "averageRating": 4.5,
          "reviewCount": 1000,
          "badge": "best_seller"
        }
      ]
    }
  }
}
```

## Updating Links

1. Edit the appropriate category JSON file
2. Increment `itemVersion` for changed items
3. Update `lastUpdated` date
4. Commit and push changes
5. GitHub Pages will automatically update (1-2 minutes)

## License

These configurations are provided for use with the DormReady iOS app.
Affiliate links support the continued development of DormReady.
