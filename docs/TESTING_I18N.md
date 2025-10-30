# Testing Multilingual Documentation

This guide provides comprehensive instructions for testing the mkdocs-static-i18n multilingual documentation implementation for d-back.

## Prerequisites

Before testing, ensure the following are installed:

1. **Install mkdocs-static-i18n**:
   ```bash
   pip install -e .[docs]
   ```

2. **Verify installation**:
   ```bash
   pip list | grep mkdocs-static-i18n
   ```

   You should see output similar to:
   ```
   mkdocs-static-i18n    1.2.0
   ```

## Local Testing

### 1. Serve Documentation Locally

Start the MkDocs development server:

```bash
mkdocs serve
```

**Expected Output:**
```
INFO     -  Building documentation...
INFO     -  [i18n] enabling 3 language(s): ['en', 'es', 'de']
INFO     -  [i18n] default/main language: en
INFO     -  Cleaning site directory
INFO     -  Documentation built in 2.34 seconds
INFO     -  [00:00:00] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO     -  [00:00:00] Serving on http://127.0.0.1:8000/
```

**Expected Behavior:**
- Server starts on `http://127.0.0.1:8000/`
- Default language (English) loads
- Language selector appears in the top navigation bar (Material theme header)

### 2. Test Language Switching

In your browser, navigate to `http://127.0.0.1:8000/`:

1. **Locate the language selector** in the top navigation bar (next to the search icon)
2. **Click the language selector dropdown**
3. **Select "Español"**:
   - URL should change to `/es/`
   - Page content should be in Spanish
   - Navigation items should be translated (e.g., "Inicio", "Primeros Pasos")
4. **Select "Deutsch"**:
   - URL should change to `/de/`
   - Page content should be in German
   - Navigation items should be translated (e.g., "Startseite", "Erste Schritte")
5. **Select "English"**:
   - URL should return to `/`
   - Page content should be in English

**What to Check:**
- ✅ Navigation items are properly translated
- ✅ Page content matches the selected language
- ✅ Code examples remain in English (universal)
- ✅ Links work correctly across language versions
- ✅ No broken links or 404 errors

### 3. Test Fallback Behavior

The configuration includes `fallback_to_default: true`, which means:

- If a translation file is missing, the English version will be displayed
- The language selector should still work
- No errors should occur

To test this (optional):
1. Temporarily rename a translation file (e.g., `getting-started.es.md` → `getting-started.es.md.bak`)
2. Reload the Spanish version
3. The English content should display
4. Restore the file after testing

### 4. Test All Pages

Navigate through all documentation pages in each language:

**English (`/`):**
- Home (`/`)
- Getting Started (`/getting-started/`)
- User Guide (`/user-guide/`)
  - Overview (`/user-guide/`)
  - Configuration (`/user-guide/configuration/`)
  - Callbacks & Customization (`/user-guide/callbacks/`)
  - Custom Data Providers (`/user-guide/custom-data-providers/`)
- API Reference (`/api-reference/`)
- Developer Guide (`/developer-guide/`)

**Spanish (`/es/`):**
- Inicio (`/es/`)
- Primeros Pasos (`/es/getting-started/`)
- Guía del Usuario (`/es/user-guide/`)
  - Resumen (`/es/user-guide/`)
  - Configuración (`/es/user-guide/configuration/`)
  - Callbacks y Personalización (`/es/user-guide/callbacks/`)
  - Proveedores de Datos Personalizados (`/es/user-guide/custom-data-providers/`)
- Referencia de API (`/es/api-reference/`)
- Guía del Desarrollador (`/es/developer-guide/`)

**German (`/de/`):**
- Startseite (`/de/`)
- Erste Schritte (`/de/getting-started/`)
- Benutzerhandbuch (`/de/user-guide/`)
  - Übersicht (`/de/user-guide/`)
  - Konfiguration (`/de/user-guide/configuration/`)
  - Callbacks & Anpassung (`/de/user-guide/callbacks/`)
  - Benutzerdefinierte Datenanbieter (`/de/user-guide/custom-data-providers/`)
- API-Referenz (`/de/api-reference/`)
- Entwicklerhandbuch (`/de/developer-guide/`)

## Build Testing

### 1. Build All Languages

Build the complete documentation site:

```bash
mkdocs build
```

**Expected Output:**
```
INFO     -  Cleaning site directory
INFO     -  Building documentation to directory: /path/to/d-back/site
INFO     -  [i18n] enabling 3 language(s): ['en', 'es', 'de']
INFO     -  [i18n] default/main language: en
INFO     -  [i18n] building site for 'en' to 'site/'
INFO     -  [i18n] building site for 'es' to 'site/es'
INFO     -  [i18n] building site for 'de' to 'site/de'
INFO     -  Documentation built in 3.21 seconds
```

### 2. Verify Build Output

Check that all three language versions were built:

**Windows PowerShell:**
```powershell
Get-ChildItem site -Directory
```

**macOS/Linux:**
```bash
ls -la site/
```

**Expected Structure:**
```
site/
├── index.html             # English (default)
├── getting-started/
├── user-guide/
├── api-reference/
├── developer-guide/
├── es/                    # Spanish
│   ├── index.html
│   ├── getting-started/
│   ├── user-guide/
│   ├── api-reference/
│   └── developer-guide/
└── de/                    # German
    ├── index.html
    ├── getting-started/
    ├── user-guide/
    ├── api-reference/
    └── developer-guide/
```

### 3. Verify HTML Language Links

Check that alternate language links are present in the HTML:

**Check English page:**
```bash
grep -A 5 '<link rel="alternate"' site/index.html
```

**Expected Result:**
```html
<link rel="alternate" hreflang="en" href="/d-back/" />
<link rel="alternate" hreflang="es" href="/d-back/es/" />
<link rel="alternate" hreflang="de" href="/d-back/de/" />
```

