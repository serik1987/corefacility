# Installation and usage instruction

## Developers

(c) Sergei Kozhukhov, scientist in the Institute of Higher Nervous Activity, RAS

E-mail: sergei.kozhukhov@ihna.ru

URL: https://www.ihna.ru/ru/employees/sergei.kozhukhov

(c) the Institute of Higher Nervous Activity and Neurophysiology, Russian Academy of Sciences, Moscow,
Russia

Address: 5A Butlerova str., Moscow, Russia

E-mail: admin@ihna.ru

Phone number: +7 (495) 334-70-00

## Замечание для русскоязычных пользователей

Работая с данным продуктом, Вы принимаете условия лицензионного соглашения, изложенные в файле LICENSE.txt

К сожалению, данная инструкция доступна на английском языке. В случае возникновения каких-либо затруднений
в установке пожалуйста, обратитесь к разработчикам за консультацией.

## Installation instructions

The program works in stand-alone and Web server configuration. The stand-alone configuration must be
installed on your personal computer and is suitable for your personal use only. The Web Server
configuration usually installs on special Web Servers and provides cloud data storage and cloud data
processing. However, web server configuration is highly difficult and requires a person with special
skills.

The following reading will help you to gain such skills:
Nemett, E., Snyder G. Unix and Linux System Administration Handbook. Fifth Edition. 

### Requirements

_Operating system_: Any operating system where you can install Python 3 and GitHub is good.
However, if you have non-POSIX operating systems (including Microsoft Windows) you can run this application
only in stand-alone configuration.

This program works under Python 3.10 or higher. Also, you are required to install python3-pip v. 22.2.2
or higher and use this to install the Python packages mentioned below:

* psutil >= 5.8.0
* python-dotenv >= 0.19.2
* django >= 4.1.1
* django-configurations >= 2.4
* djangorestframework >= 3.13.1
* pillow >= 9.2.0
* parameterized >= 0.8.1
* pytz >= 2022.2.1
* colorama >= 0.4.4
* urllib3 >= 1.26.9
* bs4
* dateutils
* numpy >= 1.23.2
* matplotlib >= 3.5.3
* scipy >= 1.9.1

Also, GitHub client is required for the installation and update process. You need to install it as well.
If you doesn't intend to use this application in stand-alone configuration you need cron to be installed.

### Download the application

Create the folder where your application will be located. Open the command line interpreter and go to
this folder using the `cd` command. Next, type the following:

```commandline
git clone https://github.com/serik1987/corefacility.git
cd corefacility
```

### Preliminary setup

Scan the corefacility application for list of all available extensions. This could be done by the following
command

```commandline
python3 corefacility/build.py
```

After this command will run correctly, you will see the `settings` folder. The next step is to configure
the application by changing special .env files. Each such file contain line in the following form:

```dotenv
key=value
```

The value to change in on the right of the equal (`=`) sign. Do it without changing the key.

### Selection of application configuration mode.
The only option `DJANGO_CONFIGURATION` is responsible for the application running mode. Value of this
option is given configuration mode. All such modes are mentioned below.

The very easy configuration mode is `SimpleLaunchConfiguration`. This is the only configuration that works
in non-POSIX operating system (including Microsoft Windows), so use it if this is your case.
The `SimpleLaunchConfiguration` allows a stand-alone usage of this application, gathering and processing
the data. However, it doesn't allow you cloud storage and cloud processing, the performance options
are highly non-optimal (I mean, only one CPU kernel will be engaged during the processing), doesn't provide
hardware health-check and adjustment.

The next mode is `ExtendedLaunchConfiguration`. This mode is as easy to install as
`SimpleLaunchConfiguration` but requires POSIX-compliant operating system (Mac OS X, Linux, another
Unix-like operating system is good). Such configuration also requires a stand-alone usage as well as
setting up performance options, hardware health-check and adjustment. However, cloud storage is not
possible. Use this option if you are the only person responsible for the data processing and don't need
any cloud storage.

`VirtualServerConfiguration` allows to organize cloud storage and cloud data processing given that
computational difficulty of the task is low (i.e., the task can be accomplished for less than a second).
Only one CPU kernel is used for any computations. Any performance optimization, hardware health-check and
adjustment is not possible. You this option if you rent cheap virtual hosting service for the data cloud
storage.

Any other configuration options require either VPS/VDS service or dedicated Web Server or buying your
own Web server.

