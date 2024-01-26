# 1. Main usage

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

# 2. Developers

(c) Sergei Kozhukhov, scientist in the Institute of Higher Nervous Activity, RAS

E-mail: sergei.kozhukhov@ihna.ru

URL: https://www.ihna.ru/ru/employees/sergei.kozhukhov

(c) the Institute of Higher Nervous Activity and Neurophysiology, Russian Academy of Sciences, Moscow,
Russia

Address: 5A Butlerova str., Moscow, Russia

E-mail: admin@ihna.ru

Phone number: +7 (495) 334-70-00

# 3. Замечание для русскоязычных пользователей

Работая с данным продуктом, Вы принимаете условия лицензионного соглашения, изложенные в файле LICENSE.txt

К сожалению, данная инструкция доступна на английском языке. В случае возникновения каких-либо затруднений
в установке пожалуйста, обратитесь к разработчикам за консультацией.

# 4. Installation instructions

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

## 4.1. Installation instruction for the full server configuration and the part server configuration.

We imply that you are an experienced Linux user. So, if this is not the case, refer to the following literature to
fill the gaps in such skills:

Nemett, E., Snyder G. Unix and Linux System Administration Handbook. Fifth Edition.

The reference manual below is one of several possible ways to install the corefacility.

### 4.1.1. Pre-requisites

We imply that you try to install the corefacility to the high-performance server without GUI support. Such configuration
is the most preferrable because the GUI support wastes extra resources, declines the server uptime and can be
replaced by the corefacility Web-based GUI that doesn't waste extra resorces and affect the server uptime.

This kind of corefacility configuration support only UNIX-like operating systems. The reference below is written for
the Linux Ubuntu Server operating system. This means that any other UNIX-like operating system is also OK, but you
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
wget https://github.com/serik1987/corefacility/releases/download/v.0.0.2/corefacility-0.0.2-py3-none-any.whl
```

Press Enter to execute the command. The command will download the distribution to the home folder on the server.

After the package has been downloaded use the following command to install this.

```commandline
sudo pip install $(ls *.whl)
```

You have to inquire that your current directory contains only one whl-file. If this is not the case, the command above
will not work, you have to replace the `$(ls *.whl)` directive to the name of the recently downloaded file. 

### 4.1.2. Preliminary setup

Scan the corefacility application for list of all available extensions. This could be done by the following
command

```commandline
sudo corefacility configure
```

After this command will run correctly, you will see the `/etc/corefacility/django-settings` folder.
The next step is to configure
the application by changing special .env files. Each such file contain line in the following form:

```dotenv
key=value
```

where a name of an option is on the left side of the equal (=) sign and value of such an option is on the right side
of the equal sign. Please, change the value of the option and don't touch the name of the option.

### 4.1.3. Selection of application configuration mode

To select the configuration profile you need to open the `/etc/corefacility/django-settings/preliminary.env` file.

The file has the only option - `DJANGO_CONFIGURATION`. Please, type here one of the following configuration values:

* `FullServerConfiguration` for the full server configuration (automatics confirmation of POSIX administrative
operations)
* `PartSeverConfiguration` for the partial server configuration (manual confirmation of POSIX administrative operations)

Despite what configuration mode is selected, all administrative operations will be performed by a special daemon,
not the Web server itself.

### 4.1.4. Preliminary security settings

You need to specify the system POSIX user on behalf of which the Web server will process request. Such specification
must be selected based on the following notes:

1. A POSIX process that is responsible for processing the HTTP requests must be allowed to perform all actions defined
by its specification.
2. When the Web server is hacked, it must not be allowed to provide operating system administrative tasks.

Based on these notes you must ensure that the special POSIX account for the Web server has been created. To do this
use the following command:

```commandline
cat /etc/passwd | grep www-data
```

If such account doesn't exist, create it by using the following command:
```commandline
sudo useadd -r -d / -s /bin/false www-data
```

We assume on the rest of this instruction that a given system account has the following name: `www-data`. Make certain
corrections if this is not true.

At last, you have to change the ownership of your settings directory:

```commandline
sudo chown www-data:www-data /etc/corefacility/django-settings
```

Because the Django settings contain credentials to personal data of all corefacility users they must be protected from
reading and writing:

```commandline
sudo chmod 0750 /etc/corefacility/django-settings
```

### 4.1.5. Basic settings

To adjust basics settings of the corefacility application you are required to open the
`/etc/corefacility/django-settings/basics.env` file. You have to adjust the following options:

* `DJANGO_ADMIN_NAME` Your full name.
* `DJANGO_ADMIN_EMAIL` Your e-mail address. In case of troubles error messages will be sent here. Also, when POSIX
administrator operations are executed by corefacility you will also receive corresponding notifications on this address.
* `DJANGO_ALLOWED_HOSTS` When the corefacility Web server receives the HTTP request, it contains the `Host:` header.
If the host name specified in this header is not in the list provided by this option the request will be rejected.
You are recommended to specify the IP address as well as domain name of your server / virtual server. Separate several
host names by commas (don't use spaces, only commas).
An example is: `DJANGO_ALLOWED_HOSTS=192.168.0.10,corefacility.ru,www.corefacility.ru`
* `DJANGO_ALLOWED_IPS` administrative operations (i.e., CRUD operations on users or projects, setting project rights)
can be made only from IP addresses mentioned in this list. List items shall be separated by commands and can contain
either IP addresses for stand-alone hosts or adresses for the whole network written by means of CIDR notation.
* `DJANGO_DEBUG` leave this value to `yes`
* `DJANGO_LANGUAGE_CODE` defines the language for the Web interface. This option doesn't affect the language of the
Command Line Interface (CLI). The language code must contain the name of the language and locale codes separated by
dash. The language and locale codes must be written using the ISO 639-1 standards. An examples:

`en-GB` English (Great Britain)

`ru-RU` Russian (Russia)

* `DJANGO_TIME_ZONE` The time zone where your server is located. Examples are: `Europe/Moscow`, `UTC` etc. Please, find
the full list of timezones here: `https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#cite_note-1`.
* `DJANGO_CORE_WORKER_PROCESS_USER` You must create a special pseudo-user on behalf of which the Web server will run.
Use `useradd` or `adduser` POSIX commands for such a purpose


