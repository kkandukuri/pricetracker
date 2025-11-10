# CSV Export Guide

Export your scraped product data to CSV format with automatic extraction of color, size, and categories.

## 🚀 Quick Start

### Export All Products

```bash
# Export to default file (products.csv)
python export_csv.py

# Export to custom file
python export_csv.py --output my_products.csv

# Or use main.py
python main.py export --output products.csv
```

---

## 📊 CSV Output Format

### Standard Columns (Always Included)

The exported CSV will contain these columns in this exact order:

| Column | Description | Example |
|--------|-------------|---------|
| **URL** | Product page URL | https://distacart.com/products/... |
| **NAME** | Product name | Mamaearth Onion Shampoo |
| **Description** | Full product description | Complete product description text |
| **ShortDescription** | First 100 chars of description | Mamaearth Onion Hair Fall... |
| **Price** | Current price (number) | 399.00 |
| **color** | Auto-detected color | Black |
| **Size** | Auto-detected size | 250 ml |
| **Category** | Main category (auto-detected) | Beauty |
| **childCategory** | Sub-category (auto-detected) | Hair Care |

### Example CSV Output

```csv
URL,NAME,Description,ShortDescription,Price,color,Size,Category,childCategory
https://distacart.com/products/mamaearth-onion-shampoo,Mamaearth Onion Shampoo,Mamaearth Onion Hair Fall Shampoo for Hair Growth...,Mamaearth Onion Hair Fall Shampoo for Hair Growth & Hair Fall Control with Onion Oil...,399.00,Black,250 ml,Beauty,Hair Care
https://distacart.com/products/laptop,Dell Laptop,15.6 inch laptop with 8GB RAM...,15.6 inch laptop with 8GB RAM and 256GB SSD...,45000.00,Silver,15 inch,Electronics,Computers
```

---

## 🎨 Auto-Detection Features

### Color Detection

The script automatically detects colors from product names and descriptions:

**Supported colors:**
- Basic: Black, White, Red, Blue, Green, Yellow, Orange, Purple, Pink, Brown
- Extended: Grey/Gray, Silver, Gold, Beige, Navy, Teal, Maroon, Olive, Lime
- Advanced: Cyan, Magenta, Tan, Violet, Indigo, Turquoise
- Special: Multicolor, Multi-color, Assorted

**Example:**
- "Mamaearth Onion Shampoo **Black**" → color: `Black`
- "Blue Cotton Shirt" → color: `Blue`
- "Shoes - Available in **Silver**" → color: `Silver`

### Size Detection

Automatically extracts size information:

**Supported size formats:**
- Volume: 250 ml, 2 l, 500 ml
- Weight: 100 g, 2 kg, 8 oz, 2 lb
- Clothing: XS, S, M, L, XL, XXL, Small, Medium, Large
- Dimensions: 10x20, 10", 15 inch, 30 cm, 5 mm

**Example:**
- "Shampoo **250 ml**" → Size: `250 ml`
- "Laptop **15 inch**" → Size: `15 inch`
- "T-Shirt Size **XL**" → Size: `xl`

### Category Detection

Automatically categorizes products based on keywords in URL, name, and description:

**Beauty & Personal Care:**
- Keywords: beauty, hair, skin, makeup, shampoo, conditioner, lotion, cream, serum
- Categories: Beauty → Hair Care, Skin Care, Makeup, Personal Care

**Electronics:**
- Keywords: electronics, phone, laptop, computer, headphone, speaker, camera
- Categories: Electronics → Mobile, Computers, Audio, Photography

**Fashion:**
- Keywords: clothing, shirt, pants, dress, shoes
- Categories: Fashion → Clothing, Footwear

**Home:**
- Keywords: home, kitchen, furniture, bedding
- Categories: Home → Kitchen, Furniture, Bedroom

**Grocery:**
- Keywords: food, snack, beverage, organic
- Categories: Grocery → Food, Snacks, Beverages, Organic

