# corefacility

Documentation for Russian speakers:
https://github.com/serik1987/corefacility/wiki

Non-Russian speakers are unable to receive
any kind of documentation. Please, contact
the following person if you still require
this documentation:

> Prof. Igor V. Bondar, D.Sc., Chief of the Department  
> Laboratory of Physiology of Sensory Systems  
> the Institute of Higher Nervous Activity and Neurophysiology,  
> Russian Academy of Sciences  
> E-mail: bondar@ihna.ru

Here we will mention core aspects of how to install and deploy the application

## Requirements

The application is written on Python 3.8 and hence will not work without this interpreter. The following Python
packages shall be installed in advance using PIP utility:

* psutil
* django
* django-configurations
* django-restframework
* python-dotenv
* pillow

## Stage 1. Download and install your application

We suppose that you have already installed python 3.8 or higher, PIP and all python
dependencies required by the application (see github wiki for details) as well as git client.

To download the application use the following command:

    git clone https://github.com/serik1987/corefacility.git

The last step in this stage is to define the configuration defaults. Use the following command to do this
(it doesn't matter what operating system to use):

    python corefacility/corefacility/manage.py configure

If you complete this stage correctly you will see 'corefacility' folder that contains the following files:

* corefacility - the application files itself
* settings - the application settings. You will see several .env files. You need to edit these files to make your
application working properly
* venv - if you want to run this application from a virtual environment you will also see these files
* db.sqlite3 - if you use SQLite all information located in the database will be saved here
* .gitignore - This file makes github working properly
* .git - this folder makes github working properly
* LICENSE, README.md - these files doesn't influence on the program functionality

## Stage 2. Select an appropriate configuration profile

During this stage you need to find a compromise between security, installation simplicity
and functionality of the application by choosing an appropriate installation profile.
Each profile correspond to a certain function.

| Profile name        | Profile ID                  | Ports that shall be listened | Required  operating system | Access to /etc/shadow | Base project dir | SSH access to all users | Remote access to the application | Hardware health check | Overall security | Difficulty to install |
| ------------------- | --------------------------- | ---------------------------- | -------------------------- | --------------------- | ---------------- | ----------------------- | -------------------------------- | --------------------- | ---------------- | --------------------- |
| Full server         | FullServerConfiguration     | 1-1024                       | UNIX-like                  | Required              | /home            | provided                | Allowed                          | provided              | Medium           | High                  |
| Part server         | PartServerConfiguration     | 1-1024                       | UNIX-like                  | Not required          | /home            | instructed **           | Allowed                          | instructed**          | High             | High                  |
| Virtual server      | VirtualServerConfiguration  | 1-1024                       | Recommended UNIX-like *    | Not required          | ~/research       | not available           | Allowed                          | not allowed           | High             | High                  |
| Extended standalone | ExtendedLaunchConfiguration | any port                     | UNIX-like                  | Required              | ~/My Research    | not available           | Not allowed                      | provided              | Absolute         | Medium                |
| Simple standalone   | SimpleLaunchConfiguration   | any port                     | any                        | Not required          | ~/My Research    | not available           | Not allowed                      | not allowed           | Absolute         | Low                   |

\* 'Recommended UNIX-like' means that theoretically such a configuration can be run under
non-UNIX operating system but in practise we don't test this thing. So, you can apply
it but just on your risk.

** 'instructed' means that the application will not perform any UNIX administration tasks by itself. Instead it will write
a user some BASH commands and require him to login to the server via SSH and run these commands

Select an appropriate configuration profile from the table above by double-clicking on corresponding
profile ID and pressing Ctrl-C. Now open the settings/preliminary.env
configuration file and paste (Ctrl-V) the configuration profile ID after `DJANGO_CONFIGURATION=` line. For example
if you prefer the VirtualServerConfiguration your preliminary.env file must look like here:

    DJANGO_CONFIGURATION=VirtualServerConfiguration

Alternatively you can set an appropriate environment variable before starting the server like here:

    set DJANGO_CONFIGURATION=PartServerConfiguration
    python corefacility/manage.py runserver

(Written above is some kind of Bash script)

## Stage 3. Setup minor settings

Since you selected the basic configuration profile you need to adjust the minor settings like
the address of the mail server, destination of the static root directory or database access credentials.

To do this please, edit the rest of .env files located in the settings directory.

Each file correspond to a particular purpose of configuration properties located here:

| Config file     | Purpose of config parameters                                                             |
|-----------------|------------------------------------------------------------------------------------------|
| basics.env      | Basic configuration setup (allowed hosts and IP addresses, language and time zone etc.)  |
| sql.env         | Access credentials to the database                                                       |
| email.env       | These settings are important for sending e-mail notifications                            |
| staticfiles.env | Defines how the application will collect and process static files                        |
| secret.env      | Defines the secret key                                                                   |
| security.env    | Defines how the application will deal with HTTP and HTTPS connections                    |

Each line in the configuration file correspond to a particular configuration parameter and looks like:

    PARAMETER_NAME=PARAMETER_VALUE

The line must contain an equal ('=') sign. The parameter name is given before the equal sign while its value
is located after it. The parameter name and parameter value must be separated from each other by a single equal
sign, NO EXTRA SPACES ARE PERMITTED.

Depending on a certain parameter and its purpose the parameter value can be:

* either `yes` or `no`
* some positive integer
* some arbitrary string
* Comma-separated list of strings like: `ihna.ru,www.ihna.ru` In this case string separator is comma only,
no extra spaces permitted

Another way to set the application configuration is to define the same parameters using the operating
system environment variables. The following Bash script will also be OK:

    export PARAMETER1=VALUE1
    export PARAMETER2=VALUE2
    .......
    python corefacility/manage.py runserver

Configuration options read from environment will also override the configuration options read from .env files.

Please, don't touch `secret.env` file. This file was created during the system configuration and contains a secret key
related to security. The file will be created or modified automatically

### Stage 3.1. Defining basic settings (basics.env)

This is how basics.env file looks like:

    DJANGO_ADMIN_NAME=Bill Gates
    DJANGO_ADMIN_EMAIL=bill.gates@microsoft.com

    DJANGO_ALLOWED_HOSTS=192.168.0.10,127.0.0.1,localhost
    DJANGO_ALLOWED_IPS=192.168.0.0/24,192.168.88.0/24
    DJANGO_DEBUG=yes

    DJANGO_LANGUAGE_CODE=ru-ru
    DJANGO_TIME_ZONE=Europe/Moscow

The file contains three sections.

The first section defines name of the web server administrators.
When critical errors occured during the application job a corresponding message will be sent to
the application author and its copy will be sent to the system administrator which name is defined
by the `DJANGO_ADMIN_NAME` property and its E-mail is defined by the `DJANGO_ADMIN_EMAIL` property.
These two parameters don't work for virtual server, extended desktop and simple desktop
configurations. No e-mails will be sent when `DJANGO_DEBUG` property is `yes`

The second section is connected with the web server security and contains the following properties:
* `DJANGO_ALLOWED_HOSTS` the list of IP addresses or domain names assigned to your server. More formally,
the application will accept only such requests where value of the 'Host' header is within this list.
When you access the application from your web browser and use the following URL http://hostname:port/location
you will get an error 500 if hostname is not within this list.

A value beginning with a period can be used as a subdomain wildcard: '.example.com' will match example.com,
www.example.com, and any other subdomain of example.com.

* `DJANGO_ALLOWED_IPS` When the application is configured as 'Full Server Configuration' you can
add Linux users and group or perform another Linux administrative routines only when you try to access
the server from the remote host which IP is within this range. When you used any other configuration profile
execution of direct administrative routines is prohibited from any host.

The value is a list of IP addresses of single hosts or pairs of addresses of masks of subnetworks.
Example: `192.168.88.1,192.168.24.0/24,192.168.0.0/24`

* `DJANGO_DEBUG` Allows you to debug the application itself, not the server. If you are not program developer
turn this option to False

The third section defines the program localization. It contains two parameters: `DJANGO_LANGUAGE_CODE` and
`DJANGO_TIME_ZONE`. `DJANGO_LANGUAGE_CODE` defines language and regional settings that will be used for
writing messages. Examples: `ru-ru`, `en-gb`, `en-us` etc. The list of all available values are given here:
http://www.i18nguy.com/unicode/language-identifiers.html

`DJANGO_TIME_ZONE` must be set to a local time zone where the web server is located. List of available time
zones is here:
https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Stage 3.2. SQL configuration

The application saves small information in databases while large information is saved to regular files. At this
stage you need to tell the application in what way it shall interact with database management system. Of course,
such management system shall be installed before execution of this step. An SQLite is an exception: since such
system has already embedded to this application you are not required to install it.

Use the following table to choose an appropriate database management system

| Database management system | Installation website        | Additional Python package to install | management system ID          | Installation difficulty | Stability, functionality and thread safety        |
|----------------------------|-----------------------------|--------------------------------------|-------------------------------|-------------------------|---------------------------------------------------|
| SQLite                     | no installation required    | Not required                         | django.db.backends.sqlite3    |                         | not stable, little functionality, not thread-safe |
| MySQL                      | https://www.mysql.com/      | mysqlclient                          | django.db.backends.mysql      | * * *                   | stable, moderate functionality, thread-safe       |
| PostgreSQL                 | https://www.postgresql.org/ | psycopg2                             | django.db.backends.postgresql | * * *                   | stable, high functionality, thread-safe           |

Please, provide an installation of appropriate database management system together with installing additional python
package which you need to add using pip utility. If you use MySQL of PostgreSQL prepare credentials that this
application will be used to gain access to the database. Also, don't forget to create the database where the application
will write its data.

Next, look at the "management system ID" column at this table. Find the management system ID corresponding to the
selected management system, copy it to your clipboard, then open `sql.env` file in text editor and use this ID to
set the `DJANGO_SQL_BACKEND` parameter.

Finally, define another properties in the `sql.env`:

| property name       | property value (for SQLite)                            | property value (for MySQL, PostgreSQL)                                 |
|---------------------|--------------------------------------------------------|------------------------------------------------------------------------|
| DJANGO_SQL_NAME     | name of a file where all database data will be written | Name of a database where this application write all its tables         |
| DJANGO_SQL_SERVER   | this option has no effect: don't touch this            | Name of a server where the management system is installed              |
| DJANGO_SQL_PORT     | this option has no effect: don't touch this            | Port listening by your SQL server                                      |
| DJANGO_SQL_USER     | this option has no effect: don't touch this            | The application will use these credentials gain access to the database |
| DJANGO_SQL_PASSWORD | this option has no effect: don't touch this            | The application will use these credentials gain access to the database |

### Stage 3.3. E-mail configuration

The application will notify the system administrator about errors in hardware or software as well as notify
you and all your users about all important steps (e.g., including to the project etc.). E-mails are crucial during
another stages like password reminding.

If you use Simple Desktop configuration or Extended Desktop configuration just skip reading this section because
no e-mails can be sent in this case. However, for Virtual servers, Part servers and Full servers e-mail delivery
is possible.

Use the following configuration parameters to define your E-mail settings

* `DJANGO_DEFAULT_FROM_EMAIL` the application implies that all e-mails will be sent from this address. This will be
used to define the value of the 'From' header and to tell the SMTP server a particular mailbox that will be used for
sending mails
* `DJANGO_EMAIL_BACKEND` you need to select an appropriate way to deliver E-mails copy the ID of this way and
paste this ID at the right of this option

| Way to deliver E-mails                                           | Way ID                                           |
|------------------------------------------------------------------|--------------------------------------------------|
| The application will use external SMTP server to deliver e-mails | django.core.mail.backends.smtp.EmailBackend      |
| The message to deliver will be printer on console                | django.core.mail.backends.console.EmailBackend   |
| The message will be saved to some local file on the hard disk    | django.core.mail.backends.filebased.EmailBackend |
| Delete the message and do nothing with it                        | django.core.mail.backends.dummy.EmailBackend     |

As you see, using SMTP server is the only way to deliver e-mails. However, it requires SMTP server to be installed
and properly configured. If you don't want to do this, you can use an external SMTP server for mass mail delivery
like gmail or mail.ru

* `DJANGO_EMAIL_FILE_PATH` if you decided to save e-mails on the hard disk drive tell the folder where the file must be
located
* `DJANGO_EMAIL_HOST` if you use SMTP server to deliver e-mail, write down the server address. Otherwise don't touch
this option
* `DJANGO_EMAIL_PORT` if you use SMTP server to deliver e-mail, tell what port it listens to. Otherwise don't touch
this option
* `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD` if you use SMTP server and you are required to login provide
your credentials here. Otherwise, don't touch this option
* `DJANGO_EMAIL_USE_TLS` Whether to use a TLS (secure) connection when talking to the SMTP server. This is used for
explicit TLS connections, generally on port 587.
* `DJANGO_EMAIL_USE_SSL` Whether to use an implicit TLS (secure) connection when talking to the SMTP server. In most
email documentation this type of TLS connection is referred to as SSL. It is generally used on port 465. If you are
experiencing problems, see the explicit TLS setting EMAIL_USE_TLS.

Note that EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set one of those settings to True.

### Stage 3.4. Configuring static files collection

If you access this application directly (especially, when you use Simple Desktop and Extended Desktop configurations)
you shall omit this step. However, if the user access it indirectly through NGINX or any other web server you need
to read this stage carefully

All information delivered to the remote user can be divided into three categories:
* Dynamic information: the information is generated during the request and can't be retrieved outside the application;
* Static files: the files have already located on your hard disk and shall be delivered to the final user without any
changes. Static files can be retrieved without using this application;
* Media files: the media files are delivered to the application like static files. However such files are uploaded by
by the user rather than supplied by the application manufacturers.

To improve the web server performance static and media files will be delivered by the web proxy server directly, no
need is required. However, you need to define a folder where static files are located. Since such folder is defined,
edit `staticfiles.env` configuration settings to tell the corefacility:

* `DJANGO_STATIC_ROOT` directory where static files were located
* `DJANGO_MEDIA_ROOT` directory where media files were located

These parameters will be ignored if you will not try to collect all static files for the NGINX web server and
don't want to use the Web proxy server.

### Stage 3.5. Security settings

Please, skip reading this file and don't touch security.env file if you don't receive SSL certificate and did not try
working with this application using HTTPS protocol. In this case passwords and any personal data will be compromised.

By default, application allows interaction with the user by means of HTTP protocol. All passwords and another personal
data are transmitted to the web server in non-encrypted manner and can be listened by the third side (so called 'attack
at the middle').

To adjust security settings you have to check whether nginx interacts with this application though HTTP or HTTPS.
You can check this by looking for `proxy_pass` parameter inside your NGINX settings file. If you see `http://`
inside the value of this parameter you can adjust your security settings in the following way: the user connects
to NGINX through HTTPS. Next, nginx decrypts the request and send it to this application using HTTP, not HTTPS.
This is OK for security but you need to refer to your NGINX documentation to adjust the security settings not this
manual.

If you don't want this to happen, first, you need to implement HTTPS connection to your application. After the
application main page is loaded through HTTPS perfectly, mind about changing the following properties:

* `DJANGO_SECURE_SSL_REDIRECT` If this option equals to `yes` all request received using HTTP protocol will be
redirected to HTTPS. The default option value is `no` which means that HTTP request will be processed in the same
way as HTTPS requests
* `DJANGO_SECURE_SSL_HOSTNAME` If `DJANGO_SECURE_SSL_REDIRECT` is `no` this option takes no effect. Otherwise it
defines name of a server responsible for processing HTTPS requests. Leave this option empty if HTTP and HTTPS requests
are processed by the same server.
* `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`, `DJANGO_SECURE_HSTS_PRELOAD` When the response
is sent to the client using HTTP this option takes no effect. However, when the response is sent using HTTPS protocol
`Strict-Transport-Security` response header will be added at the end of request processing. This header tells
the web browser to prohibit any attempt to access this application using HTTP protocol. These three parameters are
used to adjust details of this header value: use `DJANGO_SECURE_HSTS_SECONDS` to define `max-age` option. Setting
`DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` will include `includeSubDomains` to the header value and
`DJANGO_SECURE_HSTS_PRELOAD` will include `preload` to the header. The additional information about strict transport
security is provided here:
https://developer.mozilla.org/ru/docs/Web/HTTP/Headers/Strict-Transport-Security

