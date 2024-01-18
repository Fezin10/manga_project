# Mangaweb

## files
### Static
#### images/image_placeholder.webp
  Image to be used when no image was provided, like for user icon, or manga thumbnail.
#### script.js
  It contains all functions the app have, to make buttons work, to confirm some users actions, change the page colors, adapt the page to be used in mobile, show the user selected images, do some api calls for things like the follow and like, count how much letters are inside some element, show different images to make the content more readable, and do some client side validations at some pages that have inputs.
#### styles.css
  Have the styles for the entire website, with some multi use classes.
### htmls
#### addchapter.html
  Is the page used by the authors to upload chapters to their mangas, it allow the user to choose which chapter is being created, list all user mangas with their last released chapter in case the manga have any, and let the user choose images for each page they want to upload and show which pages are selected and their number. Have client side validation.
#### addmanga.html
  Let the author create a manga entry, with name, genres, custom genres, status, sinopse, release date, end date and a thumbnail, also this page have client side validation.
#### edit.html
  Let the author edit their manga entries, all fields are prefilled with the current information.
#### edituser.html
  Here the user can edit their information, like the username, password and icon, the informations will only be changed if the user provide new content for the fields, to change the password the user need to use their previous password, and if this is not provided, the system will understand they don't want to change their password, also the user can not change password more than 1 time each 2 days.
#### index.html
  Page to display all mangas, the default filters are to shown releasing and finilized mangas ordered by popularity, but the page also supports multiple filters for status, sort order, genres and liked mangas and mangas from liked authors.
#### layout.html
  Provide the frame for all other htmls, have an adaptative navbar, a search button and the button to change the theme, also provide an csrf token to be used in the front end.
#### login.html
  Let the user log in, and offer a register button in case they don't have an account.
#### mangapage.html
  Is the main page for every manga, have the manga thumbnail, and information about the manga, like the author, genre, start date, end date, like button, author have the edit button and delete button to edit or delete the specific manga from the page, moderator options to retain the manga, free it from the retain or block it, can give the user a fault or even a ban if needed. Also show a list with the chapters, and the already read ones show in a different color, have pagination in case the manga have too much chapters.
#### mangaread_mobile.html
  Render all the images inside a chapter, with support for touch buttons to improve the mobile usuability, provide a link to previous chapter if exists, and for the next chapter if exists, pages are read right to left on purpose.
#### mangaread.html
  PC version for reading the pages of the chapters, have a delete button in case the user is the author of that manga, have support to use the keyboard arrows to change page, also have link to previous and next chapter in case it exists, pages are read right to left on purpose.
#### moderator.html
  Page for the moderator see every retained user and manga, to simplify the process of moderation.
#### register.html
  Let the user register himself if no username equal to what they want and the email is not in the blocked list, have client side validation.
#### user.html
  Show some information of the user, like when the user registered, followers and following, and if the user is an author or a moderator, in case the user is a author, show how much works the user publisehd and the works at the bottom of the page. Like the mangapage.html, have support to moderator options, like retain, free and ban.
### Python
#### admin.py
  Some useful functions to use while creating the application.
#### helper.py
  Have some functions to auxiliate the views.py to be shorter and simplier. Also have function that have ratelimit to prevent abuse of some functions.
#### models.py
  Have the models used and linked to each other, also have the deletion handlers to delete the folders and file when an above level model is deleted.
#### uploaders.py
  Functions to handle where each file should be saved to create some organization.
#### urls.py
  Urls to connect each path to a view, at the end a setting to make the images work when in debug mode.
#### views.py
  All functions to render the pages with the needed values, some are apis to be connected with the front end to keep the flow of the pages.
### Requiriments
#### requiriments.txt
  To save each package that need to be downloaded to make the application run correctly.
## How to run
  First import the libraries in the requiriments.txt and assure that django is installed.    
  To run the application you need to run `python3 manage.py makemigrations mangaweb` then `python3 manage.py migrate`, also need to create an folder called "media" at the same level as the manage.py, then run the server.
## Additional
  + To become an author, log in, go to the user page, clicking in your username and clicking the button "become an author", to become an moderator, go to the /admin and set yourself to be an moderator.  
  + Some pages will detect mobile access at the start of the page only, so just turn on the mobile mode and refresh the page.  
  + Mangas are read right to left, that's why the mangaread show images from right to left.  
  + Both mangaread will set a chapter to "readed" when reach the "next chapter" page.
