
### 1) data seeding / faking: create more robust solution using fixtures/mixer/more customization
https://nkpremices.com/graphene-testing-factories-and-data-seeding-in-django-pytest-mixer/
another example with lots of default fake data
https://github.com/chepe4pi/frameworks_compare/blob/main/myapp/management/commands/generate_data.py

### 2) Cover all models with relevant tests

### 3) Save historical reference to order and reservation book/member
via extra field like member_fullname and book_title, which should be unique in the system
at the moment of order/reservation creation.

+ add a comment field about order/resrevation refusal reason for example or any other useful notes

### 3) Add type hints. Especially useful for self.{model} references within associated model.

### 4) Delete book orders older then 1 year. Otherwise might collect quite a bunch

### 5) Add reservation renew / extend functionality

### 6) Notify user about upocoming session expiration(e.g. in 60 minutes)
Aslo, need to double chekc in which occassions to use refresh token calls


### 7) Add issued_by/processed_ny fields, to understand who processed the order/reservation in admin.


### 8) Setup proper localization (ru, en, lv)

### 9) What if combine backend/frontend ultimately.
Having 1 template served by django backend will allow sending authenticated tokens immediately
without extra calls from frontend. This will allow smoother experience on initial page loads.
Combining with non-reload ajax calls will make it a good combo eventually.

### 10) Book cover image upload(s3 e.g.)
