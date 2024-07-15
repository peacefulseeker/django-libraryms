
### 1) data seeding / faking: create more robust solution using fixtures/mixer/more customization
https://nkpremices.com/graphene-testing-factories-and-data-seeding-in-django-pytest-mixer/
another example with lots of default fake data
https://github.com/chepe4pi/frameworks_compare/blob/main/myapp/management/commands/generate_data.py

### 2) Cover all models with relevant tests

### 3) Save historical reference to order and reservation book/member
via extra field like member_fullname and book_title, which should be unique in the system
at the moment of order/reservation creation.

### 3) Add type hints. Especially useful for self.{model} references within associated model.

### 4) Delete book orders older then 1 year. Otherwise might collect quite a bunch

### 5) Add reservation renew / extend functionality
