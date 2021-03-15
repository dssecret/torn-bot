# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [Unreleased]
### Added
 - Access log to log unauthorized attempts to run commands
 - Code of Conduct
 - Version command
 - Secondary/child faction support
 - Setkey command to set secondary API key
 - On join event
 - One unified configuration command
 - Editable original message from the withdrawal command
 - ID storage with addid command
 - Auto-deletion of non-command messages in banking channel
 - Banking channel to config
 - Cooldown to most commands
 - Autodelete of balance commands
 - Autodelete of withdrawal commands
 - Discord logging (via logging module)
 - Added license command
 - Info command
 - Function to make API calls to Torn
 - Additional commands in the Torn cog (e.g. add key)
 - Discord User ID check in vault commands
 - Support for mil and bil in the text_to_num function
 - Fulfill command to indicate the fulfillment of a withdrawal request

## Changed
 - Withdrawal command to have a specific on reaction loop instead of a general loop
 - Help command to be paginated and to include bot commands
 - Withdrawal command to not use a loop (to prevent Discord disconnects from breaking reaction)

## Fixed
 - Lack of support of commas in text_to_num function

## Removed
 - Noob functions (and related variables and functions)
 - Superuser pull command
 - Superuser restart command
 - Reaction to fulfill withdrawal request

## [1.2]
### Added
 - Noob role for users under level 15
 - Purge command
 - Superuser shutdown and restart commands
 - Superuser check to admin commands
 - Setguild command
 - Balance as alias for full balance command
 - Automatic running of noob function every hour
 - Wait until bot is ready for noob function
 - Check to stop the runnoob command and noob function if the noob role has not been set
 - Noob status to enable or to disable the automatic noob function
 - Over15 key to config.ini
 - Message to runnoob command to indicate the end of function run
 - Log message for noob functions to log run time of functions
 - Requirement for version python 3.6 or greater
 - Configuration command that returns the current configuration
 - Random color to all embeds (issue #11)
 - Pull command to pull the latest commit (Untested)
### Changed
 - Readme's TODO updated
 - Balance command to bal
 - Bal command to b
 - Indentation on withdrawal command 
 - Automatic noob function to run every 12 hours from every hour
 - Automatic noob function and runnoob command to not check users in the list of users as value for over15 key in config.ini
 - String concatenation to string interpolation/f-strings
### Fixed
 - Issue #6
 - Issue #8
 - Some functions using "DEFAULTS" as a key instead of "DEFAULT"
 - Issue #10
 - Concatenation of Discord user and string

## [1.1] - 2021-01-07
### Added
 - Banker response to withdrawal request via emoji
 - Custom help command with important links
 - Changelog
 - Documentation on GitHub Wiki
 - Aliases for most commands
 - Prefix command that returns the prefix
 - Commas to full balance command (Issue #4)
### Changed
 - Input on first launch of bot to request Discord bot token
 - Setprefix to have a default parameter value of `?`
 - License from GNU GPLv3 to GNU APGLv3
 - Balance to have an exact and simplified command
 - Readme to include features and TODO list
 - Bot to use Cogs
### Fixed
 - Issue #5

## [1.0] - 2020-12-31
### Added
 - Faction vault withdrawals
 - Faction vault balance
 - Server ping
 - Configuration file
 - Administrator permissions check for setup commands
 - Changeable bot prefix
