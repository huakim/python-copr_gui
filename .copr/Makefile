outdir ?= $(shell rpm --eval '%{_srcrpmdir}')

srpm:
	outdir=$(outdir) bash -x .copr/main.sh
