ARG BASE_IMAGE=eclipse-temurin:11
FROM $BASE_IMAGE

LABEL maintainer="dc-deployments@atlassian.com"
LABEL securitytxt="https://www.atlassian.com/.well-known/security.txt"

ENV APP_NAME                                bamboo
ENV RUN_USER                                bamboo
ENV RUN_GROUP                               bamboo
ENV RUN_UID                                 2005
ENV RUN_GID                                 2005

# https://confluence.atlassian.com/display/BAMBOO/Locating+important+directories+and+files
ENV BAMBOO_HOME                             /var/atlassian/application-data/bamboo
ENV BAMBOO_INSTALL_DIR                      /opt/atlassian/bamboo

WORKDIR $BAMBOO_HOME

# Expose HTTP and ActiveMQ ports
EXPOSE 8085
EXPOSE 54663

CMD ["/entrypoint.py"]
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends git git-lfs openssh-client python3 python3-jinja2 tini libtcnative-1 \
    && apt-get clean autoclean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

ARG MAVEN_VERSION=3.6.3
ENV MAVEN_HOME                              /opt/maven
RUN mkdir -p ${MAVEN_HOME} \
    && curl -L --silent http://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz | tar -xz --strip-components=1 -C "${MAVEN_HOME}" \
    && ln -s ${MAVEN_HOME}/bin/mvn /usr/local/bin/mvn

ARG BAMBOO_VERSION
RUN curl -L --silent https://packages.atlassian.com/maven-external/com/atlassian/bamboo/atlassian-bamboo/${BAMBOO_VERSION}/atlassian-bamboo-${BAMBOO_VERSION}.pom > /tmp/pom.xml


ARG DOWNLOAD_URL=https://product-downloads.atlassian.com/software/bamboo/downloads/atlassian-bamboo-${BAMBOO_VERSION}.tar.gz

RUN groupadd --gid ${RUN_GID} ${RUN_GROUP} \
    && useradd --uid ${RUN_UID} --gid ${RUN_GID} --home-dir ${BAMBOO_HOME} --shell /bin/bash ${RUN_USER} \
    && echo PATH=$PATH > /etc/environment \
    \
    && mkdir -p                             ${BAMBOO_INSTALL_DIR} \
    && curl -L --silent                     ${DOWNLOAD_URL} | tar -xz --strip-components=1 -C "${BAMBOO_INSTALL_DIR}" \
    && chmod -R "u=rwX,g=rX,o=rX"           ${BAMBOO_INSTALL_DIR}/ \
    && chown -R root.                       ${BAMBOO_INSTALL_DIR}/ \
    && chown -R ${RUN_USER}:${RUN_GROUP}    ${BAMBOO_INSTALL_DIR}/logs \
    && chown -R ${RUN_USER}:${RUN_GROUP}    ${BAMBOO_INSTALL_DIR}/temp \
    && chown -R ${RUN_USER}:${RUN_GROUP}    ${BAMBOO_INSTALL_DIR}/work \
    && chown -R ${RUN_USER}:${RUN_GROUP}    ${BAMBOO_INSTALL_DIR}/conf \
    && chown -R ${RUN_USER}:${RUN_GROUP}    ${BAMBOO_HOME} \
    \
    && sed -i -e 's/^JVM_SUPPORT_RECOMMENDED_ARGS=""$/: \${JVM_SUPPORT_RECOMMENDED_ARGS:=""}/g' ${BAMBOO_INSTALL_DIR}/bin/setenv.sh \
    && sed -i -e 's/^JVM_\(.*\)_MEMORY="\(.*\)"$/: \${JVM_\1_MEMORY:=\2}/g' ${BAMBOO_INSTALL_DIR}/bin/setenv.sh \
    && sed -i -e 's/^JAVA_OPTS="/JAVA_OPTS="${JAVA_OPTS} /g' ${BAMBOO_INSTALL_DIR}/bin/setenv.sh

VOLUME ["${BAMBOO_HOME}"] # Must be declared after setting perms

COPY entrypoint.py \
     shutdown-wait.sh \
     shared-components/image/entrypoint_helpers.py  /
COPY shared-components/support                      /opt/atlassian/support
COPY config/*                                       /opt/atlassian/etc/
