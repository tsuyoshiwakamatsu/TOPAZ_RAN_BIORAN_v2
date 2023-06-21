#!/bin/bash

set -e # exit on error
set -u # exit on unset variables
set -o pipefail
set -x

. assimilation_specs.sh

echo "   Date:"
echo "     JULDAY = ${JULDAY}"

# specs for analysis day
#
year=`jultodate $JULDAY 1950 1 1 | cut -c1-4`
echo "     year = $year"
(( day = ${JULDAY} - `datetojul $year 1 1 1950 1 1`  + 1 ))
day=`printf "%03d" $day`
echo "     day = $day"

# specs for analysis day - 7
#
(( juldayprev = ${JULDAY} - 7 ))
echo "     juldayprev = $juldayprev"
yearprev=`jultodate $juldayprev 1950 1 1 | cut -c1-4`

#echo "     previous year = $yearprev"
# it brings some potential issue if dayprev==0
#(( dayprev = ${juldayprev} - `datetojul $yearprev 1 1 1950 1 1` ))
#dayprev=`printf "%03d" $dayprev`
#echo "     previous day = $dayprev"

(( iday = ${JULDAY} ))
Sdate=$(jultodate ${iday} 1950 1 1)
Strdate=${Sdate:0:4}-${Sdate:4:2}-${Sdate:6:2}

#forecast_prefix="${FORECASTDIR}/${HYCOMPREFIX}restart${year}_${day}_00"
#modeldaily_prefix="${FORECASTDIR}/${HYCOMPREFIX}DAILY_${yearprev}_${dayprev}"
forecast_prefix="${FORECASTDIR}/restart.${year}_${day}_00_0000"

#modeldaily_prefix="${FORECASTDIR}/archm.${yearprev}_${dayprev}"
# modified in TP5: (the previous date are indicated before 7 days)
modeldaily_prefix="${FORECASTDIR}/archm."   

forecast_ice_prefix="${FORECASTDIR}/cice/iced.${Strdate}-00000"

# for checking -----hycom restart
echo forecast_prefix=${forecast_prefix}
echo ANALYSISDIR=${ANALYSISDIR}

cd "${ANALYSISDIR}"
for ((e = 1; e <= ${ENSSIZE}; ++e))
do
    mem=`printf "%03d\n" $e`
    prefix="${forecast_prefix}_mem${mem}"
    if [ ! -r "${prefix}.a" -o ! -r "${prefix}.b" ]
    then
	echo "ERROR: could not access ${prefix}.a or ${prefix}.b"
	exit 1
    fi
    ln -sf "${prefix}.a" "forecast${mem}.a"
    ln -sf "${prefix}.b" "forecast${mem}.b"
    
    ice_prefix="${forecast_ice_prefix}_mem${mem}"
    if [ ! -r "${ice_prefix}.nc" ]
    then
	echo "ERROR: could not access ${ice_prefix}.nc"
	exit 1
    fi
    ln -sf "${ice_prefix}.nc" "ice_forecast${mem}.nc"
    
done

# cancal to link the ice.uf file
#ln -sf "${forecast_prefix}ICE.uf" forecastICE.uf

# link the daily files
modeldaily_prefix="${FORECASTDIR}/archm."

for ((i = 0; i <= 6; i++))
do
    (( juldaynow = $JULDAY - $i - 1))
    yearnow=`jultodate $juldaynow 1950 1 1 | cut -c1-4`
   
    Jday=`datetojul $yearnow 1 1 1950 1 1`
    if [ ${juldaynow} -eq ${Jday} ]; then
      daynow=0
    else
      let daynow=${juldaynow}-${Jday} 
    fi
    #(( daynow = ${juldaynow} - `datetojul $yearnow 1 1 1950 1 1` ))
    daynow=`printf "%03d" $daynow`
    if (( `expr match "${OBSTYPES}" TSLA` > 0 ))
    then
        echo 'TSLA or SSH: ' $i
	Fdaily=${modeldaily_prefix}${yearnow}_${daynow}_12
        echo ${Fdaily}
	Fnew=forecast_daily_`echo 0$i|tail -3c`
	if [ -r ${Fdaily}.a -a -r ${Fdaily}.b ]; then
           ln  -sf ${Fdaily}.a ${Fnew}.a 
           ln  -sf ${Fdaily}.b ${Fnew}.b 
        fi
        # link the concerned daily SSH
	if [ -r ${Fdaily}_SSH.uf ]; then
           ln  -sf ${Fdaily}_SSH.uf model_TSSH_`echo 0$i|tail -3c`.uf 
        fi
    fi

    # link the ice snapshot including ice drift
    Datenow=$(jultodate ${juldaynow} 1950 1 1)
    Ficesnap=${FORECASTDIR}/cice/ICEDRIFT.${Datenow:0:4}-${Datenow:4:2}-${Datenow:6:2}.nc 
    echo 'IDRFT: ' $i
    echo $(pwd)
    if [ ! -r ${Ficesnap} ]
        then
	    echo "ERROR: could not access ${Ficesnap}"
	    exit 1
    fi
    ln -sf ${Ficesnap} model_ICEDRIFT_0"$i".nc

done

if [ -f "{PREPOBSDIR}/observations.uf" ]
then
    cp "${PREPOBSDIR}"/observations-*.nc .
    ln -sf "${PREPOBSDIR}"/observations.uf .
fi
# linking the ice drift files simulated by model daily.
if [ -s "${PREPOBSDIR}/observations.uf.IDRFT" ]; then
  cd "${FORECASTDIR}"
  if [ ! -s ./pre_icedrift_osisaf.sh ]; then
    ln -sf ${BINDIR}/pre_icedrift_osisaf.sh . 
    ln -sf ${BINDIR}/icedrift_osisaf . 
  fi
  ./pre_icedrift_osisaf.sh ${JULDAY}
  cd "${ANALYSISDIR}"
  for ii in `seq 1 5`; do
    if [ -s ${FORECASTDIR}/model_ICEDRIFT_OSISAF${ii}.uf ]; then
      mv ${FORECASTDIR}/model_ICEDRIFT_OSISAF${ii}.uf .
    fi
  done
fi