To check that all settings have been made correctly run the following command:

```commandline
sudo -u www-data corefacility shell
```

If you see the Python shell it means that all settings have been made correctly. Quit from the shell by running the
following command:

```python
quit()
```

### 4.1.6. Installation of SQL server

The SQL database management system is required to store information about users and projects, optimize the search,
resolve the conflicts when several processes request the same resource etc.

We strongly recommend you to use PostgreSQL server for such a purpose. However, you are also free to use MySQL. Any
other database management systems are not supported by corefacility.

The instructions mentioned in this section imply that you use PostgreSQL. This is your responsibility to find another
instructions related to the MySQL.

First of all, check for `https://postgresql.org/download` to find how to install the PostgreSQL on your server. After
you do this successfully create stand-alone database for the corefacility web server using the following command:

```commandline
sudo -u postgres createdb corefacility
```

Create a special SQL user on behalf of which the corefacility Web server will send SQL queries to the database server.

```commandline
sudo -u postgres createuser -P corefacility
```

Think and type the password of this user.

Next, enter the corefacility database:

```commandline
sudo -u postgres psql corefacility
```

Change the privileges for the corefacility user:

```sql
GRANT ALL ON DATABASE corefacility TO corefacility;
GRANT ALL ON SCHEMA public TO corefacility;
```

Exit from the SQL client by typing:

```
\q
```

After you installed the SQL server you have to install the SQL client. The SQL client is a special Python package
that is used by the corefacility to interact with the SQL server. Use `psycopg2` for the PostgreSQL and `mysqlclient`
for the MySQL. In case of Postgresql use the following command to install the SQL client:

```commandline
sudo pip install psycopg2
```

Open the `/etc/corefacility/django-settings/sql.env` file to write down the SQL settings. The SQL settings are required
for corefacility to access the SQL database. You need to adjust the following settings:

