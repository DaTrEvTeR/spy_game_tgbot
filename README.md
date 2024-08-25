# Telegram Spy Game Bot

## Description

This Telegram bot allows users to play the game "Spy" directly in a group chat.  
The game requires a minimum of 4 players.  
One or more players are assigned the role of "Spy," while the others are "Informed".  
The game proceeds in rounds where players ask each other questions to identify the Spy.  
The bot manages the entire game process, from player joining to determining the winner.

## How to Install and Run

1. Clone the Repository:

   ```shell
   git clone https://github.com/yourusername/telegram-spy-game-bot.git
   cd telegram-spy-game-bot
   ```

2. Rename ".env.example" to ".env" and replace "yourapikey" with your API key from BotFather:

   ```
   BOT_API_KEY=yourapikey
   ```

3. Use fololowing command to run app with docker:

   ```shell
   make d-run
   ```

4. Purge all data after you finish using the app.:

   ```shell
   make d-purge
   ```

## Developer Setup

1. Fork and Clone the Repository:

   ```shell
   git clone https://github.com/yourusername/telegram-spy-game-bot.git
   cd telegram-spy-game-bot
   ```

2. Create a Virtual Environment and Install Dependencies:

   ```shell
   make init-dev
   ```

3. Code and Contribute:

- Implement new features or fix bugs.
- Write tests for new functionality.
- Submit a pull request when ready.

## Dependencies

**Python** version 3.12
