# Web App

A simple app built with Django, that makes it easier to navigate through tech-related news provided by the public API of Hacker News. 
The app syncs the published news to a database every 5 minutes and implements features such as filtering by item type, searching by text, and pagination.


Also contains an API with endpoints:

`GET` List the items, allowing filters to be specified; <br /> 
`POST` Add new items to the database (not present in Hacker News);
