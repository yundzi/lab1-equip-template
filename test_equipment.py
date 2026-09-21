from equipment import Item, Player, equip, unequip, total_power


def _contains(items, item):
    for existing in items:
        if existing is item:
            return True
    return False


def count_unique(player):
    seen = []
    for item in player.inventory:
        if not _contains(seen, item):
            seen.append(item)
    for slot in player.slots:
        item = player.slots[slot]
        if item is not None and not _contains(seen, item):
            seen.append(item)
    return len(seen)


def assert_preserved(player, before):
    after = count_unique(player)
    assert after == before, (before, after)


def test_equip_swap_and_two_handed():
    sword = Item("sword", "right_hand", power=10)
    shield = Item("shield", "left_hand", power=5)
    axe = Item("axe", "right_hand", power=20, two_handed=True)

    p = Player("A", level=5, inventory=[sword, shield, axe])
    before = count_unique(p)

    assert equip(p, sword) is True
    assert_preserved(p, before)
    assert p.slots["right_hand"] is sword

    assert equip(p, shield) is True
    assert_preserved(p, before)
    assert p.slots["left_hand"] is shield

    assert equip(p, axe) is True
    assert_preserved(p, before)
    assert p.slots["right_hand"] is axe
    assert p.slots["left_hand"] is axe
    assert sword in p.inventory
    assert shield in p.inventory
    assert total_power(p) == 20

    assert unequip(p, "left_hand") is True
    assert_preserved(p, before)
    assert p.slots["right_hand"] is None
    assert p.slots["left_hand"] is None
    assert axe in p.inventory


def test_broken_item():
    broken = Item("broken", "head", power=10, durability=0)
    p = Player("A", inventory=[broken])
    before = count_unique(p)

    assert equip(p, broken) is True
    assert_preserved(p, before)
    assert p.slots["head"] is broken
    assert total_power(p) == 0

    assert unequip(p, "head") is True
    assert_preserved(p, before)
    assert p.slots["head"] is None
    assert broken in p.inventory


def test_full_inventory_two_handed_refuse():
    right = Item("right", "right_hand", power=1)
    left = Item("left", "left_hand", power=1)
    axe = Item("axe", "right_hand", power=10, two_handed=True)

    p = Player("A", inventory=[axe], capacity=1)
    p.slots["right_hand"] = right
    p.slots["left_hand"] = left

    before = count_unique(p)
    assert equip(p, axe) is False
    assert_preserved(p, before)
    assert p.slots["right_hand"] is right
    assert p.slots["left_hand"] is left
    assert axe in p.inventory