* `DJANGO_SQL_BACKEND` If you selected the Postgresql use the following value: `django.db.backends.postgresql`
If toy selected the MySQL use the following value: `django.db.backends.mysql`
* `DJANGO_SQL_NAME` Name of the database (Use `corefacility` in the example above).
* `DJANGO_SQL_SERVER` Address of your SQL server (Use `localhost` in the example above).
* `DJANGO_SQL_PORT` A port listening by the SQL server. If you didn't change the SQL server default settings,
PostgreSQL listens to the port `5432` while MySQL listens to the port `3306`.
* `DJANGO_SQL_USER` Name of the database user on behalf of which the corefacility accesses the database.
Use `corefacility` in the example above
* `DJANGO_SQL_PASSWORD` A password you have set for the corefacility database user. Have you still remembered it?

And the last stage is to create SQL tables. Allow the corefacility to do this by running the following command:

```commandline
sudo corefacility migrate
```

If the migration process completed successfully, this means that all corefacility settings have been accomplished.

### 4.1.7. Distribution of static  and media files

__Static files__ are stand-alone files containing in the corefacility distribution that the server must distribute to
the client hosts as they are, that is, without any modification. The static files include a frontend application, CSS
tables, translation tables used by the Web browser, images and icons etc.

__Media files__ are stand-alone files uploaded by the corefacility users that: (a) have public access (i.e., anybody
can read these files); (b) shall be distributed by the server to the client hosts without any modification. Examples of
media files are user's avatars, project icons etc.

corefacility can't distribute media files among the client effectively. So, you need to use a third-party Web server
for such purpose. We recommend you to use nginx.

First, look at the `https://nginx.org/ru/linux_packages.html`. Follow instructions mentioned there to download and
install the nginx server.

The following text is based on the assumption that the public root for the nginx server is `/usr/share/nginx/html`.
If you intend to store the Web server files to another directory, just make necessary substitutions in the POSIX
commands given below.

First of all, you need to configure the nginx server. Download the special configuration made for the corefacility:

```commandline
wget https://raw.githubusercontent.com/serik1987/corefacility/main/server_config/nginx/default.conf
```

This command will download the `default.conf` file to your folder. Copy this file to the nginx configuration folder:

```commandline
sudo cp default.conf /etc/nginx/conf.d
```

You can modify the nginx configuration files at this stage and check that the configuration options are valid. After
you finish doing this restart the nginx server to apply the configuration settings:

```commandline
sudo service nginx restart
```

Change the ownership to the document root:

```commandline
sudo chown -R www-data:www-data /usr/share/nginx/html
sudo chmod 02775 /usr/share/nginx/html
```

Check that the nginx user is in the www-data group:

```commandline
sudo usermod -aG www-data nginx
```

Next, tell the corefacility where the static files are located. To do this, open the
`/etc/corefacility/django-settings/staticfiles.env` file for editing. Adjust the following options:

* `DJANGO_STATIC_ROOT` an absolute path to the folder where static files are located. This folder shall be `static` and
must be located inside the document root of the nginx server.
* `DJANGO_MEDIA_ROOT` an absolute path to the folder where media files are located. This folder shall be `media` and
must be located inside the document root of the nginx server.

Here is an example of an optimal settings for this file:

```commandline
DJANGO_STATIC_ROOT=/usr/share/nginx/html/static
DJANGO_MEDIA_ROOT=/usr/share/nginx/html/media
```

When all settings are done: fill the document root of your nginx folder by the corefacility static and media files:

```commandline
sudo corefacility collectstatic
```

Ensure that the `/usr/share/nginx/html` folder contains the following sub-folders:

* `media` that must be empty at this stage. Media files will be located at this directory.
* `static` filled by the static files.

Ensure that the static files are distributed correctly. To do this, follow the following URL in your Web browser:

```commandline
https://<your-host-name>/static/ru.ihna.kozhukhov.core_application/user.svg
```

You must see the user icon.

### 4.1.8. Connecting nginx and gunicorn

The nginx Web server accepts all HTTP requests from the client hosts. In order to make the corefacility server working,
some of the requests must be redirected from the nginx to the corefacility. The easiest way to do this is to install
a simple connector called `gunicorn`. To install the gunicorn use the following command:

```commandline
sudo apt install gunicorn
```

The gunicorn is another Web server. All HTTP requests excluding the requests to static files are received by nginx,
then redirects to the gunicorn that are processed by the corefacility. The connection between nginx and gunicorn is
established by the Unix socket. Such a socket must be accessible for the root and the www-data user (effective users
for both web servers) but inaccessible for ordinary POSIX users. The best way to do this is to create a specific folder
where such socket is located:

