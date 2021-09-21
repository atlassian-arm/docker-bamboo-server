import pytest
import testinfra
import xml.sax.saxutils as saxutils

from helpers import get_app_home, get_app_install_dir, get_bootstrap_proc, get_procs, \
    parse_properties, parse_xml, run_image, wait_for_http_response, wait_for_proc


PORT = 8085
STATUS_URL = f'http://localhost:{PORT}/status'

def test_jvm_args(docker_cli, image, run_user):
    environment = {
        'JVM_MINIMUM_MEMORY': '383m',
        'JVM_MAXIMUM_MEMORY': '2047m',
        'JVM_SUPPORT_RECOMMENDED_ARGS': '-verbose:gc',
    }
    container = run_image(docker_cli, image, user=run_user, environment=environment)
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    procs_list = get_procs(container)
    jvm = [proc for proc in procs_list if get_bootstrap_proc(container) in proc][0]

    assert f'-Xms{environment.get("JVM_MINIMUM_MEMORY")}' in jvm
    assert f'-Xmx{environment.get("JVM_MAXIMUM_MEMORY")}' in jvm
    assert '-Dbamboo.setup.rss.in.docker=false' in jvm
    assert environment.get('JVM_SUPPORT_RECOMMENDED_ARGS') in jvm



def test_install_permissions(docker_cli, image):
    container = run_image(docker_cli, image)

    assert container.file(f'{get_app_install_dir(container)}/conf/server.xml').user == 'root'

    for d in ['logs', 'work', 'temp']:
        path = f'{get_app_install_dir(container)}/{d}/'
        assert container.file(path).user == 'bamboo'


def test_first_run_state(docker_cli, image, run_user):
    container = run_image(docker_cli, image, user=run_user, ports={PORT: PORT})

    wait_for_http_response(STATUS_URL, expected_status=200)


def test_clean_shutdown(docker_cli, image, run_user):
    container = docker_cli.containers.run(image, detach=True, user=run_user, ports={PORT: PORT})
    host = testinfra.get_host("docker://"+container.id)

    wait_for_http_response(STATUS_URL, expected_status=200)

    container.kill(signal.SIGTERM)

    end = r'org\.apache\.coyote\.AbstractProtocol\.destroy Destroying ProtocolHandler'
    wait_for_log(container, end)


def test_shutdown_script(docker_cli, image, run_user):
    container = docker_cli.containers.run(image, detach=True, user=run_user, ports={PORT: PORT})
    host = testinfra.get_host("docker://"+container.id)

    wait_for_http_response(STATUS_URL, expected_status=200)

    container.exec_run('/shutdown-wait.sh')

    end = r'org\.apache\.coyote\.AbstractProtocol\.destroy Destroying ProtocolHandler'
    wait_for_log(container, end)


def test_server_xml_defaults(docker_cli, image):
    container = run_image(docker_cli, image)
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    xml = parse_xml(container, f'{get_app_install_dir(container)}/conf/server.xml')
    connector = xml.find('.//Connector')
    context = xml.find('.//Context')


    assert connector.get('port') == '8085'
    assert connector.get('maxThreads') == '150'
    assert connector.get('minSpareThreads') == '25'
    assert connector.get('connectionTimeout') == '20000'
    assert connector.get('enableLookups') == 'false'
    assert connector.get('protocol') == 'HTTP/1.1'
    assert connector.get('acceptCount') == '100'
    assert connector.get('secure') == 'false'
    assert connector.get('scheme') == 'http'
    assert connector.get('proxyName') == ''
    assert connector.get('proxyPort') == ''

    assert context.get('path') == ''


def test_server_xml_catalina_fallback(docker_cli, image):
    environment = {
        'CATALINA_CONNECTOR_PROXYNAME': 'PROXYNAME',
        'CATALINA_CONNECTOR_PROXYPORT': 'PROXYPORT',
        'CATALINA_CONNECTOR_SECURE': 'SECURE',
        'CATALINA_CONNECTOR_SCHEME': 'SCHEME',
        'CATALINA_CONTEXT_PATH': 'CONTEXT'
    }
    container = run_image(docker_cli, image, environment=environment)
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    xml = parse_xml(container, f'{get_app_install_dir(container)}/conf/server.xml')
    connector = xml.find('.//Connector')
    context = xml.find('.//Context')

    assert connector.get('proxyName') == 'PROXYNAME'
    assert connector.get('proxyPort') == 'PROXYPORT'
    assert connector.get('scheme') == 'SCHEME'
    assert connector.get('secure') == 'SECURE'
    assert context.get('path') == 'CONTEXT'


