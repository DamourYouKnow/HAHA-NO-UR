# Changelog

## 1.3.0 | 2018-12-01

### Added
- Feedback now logs your discriminator so that I can actually get in touch 
with people for clarification purposes.
- More aliases.

### Fixed
- You no longer get a scary message if you try to idolize a card that isn't in 
your album. You'll now get a less scary message telling you don't have the card.
- The bot will no longer get confused when someone posts an attachment with no 
message.

## 1.2.0

### Added
- Support ticket scouting allowing you to finally reach the highest tier of 
whaling.

### Fixed
- You can now view idolized cards in unidolized mode even if you don't have any 
unidolized copies.

## 1.1.0

### Added
- You can now change the command prefix. I can work alongside other bots.
- You can now filter by last name. Holy whiskers you go Kurosawa sisters.
- !stats and !botstats are new commands (work in progress).

### Changed
- The bot is no longer dependent on School Idol Tomodachi being online.
- Greatly improved backend performance (No longer making a dozen API calls 
whenever you scout).
- More async, that's a cool buzzword that means faster bot.

### Fixed
- Fixed a bug where scouts with small search spaces would have a bias for 
certain cards.
- Fixed sorting by release date of cards.
- Stopped the bot from crashing whenever it fails to pull new card information 
from SIT.

## 1.0.0

- Initial launch.