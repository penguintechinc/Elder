# Website Integration Requirements

## Overview

Each project MUST have two dedicated websites:
- Marketing/Sales website (Node.js based)
- Documentation website (Markdown based)

## Website Design Preferences

- **Multi-page design preferred** - avoid single-page applications for marketing sites
- **Modern aesthetic** with clean, professional appearance
- **Not overly bright** - use subtle, sophisticated color schemes
- **Gradient usage encouraged** - subtle gradients for visual depth and modern appeal
- **Responsive design** - must work seamlessly across all device sizes
- **Performance focused** - fast loading times and optimized assets

## Web Application UI/UX Principles

### Modal-First Approach
- Prefer modals over dedicated routes for secondary actions
- Minimize navigation disruption - keep users focused on main pages
- Inline editing when possible - allow editing without leaving the current context
- Progressive disclosure - reveal complexity only when needed
- Contextual actions - actions should be available where they're needed
- Consistent patterns - use the same UI patterns throughout the application

### Clickable Cards Pattern
Cards displaying objects (identities, entities, organizations, issues, etc.) should be clickable:
- Clicking anywhere on the card (outside of action buttons) should open the detail view modal
- Add hover effects (e.g., `hover:border-primary-500/50`) and cursor pointer to indicate interactivity
- Action buttons (View, Edit, Delete) should stop event propagation to prevent double-triggering
- This pattern applies to ALL pages displaying object cards in Elder

### When to Use Modals
- Create operations (creating sub-organizations, entities, issues, etc.)
- Edit operations (updating metadata, editing properties)
- Quick views (previewing details without full navigation)
- Confirmations and deletions

### When to Use Dedicated Routes
- Primary entity views (organization detail, entity detail, issue detail)
- List pages (organizations list, entities list, issues list)
- Complex multi-step workflows that require dedicated space

## Website Repository Integration

Add `github.com/penguintechinc/website` as a sparse checkout submodule. Only include the project's specific website folders.

### Folder Naming Convention
- `{app_name}/` - Marketing and sales website
- `{app_name}-docs/` - Documentation website

### Sparse Submodule Setup

```bash
# First, check if folders exist in the website repo and create if needed
git clone https://github.com/penguintechinc/website.git temp-website
cd temp-website

# Create project folders if they don't exist
mkdir -p {app_name}/
mkdir -p {app_name}-docs/

# Create initial template files if folders are empty
if [ ! -f {app_name}/package.json ]; then
  # Initialize Node.js marketing website
  echo "Creating initial marketing website structure..."
  # Add basic package.json, index.js, etc.
fi

if [ ! -f {app_name}-docs/README.md ]; then
  # Initialize documentation website
  echo "Creating initial docs website structure..."
  # Add basic markdown structure
fi

# Commit and push if changes were made
git add .
git commit -m "Initialize website folders for {app_name}"
git push origin main
cd .. && rm -rf temp-website

# Now add sparse submodule for website integration
git submodule add --name websites https://github.com/penguintechinc/website.git websites
git config -f .gitmodules submodule.websites.sparse-checkout true

# Configure sparse checkout to only include project folders
echo "{app_name}/" > .git/modules/websites/info/sparse-checkout
echo "{app_name}-docs/" >> .git/modules/websites/info/sparse-checkout

# Initialize sparse checkout
git submodule update --init websites
```

## Maintenance

- Both websites must be kept current with project releases and feature updates
- If project folders don't exist in the website repo, they must be created and initialized with basic templates before setting up the sparse submodule
