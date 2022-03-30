![Atlassian Bamboo](https://wac-cdn.atlassian.com/dam/jcr:560a991e-c0e3-4014-bd7d-2e65d4e4c84a/bamboo-icon-gradient-blue.svg?cdnVersion=814)

Bamboo is a continuous integration and deployment tool that ties automated builds, tests and releases together in a single workflow.

Learn more about Bamboo: [https://www.atlassian.com/software/bamboo](https://www.atlassian.com/software/bamboo)

# Overview

This Docker container makes it easy to get an instance of Bamboo up and running.

This Docker image is published as both `atlassian/bamboo` and
`atlassian/bamboo-server`. These are the same image, but the `-server`
version is deprecated and only kept for backwards-compatibility; for new
installations it is recommended to use the shorter name.

# Quick Start

For the `BAMBOO_HOME` directory that is used to store the repository data
(amongst other things) we recommend mounting a host directory as a [data
volume](https://docs.docker.com/engine/tutorials/dockervolumes/#/data-volumes),
or via a named volume if using a docker version >= 1.9.

Additionally, if running Bamboo in Data Center mode it is required that a
shared filesystem is mounted.

To get started you can use a data volume, or named volumes. In this example
we'll use named volumes.

    $> docker volume create --name bambooVolume
    $> docker run -v bambooVolume:/var/atlassian/application-data/bamboo --name="bamboo" -d -p 8085:8085 -p 54663:54663 atlassian/bamboo


**Success**. Bamboo is now available on [http://localhost:8085](http://localhost:8085)*

Please ensure your container has the necessary resources allocated to it. We
recommend 2GiB of memory allocated to accommodate the application server. See
[System
Requirements](https://confluence.atlassian.com/display/BAMBOO/Bamboo+Best+Practice+-+System+Requirements)
for further information.

_* Note: If you are using `docker-machine` on Mac OS X, please use `open http://$(docker-machine ip default):8085` instead._

## Memory / Heap Size

If you need to override Bamboo's default memory allocation, you can control the minimum heap (Xms) and maximum heap (Xmx) via the below environment variables.

* `JVM_MINIMUM_MEMORY` (default: 512m)

   The minimum heap size of the JVM

* `JVM_MAXIMUM_MEMORY` (default: 1024m)

   The maximum heap size of the JVM

## Tomcat and Reverse Proxy Settings

If Bamboo is run behind a reverse proxy server as [described
here](https://confluence.atlassian.com/kb/integrating-apache-http-server-reverse-proxy-with-bamboo-753894403.html),
then you need to specify extra options to make Bamboo aware of the setup. They
can be controlled via the below environment variables.

* `ATL_PROXY_NAME` (default: NONE)

   The reverse proxy's fully qualified hostname. `CATALINA_CONNECTOR_PROXYNAME`
   is also supported for backwards compatability.

* `ATL_PROXY_PORT` (default: NONE)

   The reverse proxy's port number via which Bamboo is
   accessed. `CATALINA_CONNECTOR_PROXYPORT` is also supported for backwards
   compatability.

* `ATL_TOMCAT_PORT` (default: 8085)

   The port for Tomcat/Bamboo to listen on. Depending on your container
   deployment method this port may need to be
   [exposed and published][docker-expose].

* `ATL_TOMCAT_SCHEME` (default: http)

   The protocol via which the application is accessed. `CATALINA_CONNECTOR_SCHEME` is also
   supported for backwards compatability.

* `ATL_TOMCAT_SECURE` (default: false)

   Set 'true' if `ATL_TOMCAT_SCHEME` is 'https'. `CATALINA_CONNECTOR_SECURE` is
   also supported for backwards compatability.

* `ATL_TOMCAT_CONTEXTPATH` (default: NONE)

   The context path the application is served over. `CATALINA_CONTEXT_PATH` is
   also supported for backwards compatability.

The following Tomcat/Catalina options are also supported. For more information,
see https://tomcat.apache.org/tomcat-7.0-doc/config/index.html.

* `ATL_TOMCAT_MGMT_PORT` (default: 8007)
* `ATL_TOMCAT_MAXTHREADS` (default: 150)
* `ATL_TOMCAT_MINSPARETHREADS` (default: 25)
* `ATL_TOMCAT_CONNECTIONTIMEOUT` (default: 20000)
* `ATL_TOMCAT_ENABLELOOKUPS` (default: false)
* `ATL_TOMCAT_PROTOCOL` (default: HTTP/1.1)
* `ATL_TOMCAT_ACCEPTCOUNT` (default: 100)

The standard HTTP connectors (NIO, NIO2 and APR/native) settings

* `ATL_TOMCAT_ADDRESS`

   For servers with more than one IP address, this attribute specifies which 
   address will be used for listening on the specified port.

* `ATL_TOMCAT_SECRET` (default: null)

   Only requests from workers with this secret keyword will be accepted. The
   default value is null. This attribute must be specified with a non-null, 
   non-zero length value unless secretRequired is explicitly configured to be false. 
   If this attribute is configured with a non-null, non-zero length value then the workers
   must provide a matching value else the request will be rejected irrespective of the
   setting of secretRequired.

* `ATL_TOMCAT_SECRET_REQUIRED` (default: false)

   If this attribute is true, the AJP Connector will only start if the secret 
   attribute is configured with a non-null, non-zero length value. This attribute only 
   controls whether the secret attribute is required to be specified for the AJP Connector
   to start. It does not control whether workers are required to provide the secret. The
   default value is true. This attribute should only be set to false when the Connector 
   is used on a trusted network.

* `ATL_TOMCAT_BAMBOO_ENCRYPTION_KEY`
  
   File which contains encryption key used for Bamboo-specific connectors.

* `ATL_TOMCAT_SSL_ENABLED`

  Use this attribute to enable SSL traffic on a connector.

* `ATL_TOMCAT_SSL_PROTOCOL`

   JSSE only.  The SSL protocol(s) to use (a single value may enable multiple protocols
   - see the JVM documentation for details).
  
* `ATL_TOMCAT_SSL_CERTIFICATE_FILE`

   Name of the file that contains the server certificate. The format is PEM-encoded. 
   Relative paths will be resolved against $CATALINA_BASE.

* `ATL_TOMCAT_SSL_CERTIFICATE_KEY_FILE`

   Name of the file that contains the server private key. The format is PEM-encoded. 
   The default value is the value of certificateFile and in this case both certificate
   and private key have to be in this file (NOT RECOMMENDED). Relative paths will be 
   resolved against $CATALINA_BASE.

* `ATL_TOMCAT_SSL_PASS`

   The password used to access the private key associated with the server certificate 
   from the specified file.

* `ATL_TOMCAT_KEYSTORE_FILE`

   JSSE only. The pathname of the keystore file where you have stored the server certificate
   and key to be loaded. By default, the pathname is the file .keystore in the operating 
   system home directory of the user that is running Tomcat.

* `ATL_TOMCAT_KEYSTORE_PASS`

   JSSE only. The password to use to access the keystore containing the server's private
   key and certificate. If not specified, a default of _changeit_ will be used.

* `ATL_TOMCAT_KEY_PASS`

   The password used to access the private key associated with the server certificate 
   from the specified file.

* `ATL_TOMCAT_CLIENT_AUTH`
 
   Set to required if you want the SSL stack to require a valid certificate chain from
   the client before accepting a connection. Set to optional if you want the SSL stack
   to request a client Certificate, but not fail if one isn't presented. Set to optionalNoCA
   if you want client certificates to be optional and you don't want Tomcat to check them 
   against the list of trusted CAs. If the TLS provider doesn't support this option (OpenSSL
   does, JSSE does not) it is treated as if optional was specified. A none value (which is 
   the default) will not require a certificate chain unless the client requests a resource 
   protected by a security constraint that uses CLIENT-CERT authentication.

* `ATL_TOMCAT_TRUSTSTORE_FILE`

   JSSE only. The trust store file to use to validate client certificates. The default is
   the value of the javax.net.ssl.trustStore system property. If neither this attribute nor
   the default system property is set, no trust store will be configured. Relative paths will
   be resolved against $CATALINA_BASE. A URL may also be used for this attribute.

* `ATL_TOMCAT_TRUSTSTORE_PASS`
   JSSE only. The password to access the trust store. The default is the value of the 
   javax.net.ssl.trustStorePassword system property. If that property is null, no trust
   store password will be configured. If an invalid trust store password is specified, 
   a warning will be logged and an attempt will be made to access the trust store without
   a password which will skip validation of the trust store contents.

## JVM configuration

If you need to pass additional JVM arguments to Bamboo, such as specifying a
custom trust store, you can add them via the below environment variable

* `JVM_SUPPORT_RECOMMENDED_ARGS`

   Additional JVM arguments for Bamboo

Example:

    $> docker run -e JVM_SUPPORT_RECOMMENDED_ARGS=-Djavax.net.ssl.trustStore=/var/atlassian/application-data/bamboo/cacerts -v bambooVolume:/var/atlassian/application-data/bamboo --name="bamboo" -d -p 8085:8085 -p 54663:54663 atlassian/bamboo

## Bamboo-specific settings

* `ATL_AUTOLOGIN_COOKIE_AGE` (default: 1209600; two weeks, in seconds)

   The maximum time a user can remain logged-in with 'Remember Me'.

* `BAMBOO_HOME`

   The Bamboo home directory. This may be on an mounted volume; if so it
   should be writable by the user `bamboo`. See note below about UID
   mappings.

* `ATL_BROKER_URI` (default: nio://0.0.0.0:54663)

   The ActiveMQ Broker URI to listen on for in-bound remote agent communication.

* `ATL_BROKER_CLIENT_URI`

   The ActiveMQ Broker Client URI that remote agents will use to attempt to establish a connection to the ActiveMQ Broker on the Bamboo server.

* `ATL_BAMBOO_SKIP_CONFIG` (defaults to `False`)

   If `true` skip the generation of `bamboo.cfg.xml`. This is only really useful
   for Bamboo versions >= 8.1, which added environment-based configuration (see
   next section).

### Optional configuration pre-seeding

Optionally, for new deployments, the setup flow can be skipped by provided the
required values via the environment. NOTE: This only work with Bamboo versions >= 8.1.

* `SECURITY_TOKEN`

   The security token to use for server/agent authentication. Additional details
   [are available here](https://confluence.atlassian.com/bamboo/agent-authentication-289277196.html#Agentauthentication-SecuritytokenverificationSecuritytokenverification)

* `ATL_BAMBOO_DISABLE_AGENT_AUTH` (default: false)

   Whether to disable agent authentication. Defaults to false.

* `ATL_LICENSE`

   The licence to supply. Licenses can be generated at https://my.atlassian.com/

* `ATL_BASE_URL`

   Bamboo instance Base URL.

* `ATL_ADMIN_USERNAME`
* `ATL_ADMIN_PASSWORD`
* `ATL_ADMIN_FULLNAME`
* `ATL_ADMIN_EMAIL`

The admin details and credentials.

* `ATL_IMPORT_OPTION`
   
   Import data from backup file during setup. Default value is 'clean' which skip import step and create Bamboo home from scratch. If value is 'import' then `ATL_IMPORT_PATH` should contain path to backup archive.

* `ATL_IMPORT_PATH`

   Full path to backup archive. 
   
## Database configuration

It is optionally possible to configure the database from the environment,
which will pre-fill it for the installation wizard. The password cannot be pre-filled.

The following variables are all must all be supplied if using this feature:

* `ATL_JDBC_URL`

   The database URL; this is database-specific.

* `ATL_JDBC_USER`

   The database user to connect as.

* `ATL_JDBC_PASSWORD`

   The database user password to connect with.

* `ATL_DB_TYPE`

   The type of database; valid supported values are:

   * `h2` - for evaluation needs only
   * `mssql`
   * `mysql`
   * `oracle12c`
   * `postgresql`

Note: Due to licensing restrictions Bamboo does not ship with a MySQL or
Oracle JDBC drivers (since Bamboo 7.0). To use these databases you will need to copy a suitable
driver into the container and restart it. For example, to copy the MySQL driver
into a container named "bamboo", you would do the following:

    docker cp mysql-connector-java.x.y.z.jar bambooo:/opt/atlassian/bamboo/lib
    docker restart bamboo

### Optional database settings

The following variables are for the database connection pool, and are
optional.

* `ATL_DB_POOLMINSIZE` (default: 3)
* `ATL_DB_POOLMAXSIZE` (default: 170)
* `ATL_DB_TIMEOUT` (default: 120000)

## Container Configuration

* `SET_PERMISSIONS` (default: true)

   Define whether to set home directory permissions on startup. Set to `false` to disable
   this behaviour.

# File system permissions and user IDs

By default the Bamboo application runs as the user `bamboo`, with a UID
and GID of 2005. Bamboo this UID must have write access to the home directory
filesystem. If for some reason a different UID must be used, there are a number
of options available:

* The Docker image can be rebuilt with a different UID.
* Under Linux, the UID can be remapped using
  [user namespace remapping][8].

# Upgrade

To upgrade to a more recent version of Bamboo you can simply stop the `bamboo` container and start a new one based on a more recent image:

    $> docker stop bamboo
    $> docker rm bamboo
    $> docker run ... (See above)

As your data is stored in the data volume directory on the host it will still  be available after the upgrade.

_Note: Please make sure that you **don't** accidentally remove the `bamboo` container and its volumes using the `-v` option._

# Backup

For evaluations you can use the built-in database that will store its files in the Bamboo home directory. In that case it is sufficient to create a backup archive of the docker volume.

If you're using an external database, you can configure Bamboo to make a backup automatically each night. This will back up the current state, including the database to the `bambooVolume` docker volume, which can then be archived. Alternatively you can backup the database separately, and continue to create a backup archive of the docker volume to back up the Bamboo Home directory.

Read more about data recovery and backups: [https://confluence.atlassian.com/display/BAMBOO/Data+and+backups](https://confluence.atlassian.com/display/BAMBOO/Data+and+backups)

# Shutdown

Depending on your configuration Bamboo may take a short period to shutdown any
active operations to finish before termination. If sending a `docker stop` this
should be taken into account with the `--time` flag.

Alternatively, the script `/shutdown-wait.sh` is provided, which will initiate a
clean shutdown and wait for the process to complete. This is the recommended
method for shutdown in environments which provide for orderly shutdown,
e.g. Kubernetes via the `preStop` hook.

# Versioning

The `latest` tag matches the most recent release of Atlassian Bamboo. Thus
`atlassian/bamboo:latest` will use the newest version of Bamboo available.

Alternatively you can use a specific major, major.minor, or major.minor.patch
version of Bamboo by using a version number tag:

* `atlassian/bamboo:8`
* `atlassian/bamboo:8.0`
* `atlassian/bamboo:8.0.1`

All versions from 8.0+ are available. Legacy builds for older versions are
available but are no longer supported.

# Supported JDK versions

All the Atlassian Docker images are now JDK 11 only, and generated from the
[official Eclipse Temurin Docker images](https://hub.docker.com/_/eclipse-temurin/).

The Docker images follow the [Atlassian Support end-of-life
policy](https://confluence.atlassian.com/support/atlassian-support-end-of-life-policy-201851003.html);
images for unsupported versions of the products remain available but will no longer
receive updates or fixes.

However, Bamboo is an exception to this. Due to the need to support JDK 11 and
Kubernetes, we currently only generate new images for Bamboo 8.0 and up. Legacy
builds for JDK 8 are still available in Docker Hub, and building custom images
is available (see below).

Historically, we have also generated other versions of the images, including
JDK 8, Alpine, and 'slim' versions of the JDK. These legacy images still exist in
Docker Hub, however they should be considered deprecated, and do not receive
updates or fixes.

If for some reason you need a different version, see "Building your own image".

# Building your own image

* Clone the Atlassian repository at https://bitbucket.org/atlassian-docker/docker-bamboo-server/
* Modify or replace the [Jinja](https://jinja.palletsprojects.com/) templates
  under `config`; _NOTE_: The files must have the `.j2` extensions. However you
  don't have to use template variables if you don't wish.
* Build the new image with e.g: `docker build --tag my-bamboo-image --build-arg BAMBOO_VERSION=8.x.x .`
* Optionally push to a registry, and deploy.

# Troubleshooting

These images include built-in scripts to assist in performing common JVM diagnostic tasks.

## Thread dumps

`/opt/atlassian/support/thread-dumps.sh` can be run via `docker exec` to easily trigger the collection of thread
dumps from the containerized application. For example:

    docker exec my_container /opt/atlassian/support/thread-dumps.sh

By default this script will collect 10 thread dumps at 5 second intervals. This can
be overridden by passing a custom value for the count and interval, by using `-c` / `--count`
and `-i` / `--interval` respectively. For example, to collect 20 thread dumps at 3 second intervals:

    docker exec my_container /opt/atlassian/support/thread-dumps.sh --count 20 --interval 3

Thread dumps will be written to `$APP_HOME/thread_dumps/<date>`.

Note: By default this script will also capture output from top run in 'Thread-mode'. This can
be disabled by passing `-n` / `--no-top`

## Heap dump

`/opt/atlassian/support/heap-dump.sh` can be run via `docker exec` to easily trigger the collection of a heap
dump from the containerized application. For example:

    docker exec my_container /opt/atlassian/support/heap-dump.sh

A heap dump will be written to `$APP_HOME/heap.bin`. If a file already exists at this
location, use `-f` / `--force` to overwrite the existing heap dump file.

## Manual diagnostics

The `jcmd` utility is also included in these images and can be used by starting a `bash` shell
in the running container:

    docker exec -it my_container /bin/bash

# Support

For product support, go to [support.atlassian.com](https://support.atlassian.com/)

You can also visit the [Atlassian Data Center on
Kubernetes](https://community.atlassian.com/t5/Atlassian-Data-Center-on/gh-p/DC_Kubernetes)
forum for discussion on running Atlassian Data Center products in containers.

[docker-expose]: https://docs.docker.com/v17.09/engine/userguide/networking/default_network/binding/
