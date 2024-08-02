## PRIO

### Try combining backend/frontend ultimately.
Having 1 template served by django backend will allow sending authenticated tokens immediately
without extra calls from frontend. This will allow smoother experience on initial page loads.
Combining with non-reload ajax calls will make it a good combo eventually.
### use loading on submit, disable button as well
### add book covers(need to automate image upload as wel)
### add a cron job pinging https://django-libraryms.onrender.com/ every 30/60 mins to wake up instance regularly

### Notify librarian about new order(notification row / email)
### Notify member about processed order(ready to be picked up / issued for now) ( email )

## SECONDARY
### can Book.clean() be somehow leveraged for reservation status checking?
### TESTS: Cover all models and API endpoints primarily
### Add reservation renew / extend functionality
### set up rate limiter for all auth-demanding requests
### allow member change password and request password reset
### data seeding / faking: create more robust solution using fixtures/mixer/more customization
https://nkpremices.com/graphene-testing-factories-and-data-seeding-in-django-pytest-mixer/
another example with lots of default fake data
https://github.com/chepe4pi/frameworks_compare/blob/main/myapp/management/commands/generate_data.py


### Delete book orders older then 1 year. Otherwise might collect quite a bunch

### Setup proper localization (ru, en, lv)

### Book cover image upload(s3 e.g.)

### Get proper status display in order history view

### Deploy to AWS

### Add book library relations. Same book examplar can be located in multiple libraries
### Add book shelf relation(along with library)
