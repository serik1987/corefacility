# Main usage

The corefacility facilitates the neuroscience research and application of high-performance servers in Neuroscience
by providing the following features:

1. The corefacility provides very simple and understandeable interface that:
   1. doesn't engage the server resource (e.g., the CPU time, operating memory);
   2. doesn't decline the server uptime;
   3. allows several users to work on the same server simultaneously.
2. The corefacility manages user accounts and provides the following security issues:
   1. GUI interface for managing the opertating system users and group;
   2. Managing user access rights to the experimental data;
   3. User authorization, authentication, accounting, lock/unlock etc.
3. The corefacility operates some administrative tasks in background:
   1. Alarming the user when sufficient health check values are beyond the normal range (i.e., when the CPU temperature
is too high or amount of free operating memory is too low).
   2. Providing the every-month health check diagnostics and experimental database backups.
4. The corefacility will distribute computational resources among different users.

# Developers

(c) Sergei Kozhukhov, scientist in the Institute of Higher Nervous Activity, RAS

E-mail: sergei.kozhukhov@ihna.ru

URL: https://www.ihna.ru/ru/employees/sergei.kozhukhov

(c) the Institute of Higher Nervous Activity and Neurophysiology, Russian Academy of Sciences, Moscow,
Russia

Address: 5A Butlerova str., Moscow, Russia

E-mail: admin@ihna.ru

Phone number: +7 (495) 334-70-00

# Замечание для русскоязычных пользователей

Работая с данным продуктом, Вы принимаете условия лицензионного соглашения, изложенные в файле LICENSE.txt

К сожалению, данная инструкция доступна на английском языке. В случае возникновения каких-либо затруднений
в установке пожалуйста, обратитесь к разработчикам за консультацией.

# Installation instructions

In order to start the installation process choose one of the following system configurations:

* __Full server configuration__: The configuration is suitable for dedicated / virtual private servers and imply that
you gain the administrative privileges to corefacility. The corefacility under the full server configuration will 
provide an automatic management of operating system accounts and groups and user access to experimental data.

* __Part server configuration__: The configuration is also suuitable for dedicated / virtual private servers but doesn't
provide an automatic management of operating system accounts and groups. This means that the corefacility is still able
to provide the account management but only with the help of the system administrator. Use such configuration if you
don't trust the security solutions of the corefacility.

* __Standalone configuration__: The configuration is suitable for your own computer and laptop when you want to run
the experimental data processing programme that requires the corefacility framework. The corefacility under the
standalone configuration will not provide the management of operating system accounts and will not manage an access
to experimental data.

## Installation instruction for the full server configuration and the part server configuration.

We imply that you are an experienced Linux user. So, if this is not the case, refer to the following literature to
fill the gaps in such skills:

Nemett, E., Snyder G. Unix and Linux System Administration Handbook. Fifth Edition.

The reference manual below is one of several possible ways to install the corefacility.

### Pre-requisites

We imply that you try to install the corefacility to the high-performance server without GUI support. Such configuration
is the most preferrable because the GUI support wastes extra resources, declines the server uptime and can be
replaced by the corefacility Web-based GUI that doesn't waste extra resorces and affect the server uptime.

The corefacility supports only UNIX-like operating systems under this support. The reference below is written for
the Linux Ubuntu Server operating system. This means that any other UNIX-like operating system is also OK but you
have to make necessary corrections when reading this manual.

The installation requires administrative rights even when the corefacility is run under the part server configuration.
So, if you don't have such rights, gain them.

First, upgrade all packages in your operating system:

```commandline
sudo apt update
sudo apt upgrade
```

Next, ensure, that the Python v. 3.10 or higher has already been installed.

```commandline
sudo apt install python3 python3-dev python3-pip libpq-dev
```

### Download and install the corefacility package

In order to download and install the corefacility follow the link below that contains the list of corefacility releases:

```
https://github.com/serik1987/corefacility/releases
```

Select the latest release, next, click on Assets and move the mouse to the name of the .whl file. Then you need to
right-click on the whl-file and copy the link to the release installation file to the clipboard.

To go the command line of your server type the `wget`, put space and paste the information from the clipboard to the
terminal. In the long run, you have to see something like this:

```commandline
wget https://github.com/serik1987/corefacility/releases/download/v.0.0.1/corefacility-0.0.1-py3-none-any.whl
```

Press Enter to execute the command. The command will download the distribution to the home folder on the server.

After the package has been downloaded use the following command to install this.

```commandline
sudo pip install $(ls *.whl)
```

You have to inquire that your current directory contains only one whl-file. If this is not the case, the command above
will not work, you have to replace the `$(ls *.whl)` directive to the name of the recently downloaded file. 

### Preliminary setup

Scan the corefacility application for list of all available extensions. This could be done by the following
command

```commandline
corefacility configure
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

`DJANGO_URL_BASE` is URL for the Web application main page.
The value of the property must be in the following form:
"""
scheme://hostname
"""
(without slash at the end!)
Here scheme is https is you intend to use HTTPS for your Web server or http otherwise and hostname is
 (a) 127.0.0.1 if you intend to run the corefacility only locally (SimpleLaunchConfiguration or
 		ExtendedLaunchConfiguration);
 (b) the domain name if you registered domain for your Web server;
 (c) IP address for your host if you don't register domain for your Web server

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

`DJANGO_CORE_PROJECT_BASEDIR` Defines a directory where all project files shall be stored. The parameter
is useful for `VirtualServerConfiguration`, `ExtendedLaunchConfiguration` and `SimpleLaunchConfiguration`
while `FullServerConfiguration` and `PartServerConfiguration` always use `/home` for this purpose.

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
corefacility migrate
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
corefacility collectstatic
```

### Trial launch

If everything is OK you need to run your Web server. To run the Web server in `SimpleLaunchConfiguration`
and `ExtendedLaunchConfiguration` use the following command:

```commandline
corefacility runserver
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
* Now the corefacility is safe

### Corefacility update

Always update your corefacility application because new updated version contain bug fixes and security
improvements. The corefacility application can be updated by the following command:

```commandline
git pull
```

Use your operating system to schedule the corefacility update!

## How to add new application to corefacility

### Tell corefacility that you have added your application

To do this open the `applications.list` file and write here full name of the application root module
on the new last line.

### Apply all changes

To apply all changes reconfigure your application by the following way:

```commandline
corefacility configure
```

Corefacility will tell Django where your application is located.

### Create tables in the database

In order to do this, repeat the migration process:

```commandline
corefacility migrate
```

### Static files collection

Collect all static files from your new application. In order to do this provide the following thing:

```commandline
corefacility collectstatic
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
corefacility startapp <name-of-your-application>
```

### Write your Backend side of the application

The application is created as additional package inside the corefacility application directory. Put your
own code there.

_Don't forget to develop the App class_: this class must contain exactly in the package root module and must
be a subclass of the `core.entity.corefacility_module.CorefacilityModule` class.

### Tell corefacility that you have been created application

Put your application root module to the `applications.list` file and reconfigure the corefacility:

```commandline
corefacility configure
```

### Create application tables

There are two types of migration files you need to create - initialization migration files and installation
migration files. The initialization migration files create all tables connected with your application. The
installation migration files link your application to the corefacility. To create initialization migration
scripts use the following command:

```commandline
corefacility makemigrations
```

To create installation migration files use the following command:

```commandline
corefacility makeinstall
```

When you create all migration files run them:

```commandline
corefacility migrate
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