# Keycloak Configuration

## Security Notice

This directory contains Keycloak realm configuration files. For security reasons:

- **`realm-import.json.template`** - Template file committed to git with placeholders for secrets
- **`realm-import.json`** - Generated file with actual secrets (NOT committed to git)

## How it Works

1. The `realm-import.json.template` file contains placeholder values like `{{KEYCLOAK_CLIENT_SECRET}}`
2. When you run `./init-env.sh`, it generates the actual `realm-import.json` file by replacing placeholders with secure random values
3. The actual `realm-import.json` file is ignored by git to prevent committing secrets

## Template Placeholders

- `{{KEYCLOAK_CLIENT_SECRET}}` - Replaced with a secure 64-character random client secret

## Important

- Never edit `realm-import.json` directly - your changes will be lost when regenerating
- Always edit `realm-import.json.template` for configuration changes
- The `realm-import.json` file is automatically generated and should never be committed to version control

## Regenerating Configuration

If you need to regenerate the realm configuration with new secrets:

```bash
./init-env.sh
```

This will create a new `realm-import.json` file with fresh random secrets.