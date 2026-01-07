# File Structure

## Core Files (5)

**assistant_with_projects.py** - Main assistant with AI chat, memory sculpting, project switching

**view_project_memory.py** - Display memory hierarchy (foundation → checkpoint → facts → state → outcomes)

**create_checkpoint.py** - Generate compressed project summary using LLM

**list_checkpoints.py** - Show all historical checkpoints for current project

**add_foundation.py** - Add immutable principles to sacred foundation (requires confirmation)

## Config

**requirements.txt** - Python dependencies (redis)

**README.md** - Setup and usage guide

**.project_info** - Auto-displayed help when cd into directory

## Folders

**venv/** - Python virtual environment

**archive/** - Old migration scripts (safe to delete)
