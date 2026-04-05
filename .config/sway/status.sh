#!/bin/sh
RED="#ff5555"
PINK="#ff79c6"
PURPLE="#bd93f9"
WHITE="#ffffff"

echo '{"version":1}'
echo '['
echo '[]'

while true; do
    cpu_raw=$(awk '/^cpu /{u2=$2+$4; t2=$2+$3+$4+$5+$6+$7+$8; print u2, t2}' /proc/stat)
    sleep 1
    cpu_val=$(awk -v prev="$cpu_raw" 'BEGIN{split(prev,a," ")} /^cpu /{u=$2+$4; t=$2+$3+$4+$5+$6+$7+$8; printf "%.0f", (u-a[1])/(t-a[2])*100}' /proc/stat)
    cpu_color=$WHITE
    [ "$cpu_val" -gt 90 ] && cpu_color=$RED

    mem_val=$(awk '/MemTotal/{t=$2} /MemAvailable/{a=$2} END{printf "%.0f", (t-a)/t*100}' /proc/meminfo)
    mem_color=$PINK
    [ "$mem_val" -gt 90 ] && mem_color=$RED

    disk_pct=$(df / | awk 'NR==2{sub(/%/,"",$5); print $5}')
    disk_text=$(df -h / | awk 'NR==2{printf "%s/%s", $3, $2}')
    disk_color=$PURPLE
    [ "$disk_pct" -gt 90 ] && disk_color=$RED

    net_color=$WHITE
    iface=$(ip route show default 2>/dev/null | awk '{print $5; exit}')
    if [ -n "$iface" ]; then
        ip_addr=$(ip -4 addr show "$iface" 2>/dev/null | awk '/inet /{sub(/\/.*/, "", $2); print $2; exit}')
        net="${iface} ${ip_addr}"
    else
        net="down"
        net_color=$RED
    fi

    bat=""
    if [ -d /sys/class/power_supply/BAT0 ]; then
        cap=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null)
        state=$(cat /sys/class/power_supply/BAT0/status 2>/dev/null)
        [ "$state" = "Charging" ] && sym="+" || sym=""
        bat_color=$PINK
        [ "$state" != "Charging" ] && [ "$cap" -lt 15 ] && bat_color=$RED
        bat=",{\"full_text\":\" bat: ${cap}%${sym} \",\"color\":\"${bat_color}\"}"
    fi

    vol=$(pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null | grep -oP '\d+%' | head -1)
    vol=${vol:+,\{\"full_text\":\" vol: $vol \",\"color\":\"$PURPLE\"\}}

    date_str=$(date '+%a %b %d %H:%M')

    echo ",[{\"full_text\":\" cpu: ${cpu_val}% \",\"color\":\"${cpu_color}\"},{\"full_text\":\" mem: ${mem_val}% \",\"color\":\"${mem_color}\"},{\"full_text\":\" disk: ${disk_text} \",\"color\":\"${disk_color}\"},{\"full_text\":\" net: ${net} \",\"color\":\"${net_color}\"}${bat}${vol},{\"full_text\":\" ${date_str} \",\"color\":\"${PINK}\"}]"
done
