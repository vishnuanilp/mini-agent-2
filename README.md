# Mini Agent 2 — Content Generation Pipeline

## What It Does
A social media content generation agent that takes a business description and automatically creates promotional content through a multi-step AI pipeline.

## How It Works
The agent runs a 2-step pipeline:

1. **Step 1 — Research:** Claude analyzes the topic using XML-structured prompts and returns key facts
2. **Step 2 — Poster Generation:** Claude uses the research to generate poster designs, using tools and saving results to MongoDB

## Skills Used (Week 2)
- **Claude API** — Anthropic's Claude for AI responses
- **XML Tags** — `<task>`, `<rules>`, `<format>` to guide Claude at each step
- **Prompt Chaining** — Step 1 output feeds into Step 2
- **Tool Use** — Claude decides when to use poster_generator and save_to_notes tools
- **MongoDB** — Every step saved to database with timestamps
- **Error Handling** — try/except in all tool functions

## Tools
| Tool | What It Does |
|------|-------------|
| poster_generator | Generates a poster design based on a topic |
| save_to_notes | Saves content to MongoDB for future reference |

## Setup
1. Install dependencies:
   ```
   pip install anthropic pymongo python-dotenv
   ```
2. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
3. Make sure MongoDB is running locally on `mongodb://localhost:27017/`
4. Run:
   ```
   python mini_agent_2.py
   ```

## Built By
 Week 2 of the 4-Month AI Agent Mastery Plan
