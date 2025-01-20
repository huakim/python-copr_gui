dnf install -y python3-build python3-py2pack
bash -x ./st/main.sh
rpmbuild "-D_srcrpmdir ${outdir}" "-D_sourcedir ${outdir}" --bs "python-corp_gui.spec"

