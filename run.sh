python3 table_parse.py
# uncomment these to see intermediate results
rm -rf enchant_table_*.txt
rm -rf Enchantrix.lua

cp READMEBASE.md README.md
mdtable detable.csv >> README.md
