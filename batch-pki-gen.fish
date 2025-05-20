set -l NUM_CLIENTS 100

for i in (seq 1 $NUM_CLIENTS)
    echo "fish pki-gen.fish -c client$i"
    fish pki-gen.fish -c client$i
end

