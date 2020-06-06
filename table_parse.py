import copy
from collections import OrderedDict
import subprocess

rarity_lut = OrderedDict({
    2: "Uncommon",
    3: "Rare",
    4: "Epic",
    5: "Legendary",
})
itype_lut = OrderedDict({
    2: "Weapon",
    4: "Armor",
})

def docmd(cmd):
    # make delimiter something stupid so we can have spaces in names and because i'm lazy
    # check_output expects to get arguments as a list, so we need a delimiter for paths with spaces
    return subprocess.check_output(cmd.split(",,,,,,,,")).decode("utf-8")

# make bidirectional lookup table for item names and IDs
def load_items_csv(item_db):
    f = open("item_names.csv").readlines()
    for e in f:
        esplit = e.split(",")
        iid  = int(esplit[0])
        name = "".join(esplit[1:]).strip().lower()
        item_db[name] = iid
        item_db[iid]  = name

# kirtonos alliance price lookup table
def price_table(item_cost):
    item_cost["strange dust"]            = 256
    item_cost["lesser magic essence"]    = 697
    item_cost["greater magic essence"]   = 1526
    item_cost["small glimmering shard"]  = 194
    item_cost["soul dust"]               = 1177
    item_cost["large glimmering shard"]  = 1780
    item_cost["lesser mystic essence"]   = 2300
    item_cost["greater mystic essence"]  = 5800
    item_cost["large glowing shard"]     = 3200
    item_cost["vision dust"]             = 242
    item_cost["lesser nether essence"]   = 11599
    item_cost["small radiant shard"]     = 49246
    item_cost["greater nether essence"]  = 29000
    item_cost["dream dust"]              = 1775
    item_cost["large radiant shard"]     = 55500
    item_cost["lesser eternal essence"]  = 26400
    item_cost["greater eternal essence"] = 62998
    item_cost["large brilliant shard"]   = 29399
    item_cost["illusion dust"]           = 1403
    item_cost["lesser astral essence"]   = 5300
    item_cost["greater astral essence"]  = 6499
    item_cost["small glowing shard"]     = 1290
    item_cost["small brilliant shard"]   = 19960


    # make the prices of essences the minimum of the price of lesser and greater, because they're
    # interchangable
    triple_min = min(item_cost["lesser magic essence"]*3, item_cost["greater magic essence"])
    item_cost["lesser magic essence"] = triple_min/3
    item_cost["greater magic essence"] = triple_min

    triple_min = min(item_cost["lesser mystic essence"]*3, item_cost["greater mystic essence"])
    item_cost["lesser mystic essence"] = triple_min/3
    item_cost["greater mystic essence"] = triple_min

    triple_min = min(item_cost["lesser nether essence"]*3, item_cost["greater nether essence"])
    item_cost["lesser nether essence"] = triple_min/3
    item_cost["greater nether essence"] = triple_min

    triple_min = min(item_cost["lesser eternal essence"]*3, item_cost["greater eternal essence"])
    item_cost["lesser eternal essence"] = triple_min/3
    item_cost["greater eternal essence"] = triple_min

    triple_min = min(item_cost["lesser astral essence"]*3, item_cost["greater astral essence"])
    item_cost["lesser astral essence"] = triple_min/3
    item_cost["greater astral essence"] = triple_min

# use ench_import.lua to convert each lua log to a text file
# see docmd() for comma delimiter explanation
def lua_convert():
    # get all files in dbfiles
    files = docmd("ls,,,,,,,,dbfiles").strip().split("\n")
    for i in range(len(files)):
        f = files[i]
        # copy working file to upper directory so ench_import.lua can include it when run
        docmd("""cp,,,,,,,,dbfiles/%s,,,,,,,,Enchantrix.lua"""%(f))
        # run lua converter and save it to a text file
        open("enchant_table_%d.txt"%(i), "w").write(docmd("lua,,,,,,,,ench_import.lua"))
    return ["enchant_table_%d.txt"%(i) for i in range(len(files))]

