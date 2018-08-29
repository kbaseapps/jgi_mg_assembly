FROM kbase/kbase:sdkbase2.latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# update security libraries in the base image
RUN apt-get -y update \
    && apt-get install -y pigz python-dev libffi-dev libssl-dev ca-certificates

RUN pip install cffi ndg-httpsclient pyopenssl==17.03 cryptography==2.0.3 --upgrade \
    && pip install pyasn1 --upgrade \
    && pip install requests --upgrade \
    && pip install 'requests[security]' --upgrade \
    && pip install coverage \
    && pip install psutil \
    && pip install pyyaml \
    && pip install yattag \
    && pip install numpy \
    && pip install matplotlib \
    && pip install pandas

# -----------------------------------------

WORKDIR /kb/module
COPY ./ /kb/module

ARG CONFIG_FILE=/kb/module/pipeline.cfg

# install BBTools
RUN BBMAP_VERSION=$(grep BBTools $CONFIG_FILE | sed -r 's/(\S+)\s*=\s*(\S+)/\2/') \
    && BBMAP=BBMap_$BBMAP_VERSION.tar.gz \
    && wget -O $BBMAP https://sourceforge.net/projects/bbmap/files/$BBMAP/download \
    && tar -xf $BBMAP \
    && rm $BBMAP

# build BBTools small C-lib
RUN cd /kb/module/bbmap/jni \
    && make -f makefile.linux

# install SPAdes
RUN SPADES_VER=$(grep SPAdes $CONFIG_FILE | sed -r 's/(\S+)\s*=\s*(\S+)/\2/') \
    && cd /opt \
    && SPADES=SPAdes-$SPADES_VER-Linux.tar.gz \
    && wget http://cab.spbu.ru/files/release$SPADES_VER/$SPADES \
    && tar -xvzf $SPADES \
    && rm $SPADES

# -----------------------------------------

# Install the module code.

RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
