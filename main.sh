if [[ -z "$outdir" ]]
then
  outdir='.'
fi

pushd *copr_gui
#for i in gui pyside6 wxpython
#do
#export spec=$SPEC
. ./main.sh
sed -i "/# SECTION test requirements/,/# \/SECTION/d; s~%{python_sitelib}/copr_${i}-%{version}.dist-info~~; s~%{python_sitelib}/copr_${i}~%{python_sitelib}/\*~;" "python-copr_${spec}.spec"
#done
popd


mv *copr_gui/*.{spec,tar.gz} "${outdir}/"
(
cd "${outdir}/"
for i in *.spec
do
sed  -i '1i %global debug_package %{nil}' "$i"
sed  -i 's~python-wxpython~python-wxpython4~' "$i"

done
)
