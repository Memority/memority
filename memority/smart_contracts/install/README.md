
# prepare clint
geth --datadir client_dir/ init mmr_chain_v1.json 

# copy nodes addresses to client dir
cp static-nodes.json client_dir/geth/

# start client
geth --datadir client_dir/ --port 30320 --networkid 232019 --identity mmr_chain_v1 --nodiscover

# start light client
geth --verbosity 5 --datadir client_dir/ --port 30710 --networkid 232019 --identity mmr_chain _v1 --nodiscover --lightserv 25 --lightpeers 10

# token contract address
0x2c02Aaa80ADC4cdF6Bf33ce36Fffc8A380C3bD34