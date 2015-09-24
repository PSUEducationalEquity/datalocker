## Introduction

This package provides a [Django](http://www.djangoproject.com) application
for collecting, storing, and reviewing online form submissions.

Repository: (https://github.com/PSUEducationalEquity/datalocker)

Issues tracked at: (https://github.com/PSUEducationalEquity/datalocker/issues)


## Overview

The Data Locker provides a repository for form submissions. Built using the
[Django](http://www.djangoproject.com) framework, it provides a core
application that can be extended to add additional features and functionality.

At it's core, it's designed to capture all the submission from a given online
form into a "locker". These submissions can then be viewed, moved through a
workflow, commented on, and/or exported.

Lockers are owned by a single user based on the first form submission's
information. The owner can then share access to the locker with other users.


## Dependencies

Tested for use with Django 1.8.x, backwards compatibility is unknown and highly
unlikely beyond 1.7.x due to the use of build-in database schema migrations.


## Installation

1. Clone the repository into an existing Django project
1. Add `'datalocker'` to the `INSTALLED_APPS` **before** `'django.contrib.admin'`
1. Run the database migrations `./manage.py migrate datalocker`
1. Add the necessary settings into `settings.py` (TODO: details here)
1. Have fun!


## Credits

Thanks to the Django creators and community for an excellent framework to
build upon.

The [image](http://findicons.com/icon/49510/encrypted?id=49510) for the
favicon is courtesy of [Marco Martin](http://notmart.org/blog/) and is
licensed GNU/GPL.

The image was converted to a favicon using the
[Favicon & App Icon Generator](http://www.favicon-generator.org/).


## License

Developed at the Pennsylvania State University and licensed as open source.

See `license.txt` for details.