**And more:** Toys, Books, Sports, etc.

---

## 💡 Usage Examples

### Example 1: Basic Export

```bash
# Export all products with standard columns
python export_csv.py --output products.csv
```

**Output:** `products.csv` with URL, NAME, Description, ShortDescription, Price, color, Size, Category, childCategory

### Example 2: Include Image URLs

```bash
# Export with image URLs
python export_csv.py --output products_with_images.csv --include-images
```

**Additional column:**
- `ImageURLs`: Semicolon-separated image URLs

**Example:**
```csv
...Category,childCategory,ImageURLs
...Beauty,Hair Care,"https://example.com/img1.jpg; https://example.com/img2.jpg; https://example.com/img3.jpg"
```

### Example 3: Include Metadata

```bash
# Export with all metadata
python export_csv.py --output full_export.csv --include-metadata
```

**Additional columns:**
- `Currency`: USD, EUR, INR, etc.
- `Site`: distacart.com, amazon.com, etc.
- `ProductID`: Database ID
- `CreatedAt`: When product was first tracked
- `UpdatedAt`: Last update timestamp

### Example 4: Full Export

```bash
# Export everything
python export_csv.py --output complete.csv --include-images --include-metadata
```

### Example 5: Use Main CLI

```bash
# Export using main.py
python main.py export --output products.csv

# With images
python main.py export --output products.csv --include-images
```

---

## 📁 Export Price History

Export complete price history for all products:

```bash
python export_csv.py --price-history --output price_history.csv
```

**Columns:**
- `ProductID`: Database ID
- `ProductName`: Product name
- `Date`: When price was recorded
- `Price`: Price at that time
- `Currency`: Currency code
- `PriceChange`: Change from previous price

**Example:**
```csv
ProductID,ProductName,Date,Price,Currency,PriceChange
1,Mamaearth Onion Shampoo,2025-11-10 10:00:00,399.00,INR,
1,Mamaearth Onion Shampoo,2025-11-10 18:00:00,349.00,INR,-50.00
1,Mamaearth Onion Shampoo,2025-11-11 10:00:00,399.00,INR,+50.00
```

---

## 🔧 Command Reference

### Using export_csv.py Directly

```bash
# Basic export
python export_csv.py

# Custom output file
python export_csv.py --output FILE.csv
python export_csv.py -o FILE.csv

# Include image URLs
python export_csv.py --include-images

# Include metadata
python export_csv.py --include-metadata

# Export price history
python export_csv.py --price-history --output history.csv

# Full export with everything
python export_csv.py --output full.csv --include-images --include-metadata

# View help
python export_csv.py --help
```

### Using main.py CLI

```bash
# Basic export
python main.py export

# Custom output
python main.py export --output products.csv
python main.py export -o products.csv

# With images
python main.py export --include-images

# With metadata
python main.py export --include-metadata

# View help
python main.py export --help
```

---

## 📝 Complete Workflow Example

### Scrape → Export → Analyze

```bash
# Step 1: Scrape products
python bulk_scraper.py urls.txt --delay 5

# Step 2: View what you have
python main.py list

# Step 3: Export to CSV
python export_csv.py --output products.csv --include-images

# Step 4: Open in spreadsheet software
# Excel, Google Sheets, LibreOffice Calc, etc.

# Step 5: Update prices later
python main.py update

# Step 6: Export again to see price changes
python export_csv.py --output products_updated.csv

# Step 7: Export price history
python export_csv.py --price-history --output price_history.csv
```

---

## 💻 Programmatic Export

You can also export programmatically in your Python scripts:

```python
from export_csv import export_to_csv, export_price_history_csv

# Export products
export_to_csv(
    output_file='products.csv',
    include_images=True,
    include_metadata=False
)

# Export price history
export_price_history_csv('price_history.csv')
```

---

