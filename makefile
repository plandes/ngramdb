## makefile automates the build and deployment for python projects

# project
PROJ_TYPE =	python
PROJ_MODULES=	python-resources
PROJ_ARGS =	-c test-resources/test.conf
ADD_CLEAN +=	$(wildcard *.log nohup.out)

# corpus
SINCE_YEAR ?= 	1950
N_GRAMS ?=	3

include ./zenbuild/main.mk

# download ngrams as defined in the configuration file
.PHONY:		download
download:
		nohup make PYTHON_BIN_ARGS="download $(PROJ_ARGS)" run \
			> download.log 2>&1 &

# uncompress the corpus
.PHONY:		uncompress
uncompress:
		$(eval ZIP_DIR=\
		    $(shell make PYTHON_BIN_ARGS="env $(PROJ_ARGS) -n $(N_GRAMS)" run \
			| grep data.file_path | sed 's/^.*=//' |xargs dirname))
		@echo "unzipping all in $(ZIP_DIR)"
		( cd $(ZIP_DIR) ; nohup unzip *.zip > unzip.log 2>&1 & )

# insert only ngrams matched on or after 1990
.PHONY:		load
load:
		nohup make PYTHON_BIN_ARGS="load $(PROJ_ARGS) -n $(N_GRAMS) -y $(SINCE_YEAR)" run \
			> load.log 2>&1 &

# query for ngrams
.PHONY:		query
query:
		@echo "connecting to ${NLP_SERV}"
		make PYTHON_BIN_ARGS="query $(PROJ_ARGS) -g 'I love you'" run

# compute the probability of ngrams
.PHONY:		probability
probability:
		@echo "connecting to ${NLP_SERV}"
		make PYTHON_BIN_ARGS="probability $(PROJ_ARGS) -g 'I love %'" run

# stop all processing for the application
.PHONY:		kill
kill:
		ps -eaf | grep ngramdb | grep -v grep | awk '{print $$2}' | xargs kill
