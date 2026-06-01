# Task 3: Create project scaffolding

Set up all non-dataset files needed for the concept-browser build.

## Files to create
1. **`site-config.yml`** — adapted from oiml-viml, with:
   - id: `g18`
   - domain: `g18.oiml.info`
   - dataset: `g18`
   - Proper title/subtitle/description
   - Logo path, branding, features

2. **`package.json`** — minimal, with `npx concept-browser build` script

3. **`.gitignore`** — node_modules, public, dist, .datasets

4. **`about.md`** / **`about-fra.md`** — About page content from PDF foreword

5. **`logos/oiml-logo.svg`** — Copy from oiml-viml

6. **`.github/workflows/build_deploy.yml`** — CI/CD for GitHub Pages

## Dependencies
- None (can be done in parallel with Tasks 1-2)
