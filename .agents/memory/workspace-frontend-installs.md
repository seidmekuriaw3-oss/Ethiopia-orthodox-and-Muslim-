---
name: Workspace frontend installs
description: Replit workspace behavior when artifact node_modules are missing but dependencies are already declared.
---

When a workspace artifact reports a missing executable such as `vite` while its package.json and lockfile already declare the dependency, use the workspace package manager's install operation rather than adding the dependency again.

**Why:** The managed package installer may translate an install request into `pnpm add` at the workspace root, which is rejected by pnpm's workspace-root safety check and does not repair the artifact's missing node_modules.

**How to apply:** Run the lockfile-respecting workspace install, then restart the affected artifact workflow and verify its typecheck or dev server. Do not bump versions unless the lockfile actually lacks the package.