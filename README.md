# Django Admin Setup

This guide explains how to gain admin access in Django and create a superuser.

## 1. Accessing Django Admin Panel

Once your Django project is running, you can access the admin panel by visiting:

```
http://127.0.0.1:8000/admin/
```

If you haven't created a superuser yet, follow the steps below.

## 2. Creating a Superuser

To create a superuser, run the following command inside your Django project directory:

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- **Username**
- **Email address** (optional, depending on your settings)
- **Password**

After confirming your password, the superuser account will be created.

## 3. Running Migrations (If Necessary)

If you encounter any issues, ensure the database is migrated:

```bash
python manage.py migrate
```

## 4. Logging into Django Admin

Once the superuser is created, go to:

```
http://127.0.0.1:8000/admin/
```

Enter the superuser credentials to log in.

## 5. Assigning Moderator Role

To allow a user to manage the system efficiently as a moderator:

1. Log into Django Admin.
2. Navigate to **Users** under the **Authentication and Authorization** section.
3. Select a user to grant moderator rights.
4. Ensure the user has **Staff status** checked to allow admin access.
5. Navigate to **User Profiles** under the **User Management** section.
6. Select the user’s profile and check the "Is Moderator" box.
7. Save changes.

Now, the user has moderator privileges and can manage training subjects and affiliated users.

## 6. Accessing the System

Once you have assigned the necessary roles, navigate to the main site and use the system as intended.

To access the system, go to:

```
http://127.0.0.1:8000/
```

Log in with your credentials and start managing the platform efficiently.

---

### Push to Git
To commit and push this `README.md` file to your repository, use the following commands:



