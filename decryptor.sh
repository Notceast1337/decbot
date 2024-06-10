#!/bin/bash
pattern=false
ulimit -s unlimited >/dev/null 2>&1
echo ""
echo "Universal Shell DEC 8.8"
dec() {
  if grep -q -e '=.*;.*=.*;' -e 'base64 -d | sh$' -e '| base64 -d' -e '" | sh' -e '^#[[:print:]]\{50,\}' "$(pwd)/$shuf.temp1.sh"; then
    while true; do
      if grep -q '=.*;.*=.*;' "$(pwd)/$shuf.temp1.sh"; then
        counter=$((counter + 1))
        echo "$counter. Eval" >> "$(pwd)/decrypt.log"
        sed 's/eval "\$/echo "\$/g; s/\[ "$(id -u)" -ne 2000 \]/! true/' "$(pwd)/$shuf.temp1.sh" > "$(pwd)/$shuf.temp2.sh"
        bash "$(pwd)/$shuf.temp2.sh" > "$(pwd)/$shuf.temp1.sh"
        rm "$(pwd)/$shuf.temp2.sh"
      elif grep -q 'base64 -d | sh$' "$(pwd)/$shuf.temp1.sh"; then
        counter=$((counter + 1))
        echo "$counter. Base64" >> "$(pwd)/decrypt.log"
        sed 's/base64 -d | sh/base64 -d/; s/\[ "$(id -u)" -ne 2000 \]/! true/' "$(pwd)/$shuf.temp1.sh" > "$(pwd)/$shuf.temp2.sh"
        bash "$(pwd)/$shuf.temp2.sh" > "$(pwd)/$shuf.temp1.sh"
        rm "$(pwd)/$shuf.temp2.sh"
      elif grep -q '| base64 -d' "$(pwd)/$shuf.temp1.sh"; then
        counter=$((counter + 1))
        echo "$counter. base64eval" >> "$(pwd)/decrypt.log"
        sed 's/eval "\$/echo "\$/g; s/\[ "$(id -u)" -ne 2000 \]/! true/' "$(pwd)/$shuf.temp1.sh" > "$(pwd)/$shuf.temp2.sh"
        bash "$(pwd)/$shuf.temp2.sh" > "$(pwd)/$shuf.temp1.sh"
        rm "$(pwd)/$shuf.temp2.sh"
      elif grep -q '" | sh' "$(pwd)/$shuf.temp1.sh"; then
        counter=$((counter + 1))
        echo "$counter. Other" >> "$(pwd)/decrypt.log"
        sed 's/\" | sh/\" > \"\$(pwd)\/$shuf.temp1.sh\"/g; s/\[ "$(id -u)" -ne 2000 \]/! true/' "$(pwd)/$shuf.temp1.sh" > "$(pwd)/$shuf.temp2.sh"
        bash "$(pwd)/$shuf.temp2.sh"
        rm "$(pwd)/$shuf.temp2.sh"
      elif grep -q '^#[[:print:]]\{50,\}' "$(pwd)/$shuf.temp1.sh"; then
        counter=$((counter + 1))
        echo "$counter. Pattern" >> "$(pwd)/decrypt.log"
        cp "$(pwd)/$shuf.temp1.sh" "$(pwd)/$shuf.temp2.sh"
        cat "$(pwd)/$shuf.temp2.sh" | grep -v '^#[[:print:]]\{50,\}' > "$(pwd)/$shuf.temp1.sh"
        rm "$(pwd)/$shuf.temp2.sh"
        pattern=true
      else
        break
      fi
    done
  else
    for sec in $(seq 1 16); do
      exec="$(pwd)/$shuf.temp1.sh"
      "$exec" > /dev/null 2>&1 &
      child=$!
      sleep 0.0"$sec"
      kill -STOP $child
      cmdline=$(cat /proc/$child/cmdline)
      echo "$cmdline" | sed 's/.*\(#!\)/\1/' | head -c "-$(echo "$exec" | wc -c)" > "$(pwd)/$shuf.temp2.sh"
      kill -TERM $child
      if grep -q '#!/' "$(pwd)/$shuf.temp2.sh"; then
        counter=$((counter + 1))
        echo "$counter. SHC" >> "$(pwd)/decrypt.log"
        break
      else
        rm "$(pwd)/$shuf.temp2.sh"
        touch "$(pwd)/$shuf.temp2.sh"
      fi
    done
  fi
  mv "$(pwd)/$shuf.temp2.sh" "$(pwd)/$shuf.temp1.sh"
  echo ""
}

if [ "$#" -eq 0 ]; then
  echo "Usage: bash decryptor.sh <file_to_decrypt>"
  exit 1
fi

input="$1"

if [ ! -f "$input" ]; then
  echo "Error: File not found."
  exit 1
fi

shuf=$(shuf -i 1-100 -n 1)
counter=0
touch "$(pwd)/decrypt.log"
cp "$input" "$(pwd)/$shuf.temp1.sh"
chmod +x "$(pwd)/$shuf.temp1.sh"
echo "Decrypting $(basename "$input")"
dec > /dev/null 2>&1
if grep -q -e '=.*;.*=.*;' -e 'base64 -d | sh$' -e '| base64 -d' -e '" | sh' -e '^#[[:print:]]\{50,\}' "$(pwd)/$shuf.temp1.sh"; then
  dec > /dev/null 2>&1
fi
cat "$(pwd)/decrypt.log"
rm "$(pwd)/decrypt.log"
if [ -s "$(pwd)/$shuf.temp1.sh" ]; then
  mv "$(pwd)/$shuf.temp1.sh" "$input"
  echo "Success: Decryption of $(basename "$input") completed."
else
  echo "Failed: Unable to decrypt $(basename "$input")."
  rm "$(pwd)/$shuf.temp1.sh"
fi

echo ""
if [ "$pattern" = true ]; then
  echo "Warning: Decryption pattern mode used. Some code comments may be lost."
  echo ""
fi