```commandline
sudo mkdir /var/gunicorn
sudo chown www-data:www-data /var/gunicorn
sudo chmod 0770 /var/gunicorn
```

Open the `/etc/nginx/conf.d/default.conf` file and ensure that it refers to the `/var/gunicorn/gunicorn.sock` file.

On the next stage check that the corefacility Web server works file: Try the following command on the command line:

```commandline
sudo -u www-data gunicorn
    --workers=3 \
    --bind=unix:/var/gunicorn/gunicorn.sock \
    --access-logfile=/var/log/gunicorn/access.log \
    --error-logfile=/var/log/gunicorn/error.log
    ru.ihna.kozhukhov.corefacility.wsgi:application
```

Ensure that the gunicorn server started correctly. Then, ensure that corefacility works correctly - just follow the link
on your Web browser: `http://<name-or-IP-address-of-your-Web-server`.

If everything is file, press <Ctrl-C> to quit the gunicorn Web server.

The last stage is to tell the systemd to run the gunicorn server at startup.

To do this, first, download the systemd configuration for the gunicorn.

```commandline
wget https://raw.githubusercontent.com/serik1987/corefacility/main/server_config/gunicorn.service
```

Next, copy this configuration file to the systemd system configuration folder:

```commandline
sudo cp gunicorn.service /etc/systemd/system
```

Then, edit this file is necessary. Finally, start and enable the gunicorn service.

```commandline
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

You can restart your server to ensure that the corefacility server works correcly.

### 4.1.9. Adjustment of E-mail delivery

All corefacility users are required to receive E-mails from your server. The e-mails are important for the password
recovery and notification about an important things. To allow the corefacility to deliver e-mails you need to first,
adjust the SMTP server (this is an application that delivers mails) and second, adjust the interaction between the
corefacility and the SMTP server.

You can choose an internal or external SMTP server. An internal one is an SMTP server application (a postfix is a good
example) that you need to install and configure. An external server is https://www.mail.ru, https://www.gmail.com etc.
services where you need to create an additional mail box (e.g., corefacility_no-reply@gmail.com etc.). Check the
reference manual of your external server, this will help you to adjust the corefacility.

The external server is the only option when your server has no public access (i.e., is accessible from intranet or VPN).

To adjust the integration between the corefacility and the SMTP server open the
`/etc/corefacility/django-settings/email.env` file for editing. Set up the following options:

* `DJANGO_DEFAULT_FROM_EMAIL` the mailbox your created on the external or internal SMTP server. Despite what kind of
server you use, you need one external mailbox for the corefacility.
* `DJANGO_EMAIL_BACKEND` for this type of configuration it must be equal to
`django.core.mail.backends.smtp.EmailBackend`
* `DJANGO_EMAIL_HOST` E-mail host name. Consult the reference manual on the SMTP server for details.
* `DJANGO_EMAIL_PORT` Port listening by the SMTP service. Consult the reference manual on the SMTP server for details.
* `DJANGO_EMAIL_HOST_USER` Login from the mailbox account.
* `DJANGO_EMAIL_HOST_PASSWORD` Password from the mailbox account.
* `DJANGO_EMAIL_SUBJECT_PREFIX` Prefix to the E-mail headers.
* `DJANGO_EMAIL_USE_TLS` whether the SMTP server uses the TLS encryption. Available values are: `yes` or `no`
* `DJANGO_EMAIL_USE_SSL` whether the SMTP server uses the SSL encryption. Available values are: `yes` or `no`

When all these settings are made, check out how they are correct. Just do the following things.

First, enter the corefacility shell:

```commandline
sudo -u www-data corefacility shell
```

Next, try to send e-mail:

```python
from django.core.mail import send_mail
send_mail("This is the test message", "A test message from the corefacility.", "no-reply@gmail.com", ["your-box@gmail.com"])
```

where "no-reply@gmail.com" must be substituted to the additional mailbox you created for the corefacility and
"your-box@gmail.com" is your personal mailbox.

Ensure that the test mail has been delivered successfully and close the Python interpreter.

```python
quit()
```

### 4.1.10. SSL encryption properties

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