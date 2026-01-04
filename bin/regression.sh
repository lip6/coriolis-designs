#!/bin/bash

 getString ()
 {
   string=`echo $1 | cut -d '=' -f 2-` 
   echo $string
 }

 getRuntime ()
 {
   startTime="$1"
   mins=$(( (SECONDS - startTime)/60 ))
   secs=$(( (SECONDS - startTime)%60 ))
   printf "%u:%02u" $mins $secs
 }

      runSetId="not_set"
      onGithub="false"
     gf180rule="gds"
 ihpsg13g2rule="gds"
 while [ $# -gt 0 ]; do
   case $1 in
     --github-runner) echo "Github/runner mode..";
                      onGithub="true";;
     --run-set=*)     runSetId=`getString $1`;;
     --gf180-drc)     gf180rule="drc";;
     --ihpsg13g2-drc) ihpsg13g2rule="drc";;
     --all-drc)       gf180rule="drc"
		      ihpsg13g2rule="drc";;
   esac
   shift
 done

 

 declare -A benchRules
 benchRules["picorv32/nsx2"]="gds"
 benchRules["picorv32/sky130_c4m"]="gds"
 benchRules["picorv32/ihpsg13g2_c4m"]="${ihpsg13g2rule}"
 benchRules["picorv32/gf180mcu_gf"]="${gf180rule}"
 benchRules["picorv32/gf180mcu_c4m"]="${gf180rule}"
 benchRules["arlet6502/original/nsx2"]="gds"
 benchRules["arlet6502/original/sky130_c4m"]="gds"
 benchRules["arlet6502/original/ihpsg13g2_c4m"]="${ihpsg13g2rule}"
 benchRules["arlet6502/original/gf180mcu_gf"]="${gf180rule}"
 benchRules["arlet6502/original/gf180mcu_c4m"]="${gf180rule}"
 benchRules["arlet6502/fixed/nsx2"]="gds"
 benchRules["arlet6502/fixed/sky130_c4m"]="gds"
 benchRules["arlet6502/fixed/ihpsg13g2_c4m"]="${ihpsg13g2rule}"
 benchRules["arlet6502/fixed/gf180mcu_gf"]="${gf180rule}"
 benchRules["arlet6502/fixed/gf180mcu_c4m"]="${gf180rule}"

 benchsSet1=""
 benchsSet2=""
 benchsSet3=""
 benchsSet4=""
 benchsSet5=""

 if [ -e "../coriolis-pdk-sky130-c4m" ]; then
   benchsSet1="${benchsSet1} arlet6502/original/sky130_c4m"
   benchsSet1="${benchsSet1} arlet6502/fixed/sky130_c4m"
   benchsSet1="${benchsSet1} picorv32/sky130_c4m"
 fi
 if [ -e "../coriolis-pdk-gf180mcu" ]; then
   benchsSet2="${benchsSet2} arlet6502/original/gf180mcu_gf"
   benchsSet2="${benchsSet2} arlet6502/fixed/gf180mcu_gf"
   benchsSet2="${benchsSet2} picorv32/gf180mcu_gf"
 fi
 if [ -e "../coriolis-pdk-gf180mcu-c4m" ]; then
   benchsSet3="${benchsSet3} arlet6502/original/gf180mcu_c4m"
   benchsSet3="${benchsSet3} arlet6502/fixed/gf180mcu_c4m"
   benchsSet3="${benchsSet3} picorv32/gf180mcu_c4m"
 fi
 if [ -e "../coriolis-pdk-ihpsg13g2-c4m" ]; then
   benchsSet4="${benchsSet4} arlet6502/original/ihpsg13g2_c4m"
   benchsSet4="${benchsSet4} arlet6502/fixed/ihpsg13g2_c4m"
   benchsSet4="${benchsSet4} picorv32/ihpsg13g2_c4m"
 fi
 if [ -e "../coriolis-pdk-nsx2" ]; then
   benchsSet5="${benchsSet5} arlet6502/original/nsx2"
   benchsSet5="${benchsSet5} arlet6502/fixed/nsx2"
   benchsSet5="${benchsSet5} picorv32/nsx2"
 fi

 crlenv="`pwd`/bin/crlenv.py"
 if [ ! -x "${crlenv}" ]; then
   echo "[ERROR] regression.sh: Unable to find crlenv.py script."
   echo "        (${crlenv})"
   exit 1
 fi
 if [ "${runSetId}" = "not_set" ]; then
   if [ "${gf180rule}" = "drc" ]; then
     echo "  o  DRC for GF 180 MCU enabled."
   fi
   if [ "${ihpsg13g2rule}" = "drc" ]; then
     echo "  o  DRC for IHP sg13g2 enabled."
   fi
 fi
     
