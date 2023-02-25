FROM ubuntu:20.04

### Install conda
### ==============================================
## add a conda for python 3 environment
# Install miniconda - this is from 
# https://github.com/ContinuumIO/docker-images/blob/master/miniconda3/debian/Dockerfile
# hadolint ignore=DL3008
RUN apt-get update -q && \
    apt-get install -q -y --no-install-recommends \
    bzip2 \
    ca-certificates \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    mercurial \
    openssh-client \
    procps \
    subversion \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /opt/conda/bin:$PATH

# Leave these args here to better use the Docker build cache
# SEE: https://repo.anaconda.com/miniconda/
# Leave these args here to better use the Docker build cache
ARG CONDA_VERSION=py38_4.9.2
ARG CONDA_MD5=122c8c9beb51e124ab32a0fa6426c656

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O miniconda.sh && \
    echo "${CONDA_MD5}  miniconda.sh" > miniconda.md5 && \
    if ! md5sum --status -c miniconda.md5; then exit 1; fi && \
    mkdir -p /opt && \
    sh miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh miniconda.md5 && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    /opt/conda/bin/conda clean -afy

###################################################################
####   INSTALL OPENMODELICA
# Avoid warnings
# debconf: unable to initialize frontend: Dialog
# debconf: (TERM is not set, so the dialog frontend is not usable.)
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

#####################################################################
RUN apt-get update && \
    apt-get --no-install-recommends install -y \
    gnupg2 \
    libgfortran4 \
    curl \
    lsb-release \
    && \
    rm -rf /var/lib/apt/lists/*

#RUN echo "deb https://build.openmodelica.org/apt focal nightly" | tee -a /etc/apt/sources.list
#RUN echo "deb https://build.openmodelica.org/apt focal stable"  | tee -a /etc/apt/sources.list
#RUN echo "deb https://build.openmodelica.org/apt focal release" | tee -a /etc/apt/sources.list
#RUN wget -qO- http://build.openmodelica.org/apt/openmodelica.asc | apt-key add -

# See https://build.openmodelica.org/apt/dists/focal/stable/binary-amd64/Packages for package version.
RUN curl -fsSL http://build.openmodelica.org/apt/openmodelica.asc | gpg --dearmor -o /usr/share/keyrings/openmodelica-keyring.gpg
# Or replace stable with nightly or release
RUN echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/openmodelica-keyring.gpg] https://build.openmodelica.org/apt \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/openmodelica.list > /dev/null

# See https://build.openmodelica.org/apt/dists/focal/stable/binary-amd64/Packages for package version.
RUN apt-get update && \
    apt-get --no-install-recommends install -y \
    omc=1.20.0~1-g2faf7aa-1 && \
    rm -rf /var/lib/apt/lists/*

#################################################
####  INSTALL DEPENDENCY
# --------------------------------
# FMU simulationL pyfmi or fmpy
# create a conda environment install pyfmi or fmpy for simulating FMUs.
# NOTE: neither of current versions of pyfmi or fmpy support ARM architecture
RUN conda update conda && \
    conda config --add channels conda-forge && \
    conda install numpy matplotlib pandas pyfmi

# Specify ModelicaPath if any

# Set user id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    mkdir -p /etc/sudoers.d && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer && \
    mkdir -m 1777 /tmp/.X11-unix

USER developer
ENV HOME /home/developer

# Install MSL
#RUN echo \
#    "updatePackageIndex(); getErrorString();\ninstallPackage(Modelica, \"3.2.3\"); getErrorString();" >> /tmp/installMSL.mos && \
#    omc /tmp/installMSL.mos && \
#    rm /tmp/installMSL.mos

ENV MODELICAPATH $HOME/.openmodelica/libraries

# COPY depdency from local to docker
#COPY ./dependency $MODELICAPATH
#
# Define environment variable for mounted test
# This should be updated if external Modelica library is tested in this docker
#RUN mkdir $HOME/modelica_test
#ENV MODELICATEST_PATH $HOME/modelica_test 
#ENV MODELICAPATH="${MODELICATEST_PATH}:${MODELICAPATH}"

### ============================================
# run as a user
USER developer
WORKDIR $HOME

CMD [ "/bin/bash" ]
# Avoid warning that Matplotlib is building the font cache using fc-list. This may take a moment.
# This needs to be towards the end of the script as the command writes data to
# /home/developer/.cache
RUN python -c "import matplotlib.pyplot"

RUN echo "=== Installation successful"