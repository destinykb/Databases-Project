Destiny Brewington
Divya Shanmugam

Fall 2025, Intro to Databases, Columbia University

Implementations: 
- Users can search artists, venues, city, country, or date and receive resulting concerts related to the respective filter
- Users can "purchase" a ticket (or multiple) for a specific concert
- Users can view ratings left by other users for a particular artist
- Users can leave their own ratings and a text review for an artist
- Users can access their reviews and delete a review after posting it

Ticket Purchasing Page:
After clicking the "Buy" button next to a specific concert, a user will be led to a separate purchasing page containing
the information related to the concert (date, time, ticket prices, etc.) where they can select quantity of tickets they
wish to purchase, then a second page where they enter their personal information (full name, email, and credit card 
number), and then a final page with a statement confirming their purchase. This page conducts queries across the Concert,
Performer, and Venue tables in the database in order to provide information relevant to the ticket purchase. When a user
"purchases" a ticket, the Customer table is updated with a new instance of user (unless they are a returning customer), 
the Tickets table is updated with a new instance of ticket per each ticket purchased, and ticket information in the Concerts
table is updated for the respective concert. I find this function of our application interesting because it mimics the primary
function of popular real-world ticket vending applications such as Ticketmaster.

Ratings Page:
Users can search for a specific artist and then view all the numerical and text ratings for that specific artist. The user
also has the option to leave their own rating and text review for that artist. After posting a rating, a user can then
click the "My Ratings" button, enter their email to search for the reviews they have left across all artists, and then have
the option to delete past reviews they have left. This page performs queries joining the Performer and Ratings table, and when
a user posts or deletes a rating the Ratings table is updated and the average_rating for the artist is updated in the Performer
table. I think this function of our application is interesting because it adds an interactive aspect to the overall site
that enables users to repeatedly visit and interact with the site over time.

This repo contains html files for the webfront of the Find-A-Concert Application that returns upcoming concerts based on user parameters (artist, venue, city, country, or date).
ChatGPT was used to improve the UI, debug Flask, understand how Flask interacts with html files, and understand error messages.

Prompt examples:
1. how does the server interact with the html files?
2. how does the server receive information from the html files and vice versa?
3. what is a value bind parameter?
4. how would I create a search bar and drop-down in html?
5. how do I create a button in html
