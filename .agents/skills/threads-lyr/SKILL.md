---
name: threads-lyr
description: Threads.net automation with profile access and posts. Use this skill whenever the user requests Threads operations, social media posting, content creation, or any Threads-related tasks. Triggers on phrases like "threads post", "threads profile", "threads search", "threads automation", "social media posting", "content creation", "get threads profile", "search threads", or any request for Threads functionality.
---

# Threads-lyr Skill

This skill enables AI agents to interact with Threads.net using the threads-lyr CLI tool. It provides comprehensive Threads automation including profile access and posts.

## Prerequisites

- threads-lyr CLI must be installed globally on the system
- The CLI must be accessible in the system PATH
- No authentication required (public profiles only)

## Command Structure

### Available Commands

```bash
# Session management
threads-lyr                          # Start MCP server
threads-lyr --list-tools             # List available MCP tools

# Content commands
threads-lyr get_threads_profile --username zuck
threads-lyr get_threads_posts --username zuck --limit 10
```

## MCP Tool Usage

The threads-lyr CLI serves as an MCP server with the following tools:

- `get_threads_profile` - Get a Threads user's profile
- `get_threads_posts` - Get a Threads user's posts

## MCP Configuration

```json
{
  "mcpServers": {
    "threads": {
      "command": "uvx",
      "args": ["threads-lyr"]
    }
  }
}
```

## Workflow

### Step 1: Analyze User Request
- Determine the type of Threads operation needed (profile, posts)
- Select appropriate command based on user intent

### Step 2: Generate Command
- Use the command structure above to build the appropriate CLI command
- Add relevant flags for limits and output format
- Include any required parameters (usernames, etc.)

### Step 3: Execute and Validate
- Run the command using shell execution
- Check for successful completion
- Parse the output in the appropriate format
- Report the result to the user

### Step 4: Handle Errors
- If command not found: suggest installing threads-lyr
- If invalid parameters: provide correct usage examples
- If profile not found: suggest verifying the username

## Error Handling

### Common Issues and Solutions

1. **Command not found**
   - Error: "threads-lyr: command not found"
   - Solution: Install threads-lyr globally or add to PATH

2. **Invalid parameters**
   - Error: "Invalid username"
   - Solution: Verify the Threads username is correct

3. **Profile not found**
   - Error: "Profile not found"
   - Solution: The Threads username may not exist or be private

## Integration Example

### User Request: "Get Mark Zuckerberg's Threads profile"

**Skill Processing:**
1. Identify as a profile operation
2. Generate command: `threads-lyr get_threads_profile --username zuck`
3. Execute and parse results
4. Report profile to user

### User Request: "Get Mark Zuckerberg's recent Threads posts"

**Skill Processing:**
1. Identify as a posts operation
2. Generate command: `threads-lyr get_threads_posts --username zuck --limit 10`
3. Execute and format results
4. Report posts to user

## Best Practices

1. **Use reasonable limits** when browsing to avoid overwhelming results
2. **Verify usernames** before accessing profiles to ensure they exist
3. **Handle errors with actionable suggestions** for resolution
4. **Provide context in results** when returning content data (author, timestamp, metrics)
5. **Remember this is read-only** - no posting or engagement features available