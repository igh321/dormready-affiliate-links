#!/usr/bin/env python3
"""
Convert v2 affiliate links JSON files to v1 format for iOS app compatibility.

v2 Format (input):
{
  "id": "bedding_sleep",
  "label": "Bedding & Sleep",
  "items": [
    {
      "id": "twin-xl-sheets",
      "name": "...",
      "affiliateLinks": [
        {
          "retailer": "Amazon",
          "url": "...",
          "displayName": "...",
          "averageRating": 4.5,
          "reviewCount": 400000,
          "badge": "budget best-seller"
        }
      ]
    }
  ]
}

v1 Format (output):
{
  "categoryId": "bedding_sleep",
  "version": 3,
  "lastUpdated": "2025-12-01",
  "items": {
    "twin-xl-sheets": {
      "itemVersion": 1,
      "links": [
        {
          "retailer": "amazon",
          "url": "...",
          "displayName": "...",
          "affiliateTag": "dormready-20",
          "priority": 1,
          "averageRating": 4.5,
          "reviewCount": 400000,
          "badge": "amazons_choice"
        }
      ]
    }
  }
}
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
VERSION = 3
DEFAULT_AFFILIATE_TAG_AMAZON = "dormready-20"
DEFAULT_AFFILIATE_TAG_WALMART = "dormready"
DEFAULT_AFFILIATE_TAG_TARGET = "dormready"
DEFAULT_AFFILIATE_TAG_OTHER = "dormready"
TODAY = datetime.now().strftime("%Y-%m-%d")

# Badge normalization mapping
BADGE_MAPPING = {
    "budget best-seller": "best_seller",
    "best-seller": "best_seller",
    "Amazon no.1 best-seller": "best_seller",
    "amazons choice": "amazons_choice",
    "amazon choice-style": "amazons_choice",
    "budget pick": "budget_pick",
    "dorm bundle": "dorm_bundle",
    "adjustable luxury": "premium",
    "premium adjustable": "premium",
    "multiple options": "multiple_options",
    "multiple styles": "multiple_options",
    "heavy-duty": "heavy_duty",
    "adjustable height": "adjustable",
    "popular dorm upgrade": "popular",
    "popular dorm lamp": "popular",
    "plush comfort": "comfort",
    "decor + luxe feel": "premium",
    "top-rated": "top_rated",
    "budget encasement": "budget_pick",
    "soft & quiet": "comfort",
    "allergy-friendly": "allergy_friendly",
    "value pack": "value_pack",
    "big-box option": "in_store",
    "budget full-body": "budget_pick",
    "budget set": "budget_pick",
    "budget cozy": "budget_pick",
    "large capacity": "large_capacity",
    "many options": "multiple_options"
}

def normalize_retailer(retailer: str) -> str:
    """Normalize retailer name to lowercase."""
    return retailer.lower().strip()

def normalize_badge(badge: str | None) -> str | None:
    """Normalize badge to snake_case format."""
    if not badge:
        return None

    badge_lower = badge.lower().strip()
    return BADGE_MAPPING.get(badge_lower, badge_lower.replace(" ", "_").replace("-", "_"))

def get_affiliate_tag(retailer: str) -> str:
    """Get appropriate affiliate tag for retailer."""
    retailer_lower = retailer.lower()
    if "amazon" in retailer_lower:
        return DEFAULT_AFFILIATE_TAG_AMAZON
    elif "walmart" in retailer_lower:
        return DEFAULT_AFFILIATE_TAG_WALMART
    elif "target" in retailer_lower:
        return DEFAULT_AFFILIATE_TAG_TARGET
    else:
        return DEFAULT_AFFILIATE_TAG_OTHER

def convert_link(link: dict, priority_index: int) -> dict:
    """Convert a v2 affiliate link to v1 format."""
    retailer = normalize_retailer(link.get("retailer", ""))

    v1_link = {
        "retailer": retailer,
        "url": link["url"],
        "displayName": link.get("displayName"),
        "affiliateTag": get_affiliate_tag(retailer),
        "priority": priority_index + 1,  # 1-indexed
    }

    # Add optional fields if present
    if "averageRating" in link and link["averageRating"] is not None:
        v1_link["averageRating"] = link["averageRating"]

    if "reviewCount" in link and link["reviewCount"] is not None:
        v1_link["reviewCount"] = link["reviewCount"]

    if "badge" in link and link["badge"] is not None:
        v1_link["badge"] = normalize_badge(link["badge"])

    return v1_link

def convert_item(item: dict) -> tuple[str, dict]:
    """Convert a v2 item to v1 format.

    Returns:
        Tuple of (item_id, item_config)
    """
    item_id = item["id"]
    affiliate_links = item.get("affiliateLinks", [])

    # Convert links with priority based on array order
    v1_links = [
        convert_link(link, idx)
        for idx, link in enumerate(affiliate_links)
    ]

    v1_item = {
        "itemVersion": 1,
        "links": v1_links
    }

    return item_id, v1_item

def convert_category(v2_data: dict) -> dict:
    """Convert a v2 category file to v1 format."""
    category_id = v2_data["id"]
    items_array = v2_data.get("items", [])

    # Convert array of items to dict keyed by item ID
    items_dict = {}
    for item in items_array:
        item_id, item_config = convert_item(item)
        items_dict[item_id] = item_config

    v1_data = {
        "categoryId": category_id,
        "version": VERSION,
        "lastUpdated": TODAY,
        "items": items_dict
    }

    return v1_data

def convert_file(input_path: Path, output_path: Path) -> bool:
    """Convert a single v2 JSON file to v1 format.

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Converting {input_path.name}...")

        # Read v2 file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Check if this is a JSON fragment (starts with "key": {)
        # If so, wrap it in outer braces and parse
        if content.startswith('"'):
            # Extract the category key and wrap in {}
            content = '{' + content + '}'
            wrapped_data = json.loads(content)
            # Get the first (and should be only) key
            category_key = list(wrapped_data.keys())[0]
            v2_data = wrapped_data[category_key]
            # Add the 'id' field from the key if not present
            if 'id' not in v2_data:
                v2_data['id'] = category_key
        else:
            # Standard JSON object
            v2_data = json.loads(content)

        # Convert to v1
        v1_data = convert_category(v2_data)

        # Write v1 file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(v1_data, f, indent=2, ensure_ascii=False)

        # Print statistics
        item_count = len(v1_data["items"])
        link_count = sum(len(item["links"]) for item in v1_data["items"].values())
        print(f"  ✅ {input_path.name}: {item_count} items, {link_count} links")

        return True

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON decode error in {input_path.name}: {e}")
        return False
    except KeyError as e:
        print(f"  ❌ Missing required field in {input_path.name}: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error converting {input_path.name}: {e}")
        return False

def main():
    """Main conversion function."""
    # Get script directory
    script_dir = Path(__file__).parent
    v2_dir = script_dir / "v2"
    v1_dir = script_dir / "v1"

    # Check v2 directory exists
    if not v2_dir.exists():
        print(f"❌ v2 directory not found: {v2_dir}")
        return 1

    # Create v1 directory if it doesn't exist
    v1_dir.mkdir(exist_ok=True)

    # Get all JSON files in v2 directory
    v2_files = sorted(v2_dir.glob("*.json"))

    if not v2_files:
        print(f"❌ No JSON files found in {v2_dir}")
        return 1

    print(f"Found {len(v2_files)} files to convert\n")

    # Convert each file
    success_count = 0
    fail_count = 0

    for v2_file in v2_files:
        v1_file = v1_dir / v2_file.name
        if convert_file(v2_file, v1_file):
            success_count += 1
        else:
            fail_count += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Conversion Summary:")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    print(f"  📁 Output directory: {v1_dir}")
    print(f"{'='*60}")

    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    exit(main())