### 4. Serve Built Site

Test the built site locally:

**Windows PowerShell:**
```powershell
python -m http.server 8000 --directory site
```

**macOS/Linux:**
```bash
cd site && python -m http.server 8000
```

Navigate to `http://localhost:8000` and test language switching as before.

## Validation Checklist

Use this checklist to validate the implementation:

- [ ] **Language selector appears** in the navigation bar
- [ ] **All three languages selectable** (English, Español, Deutsch)
- [ ] **Navigation items translated correctly** according to `nav_translations` in `mkdocs.yml`
- [ ] **Page content is translated** (except code examples)
- [ ] **Code examples remain in English** (universal programming language)
- [ ] **Links work across languages** (relative links resolve correctly)
- [ ] **Search works in each language** (Material theme search)
- [ ] **Fallback to English works** for missing translations
- [ ] **No console errors** in browser developer tools
- [ ] **Material theme features work** in all languages (navigation, search, dark mode)
- [ ] **Build completes successfully** without errors or warnings
- [ ] **All three language directories exist** in `site/` after build
- [ ] **Alternate language links present** in HTML `<head>` tags

## Common Issues and Solutions

### Issue: Language Selector Not Appearing

**Symptoms:** Language selector is missing from the navigation bar

**Solutions:**
1. Verify `reconfigure_material: true` is set in `mkdocs.yml`:
   ```yaml
   plugins:
     - i18n:
         reconfigure_material: true
   ```
2. Check that `navigation.instant` feature is NOT enabled in theme features (it conflicts with language switcher)
3. Clear browser cache and reload: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (macOS)
4. Rebuild with clean: `mkdocs build --clean`

### Issue: Translations Not Loading

**Symptoms:** Clicking language selector doesn't change content, or shows 404 errors

**Solutions:**
1. Verify file naming follows suffix pattern: `index.es.md`, `index.de.md` (not folder structure)
2. Check that files are in the correct directory (`docs/`, not `docs/es/` or `docs/de/`)
3. Verify file extensions are `.md` not `.markdown`
4. Rebuild: `mkdocs build --clean`
5. Check MkDocs console output for build warnings

### Issue: Navigation Not Translated

**Symptoms:** Navigation items remain in English in translated versions

**Solutions:**
1. Verify `nav_translations` are correctly defined in `mkdocs.yml` for both `es` and `de`
2. Check that navigation item names in `nav_translations` match EXACTLY the names in the `nav` section
3. Verify YAML indentation is correct (use spaces, not tabs)
4. Rebuild and check console output for warnings

### Issue: Search Not Working in Translated Versions

**Symptoms:** Search returns no results or only English results in Spanish/German versions

**Solutions:**
1. Verify `reconfigure_search: true` is set in `mkdocs.yml`:
   ```yaml
   plugins:
     - i18n:
         reconfigure_search: true
   ```
2. Check that `search` plugin is listed BEFORE `i18n` plugin in `plugins` list
3. Rebuild with clean: `mkdocs build --clean`

### Issue: Build Errors

**Symptoms:** `mkdocs build` fails with errors

**Solutions:**
1. Check MkDocs version: `mkdocs --version` (should be 1.5.0+)
2. Check mkdocs-static-i18n version: `pip show mkdocs-static-i18n` (should be 1.2.0+)
3. Verify YAML syntax in `mkdocs.yml` is valid
4. Check for typos in language locales: must be `en`, `es`, `de` (not `en-US`, `es-ES`, etc.)
5. Reinstall dependencies: `pip install -e .[docs] --force-reinstall`

## Testing Commands Summary

```bash
# Install dependencies
pip install -e .[docs]

# Verify installation
pip list | grep mkdocs-static-i18n

# Serve locally with live reload
mkdocs serve

# Build all languages
mkdocs build

# Clean build (removes site/ directory first)
mkdocs build --clean

# Serve built site
python -m http.server 8000 --directory site
```

## Next Steps

After successful local testing:

1. **Commit changes** to your feature branch
2. **Push to GitHub**
3. **Create Pull Request** for review
4. **GitHub Actions** (if configured) will automatically build and deploy to GitHub Pages
5. **Future phase**: Consider integrating Crowdin for community-driven translations
6. **Future phase**: Set up automated deployment workflow

## Additional Testing (Advanced)

### Test SEO and Alternate Links

Use browser developer tools to verify alternate language links:

1. Open browser developer tools (`F12`)
2. Navigate to the Elements/Inspector tab
3. Search for `<link rel="alternate"`
4. Verify all three languages are listed with correct `hreflang` and `href` attributes

### Test Search Functionality

1. In each language version, use the search bar
2. Search for a term that appears in documentation (e.g., "WebSocket", "server", "callback")
3. Verify search results are relevant and in the correct language
4. Verify search doesn't return duplicate results across languages

### Test Mobile Responsiveness

1. Open documentation in browser
2. Open developer tools (`F12`)
3. Toggle device toolbar (mobile view)
4. Test language selector on mobile devices
5. Verify navigation and content are properly responsive

## Reporting Issues

If you encounter issues during testing:

1. **Check this guide first** for solutions
2. **Review MkDocs console output** for error messages
3. **Check browser console** for JavaScript errors
4. **Create a GitHub Issue** with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Console output or error messages
   - Environment details (OS, Python version, MkDocs version)

## Conclusion

The multilingual documentation implementation is complete when:

- ✅ All pages exist in all three languages (English, Spanish, German)
- ✅ Language selector works correctly
- ✅ Navigation is properly translated
- ✅ Build completes without errors
- ✅ All validation checklist items are checked

Happy testing! 🚀
