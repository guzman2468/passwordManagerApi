# passwordManagerApi
Server side logic for passwordManagerGui


.env file, database connection string, and key generation I obviously cannot post on GitHub because of security, but all of those are passed in to Render which handles deployments of my application for me. This repo of course has all the backend logic that is used interact with my MongoDB database.

NOTE: please clone the passwordManagerGui repository I have on my GitHub. That is the actual code that interacts with my backend. In addition to Render spinning down instances that are not being constantly used, MongoDB does the same but I monitor it frequently so more than likely you will only deal with my Render instance spinning back up and that time delay.