# parse an enchant_table_*.txt file and add its contents to data_handle
# table format:
#    ilvl:quality:type ### yielded_item1:times_seen1:number_of_items_yielded1:0;yielded_item2:times_seen2:number_of_items_yielded2:0;...
# @data_handle is set up to be like a json file, there are nested dicts for each level of
# information, with the final level being just information leaves (no more branches necessary)
def parse_file(filename, data_handle):
    enchant_table_str = [x.strip() for x in open(filename, "r").readlines()]
    for e in enchant_table_str:
        conts = e.split("### ")
        key_split = conts[0].split(":")
        item_levl = int(key_split[0])
        item_qual = int(key_split[1])
        item_type = int(key_split[2])

        # parse fields before ### delimiter
        # cur_level, cur_type, and cur_qual each delve one level deeper into the tree
        if item_levl not in data_handle:
            data_handle[item_levl] = OrderedDict()
        cur_level = data_handle[item_levl]

        if item_type not in data_handle[item_levl]:
            cur_level[item_type] = OrderedDict()
        cur_type = cur_level[item_type]

        if item_qual not in cur_type:
            data_handle[item_levl][item_type][item_qual] = OrderedDict()
        cur_qual = data_handle[item_levl][item_type][item_qual]

        # parse fields after ### delimiter
        for result in conts[1].split(";"):
            indiv_result = result.split(":")
            result_id     = int(indiv_result[0])
            times_seen    = int(indiv_result[1])
            items_yielded = int(indiv_result[2])
            if result_id not in cur_qual:
                # tuple of type (times_seen, items_yielded)
                cur_qual[result_id] = (0,0)
            cur_res = cur_qual[result_id]
            cur_qual[result_id] = (cur_res[0] + times_seen, cur_res[1] + items_yielded)

def main():
    tables_converted = lua_convert()

    item_cost = OrderedDict()
    price_table(item_cost)

    # bidirectional lookup table for item names and IDs
    item_db = OrderedDict()
    load_items_csv(item_db)

    data_handle = OrderedDict()
    for f in tables_converted:
        parse_file(f, data_handle)

    csv = ""
    CSV_STRING = "#rarity, #itype, #ilvl, #item_drop_id, #item_drop_name, #item_amt, #yield_pct, #trials"
    csv += CSV_STRING.replace("#", "") + "\n"
    for rarity in rarity_lut:
        for itype in itype_lut:
            for ilvl in range(75):
                if      ilvl   in data_handle and \
                        itype  in data_handle[ilvl] and \
                        rarity in data_handle[ilvl][itype]:
                    de_total = float(sum([data_handle[ilvl][itype][rarity][y][0] for y in data_handle[ilvl][itype][rarity]]))
                    for yielded in data_handle[ilvl][itype][rarity]:
                        total_disenchants = float(data_handle[ilvl][itype][rarity][yielded][1])
                        total_yeilded = float(data_handle[ilvl][itype][rarity][yielded][0])
                        avg_yield = total_disenchants/total_yeilded
                        drop_chance = float(data_handle[ilvl][itype][rarity][yielded][0]/de_total)

                        item_yield_csv_string = copy.deepcopy(CSV_STRING)
                        item_yield_csv_string = item_yield_csv_string.replace("#rarity", rarity_lut[rarity])
                        item_yield_csv_string = item_yield_csv_string.replace("#itype", itype_lut[itype])
                        item_yield_csv_string = item_yield_csv_string.replace("#ilvl", str(ilvl))
                        item_yield_csv_string = item_yield_csv_string.replace("#item_drop_id", str(yielded))
                        item_yield_csv_string = item_yield_csv_string.replace("#item_drop_name", item_db[yielded])
                        item_yield_csv_string = item_yield_csv_string.replace("#item_amt",  "%2.5f"%avg_yield)
                        item_yield_csv_string = item_yield_csv_string.replace("#yield_pct", "%2.5f"%drop_chance)
                        item_yield_csv_string = item_yield_csv_string.replace("#trials", str(int(de_total)))
                        csv += item_yield_csv_string + "\n"
    print("table written to detable.csv")
    open("detable.csv", "w").write(csv)

main()
