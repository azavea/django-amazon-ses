2.0.0 - 2018-04-10
==================

- Remove support for Django < 1.11.
- Add ``AWS_SES_*`` settings to configure AWS credentials through
  ``settings.py``.
- Add ``EmailBackend`` constructor arguments to override AWS credentials.

1.0.0 - 2017-12-07
==================

- Drop support for Python 3.3.
- Add testing and support for Django 2.0 (no actual code changes were
  required).
- Add settings ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` to configure
  credentials through ``settings.py``.
- Rename setting ``DJANGO_AMAZON_SES_REGION`` to ``AWS_DEFAULT_REGION`` (to
  match the Boto 3 environment variable).
- ``django_amazon_ses`` is now a module instead of a package. To upgrade,
  change the ``EMAIL_BACKEND`` setting in ``settings.py``:

  .. code:: python

    EMAIL_BACKEND = 'django_amazon_ses.EmailBackend'

  Importing signals should now be imported from ``django_amazon_ses`` instead
  of ``django_amazon_ses.backends.boto``.

0.3.2 - 2017-11-15
==================

- Fix Travis CI deployment process to account for wheels.
- Ensure that only one element of the build matrix publishes to PyPI.

0.3.1 - 2017-11-15
==================

- Fix ``tox`` installation of test dependencies.
- Add ``pip`` cache to Travis CI configuration.
- Include license file in wheel package.

0.3.0 - 2017-03-30
==================

- Officially support Python 3.x.
- Use a more sophisticated matrix build process to test Django compatibility.
- Add support for ``DJANGO_AMAZON_SES_REGION`` setting.

0.2.2 - 2017-01-05
==================

- Functionally identical to ``0.2.0-0.2.1``, but includes a reStructuredText formatting change to the ``README`` for PyPi compatibility.

0.2.1 - 2017-01-05
==================

- Functionally identical to ``0.2.0``, but includes a reStructuredText formatting change to the ``README`` for PyPi compatibility.

0.2.0 - 2017-01-05
==================

- Add support for ``pre_send`` and ``post_send`` signals for email messages.

0.1.3 - 2016-03-23
==================

- Update PyPI credentials; functionally identical to ``0.1.0-0.1.2``.

0.1.2 - 2016-03-23
==================

- Functionally identical to ``0.1.0-0.1.1``, but actually updates ``setup.py``.

0.1.1 - 2016-03-23
==================

- Ensure that manifest accounts for ``CHANGELOG.rst``.

0.1.0 - 2016-03-23
==================

- Initial release.