`FullServerConfiguration` has absolutely no restrictions: you can organize cloud data storage and
processing, provide administration of the operating system accounts and groups (this is needed for SSH
access to all users), adjust CPU optimization, hardware health-check and adjustment. If you select this
option, the program installation will be the hardest. Also, the Shell crawler process requires
administrative privileges. (_However this is not the case for worker processes of your Web server._)

`PartServerConfiguration` We always try to provide all necessary security tests and find and fix all
found security holes. However, this is OK that you don't trust our application, treat it as insecure and
don't  want it to give an administrative privileges to it. Under this configuration the application will not
require administrative privileges. However, it requires your attention when somebody wants to create
users and projects and during the hardware health-check and adjust routines, performance optimization etc.
(i.e., such features will be accomplished by corefacility + SSH + yourself logged in using your sudo account
and are impossible solely by corefacility).

| Configuration options         | Cloud storage | POSIX account administration                       | Hardware health-check and adjustments                                                                     | Number of CPU cores for data processing and simulation  | Operating system required |
|-------------------------------|---------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------|---------------------------|
| `SimpleLaunchConfiguration`   | Not allowed   | Not provided                                       | Not provided                                                                                              | 1                                                       | Any                       |
| `ExtendedLaunchConfiguration` | Not allowed   | Not provided                                       | Provided                                                                                                  | As many as you have                                     | POSIX-compliant           |
| `VirtualServerConfiguration`  | Allowed       | Not provided                                       | Not provided                                                                                              | 1, algorithm execution time is not less that 2 seconds. | POSIX-compliant           |
| `FullServerConfiguration`     | Allowed       | Provided                                           | Provided                                                                                                  | As many as you have                                     | POSIX-compliant           |
| `PartServerConfiguration`     | Allowed       | Requires attention of the Web server administrator | Hardware health-check is provided. Any other operations require attention of the web server administrator | As many as you have                                     | POSIX-compliant           |

### Basic settings

Open the `basics.env` file to adjust the application Basic settings.

The first setting is E-mail address. The corefacility application will send an E-mail to administrators
in case of troubles. `DJANGO_ADMIN_NAME` and `DJANGO_ADMIN_EMAIL` options are responsible for this.
Value of the `DJANGO_ADMIN_NAME` will be written to the To: field of an emergency e-mail. The e-mail itself
will be sent to the address defined by the value of the `DJANGO_ADMIN_EMAIL` option

`DJANGO_ALLOWED_HOST` Left this field intact in `SimpleLaunchConfiguration` and
`ExtendedLaunchConfiguration` profile. If your application is needed to have cloud hosting it implies that
some URL corresponds to such application. An example of such URL:
```
http://192.168.0.20
http://hendrikje.uni-tuebingen.de:1500
```
and so on...
Such a URL consists of protocol name (HTTP or HTTP secured), host name and port number preceded by the
colon (`:`). Put here names of all hosts in such URL separated by commas. The application will not respond
request designated for another hosts. If you follow the application URL and get `Bad Request (400)` you
probably incorrectly setup this option.

`DJANGO_ALLOWED_IPS` When you use `FullServerConfiguration` mention here all IPs from which you can
provide administration tasks (manage users, groups and projects, adjust performance and hardware options).
Please, note that they must be internal IPs from your laboratory or University network and IP spoofing
protecting must be turned on for your Internet gateway (e.g., laboratory router). Otherwise, this option
will not work. This option is ignored in any other types of configurations: `VirtualServerConfiguration`
and `PartServerConfiguration` allows administration and network adjust tasks from any IP,
`ExtendedLaunchConfiguration` and `SimpleLaunchConfiguration` don't support data transmission over the
network.

`DJANGO_DEBUG` At first start turn this option to `yes`. When you finish your application and the
application will work correctly turn this option to `no`. Also, turn this option to `yes` when you develop
an extension to this application. Another point is `SimpleLaunchConfiguration` and
`ExtendedLaunchConfiguration` will not work when `DJANGO_DEBUG` is `no`. So, set it to `yes` for such modes.

`DJANGO_LANGUAGE_CODE` Defines language and locale of all messages generated by the corefacility. Two
languages only are supported here:
`ru-RU` Russian
`en-GB` English (Great Britain)
Another languages will be available if you create special language files. See reference here on how to do
it:

(a) Language files for Backend:

https://docs.djangoproject.com/en/4.2/topics/i18n/translation/#localization-how-to-create-language-files

(b) Language files for Frontend:

https://react.i18next.com/

`DJANGO_TIME_ZONE` Defines a timezone where you are (for stand-alone configuration) or where your Web
Server are (for web server configuration).

### Database settings

Database is a special kind of storage where metadata, user list, logs, groups and project etc. are saved.

