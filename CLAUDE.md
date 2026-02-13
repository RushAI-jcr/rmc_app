# Every Marketplace - Claude Code Plugin Marketplace

This repository is a Claude Code plugin marketplace that distributes the `compound-engineering` plugin to developers building with AI-powered tools.

## Repository Structure

```
every-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog (lists available plugins)
├── docs/                         # Documentation site (GitHub Pages)
│   ├── index.html                # Landing page
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript
│   └── pages/                     # Reference pages
└── plugins/
    └── compound-engineering/   # The actual plugin
        ├── .claude-plugin/
        │   └── plugin.json        # Plugin metadata
        ├── agents/                # 24 specialized AI agents
        ├── commands/              # 13 slash commands
        ├── skills/                # 11 skills
        ├── mcp-servers/           # 2 MCP servers (playwright, context7)
        ├── README.md              # Plugin documentation
        └── CHANGELOG.md           # Version history
```

## Philosophy: Compounding Engineering

**Each unit of engineering work should make subsequent units of work easier--not harder.**

When working on this repository, follow the compounding engineering process:

1. **Plan** -> Understand the change needed and its impact
2. **Delegate** -> Use AI tools to help with implementation
3. **Assess** -> Verify changes work as expected
4. **Codify** -> Update this CLAUDE.md with learnings

## Working with This Repository


### Install this marketplace in Claude Code (local)

Use this repo as the plugin marketplace so Claude Code loads plugins from your local copy:

```bash
# Add this repo as the marketplace (use the absolute path to rmc_every)
claude /plugin marketplace add /Users/JCR/Desktop/rmc_every

# Install the compound-engineering plugin
claude /plugin install compound-engineering

# Verify
claude /plugin list
```

Replace `/Users/JCR/Desktop/rmc_every` with your actual path to this repo if different. To use the upstream marketplace from GitHub instead of this local copy, run `claude /plugin marketplace add https://github.com/EveryInc/compound-engineering-plugin` then `claude /plugin install compound-engineering`. After installation you can use compound-engineering agents and commands (e.g. `claude /review`, `claude agent kieran-rails-reviewer "..."`).

### Adding a New Plugin

1. Create plugin directory: `plugins/new-plugin-name/`
2. Add plugin structure:
   ```
   plugins/new-plugin-name/
   ├── .claude-plugin/plugin.json
   ├── agents/
   ├── commands/
   └── README.md
   ```
3. Update `.claude-plugin/marketplace.json` to include the new plugin
4. Test locally before committing

### Updating the Compounding Engineering Plugin

When agents, commands, or skills are added/removed, follow this checklist:

#### 1. Count all components accurately

```bash
# Count agents
ls plugins/compound-engineering/agents/*.md | wc -l

# Count commands
ls plugins/compound-engineering/commands/*.md | wc -l

# Count skills
ls -d plugins/compound-engineering/skills/*/ 2>/dev/null | wc -l
```

#### 2. Update ALL description strings with correct counts

The description appears in multiple places and must match everywhere:

- [ ] `plugins/compound-engineering/.claude-plugin/plugin.json` -> `description` field
- [ ] `.claude-plugin/marketplace.json` -> plugin `description` field
- [ ] `plugins/compound-engineering/README.md` -> intro paragraph

Format: `"Includes X specialized agents, Y commands, and Z skill(s)."`

#### 3. Update version numbers

When adding new functionality, bump the version in:

- [ ] `plugins/compound-engineering/.claude-plugin/plugin.json` -> `version`
- [ ] `.claude-plugin/marketplace.json` -> plugin `version`

#### 4. Update documentation

- [ ] `plugins/compound-engineering/README.md` -> list all components
- [ ] `plugins/compound-engineering/CHANGELOG.md` -> document changes
- [ ] `CLAUDE.md` -> update structure diagram if needed

#### 5. Rebuild documentation site

Run the release-docs command to update all documentation pages:

```bash
claude /release-docs
```

#### 6. Validate JSON files

```bash
cat .claude-plugin/marketplace.json | jq .
cat plugins/compound-engineering/.claude-plugin/plugin.json | jq .
```

#### 7. Verify before committing

```bash
# Ensure counts in descriptions match actual files
grep -o "Includes [0-9]* specialized agents" plugins/compound-engineering/.claude-plugin/plugin.json
ls plugins/compound-engineering/agents/*.md | wc -l
```

### Marketplace.json Structure

The marketplace.json follows the official Claude Code spec:

```json
{
  "name": "marketplace-identifier",
  "owner": {
    "name": "Owner Name",
    "url": "https://github.com/owner"
  },
  "metadata": {
    "description": "Marketplace description",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "Plugin description",
      "version": "1.0.0",
      "author": { ... },
      "homepage": "https://...",
      "tags": ["tag1", "tag2"],
      "source": "./plugins/plugin-name"
    }
  ]
}
```

**Only include fields that are in the official spec.** Do not add custom fields like:

- `downloads`, `stars`, `rating` (display-only)
- `categories`, `featured_plugins`, `trending` (not in spec)
- `type`, `verified`, `featured` (not in spec)

### Plugin.json Structure

Each plugin has its own plugin.json with detailed metadata:

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": { ... },
  "keywords": ["keyword1", "keyword2"],
  "components": {
    "agents": 15,
    "commands": 6,
    "hooks": 2
  },
  "agents": {
    "category": [
      {
        "name": "agent-name",
        "description": "Agent description",
        "use_cases": ["use-case-1", "use-case-2"]
      }
    ]
  },
  "commands": {
    "category": ["command1", "command2"]
  }
}
```

## Documentation Site

The documentation site is at `/docs` in the repository root (for GitHub Pages). This site is built with plain HTML/CSS/JS (based on Evil Martians' LaunchKit template) and requires no build step to view.

### Keeping Docs Up-to-Date

**IMPORTANT:** After ANY change to agents, commands, skills, or MCP servers, run:

```bash
claude /release-docs
```

## Testing Changes

### Validate JSON

Before committing, ensure JSON files are valid:

```bash
cat .claude-plugin/marketplace.json | jq .
cat plugins/compound-engineering/.claude-plugin/plugin.json | jq .
```

## Common Tasks

### Adding a New Agent

1. Create `plugins/compound-engineering/agents/new-agent.md`
2. Update plugin.json agent count and agent list
3. Update README.md agent list
4. Test with `claude agent new-agent "test"`

### Adding a New Command

1. Create `plugins/compound-engineering/commands/new-command.md`
2. Update plugin.json command count and command list
3. Update README.md command list
4. Test with `claude /new-command`

### Adding a New Skill

1. Create skill directory: `plugins/compound-engineering/skills/skill-name/`
2. Add skill structure:
   ```
   skills/skill-name/
   ├── SKILL.md           # Skill definition with frontmatter (name, description)
   └── scripts/           # Supporting scripts (optional)
   ```
3. Update plugin.json description with new skill count
4. Update marketplace.json description with new skill count
5. Update README.md with skill documentation
6. Update CHANGELOG.md with the addition
7. Test with `claude skill skill-name`

### Updating Tags/Keywords

Tags should reflect the compounding engineering philosophy:

- Use: `ai-powered`, `compound-engineering`, `workflow-automation`, `knowledge-management`
- Avoid: Framework-specific tags unless the plugin is framework-specific

## Commit Conventions

Follow these patterns for commit messages:

- `Add [agent/command name]` - Adding new functionality
- `Remove [agent/command name]` - Removing functionality
- `Update [file] to [what changed]` - Updating existing files
- `Fix [issue]` - Bug fixes
- `Simplify [component] to [improvement]` - Refactoring

Include the Claude Code footer:

```
Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Resources

- [Claude Code Plugin Documentation](https://docs.claude.com/en/docs/claude-code/plugins)
- [Plugin Marketplace Documentation](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference)

## Key Learnings

### 2024-11-22: Added gemini-imagegen skill and fixed component counts

Added the first skill to the plugin and discovered the component counts were wrong (said 15 agents, actually had 17). Created a comprehensive checklist for updating the plugin to prevent this in the future.

**Learning:** Always count actual files before updating descriptions. The counts appear in multiple places (plugin.json, marketplace.json, README.md) and must all match. Use the verification commands in the checklist above.

### 2024-10-09: Simplified marketplace.json to match official spec

The initial marketplace.json included many custom fields (downloads, stars, rating, categories, trending) that aren't part of the Claude Code specification. We simplified to only include:

- Required: `name`, `owner`, `plugins`
- Optional: `metadata` (with description and version)
- Plugin entries: `name`, `description`, `version`, `author`, `homepage`, `tags`, `source`

**Learning:** Stick to the official spec. Custom fields may confuse users or break compatibility with future versions.

---

## Agent Instructions (from AGENTS.md)

### Working Agreement

- **Branching:** Create a feature branch for any non-trivial change. If already on the correct branch for the task, keep using it; do not create additional branches or worktrees unless explicitly requested.
- **Safety:** Do not delete or overwrite user data. Avoid destructive commands.
- **Testing:** Run `bun test` after changes that affect parsing, conversion, or output.
- **Output Paths:** Keep OpenCode output at `opencode.json` and `.opencode/{agents,skills,plugins}`.
- **ASCII-first:** Use ASCII unless the file already contains Unicode.
