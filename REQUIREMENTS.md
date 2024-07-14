### Goal
Replicate full functionality of library management system, based on existing https://jurmala.biblioteka.lv/Alise/ru/home.aspx,
which has poor user experience and UI at the moment

### MVP Requirements
Visitor should be able to:
- search books by title and/or author without authentication
- sign up and login to a system(for now)
    - later on, member registration will only be available to librarians
- view all book actions like order or join queue, but action will require authentication

Member(user) should be able to:
- can everything what visitor can
- to recover / change password
- order a book, which on a shelf at the moment
    - send email to librarian to notify about a new book order, to prepare a book
- join a book queue, in case it's busy at the moment

Librarian(by default admin user):
- manage all members, including librarians(crud)
- manage all books(crud)

### Questions to address / edge cases
- should book have a separate status field, or it could be tied to nullable reservation,
which would store current status(none = available, reserved, ordered)
- what if book not returned by member?
- how to save historical book reference for reservation?
perhaps could store historical fields via https://github.com/jazzband/django-simple-history


### Nice to have
- Fines system in case member did not return the book in time.(.e.g 5 cents for each over-due day)
- Limit amount of books in a queue
- Limit amount of books that can be issued to member


### Tech
Django - as a web framework
Postgres - as a database
Celery/Redis - as a task management / queue system

