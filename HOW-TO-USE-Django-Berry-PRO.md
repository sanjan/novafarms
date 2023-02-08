# [Django Berry PRO](https://github.com/app-generator/django-berry-dashboard-pro)

Django starter styled with Berry Dashboard PRO, a premium Boostrap 5 design from CodedThemes The product is designed to deliver the best possible user experience with highly customizable feature-rich pages.

> **YOUR ACCESS TOKEN**: `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` 

<br />

## Features: 

- ✅ `Up-to-date Dependencies`
- ✅ `Design`: [Django Theme Berry](https://github.com/app-generator/django-admin-berry-pro) - `PRO Version`
- ✅ `Sections` covered by the design:
  - ✅ **Admin section** (reserved for superusers)
  - ✅ **Authentication**: `Django.contrib.AUTH`, Registration
  - ✅ **All Pages** available in for ordinary users 
- ✅ `Docker`
- 🚀 `Deployment` 
  - `CI/CD` flow via `Render`

<br />

## How to use the product 

> 👉 Export `GITHUB_TOKEN` in the environment: 

```bash
$ export GITHUB_TOKEN='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'  # for Linux, Mac
$ set GITHUB_TOKEN='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'     # Windows CMD
$ $env:GITHUB_TOKEN = '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'  # Windows powerShell 
```

This is required because the project has a private REPO dependency: `github.com/app-generator/priv-django-admin-berry-pro`

> 👉 Clone the sample project

```bash
$ git clone https://github.com/app-generator/django-berry-dashboard-pro.git
$ cd django-berry-dashboard-pro
```

> 👉 Follow the instructions provide by the [README](https://github.com/app-generator/django-berry-dashboard-pro)

```bash
$ # Instal dependencies 
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ 
$ # Set Up Database
$ python manage.py makemigrations
$ python manage.py migrate
$
$ # Create SuperUser
$ python manage.py createsuperuser
$
$ # Start Server
$ python manage.py runserver
```

At this point, the app runs at `http://127.0.0.1:8000/`.

## Deploy on [Render](https://render.com/)

- Create a Blueprint instance
  - Go to https://dashboard.render.com/blueprints this link.
- Click `New Blueprint Instance` button.
- Connect your `repo` which you want to deploy.
- Fill the `Service Group Name` and click on `Update Existing Resources` button.
- After that your deployment will start automatically.

At this point, the product should be LIVE.

## Screenshots

![Berry Bootstrap 5 - Sign IN, Open-source Starter by AppSeed.](https://user-images.githubusercontent.com/51070104/207091198-2753246e-3d65-4aac-96de-0598a9a94788.jpg)

<br />

> [Django Admin Berry](https://github.com/app-generator/django-admin-berry) - `Icons` Page

![Berry Bootstrap 5 - UI Icons page, Open-source Starter by AppSeed](https://user-images.githubusercontent.com/51070104/207091655-d5005e08-7ea0-4367-ab3a-2cd16934d2fd.jpg)

<br />

> [Django Admin Berry](https://github.com/app-generator/django-admin-berry) - `Colors` page

![Berry Bootstrap 5 - Colors page, Open-source Starter by AppSeed](https://user-images.githubusercontent.com/51070104/207091441-942be542-2794-4bdb-a51d-85c75b5bc692.jpg)

<br />

---
[Django Berry PRO](https://github.com/app-generator/django-berry-dashboard-pro) - **Django** starter provided by **[AppSeed](https://appseed.us/)**