#mode="stopOnFailure"
 mode="ignoreFailure"
# hline="+---+----+--------------------------------+------------+----------+-----------+"
#header="|Set| No |             bench              |    Rule    |  Runtime |  Status   |"
  hline="=====  ==  ==========================================  ================  ==========  ==========="
 header="Set    No  Bench                                       Rule                 Runtime  Status     "

 runSet () {
   setId="$1"
   benchCount=1

   logDir="`pwd`/logs"
   if [ ! -d "${logDir}" ]; then mkdir -p "${logDir}"; fi
   failedTag="`pwd`/runset-${setId}.failed"
   rm -f "${failedTag}"
   benchsSetName="benchsSet${setId}"
   for bench in ${!benchsSetName}; do
     rules="${benchRules[$bench]}"
     benchDir="./designs/${bench}"

    #statusLine="| %u | %2u | %-30s | %-10s | %10s | %-7s |"
     statusLine="%s  %2u  %-42s  %-16s  %10s  %-7s "
  
     if [ ! -d "${benchDir}" ]; then
       echo ""
       echo "[WARNING] No bench directory \"${benchDir}\", skipped."
       continue
     fi
     benchLogFile=`echo "${bench}" | sed 's,/,.,g'`.log
     benchLog="${logDir}/${benchLogFile}"
     rm -f "${benchLog}"
     echo -e "\n\n\n\n" >> ${benchLog}
     echo "=============================================================================" >> ${benchLog}
     echo "Running bench <${bench}> with rules \"${rules}\""                              >> ${benchLog}
     echo "=============================================================================" >> ${benchLog}
  
     case $setId in
       1) setIdStr="1    ";;
       2) setIdStr=" 2   ";;
       3) setIdStr="  3  ";;
       4) setIdStr="   4 ";;
       5) setIdStr="    5";;
       *) setIdStr="    X";;
     esac
     success="true"
     pushd ${benchDir} > /dev/null
     startTime="$SECONDS"
     ${crlenv} -- doit clean_flow --extras >> ${benchLog} 2>&1
     for rule in ${rules}; do
       ${crlenv} -- doit ${rule} reuse-blif=v58 >> ${benchLog} 2>&1
       if [ $? -ne 0 ]; then
         success="false"
         printf "${statusLine}\n" "$setIdStr" $benchCount "<${bench}>" "${rule}" "`getRuntime $startTime`" "FAILED"
         echo "* Bench <${bench}> \"${rule}\" failed" >> ${failedTag}
         if [ "${mode}" = "stopOnFailure" ]; then
           echo ""
           echo ""
           echo "[ERROR] regression.sh: bench <${bench}> has failed."
           exit 1
         fi
         break
       fi
     done
     ${crlenv} -- doit clean_flow --extras >> ${benchLog} 2>&1
     if [ "${success}" = "true" ]; then
       printf "${statusLine}\n" "$setIdStr"  \
                                $benchCount  \
                                "<${bench}>" \
				"`echo \"${rules}\" | sed 's/ /,/g'`" \
				"`getRuntime $startTime`" \
				"success"
     fi
     popd > /dev/null
     benchCount=`expr ${benchCount} + 1`
   done
  #echo "${hline}"
  #echo "|       | Benchs set ${setId} completed         |                                   |"
  #echo "${hline}"
 }


 timedRunSet () {
   args=""
   if [ "${gf180rule}"     != "gds" ]; then args="${args} --gf180-drc";     fi
   if [ "${ihpsg13g2rule}" != "gds" ]; then args="${args} --ihpsg13g2-drc"; fi
   startTime="$SECONDS"
   setId="$1"
   rvalue=0
   ./bin/regression.sh --run-set=${setId} ${args}
   if [ $? -ne 0 ]; then rvalue=1; fi
   printf "           **Benchs set %u completed** %45s\n" "${setId}" "`getRuntime $startTime`"
   exit $rvalue
 }


 if [ "${runSetId}" = "not_set" ]; then
   echo ""
   echo "${hline}"
   echo "${header}"
   echo "${hline}"
   timedRunSet 1 &
   timedRunSet 2 &
   timedRunSet 3 &
   timedRunSet 4 &
   timedRunSet 5 &
   wait
   echo "${hline}"
   echo ""
   if [ -e "`pwd`/runset-1.failed" ]; then exit 1; fi
   if [ -e "`pwd`/runset-2.failed" ]; then exit 1; fi
   if [ -e "`pwd`/runset-3.failed" ]; then exit 1; fi
   if [ -e "`pwd`/runset-4.failed" ]; then exit 1; fi
   if [ -e "`pwd`/runset-5.failed" ]; then exit 1; fi
 else
   runSet ${runSetId}
 fi
 
 exit 0