def test_server_xml_params(docker_cli, image):
    environment = {
        'ATL_TOMCAT_MGMT_PORT': '8008',
        'ATL_TOMCAT_PORT': '9095',
        'ATL_TOMCAT_MAXTHREADS': '151',
        'ATL_TOMCAT_MINSPARETHREADS': '26',
        'ATL_TOMCAT_CONNECTIONTIMEOUT': '20001',
        'ATL_TOMCAT_ENABLELOOKUPS': 'true',
        'ATL_TOMCAT_PROTOCOL': 'org.apache.coyote.http11.Http11Protocol',
        'ATL_TOMCAT_ACCEPTCOUNT': '101',
        'ATL_TOMCAT_SECURE': 'true',
        'ATL_TOMCAT_SCHEME': 'https',
        'ATL_PROXY_NAME': 'bamboo.atlassian.com',
        'ATL_PROXY_PORT': '443',
        'ATL_TOMCAT_CONTEXTPATH': '/mybamboo',
    }
    container = run_image(docker_cli, image, environment=environment)
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    xml = parse_xml(container, f'{get_app_install_dir(container)}/conf/server.xml')
    connector = xml.find('.//Connector')
    context = xml.find('.//Context')

    assert xml.get('port') == environment.get('ATL_TOMCAT_MGMT_PORT')

    assert connector.get('port') == environment.get('ATL_TOMCAT_PORT')
    assert connector.get('maxThreads') == environment.get('ATL_TOMCAT_MAXTHREADS')
    assert connector.get('minSpareThreads') == environment.get('ATL_TOMCAT_MINSPARETHREADS')
    assert connector.get('connectionTimeout') == environment.get('ATL_TOMCAT_CONNECTIONTIMEOUT')
    assert connector.get('enableLookups') == environment.get('ATL_TOMCAT_ENABLELOOKUPS')
    assert connector.get('protocol') == environment.get('ATL_TOMCAT_PROTOCOL')
    assert connector.get('acceptCount') == environment.get('ATL_TOMCAT_ACCEPTCOUNT')
    assert connector.get('secure') == environment.get('ATL_TOMCAT_SECURE')
    assert connector.get('scheme') == environment.get('ATL_TOMCAT_SCHEME')
    assert connector.get('proxyName') == environment.get('ATL_PROXY_NAME')
    assert connector.get('proxyPort') == environment.get('ATL_PROXY_PORT')

    assert context.get('path') == environment.get('ATL_TOMCAT_CONTEXTPATH')

def test_bamboo_cfg_xml(docker_cli, image):
    environment = {
        'BUILD_NUMBER': '61009',
        'ATL_JDBC_URL': 'jdbc:postgresql://172.17.0.2:5432/bamboodocker',
        'ATL_BROKER_CLIENT_URI': 'failover:(tcp://fa802b2849c3:54664?wireFormat.maxInactivityDuration=300000)?maxReconnectAttempts=10&amp;initialReconnectDelay=15000',
        'ATL_BROKER_URI': 'nio://0.0.0.0:54664',
        'ATL_DB_POOLMINSIZE': '4',
        'ATL_DB_TIMEOUT': '40',
        'ATL_DB_IDLETESTPERIOD': '40',
        'ATL_DB_MAXSTATEMENTS': '2',
        'ATL_DB_VALIDATE': 'true',
        'ATL_DB_ACQUIREINCREMENT': '4',
        'ATL_DB_VALIDATIONQUERY': 'select 2',
    }
    container = run_image(docker_cli, image, environment=environment)
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    xml = parse_xml(container, f'{get_app_home(container)}/bamboo.cfg.xml')

    assert xml.find(".//buildNumber").text == environment.get('BUILD_NUMBER')
    assert saxutils.escape(xml.find(".//property[@name='bamboo.jms.broker.client.uri']").text) == environment.get('ATL_BROKER_CLIENT_URI')
    assert xml.find(".//property[@name='bamboo.jms.broker.uri']").text == environment.get('ATL_BROKER_URI')
    assert xml.find(".//property[@name='hibernate.c3p0.min_size']").text == environment.get('ATL_DB_POOLMINSIZE')
    assert xml.find(".//property[@name='hibernate.c3p0.timeout']").text == environment.get('ATL_DB_TIMEOUT')
    assert xml.find(".//property[@name='hibernate.c3p0.idle_test_period']").text == environment.get('ATL_DB_IDLETESTPERIOD')
    assert xml.find(".//property[@name='hibernate.c3p0.max_statements']").text == environment.get('ATL_DB_MAXSTATEMENTS')
    assert xml.find(".//property[@name='hibernate.c3p0.validate']").text == environment.get('ATL_DB_VALIDATE')
    assert xml.find(".//property[@name='hibernate.c3p0.acquire_increment']").text == environment.get('ATL_DB_ACQUIREINCREMENT')
    assert xml.find(".//property[@name='hibernate.c3p0.preferredTestQuery']").text == environment.get('ATL_DB_VALIDATIONQUERY')

def test_seraph_defaults(docker_cli, image):
    container = run_image(docker_cli, image)
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    xml = parse_xml(container, f'{get_app_install_dir(container)}/atlassian-bamboo/WEB-INF/classes/seraph-config.xml')
    #param = xml.findall('//param-name[text()="autologin.cookie.age"]') == []
    param = xml.findall('.//param-name[.="autologin.cookie.age"]') == []


def test_seraph_login_set(docker_cli, image):
    container = run_image(docker_cli, image, environment={"ATL_AUTOLOGIN_COOKIE_AGE": "TEST_VAL"})
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    xml = parse_xml(container, f'{get_app_install_dir(container)}/atlassian-bamboo/WEB-INF/classes/seraph-config.xml')
    assert xml.findall('.//param-value[.="TEST_VAL"]')[0].text == "TEST_VAL"


def test_bamboo_init_set(docker_cli, image):
    container = run_image(docker_cli, image, environment={'BAMBOO_HOME': '/tmp/'})
    _jvm = wait_for_proc(container, get_bootstrap_proc(container))

    init = container.file(f'{get_app_install_dir(container)}/atlassian-bamboo/WEB-INF/classes/bamboo-init.properties')
    assert init.contains("bamboo.home = /tmp/")


def test_java_in_run_user_path(docker_cli, image):
    RUN_USER = 'bamboo'
    container = run_image(docker_cli, image)
    proc = container.run(f'su -c "which java" {RUN_USER}')
    assert len(proc.stdout) > 0


def test_non_root_user(docker_cli, image):
    RUN_UID = 2005
    RUN_GID = 2005
    container = run_image(docker_cli, image, user=f'{RUN_UID}:{RUN_GID}')
    jvm = wait_for_proc(container, "org.apache.catalina.startup.Bootstrap")