FROM adoptopenjdk:8-jdk-hotspot-bionic
LABEL maintainer="Atlassian Bamboo Team" \
      description="Official Bamboo Server Docker Image"

ENV BAMBOO_USER bamboo
ENV BAMBOO_GROUP bamboo

ENV BAMBOO_USER_HOME /home/${BAMBOO_USER}
ENV BAMBOO_HOME /var/atlassian/application-data/bamboo
ENV BAMBOO_INSTALL_DIR /opt/atlassian/bamboo

# Expose HTTP and AGENT JMS ports
ENV BAMBOO_JMS_CONNECTION_PORT=54663
EXPOSE 8085
EXPOSE $BAMBOO_JMS_CONNECTION_PORT

RUN set -x && \
     addgroup ${BAMBOO_GROUP} && \
     adduser ${BAMBOO_USER} --home ${BAMBOO_USER_HOME} --ingroup ${BAMBOO_GROUP} --disabled-password

RUN set -x && \
     apt-get update && \
     apt-get install -y --no-install-recommends \
          curl \
          git \
          bash \
          procps \
          openssl \
          openssh-client \
          libtcnative-1 \
          maven \
     && \
# create symlink to maven to automate capability detection
     ln -s /usr/share/maven /usr/share/maven3 && \
     rm -rf /var/lib/apt/lists/*

ARG BAMBOO_VERSION
ARG DOWNLOAD_URL=https://www.atlassian.com/software/bamboo/downloads/binary/atlassian-bamboo-${BAMBOO_VERSION}.tar.gz

RUN set -x && \
     mkdir -p ${BAMBOO_INSTALL_DIR}/lib/native && \
     mkdir -p ${BAMBOO_HOME} && \
     ln --symbolic "/usr/lib/x86_64-linux-gnu/libtcnative-1.so" "${BAMBOO_INSTALL_DIR}/lib/native/libtcnative-1.so" && \
     curl --silent -L ${DOWNLOAD_URL} | tar -xz --strip-components=1 -C "$BAMBOO_INSTALL_DIR" && \
     echo "bamboo.home=${BAMBOO_HOME}" > $BAMBOO_INSTALL_DIR/atlassian-bamboo/WEB-INF/classes/bamboo-init.properties && \
     chown -R "${BAMBOO_USER}:${BAMBOO_GROUP}" "${BAMBOO_INSTALL_DIR}" && \
     chown -R "${BAMBOO_USER}:${BAMBOO_GROUP}" "${BAMBOO_HOME}"

VOLUME ["${BAMBOO_HOME}"]
WORKDIR $BAMBOO_HOME

USER ${BAMBOO_USER}
COPY  --chown=bamboo:bamboo entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
