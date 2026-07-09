# ---------------------------------------------------------------------
# dicttoolz: non-mutating dictionary updates
# ---------------------------------------------------------------------

heading("A profile to evolve")
note(
    "Every <code>dicttoolz</code> function returns a <em>new</em> "
    "dictionary. The original input is left alone -- nice for "
    "predictable, pure-function-style code."
)

profile = {
    "name": "Ada Lovelace",
    "email": "ada@example.org",
    "preferences": {
        "theme": "light",
        "notifications": {"email": True, "sms": False},
    },
    "tags": ["analyst", "mathematician"],
}

heading("assoc and dissoc: add or remove a top-level key")
with_phone = assoc(profile, "phone", "555-0100")
without_email = dissoc(with_phone, "email")
display(without_email, append=True)

heading("get_in and update_in: read or change a nested path")
note("Drill down by giving a list of keys.")
sms_setting = get_in(["preferences", "notifications", "sms"], profile)
note(f"Current SMS setting: <strong>{sms_setting}</strong>")

# Flip the SMS notification setting deep inside the structure.
updated = update_in(
    profile,
    ["preferences", "notifications", "sms"],
    lambda v: not v,
)
display(updated["preferences"], append=True)
note(
    f"Original is unchanged: "
    f"<code>{profile['preferences']['notifications']}</code>"
)

heading("valmap and keyfilter: bulk transforms")
inventory = {"apples": 12, "pears": 5, "plums": 0, "figs": 8}

# Double every count.
doubled = valmap(lambda n: n * 2, inventory)
display(doubled, append=True)

# Keep only the items still in stock.
in_stock = keyfilter(lambda k: inventory[k] > 0, inventory)
display(in_stock, append=True)

heading("merge and merge_with: combine many dicts")
note(
    "<code>merge</code> takes the rightmost value on conflict. "
    "<code>merge_with</code> lets you choose how to combine values."
)

monday = {"latte": 12, "espresso": 7, "mocha": 3}
tuesday = {"latte": 9, "espresso": 11, "tea": 4}
wednesday = {"latte": 15, "mocha": 6, "tea": 2}

last_wins = merge(monday, tuesday, wednesday)
display(last_wins, append=True)

# Sum each drink's count across all three days.
weekly_totals = merge_with(sum, monday, tuesday, wednesday)
display(weekly_totals, append=True)
