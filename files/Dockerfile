FROM bcgovimages/von-image:node-1.12-6
ARG user=indy
ARG LOG_LEVEL=info
ARG RUST_LOG=warning
ENV LOG_LEVEL=$LOG_LEVEL
ENV RUST_LOG=$RUST_LOG

USER root
RUN apt-get update -y && \
    apt-get install -y \
    xz-utils
USER $user

ADD config ./config
ADD server/requirements.txt server/

# Install dependencies keeping original pip version for plenum compatibility
# We upgrade pip only temporarily to install indy_vdr, then downgrade back
RUN pip3 install -U pip setuptools wheel && \
    pip install --no-cache-dir indy_vdr && \
    pip install --no-cache-dir -r server/requirements.txt && \
    python -m pip install pip==9.0.3

ADD --chown=indy:indy indy_config.py /etc/indy/
ADD --chown=indy:indy . $HOME

RUN chmod +x scripts/init_genesis.sh

RUN mkdir -p \
    $HOME/cli-scripts \
    && chmod -R ug+rw $HOME/cli-scripts
