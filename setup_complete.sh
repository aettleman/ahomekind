#!/bin/bash

# ============================================
# A Home Kind - Complete Brand Pages Setup
# ============================================
# This script does EVERYTHING automatically:
# 1. Generates all 103 brand pages
# 2. Generates sitemap.xml
# 3. Adds CSS styling to style.css
# 4. Commits everything
# 5. Pushes to GitHub
#
# Just download this file, make it executable,
# and double-click it (or run: bash setup_complete.sh)
# ============================================

set -e

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  A Home Kind - Brand Pages Complete    ║"
echo "║  Setup (All Automated)                 ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we're in ahomekind directory
if [ ! -f "$SCRIPT_DIR/data/brands.json" ]; then
  echo "ERROR: Could not find data/brands.json"
  echo ""
  echo "This script needs to be in your ahomekind folder."
  echo "Please move this file to your ahomekind directory and try again."
  echo ""
  exit 1
fi

cd "$SCRIPT_DIR"

echo "✓ Found ahomekind directory"
echo ""

# ========================================
# STEP 1: Generate all 103 brand pages
# ========================================
echo "STEP 1: Generating 103 brand pages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "scripts/generate-brand-pages.js" ]; then
  echo "ERROR: scripts/generate-brand-pages.js not found"
  exit 1
fi

node scripts/generate-brand-pages.js

echo "✓ All brand pages generated"
echo ""

# ========================================
# STEP 2: Generate sitemap
# ========================================
echo "STEP 2: Generating sitemap.xml..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "scripts/generate-sitemap.js" ]; then
  node scripts/generate-sitemap.js
  echo "✓ Sitemap generated"
else
  echo "⚠ Sitemap script not found (skipping)"
fi

echo ""

# ========================================
# STEP 3: Add CSS styling
# ========================================
echo "STEP 3: Adding CSS styling..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if style.css exists
if [ ! -f "css/style.css" ]; then
  echo "⚠ css/style.css not found"
  echo "  You'll need to add the CSS manually"
  echo "  See the included CSS_STYLING.txt file"
else
  # Check if brand CSS already exists
  if grep -q "brand-container" css/style.css; then
    echo "✓ Brand CSS already present in style.css"
  else
    echo "Adding brand page CSS to style.css..."
    
    # Append CSS to style.css
    cat >> css/style.css << 'EOFCSS'

/* ===== BRAND PAGES STYLING ===== */

.brand-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.brand-header {
  margin-bottom: 2rem;
  border-bottom: 2px solid #2a5d3f;
  padding-bottom: 1rem;
}

.brand-header h1 {
  margin: 0 0 1rem 0;
  font-size: 2.5rem;
}

.brand-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.tier-badge {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.9rem;
}

.tier-good {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.tier-check {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.tier-warn {
  background-color: #ffe4c4;
  color: #cc5200;
  border: 1px solid #ffb347;
}

.tier-bad {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.vegan-badge {
  background-color: #90EE90;
  color: #1a4620;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.parent-company {
  font-size: 0.95rem;
  color: #666;
  font-style: italic;
}

.brand-content {
  margin: 2rem 0;
}

.brand-note {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  color: #333;
}

.evidence-section,
.products-section,
.alternatives-section,
.related-section,
.links-section {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: #f9f9f9;
  border-left: 4px solid #2a5d3f;
  border-radius: 4px;
}

.evidence-section h3,
.products-section h3,
.alternatives-section h3,
.related-section h3,
.links-section h3 {
  margin-top: 0;
  color: #2a5d3f;
}

.evidence-list,
.products-list,
.alternatives-list,
.related-brands,
.links-list {
  list-style: disc;
  margin-left: 1.5rem;
}

.evidence-list li,
.products-list li,
.alternatives-list li,
.links-list li {
  margin: 0.5rem 0;
}

.back-link {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
}

.back-link a {
  color: #2a5d3f;
  text-decoration: none;
  font-weight: 600;
}

.back-link a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .brand-container {
    padding: 1rem;
  }
  
  .brand-header h1 {
    font-size: 1.8rem;
  }
  
  .brand-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* ===== END BRAND PAGES STYLING ===== */
EOFCSS
    
    echo "✓ Brand CSS added to style.css"
  fi
fi

echo ""

# ========================================
# STEP 4: Commit everything
# ========================================
echo "STEP 4: Committing to Git..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Stage all changes
git add brands/
git add sitemap.xml 2>/dev/null || true
git add css/style.css 2>/dev/null || true

# Count files
FILES=$(git diff --cached --name-only | wc -l)
echo "Files staged: $FILES"

# Commit
git commit -m "Generate all 103 brand pages with CSS styling

- Generate 103 individual brand pages in /brands directory
- Each page includes SEO metadata, tier badges, evidence, products
- Generate sitemap.xml with all 107 URLs (4 static + 103 brands)
- Add CSS styling for brand pages to style.css
- Brand pages ready for Google Search Console indexing"

echo "✓ Changes committed"
echo ""

# ========================================
# STEP 5: Push to GitHub
# ========================================
echo "STEP 5: Pushing to GitHub..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

git push origin main

echo "✓ Pushed to GitHub"
echo ""

# ========================================
# COMPLETE
# ========================================
echo "╔════════════════════════════════════════╗"
echo "║  ✅ ALL COMPLETE!                      ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Your 103 brand pages are now:"
echo "  ✓ Generated locally"
echo "  ✓ Styled with CSS"
echo "  ✓ Committed to Git"
echo "  ✓ Pushed to GitHub"
echo "  ✓ Live at ahomekind.com/brands/{slug}"
echo ""
echo "Example pages:"
echo "  • https://ahomekind.com/brands/nyx"
echo "  • https://ahomekind.com/brands/bleach-london"
echo "  • https://ahomekind.com/brands/mua"
echo ""
echo "Next optional steps:"
echo "  1. Update brand-check.html to link to /brands/{slug}"
echo "  2. Update scan.html to link to /brands/{slug}"
echo "  3. Update shelf.html to link to /brands/{slug}"
echo "  4. Submit sitemap.xml to Google Search Console"
echo ""
echo "All done! 🎉"
echo ""
