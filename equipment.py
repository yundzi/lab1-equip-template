"""Экипировка"""

SLOTS = ("head", "body", "right_hand", "left_hand", "ring_1", "ring_2")
HANDS = ("right_hand", "left_hand")


class Item:

    def __init__(self, name, slot, power=0, durability=100, level_req=1,
                 two_handed=False):
        self.name = name
        self.slot = slot
        self.power = power
        self.durability = durability
        self.level_req = level_req
        self.two_handed = two_handed

    def __bool__(self):
        return self.durability > 0

    def __repr__(self):
        return f"<{self.name} {self.slot} dur={self.durability}>"


class Player:
    def __init__(self, name, level=1, inventory=None, capacity=20):
        self.name = name
        self.level = level
        self.inventory = list(inventory) if inventory else []
        self.capacity = capacity
        self.slots = {slot: None for slot in SLOTS}

    def __repr__(self):
        return f"<{self.name} lvl={self.level} inv={len(self.inventory)}>"


def _seen(seen_items, item):
    for existing in seen_items:
        if existing is item:
            return True
    return False


def _add_unique(unique_items, item):
    if item is None:
        return
    if _seen(unique_items, item):
        return
    unique_items.append(item)


def _all_item_ids(player):
    ids = set()
    for item in player.inventory:
        ids.add(id(item))
    for slot in SLOTS:
        item = player.slots[slot]
        if item is not None:
            ids.add(id(item))
    return ids


def _assert_no_bad_duplicates(player):
    for inv_item in player.inventory:
        for slot in SLOTS:
            if player.slots[slot] is inv_item:
                assert False, "Вещь одновременно в инвентаре и слоте"

    for i in range(len(SLOTS)):
        for j in range(i + 1, len(SLOTS)):
            slot1 = SLOTS[i]
            slot2 = SLOTS[j]
            item1 = player.slots[slot1]
            item2 = player.slots[slot2]
            if item1 is not None and item1 is item2:
                assert item1.two_handed, "Одноручная вещь в двух слотах"
                assert slot1 in HANDS and slot2 in HANDS, "Двуручная вещь не в руках"


def _assert_invariant(player, before_ids):
    after_ids = _all_item_ids(player)
    assert before_ids == after_ids, "Набор вещей изменился"
    _assert_no_bad_duplicates(player)


def _inventory_count(player, item):
    count = 0
    for inv_item in player.inventory:
        if inv_item is item:
            count += 1
    return count


def _remove_from_inventory(player, item):
    kept = []
    for inv_item in player.inventory:
        if inv_item is item:
            continue
        kept.append(inv_item)
    player.inventory[:] = kept


def _is_equipped(player, item):
    for slot in SLOTS:
        if player.slots[slot] is item:
            return True
    return False


def _hand_items_unique(player):
    unique = []
    for slot in HANDS:
        item = player.slots[slot]
        if item is not None:
            _add_unique(unique, item)
    return unique


def _can_return_after_remove(player, item, count_returns):
    count_in_inv = _inventory_count(player, item)
    if count_in_inv == 0:
        return False
    after_remove = len(player.inventory) - count_in_inv
    free_space = player.capacity - after_remove
    return count_returns <= free_space


def _equip_one_handed(player, item):
    target = item.slot
    old_items = []
    old = player.slots[target]
    if old is not None:
        _add_unique(old_items, old)

    if not _can_return_after_remove(player, item, len(old_items)):
        return False

    _remove_from_inventory(player, item)
    for old_item in old_items:
        player.inventory.append(old_item)

    if old is not None and old.two_handed:
        player.slots["right_hand"] = None
        player.slots["left_hand"] = None

    player.slots[target] = item
    return True


def _equip_two_handed(player, item):
    old_items = _hand_items_unique(player)
    if not _can_return_after_remove(player, item, len(old_items)):
        return False

    _remove_from_inventory(player, item)
    for old_item in old_items:
        player.inventory.append(old_item)

    player.slots["right_hand"] = item
    player.slots["left_hand"] = item
    return True


def _equip(player, item):
    if player is None or item is None:
        return False
    if item.slot not in SLOTS:
        return False
    if player.level < item.level_req:
        return False
    if _inventory_count(player, item) == 0:
        return False
    if _is_equipped(player, item):
        return False

    if item.two_handed:
        return _equip_two_handed(player, item)
    return _equip_one_handed(player, item)


def equip(player, item):
    before_ids = _all_item_ids(player)
    result = _equip(player, item)
    _assert_invariant(player, before_ids)
    return result


def _unequip(player, slot):
    if player is None:
        return False
    if slot not in SLOTS:
        return False
    item = player.slots[slot]
    if item is None:
        return False
    if len(player.inventory) >= player.capacity:
        return False

    if item.two_handed:
        player.slots["right_hand"] = None
        player.slots["left_hand"] = None
    else:
        player.slots[slot] = None

    player.inventory.append(item)
    return True


def unequip(player, slot):
    before_ids = _all_item_ids(player)
    result = _unequip(player, slot)
    _assert_invariant(player, before_ids)
    return result


def total_power(player):
    power = 0
    seen = []
    for slot in SLOTS:
        item = player.slots[slot]
        if item is None:
            continue
        if _seen(seen, item):
            continue
        seen.append(item)
        if item.durability > 0:
            power += item.power
    return power
