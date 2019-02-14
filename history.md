# History

## 19.02.1 (14 Feb 2019)

* Switched to calendar-based versioning
* Added a UI for manually adding submissions to a locker which closes the
  loop and enables failed submissions sent via the Failure Mailer to be
  added to the appropriate locker


## 1.1.0 (21 Jan 2016)

* Added support for displaying data from the PloneFormGen DataGrid field


## 1.0.6 (16 Jan 2016)

* Bug: existing locker settings are not shown when editing a locker
* Bug: discussion UI was shown to non-owners were were also superusers but
  the discussion items were not shown
* Bug: new lockers created on every submission because form-identifier alone
  was not unique enough for looking up an existing locker. Changed the lookup
  to user the form's url instead


## 1.0.5 (11 Nov 2015)

* Implemented URL guessing prevention
* Refactored LockerSubmissionsListView into a function-based view
* Deleted all of the view Mixins
* Bug: mouseover highlighting is too light
* Bug: inactive users aren't denied access using the Django login_required
  decorator; implemented custom one to fix the limitation
* Bug: discussion replies not being associated with their parent item
* Bug: sharing a locker loads the wrong list of existing users


## 1.0.2 (16 Oct 2015)

* Bug: admins prevented from being able to manage submissions because the
  "Edit submissions" button was only shown to locker owners


## 1.0.0 (7 Oct 2015)

* Initial release
* Included Bootstrap for the javascript and css handling.
* Added jquery bootstrap as well.
* Wrote a to_dict() and a data_dict() method to read in JSON and convert it into a python dictionary .
* Added fixtures to generate some test data for users to test with.
* Added submission page with a breadcrumb link back to the main locker page.
* Modified the LockerManager model removing the 'is_archived' method
* renamed the 'user' field to 'owner' in the Locker model and then also added a 'users' field.
* Added a submission_view page to see each submission for a form.
* Added loop to the submission_view page to show all of the information.
* Modified the fixtures to include realistic information so the test data was more relevant to the users.
* Modified the Locker model timestamp to be 'create_timestamp' instead of 'submitted_timestamp'.
* Created a custom Admin site object and specified a new title and url
* Added the JavaScript code that would show a modal on the Submission List page so the user can choose what information fields her/she wants to view.
* Changed the Submission models related name to 'submission' instead of 'submissions'
* Penn State Open Source License Agreement was added
* All the migrations were fixed
* Added 'sortabletable.js' to do a table sort of all the tables within the application.