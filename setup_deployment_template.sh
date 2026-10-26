#!/usr/bin/env bash
# UNIVERSAL DEPLOYMENT TEMPLATE
# Sets up Git + Vercel for any build (Obsidian vaults, HTML sites, etc.)

set -euo pipefail

PROJECT_NAME="${1:-my-project}"
PROJECT_DIR="$HOME/$PROJECT_NAME"

echo "=========================================================="
echo "[*] CREATING DEPLOYMENT TEMPLATE: $PROJECT_NAME"
echo "=========================================================="

# 1. CREATE PROJECT STRUCTURE
mkdir -p "$PROJECT_DIR"/{src,public,docs}
cd "$PROJECT_DIR"

# 2. INITIALIZE GIT
git init -b main

# 3. CREATE .gitignore
cat > .gitignore << 'GITIGNORE'
# Dependencies
node_modules/
.pnp
.pnp.js

# Build outputs
dist/
build/
.next/
.vercel/
out/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
GITIGNORE

# 4. CREATE VERCEL CONFIGURATION
cat > vercel.json << 'VERCEL'
{
  "version": 2,
  "builds": [
    {
      "src": "public/**",
      "use": "@vercel/static"
    },
    {
      "src": "docs/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/public/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
VERCEL

# 5. CREATE README
cat > README.md << README
# $PROJECT_NAME

Deployed with Vercel.

## Development

\`\`\`bash
# Install Vercel CLI
npm i -g vercel

# Deploy to production
vercel --prod
\`\`\`

## Structure

- \`public/\` - Static HTML/CSS/JS files
- \`docs/\` - Documentation and Markdown
- \`src/\` - Source code (if applicable)
README

# 6. CREATE SAMPLE INDEX.HTML
mkdir -p public
cat > public/index.html << 'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
    </style>
</head>
<body>
    <h1>Deployment Template Active</h1>
    <p>Replace this file with your build.</p>
</body>
</html>
HTML

# 7. CREATE DEPLOYMENT SCRIPT
cat > deploy.sh << 'DEPLOY'
#!/usr/bin/env bash
set -euo pipefail

echo "[*] Deploying to Vercel..."

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "[!] Installing Vercel CLI..."
    npm i -g vercel
fi

# Deploy
if [ "${1:-}" = "--prod" ]; then
    vercel --prod
else
    vercel
fi

echo "[✓] Deployment complete!"
DEPLOY

chmod +x deploy.sh

# 8. GIT COMMIT
git add .
git commit -m "Initial deployment template setup"

cat << INFO

==========================================================
[✓] DEPLOYMENT TEMPLATE CREATED
==========================================================
Location: $PROJECT_DIR

STRUCTURE:
  $PROJECT_NAME/
  ├── public/          (Your HTML/CSS/JS files go here)
  ├── docs/            (Markdown documentation)
  ├── src/             (Source code if needed)
  ├── vercel.json      (Vercel configuration)
  ├── deploy.sh        (One-command deployment script)
  └── README.md

DEPLOYMENT COMMANDS:
  cd $PROJECT_DIR
  
  # Preview deployment (creates unique URL)
  ./deploy.sh
  
  # Production deployment
  ./deploy.sh --prod

FIRST TIME SETUP:
  1. Run: vercel login
  2. Run: ./deploy.sh
  3. Follow prompts to link to your Vercel account

==========================================================
INFO