## 🎯 Use Cases

### 1. E-commerce Analysis

Export competitor product data for analysis:

```bash
python export_csv.py --output competitor_products.csv --include-metadata
```

Import into Excel/Google Sheets for:
- Price comparison
- Category analysis
- Size/color availability
- Description analysis

### 2. Price Tracking

Monitor price changes over time:

```bash
# Export current prices
python export_csv.py --output prices_$(date +%Y%m%d).csv

# Later, export again
python export_csv.py --output prices_$(date +%Y%m%d).csv

# Compare the two CSV files
```

### 3. Product Catalog

Create a product catalog:

```bash
python export_csv.py --output catalog.csv --include-images --include-metadata
```

Use the CSV to:
- Create product listings
- Generate reports
- Build price comparison sites
- Feed data into other systems

### 4. Data Science / Machine Learning

Export data for analysis:

```bash
python export_csv.py --output training_data.csv --include-metadata
python export_csv.py --price-history --output price_trends.csv
```

Use for:
- Price prediction models
- Category classification
- Sentiment analysis on descriptions
- Time series analysis

---

## 🔍 Tips & Tricks

### 1. Automatic Timestamped Exports

The default filename includes timestamp:

```bash
python export_csv.py
# Creates: products_20251110_143025.csv
```

### 2. Daily Exports (Cron Job)

```bash
# Add to crontab
0 9 * * * cd /home/user/pricetracker && python export_csv.py --output /path/to/exports/products_$(date +\%Y\%m\%d).csv
```

### 3. Filter in Spreadsheet

After exporting, use spreadsheet filters:
- Filter by Category
- Filter by Price range
- Sort by Price
- Group by Site

### 4. Improve Auto-Detection

If color/size/category detection isn't accurate:
1. Update product names/descriptions to include these details
2. Modify the detection logic in `export_csv.py`
3. Add custom categories to the script

### 5. Large Exports

For large databases (1000+ products):
- Export may take a few seconds
- Consider splitting by category
- Use `--no-progress` flag for faster export

---

## 📊 Example Output Files

Check the `exports/` directory for examples:

```bash
exports/
├── products.csv              # Standard export
├── products_with_images.csv  # With image URLs
├── full_export.csv          # With all metadata
└── price_history.csv        # Price history
```

---

## 🆘 Troubleshooting

### Issue: Missing colors/sizes

**Cause:** Information not in name/description

**Solution:**
- Ensure product descriptions include these details
- Manually add to CSV after export
- Update scraper to extract from specific fields

### Issue: Wrong categories

**Cause:** Keyword-based detection is not perfect

**Solution:**
- Modify category keywords in `export_csv.py`
- Manually correct in spreadsheet
- Add product-specific categories

### Issue: Empty CSV

**Cause:** No products in database

**Solution:**
```bash
# Check products
python main.py list

# If empty, scrape some products first
python main.py add "URL"
```

### Issue: Special characters in CSV

**Cause:** Product descriptions contain commas, quotes, etc.

**Solution:**
The script handles this automatically with CSV escaping. Open with proper CSV reader (Excel, Google Sheets) not a text editor.

---

## ✅ Summary

**Quick commands:**

```bash
# Export all products
python export_csv.py --output products.csv

# Or use main CLI
python main.py export --output products.csv

# Export with images
python export_csv.py --output products.csv --include-images

# Export price history
python export_csv.py --price-history --output history.csv
```

**CSV contains:**
- ✅ URL - Product URL
- ✅ NAME - Product name
- ✅ Description - Full description
- ✅ ShortDescription - First 100 chars
- ✅ Price - Current price
- ✅ color - Auto-detected
- ✅ Size - Auto-detected
- ✅ Category - Auto-detected
- ✅ childCategory - Auto-detected

**Auto-detection:**
- Colors from name/description
- Sizes from measurements and dimensions
- Categories from keywords

Happy exporting! 📊
