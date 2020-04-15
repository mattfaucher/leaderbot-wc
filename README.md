# leaderbot-wc
discord bot for wrld crew customs


This bot serves the purpose of keeping track of duos in a Fortnite Customs discord server.

Each command serves a purpose in making this possible, it has been created for duos but can be altered to work for solos
and squads.

To use this code for your own bot, you will need a discord app token.

the commands use the leaderboard.json file that is included which is an empty list, fill that list with objects containing
properties you want to store about each team. I gave each duo a unique 4 digit identifier which was mainly used for most of
the commands regarding scoring.

I reccommend setting up a database and passing the data into that rather than storing in memory in a .json file.

deployed on heroku

-Matt
