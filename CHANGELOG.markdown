CMS Changelog
=============


HEAD
----

*   Upgraded TinyMCE to 3.3.7.
*   Added CSRF protection to admin sitemap.
*   Django 1.2 compatibility.


2.2 - 05/05/2010
----------------

*   Email other users from within admin.
*   WYSIWYG editors are now resizeable.
*   Added 'using' clause to pagination tag.
*   Improved scalability of pages content framework.
*   Added author to CMS admin 'last modified' column.
*   Created a CMS 'core' application that contains all base functionality.
*   Merged 'staff' application with 'core' application.
*   Greatly improved efficiency of thumbnail generation routines.
*   Upgraded jQuery to version 1.4.2.
*   Upgraded TinyMCE to version 3.3.4.
*   Several tiny bug fixes.


2.1 - 01/02/2010
----------------

The main purpose of this release was to add in a filebrowser for the TinyMCE
editor. Numerous other improvements and bugfixes made it into the release too.
This was also the change for a refactoring of the applications used by the CMS,
in preparation for a potential open-source release later this year.

*   Added WYSIWYG file browser.
*   Contact form module now adds appropriate reply-to headers for notification emails.
*   More efficient thumbnail expansion in template rendering.
*   More efficient permalink expansion in template rendering.
*   More efficient page dispatch mechanism.
*   Removed keywords field from File model.
*   Removed notes field from File model.
*   Remove size field from File model.
*   Upgraded TinyMCE editor.
*   Upgraded jQuery to version 1.4.
*   More accessible and faster-loading admin sitemap.
*   Removed ability to link to pages using permalinks in HTML content.
*   Added many more unit tests to the framework.
*   Framework refactoring and several tiny bug fixes.