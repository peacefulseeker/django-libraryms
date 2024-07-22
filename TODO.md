## PRIO

### Try combining backend/frontend ultimately.
Having 1 template served by django backend will allow sending authenticated tokens immediately
without extra calls from frontend. This will allow smoother experience on initial page loads.
Combining with non-reload ajax calls will make it a good combo eventually.

###  seems like a better idea would be to link Reservation with Order rather then with book.
Order deleted -> Reservation Deleted -> Book Available
Order unprocessed - Rerervation Reserver -> Book reservered
Order processed - Rerervation Reserved -> Book reserved(until issued physically in library)
Order cancelled - Rerervation Cancelled -> Book available

### Add reservation renew / extend functionality

### Notify librarian about new order(notification row / email)

### Notify member about processed order(ready to be picked up / issued for now) ( email )


### set up CI pipeline in GitHub actions
### Dockerize app
### Deploy to render.com / fly.com other heroku free alternative

## SECONDARY

### allow member change password and request password reset

### data seeding / faking: create more robust solution using fixtures/mixer/more customization
https://nkpremices.com/graphene-testing-factories-and-data-seeding-in-django-pytest-mixer/
another example with lots of default fake data
https://github.com/chepe4pi/frameworks_compare/blob/main/myapp/management/commands/generate_data.py

### Cover all models with relevant tests

### Delete book orders older then 1 year. Otherwise might collect quite a bunch

### Setup proper localization (ru, en, lv)

### Book cover image upload(s3 e.g.)

### Get proper status display in order history view

### Deploy to AWS
