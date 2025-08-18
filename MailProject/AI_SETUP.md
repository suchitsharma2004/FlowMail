# AI Draft Assistant Setup Guide

## Getting Your Gemini API Key

1. **Visit Google AI Studio**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Copy the generated API key

3. **Configure the Application**
   - Copy `.env.example` to `.env`: `cp .env.example .env`
   - Open the `.env` file
   - Replace `your_gemini_api_key_here` with your actual API key
   - Example: `GEMINI_API_KEY=AIzaSyD...your_actual_key_here`

4. **Restart the Server**
   - Stop the Django server (Ctrl+C)
   - Start it again: `python3 manage.py runserver`

## How to Use AI Draft Assistant

1. **Navigate to Compose**
   - Go to the compose page in your mail app

2. **Use the AI Assistant**
   - You'll see an "AI Draft Assistant" section at the top
   - Enter a description of what you want to write
   - Click "Generate Draft"
   - The AI will populate the subject and body fields

3. **Example Prompts**
   - "Write a professional email to request a project update meeting for next week"
   - "Create a follow-up email about the quarterly report deadline"
   - "Draft an email to introduce a new team member to the project"
   - "Write a thank you email for completing a project milestone"

## Features

- ✅ AI-powered content generation using Google's Gemini model
- ✅ Professional email formatting
- ✅ Automatic subject line generation
- ✅ Contextual content based on your prompts
- ✅ Toggle-able AI section to save space
- ✅ Error handling and user feedback
- ✅ Clear and regenerate options

## Tips

- Be specific in your prompts for better results
- The AI generates professional, business-appropriate content
- You can edit the generated content before sending
- The AI section can be collapsed to save screen space

## Troubleshooting

- **"API key not configured"**: Make sure you've added your Gemini API key to settings.py
- **"Failed to generate"**: Check your internet connection and API key validity
- **Empty response**: Try rephrasing your prompt or being more specific
