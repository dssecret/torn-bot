# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [Unreleased]
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
### Changed
 - Readme's TODO updated
 - Balance command to bal
 - Bal command to b
 - Indentation on withdrawal command 
 - Automatic noob function to run every 12 hours from every hour
 - Automatic noob function and runnoob command to not check users in the list of users as value for over15 key in config.ini
### Fixed
 - Issue #6
 - Issue #8

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
