# Building assets

1. Install npm
2. Go to repondeur/zam_repondeur/static/
3. `npm install`
4. `npm run-script build`

At that point, a `manifest.json` should be generated,
ready to be consumed by the `ManifestCacheBuster` from Pyramid.