Database is some kind of information on your disk which access is managed by a special system, called
Database Management System. Corefacility supports the following Database Management Systems:

`PostgreSQL` (https://www.postgresql.org/) has higher performance and more features. However, this is
difficult to install this one. Use PostgreSQL for `FullServerConfiguration` and `PartServerConfiguration`.
You can use this management system in `VirtualServerConfiguration` if your hosting provider support this.

`MySQL` (https://mysql.com/) has less performance and less features. Use this database management system
when your hosting provider doesn't support PostgreSQL.

`SQLite` this is the only database system embedded to Corefacility (i.e., no difficult preliminary
installation is required). However, the management system is very slow. Also, this management system
doesn't support multiple request made at the same time. Such a feature doesn't allow it to use for the
cloud storage. You this management system for configuration where cloud storage is not allowed.

The table below mention advantages and disadvantages of all three systems.

| Database Management System | Performance | Deals with simultaneous queries | Installation process | Backend name                    | Additional python package to install |
|----------------------------|-------------|---------------------------------|----------------------|---------------------------------|--------------------------------------|
| PostgreSQL                 | high        | Yes                             | Hard                 | `django.db.backends.postgresql` | `psycopg2`                           |
| MySQL                      | low         | Yes                             | Hard                 | `django.db.backends.mysql`      | `mysqlclient`                        |
| SQLite                     | low         | No                              | Not required         | `django.db.backends.sqlite3`    | Not required                         |

When you choose proper Database management system, you have to install this. After installation has been
completed provide some administration tasks:
* issue credentials that corefacility will use to log in on the database server (username and password);
* create database for the corefacility application;
* grant permissions to the user you currently created.
In the long run you must have the following access details for PostgreSQL and MySQL:
* Address of the SQL server (its domain name, host name or IP address). Use `localhost` if Database management system has been installed on the same server as corefacility;
* A port listening by the SQL server. By default, PostgreSQL listens to the port number 5432 and MySQL listens to the port 3306
* username
* password
* database name
Write down such access details somewhere on your paper.

Next, you have to install python package that is required to link Corefacility with your Database management
system. Refer to the last column of the table above to find out which package is required. This step is not
necessary for the SQLite.

Open `sql.env` file inside the `settings` folder to tell corefacility how it should connect to the Database
Management system.

#### Database properties when you use SQLite

`DJANGO_SQL_BACKEND` Set to `django.db.backends.sqlite3`

`DJANGO_SQL_NAME` Name of a file where the database will be stored. The file is not required to exist
because it will be created during the following installation steps. However, be sure that the directory where
this file will be located exists and is available for writing. Come up with any arbitrary name of this file.
The preferrable file extension is `.sqlite3` or `.db`. Put full name of the file to this option.

Any other options will be ignored.

#### Database properties when you use PostgreSQL or MySQL

`DJANGO_SQL_BACKEND` Corresponding backend name. Refer to the table above to find out value of this feature.

`DJANGO_SQL_NAME` Name of the database that you have been created

`DJANGO_SQL_SERVER` Put address of the SQL server here

`DJANGO_SQL_PORT` Put here a port listening by the SQL server.

`DJANGO_SQL_USER` Name of the user to log in

`DJANGO_SQL_PASSWORD` Password for the user to log in

`DJANGO_SQL_INIT_COMMAND` If some initial query is required for correct job of the database, use this option
to write down such a query.

#### Migration of the data

**Migration** is a process of creation of all necessary tables in a database you have been created. If you
choose SQLite, migration is also a process of creation of database file and putting all tables here.

To provide migration, run the following command:

```commandline
python3 corefacility/manage.py migrate
```

### Construction the Web server stack

If you use `SimpleLaunchConfiguration` or `ExtendedLaunchConfiguration` this step must be definitely
omitted because everything is ready for the application launch.

#### Static and py files

The corefacility contains two major file types: static files and py files. The corefacility also have
another types of the files, however they are beyond the scope of this section. You Web server must cope
with static files and py files in different way. The static files must be delivered to the connected user
as they are: they will be downloaded, opened and used by the Web browser of your colleague, not your Web
server. These files contain _Application frontend_.

The py files must be run by your Web server with the aid of the Python interpreter. These files will be
launched in response to the user's request. The result of their execution will be delivered to the client.
These files are called _Application backend_.

When the user interacts with corefacility he uses a mouse and a keyboard. All signals from these input
devices are processed by the _Application frontend_. Application frontend constructs and sends _HTTP request_
to the Web server. HTTP request is some piece of information that delivers from the user's PC to your
Web server that tells Web Server what to do and what the user wants from it. When the Web Server receives
the HTTP request it runs _Application backend_ (or py files) that process such request. The application
backend generates another piece of information called _HTTP response_ that tells the user's PC about the
result of the operating and supply it with all necessary data. The HTTP response is delivered to the 
user's PC and process by the Application backend that shows operation results on the screen.

#### How your Web Server works

Three program must be worked together on your Web server: nginx, gunicorn and corefacility.

**nginx** accepts requests from the user and determines whether the user's Web browser requires static files
to be delivered here or accomplish some task on the Web server by means of execution of py files here.
If this is request for static files delivering such files will be delivered as they are, without any change.
In case when the user need to perform some job on the Web server, nginx does nothing with request and
send it to the next application called gunicorn.

**gunicorn** is responsible for the data transmission between nginx and corefacility and management of
the corefacility itself. gunicorn is connected with nginx by means of the Web socket.

**corefacility** is run by the gunicorn accept the request data from them, does the job required by the user
and gives output data to the gunicorn.

At this stage of installation process you need to construct a chain containing three applications:
nginx <-> gunicorn <-> corefacility

#### How to do it in VPS/VDS, Dedicated Server, your personal Web Server

* Install and configure nginx
* Install and configure gunicorn.
* Connect nginx and gunicorn by the UNIX socket.

In order to connect gunicorn and corefacility tell gunicorn to find out `application` object in
`corefacility.wsgi` module and use it for the HTTP request handling. The working directory for the gunicorn
application is `corefacility`.

#### How to do it in the Virtual Hosting

Some of the actions mentioned above has already been done by your hosting provider. Follow instructions
suggested to your hosting provider.

#### Copy static files to your document root

The **nginx** Web server can either deliver file located to the special directory named _Document root_ or
deliver the request to **gunicorn** by means of the UNIX socket. If you know your document root create
directory for static and media files here (_Media files_ are files uploaded by the user for the public
access, e.g., user's avatar, project icon etc.). Open the `staticfiles.env` file and write down full paths
to directory where you wish to store static and media files. Static files directory is value of the 
`DJANGO_STATIC_ROOT` option and media files directory is value of the `DJANGO_MEDIA_ROOT` option.

After you finish setting up the `staticfiles.env` files run the following command that copy all static files:
```commandline
python3 corefacility/manage.py collectstatic
```

### Trial launch

If everything is OK you need to run your Web server. To run the Web server in `SimpleLaunchConfiguration`
and `ExtendedLaunchConfiguration` use the following command:

```commandline
python3 corefacility/manage.py runserver
```

and follow the address printed on the console.

If you use another configuration profiles you are required to start nginx and gunicorn services or
restart them if they have already been started.

Be sure that the corefacility main window was loaded correctly.

### Adjustment of E-mail delivery

Omit this section for `SimpleLaunchConfiguration` and `ExtendedLaunchConfiguration` since they don't
support E-mail delivery.

E-mail delivery allows the users to recover their passwords and warn administrator about troubles occured
with their Web server. To deliver e-mail you need to install and configure the SMTP server or to use
external SMTP server provided by such famous mail systems as Google or Mail.ru etc. In first case be sure
that your Web server is not treated as mail spam engine by the Gmail, Mail.ru etc. (This is impossible to
done if your Web server doesn't have public or 'white' IP address.) In the second case ensure that
connection to the SMTP is not treated by the SMTP server as suspicious attempt to hack the account.

Whenever which method you use you will give mail connection details. Put such details to the `email.env`
file located in the `settings` directory.

### SSL encryption properties

SSL encryption allow you to encrypt your corefacility account credentials when transmitting from the user's
PC to the Web server. This is required when the credentials are sent by the global network and hence can
be read by unrestricted number of anonymous users (i.e., from the home of your colleague to the Web server
located on your job or from Moscow to St.Petersburg etc.). The encryption process is the following: the
Web browser encrypts the data and delivers the encrypted ones. The encrtypted data can't be read and analyze
without the decryption process. And the decryption must be done only by your Web server.

Omit this section if encryption is not required (i.e., when you transmit the data
using the wired connections within your laboratory etc.) Don't do anything in this section when your
Web server is under `SimpleLaunchConfiguration` or `ExtendedLaunchConfiguration`.

In any other cases issue the SSL certificate from the authorization center and configure your **nginx** to
deal with such certificate.  Ensure that SSL encryption works OK. To do this, open the following address:

```
https://<your-web-server-address>/
```

Yes, your protocol is HTTPS. If the page was loaded the SSL encryption works OK and hence you can start
adjustment of the corefacility security settings.

`DJANGO_SECURE_SSL_REDIRECT` When the user uses insecure channel (i.e., he accesses the Website by means
of `http://`, not `https://`) his request will not be considered and his Web browser will be redirected
to the similar page but uses `https://` for communication. Available values: `yes`, `no`.

`DJANGO_SECURE_SSL_HOSTNAME` If the previous option was set to `yes` this option must refer to the web
server to redirect when the user uses `http://`. Omit this option is you want the user to redirect to the
same Web server.

`DJANGO_SECURE_HSTS_SECONDS` tells the browser that your Web server works with HTTPS only. The Web browser
will not use HTTP protocol any more to connect to your Web server. Number defines amount of seconds that
the browser will remember this option.

`DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` If previous option was set, the Web browser will apply this rule
to all subdomains. Available values: `yes`, `no.`

`DJANGO_SECURE_HSTS_PRELOAD` the Web server tells all Google Chrome Web browsers to use HTTPS only when
connecting to your Web Server. Doesn't work for another Web browsers.

### Final launch

The last thing you should do is to open the `basics.env` file and set `DJANGO_DEBUG` to `no`. This is not
required for the `SimpleLaunchConfiguration` and `ExtendedLaunchConfiguration`.

Next, follow the corefacility Web address and open the main page.

### SECURITY ALERT!

As you can see there is no accounts, user names and passwords on your Web Server! This is fine when you
work with `SimpleLaunchConfiguration` and `ExtendedLaunchConfiguration` but absolutely disgusting when your
Web server is accessible via the Internel. In the last case do the following:

* Open Settings -> Users.
* Create your own personal account.
* Issue a password for you.
* Open Settings -> Application settings.
* Go to Authorization branch on the left tree.
* Click on standard authorization and put the checkbox at the left of "Enabled" on the right panel. Save the settings.
* Click on the automatic authorization on that tree on the left panel and clear checkbox at the left of the "Enabled" on the right panel. Save the settings.
* Reload the Web browser window.
* Enter your login and password.
* Now your corefacility application is safe.

### Corefacility update

Always update your corefacility application because new updated version contain bug fixes and security
improvements. The corefacility application can be updated by the following command:

```commandline
git pull
```

Use your operating system to schedule the corefacility update!

## Add new application to the corefacility

### Tell corefacility that you have added your application

To do this open the `applications.list` file and write here full name of the application root module
on the new last line.

### Apply all changes

To apply all changes reconfigure your application by the following way:

```commandline
python3 corefacility/manage.py configure
```

Corefacility will tell Django where your application is located.

### Create tables in the database

In order to do this, repeat the migration process:

```commandline
python3 corefacility/manage.py migrate
```

### Static files collection

Collect all static files from your new application. In order to do this provide the following thing:

```commandline
python3 corefacility/manage.py collectstatic
```

### Restart

Restart corefacility application. If you use `VirtualServerConfiguration`, `PartServerConfiguration` or
`FullServerConfiguration` restart **gunicorn**.

## Add new application

If all corefacility features are not sufficient for you and you are good in Python and Javascript
programming (Web browsers understand Javascript, not Python) you can extend the features of corefacility
by creating your own corefacility extension, or _corefacility module_.

### Corefacility module is usual Django application

Start this application by the following command:

```commandline
python3 corefacility/manage.py startapp <name-of-your-application>
```

### Write your Backend side of the application

The application is created as additional package inside the corefacility application directory. Put your
own code there.

_Don't forget to develop the App class_: this class must contain exactly in the package root module and must
be a subclass of the `core.entity.corefacility_module.CorefacilityModule` class.

### Tell corefacility that you have been created application

Put your application root module to the `applications.list` file and reconfigure the corefacility:

```commandline
python3 corefacility/manage.py configure
```

### Create application tables

There are two types of migration files you need to create - initialization migration files and installation
migration files. The initialization migration files create all tables connected with your application. The
installation migration files link your application to the corefacility. To create initialization migration
scripts use the following command:

```commandline
python3 corefacility/manage.py makemigrations
```

To create installation migration files use the following command:

```commandline
python3 corefacility/manage.py makeinstall
```

When you create all migration files run them:

```commandline
python3 corefacility/manage.py migrate
```

### Create frontend

In order to create frontend use the following commands:

```commandline
cd frontend/apps
npx create-react-app
npm run build
cd ..
./build.sh
```

Next, write your frontend code using the classes containing in the `corefacility-base` module. The frontend
code must be compiled and put into Django static files list using the following command:

```commandline
./build.sh
```

Now your own application works.