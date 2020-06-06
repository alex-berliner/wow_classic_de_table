-- itemlevel:type[weapon|armor]:quality[uncommon|rare|epic] = list of "result_id:times_seen:number_of_items_yielded:0"
-- imports an Enchantrix.lua file and outputs the contents of its EnchantedItemTypes as
-- ilvl:quality:type ### yielded_item1:times_seen1:number_of_items_yielded1:0;yielded_item2:times_seen2:number_of_items_yielded2:0;...
-- quality:
--     2: "Uncommon",
--     3: "Rare",
--     4: "Epic",
--     5: "Legendary",
-- type:
--     2: "Weapon",
--     4: "Armor",
require "Enchantrix"
function setContains(set, key)
    return set[key] ~= nil
end

function main()
    for i=0, 100 do
        for j=0, 6 do
            for k=0, 6 do
                key = tostring(i) .. ":" ..tostring(j) .. ":" ..tostring(k)
                if setContains(EnchantedItemTypes, key) then
                    print(key .. " ### " .. EnchantedItemTypes[key])
                end
            end
        end
    end
end

main()
