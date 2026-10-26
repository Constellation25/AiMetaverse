#!/usr/bin/env bash
# VERCEL DEPLOYMENT MANAGER
# Links existing Vercel projects to local Git repos and manages deployments

set -euo pipefail

ACTION="${1:-list}"
PROJECT_NAME="${2:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}[!] Vercel CLI not found. Installing...${NC}"
    npm i -g vercel
fi

# Check if logged in
if ! vercel whoami &> /dev/null; then
    echo -e "${RED}[!] Not logged in to Vercel. Run: vercel login${NC}"
    exit 1
fi

case "$ACTION" in
    list)
        echo "=========================================================="
        echo -e "${GREEN}[*] YOUR VERCEL PROJECTS${NC}"
        echo "=========================================================="
        vercel ls
        echo ""
        echo "USAGE:"
        echo "  Link a project:  ./vercel_deploy_manager.sh link <project-name>"
        echo "  Deploy:          ./vercel_deploy_manager.sh deploy [--prod]"
        echo "  Status:          ./vercel_deploy_manager.sh status"
        ;;
        
    link)
        if [[ -z "$PROJECT_NAME" ]]; then
            echo -e "${RED}[!] Project name required${NC}"
            echo "Usage: ./vercel_deploy_manager.sh link <project-name>"
            exit 1
        fi
        
        echo "[*] Linking current directory to Vercel project: $PROJECT_NAME"
        
        # Remove existing link if present
        rm -f .vercel/project.json 2>/dev/null || true
        
        # Link to the project
        vercel link --yes --project "$PROJECT_NAME"
        
        # Verify link
        if [[ -f .vercel/project.json ]]; then
            echo -e "${GREEN}[✓] Successfully linked to $PROJECT_NAME${NC}"
            
            # Add .vercel to .gitignore if not present
            if ! grep -q "\.vercel" .gitignore 2>/dev/null; then
                echo ".vercel/" >> .gitignore
                echo "[+] Added .vercel/ to .gitignore"
            fi
            
            # Create deployment validation hook
            mkdir -p .git/hooks
            cat > .git/hooks/pre-push << 'HOOK'
#!/usr/bin/env bash
# Validates Vercel link before pushing

if [[ ! -f .vercel/project.json ]]; then
    echo "ERROR: No Vercel project link found!"
    echo "Run: ./vercel_deploy_manager.sh link <project-name>"
    exit 1
fi

echo "✓ Vercel link verified"
HOOK
            chmod +x .git/hooks/pre-push
            echo "[+] Git pre-push hook installed (validates link before push)"
        else
            echo -e "${RED}[!] Link failed${NC}"
            exit 1
        fi
        ;;
        
    deploy)
        PROD_FLAG=""
        if [[ "${2:-}" == "--prod" ]]; then
            PROD_FLAG="--prod"
        fi
        
        # Check if linked
        if [[ ! -f .vercel/project.json ]]; then
            echo -e "${RED}[!] No Vercel project link found${NC}"
            echo "Run: ./vercel_deploy_manager.sh link <project-name>"
            exit 1
        fi
        
        # Show linked project
        PROJECT_ID=$(cat .vercel/project.json | grep -o '"projectId":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}[*] Deploying to linked project: $PROJECT_ID${NC}"
        
        # Deploy
        vercel $PROD_FLAG
        
        echo -e "${GREEN}[✓] Deployment complete${NC}"
        ;;
        
    status)
        echo "=========================================================="
        echo -e "${GREEN}[*] DEPLOYMENT STATUS${NC}"
        echo "=========================================================="
        
        # Check Git status
        if [[ -d .git ]]; then
            echo "Git Status:"
            git status --short || echo "  No changes"
            echo ""
        fi
        
        # Check Vercel link
        if [[ -f .vercel/project.json ]]; then
            echo -e "${GREEN}Vercel Link: ✓ Active${NC}"
            PROJECT_ID=$(cat .vercel/project.json | grep -o '"projectId":"[^"]*"' | cut -d'"' -f4)
            echo "  Project ID: $PROJECT_ID"
        else
            echo -e "${RED}Vercel Link: ✗ Not linked${NC}"
            echo "  Run: ./vercel_deploy_manager.sh link <project-name>"
        fi
        
        echo ""
        echo "Recent Deployments:"
        vercel ls 2>/dev/null | head -n 10 || echo "  No deployments found"
        ;;
        
    *)
        echo "Usage: ./vercel_deploy_manager.sh [list|link|deploy|status] [project-name|--prod]"
        ;;
esac

