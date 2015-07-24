# History
###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

## 1.0 (2015-07-08)

* Initial release

* Included Bootstrap for the javascript and css handling. Added jquery bootstrap as well.

* Wrote a to_dict() and a data_dict() method to read in JSON and convert it into a python dictionary for the application to read in submitted data.

* Added fixtures to generate some test data for users to test with.

* Added submission page with a breadcrumb link back to the main locker page.

* Modified the LockerManager model removing the 'is_archived' method

* renamed the 'user' field to 'owner' in the Locker model and then also added a 'users' field.

* Added a submission_view page to see each submission for a form.

* Added the for loop to the submission_view page to show all of the information in the same order that it would have appeared on the form.

* Modified the fixtures to include realistic information so the test data looked better and were more relevant to the users.

* Modified the Locker model timestamp to be 'create_timestamp' instead of 'submitted_timestamp'.

* Created a custom Admin site object and specified a new title and url

* Added the JavaScript code that would show a modal on the Submission List page so the user can choose what information fields her/she wants to view.

* Changed the Submission models related name to 'submission' instead of 'submissions'

* Penn State Open Source License Agreement was added

* All the migrations were fixed

* Added 'sortabletable.js' to do a table sort of all the tables within the application.