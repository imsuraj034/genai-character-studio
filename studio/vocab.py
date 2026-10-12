"""Shared vocabulary: element keywords, ability pools, personality voices."""

# Words that reveal which element an ability uses. The consistency checker
# uses these to detect off-faction magic.
ELEMENT_KEYWORDS = {
    "ice": ["ice", "frost", "glacier", "rime", "snow", "frozen", "freeze", "blizzard", "hail"],
    "fire": ["fire", "flame", "ember", "magma", "lava", "inferno", "blaze", "cinder", "scorch"],
    "nature": ["vine", "thorn", "bloom", "root", "leaf", "pollen", "grove", "briar"],
    "earth": ["stone", "boulder", "quake", "granite", "earthen", "mudslide", "crag"],
    "water": ["tide", "wave", "current", "torrent", "riptide", "brine", "whirlpool"],
    "storm": ["storm", "thunder", "lightning", "gale", "tempest", "squall"],
}

ABILITY_POOL = {
    "ice": [
        ("Rime Lance", "hurls a spear of packed frost that slows enemies"),
        ("Glacier Ward", "raises a wall of ice that absorbs the next blow"),
        ("Blizzard Step", "dashes through a burst of snow, leaving a frozen trail"),
        ("Frostbind", "roots a foe in place with creeping frozen chains"),
    ],
    "fire": [
        ("Cinder Burst", "detonates a ring of embers around the caster"),
        ("Magma Brand", "marks a foe so the next hit sears for extra damage"),
        ("Blaze Rush", "charges forward wrapped in a flame cloak"),
        ("Inferno Sigil", "draws a fire rune that ignites enemies who cross it"),
    ],
    "nature": [
        ("Thornlash", "whips a briar vine that pulls enemies closer"),
        ("Bloomheal", "grows healing flowers that restore nearby allies"),
        ("Rootsnare", "roots burst from the ground to trap a target"),
    ],
    "earth": [
        ("Granite Skin", "hardens the body like stone for a short time"),
        ("Quake Stomp", "sends a shockwave through the earth, knocking foes down"),
    ],
    "water": [
        ("Riptide Pull", "drags an enemy across the field on a rushing current"),
        ("Tidal Mend", "washes allies in a wave that cleanses poison"),
        ("Whirlpool Trap", "spins a whirlpool that holds enemies in place"),
    ],
    "storm": [
        ("Thunderclap", "stuns nearby enemies with a crack of thunder"),
        ("Gale Leap", "rides a gust of wind to reach high ground"),
        ("Tempest Arrow", "fires a bolt of lightning that chains between foes"),
    ],
}

CLASS_ABILITIES = {
    "Warrior": ("Shield Oath", "plants their feet and taunts every enemy nearby"),
    "Mage": ("Aether Focus", "channels a shard to double the next spell's power"),
    "Rogue": ("Shadow Feint", "slips behind a target after a quick decoy strike"),
    "Healer": ("Mending Hymn", "restores health to the whole party over time"),
    "Ranger": ("Hawk Eye", "marks a distant target so allies deal extra damage"),
    "Bard": ("Rally Ballad", "plays a song that boosts the party's speed"),
}

PERSONALITIES = {
    "Brave": {
        "greeting": ["Stand tall, traveller. Whatever comes, we face it together.",
                     "You look ready for trouble. Good. So am I."],
        "battle": ["Behind me! I will hold the line.", "This is where legends are made!"],
        "trade": ["Fair prices for honest blades.", "Take it. It served me well, it will serve you better."],
        "betrayal": ["I trusted you with my life... and you sold it.", "Draw your weapon. I will not ask twice."],
        "victory": ["We did it! Tell the songs it was easy.", "Another dawn earned."],
        "defeat": ["Not... yet. I can still stand.", "Fall back. Live to fight another day."],
    },
    "Sarcastic": {
        "greeting": ["Oh good, another hero. We were running low.",
                     "Let me guess: you need a favour. Everyone does."],
        "battle": ["Great. Monsters. My favourite.", "Try not to die, it ruins my afternoon."],
        "trade": ["Prices are fixed. My patience is not.", "It's cursed, probably. Half price."],
        "betrayal": ["Surprised? You really should be more careful who you trust.",
                     "Nothing personal. Well, a little personal."],
        "victory": ["Wow, we survived. Write that down.", "I'd celebrate, but I'm exhausted."],
        "defeat": ["Well. That went exactly as badly as I predicted.", "Note to self: never listen to the hero."],
    },
    "Wise": {
        "greeting": ["The Aether whispered you would come.", "Sit, child. Every journey begins with listening."],
        "battle": ["Breathe. Strike only when the moment is true.", "Patience is a blade too."],
        "trade": ["What you seek has a price, and not always in coin.", "Take this. You will know when to use it."],
        "betrayal": ["I saw this path long ago. I hoped I was wrong.", "Even the wise can be blind to those they love."],
        "victory": ["The balance holds, for now.", "Remember this day, and what it cost."],
        "defeat": ["Defeat is a teacher. Listen to it.", "Retreat is not shame. It is wisdom."],
    },
    "Cunning": {
        "greeting": ["A new face. Useful, perhaps.", "Everyone in Lumen Ford owes me something. Soon, so will you."],
        "battle": ["Let them charge. I prepared the ground.", "Strike the leader. The rest will scatter."],
        "trade": ["Information costs more than steel.", "I have exactly what you need. Funny, isn't it?"],
        "betrayal": ["Did you think I was ever on your side?", "Every alliance has an expiry date."],
        "victory": ["Just as planned. Mostly.", "The board is clearing nicely."],
        "defeat": ["A setback. Nothing more.", "You won the battle. Let's see about the war."],
    },
    "Gentle": {
        "greeting": ["Oh! You're hurt. Let me help.", "Welcome, friend. Rest a while."],
        "battle": ["Please, let's end this quickly.", "Stay close, I'll keep you safe."],
        "trade": ["Take what you need. Pay what you can.", "These herbs will ease the pain."],
        "betrayal": ["Why...? I would have helped you anyway.", "I forgive you. But I can't follow you."],
        "victory": ["Is everyone alright? That's all that matters.", "Let's tend the wounded first."],
        "defeat": ["I'm sorry... I couldn't save them all.", "We'll heal. We always do."],
    },
    "Ruthless": {
        "greeting": ["Speak quickly. My time is worth more than yours.", "Kneel, or step aside."],
        "battle": ["Leave none standing.", "Mercy is a luxury for the weak."],
        "trade": ["Pay double, or leave.", "I don't haggle."],
        "betrayal": ["You were always a tool. Tools break.", "Loyalty is just fear wearing a mask."],
        "victory": ["As expected.", "Burn their banners."],
        "defeat": ["This changes nothing!", "I will return, and you will regret this day."],
    },
}

SITUATIONS = {
    "Greeting the player": "greeting",
    "Before a boss fight": "battle",
    "Trading / shop": "trade",
    "Betrayal reveal": "betrayal",
    "Victory": "victory",
    "Defeat": "defeat",
}

APPEARANCE_BUILDS = ["tall and wiry", "broad-shouldered", "small and quick", "lean and weathered", "sturdy and calm"]
APPEARANCE_FEATURES = [
    "a scar across one eyebrow", "braided hair threaded with beads", "mismatched eyes",
    "tattooed forearms", "a crooked, friendly smile", "a cloak patched from many journeys",
    "ink-stained fingers", "a missing fingertip they joke about",
]
FLAWS = ["too proud to ask for help", "far too trusting", "haunted by a past failure",
         "reckless when friends are in danger", "secretive to a fault", "afraid of deep water"]
MOTIVATIONS = ["restore their family's lost honour", "find the last shard of the Sun-Crown",
               "protect their homeland from the coming war", "repay a debt to a mysterious stranger",
               "prove that the factions can live in peace", "uncover who betrayed their mentor"]

ARC_TEMPLATES = {
    "Redemption": {
        "logline": "{name} must undo the harm they caused before {rival} forces exploit it.",
        "beats": [
            "{name} is exiled from {homeland} after a mistake costs lives.",
            "In {place}, they protect strangers from {rival} raiders and earn a second chance.",
            "{name} returns home carrying {item} and saves the people who cast them out.",
        ],
        "ending": "Forgiven, but changed: {name} chooses to stay a wanderer.",
    },
    "Betrayal": {
        "logline": "{name} is the player's closest ally until a secret pact with the {rival} surfaces.",
        "beats": [
            "{name} joins the party and quickly becomes indispensable.",
            "Clues in {place} reveal coded letters bearing the {rival} seal.",
            "{name} steals {item} at the worst moment, forcing a final duel.",
        ],
        "ending": "The player can spare or defeat {name}, changing the ending.",
    },
    "Tragic Sacrifice": {
        "logline": "To stop a war, {name} must give up the one thing they cannot replace.",
        "beats": [
            "{name} discovers that {item} can seal a rift in {place}.",
            "Both the {faction} and the {rival} hunt them for its power.",
            "{name} uses {item} and is lost, but the war is stopped.",
        ],
        "ending": "A statue in {homeland} remembers them; their dialogue echoes in a hidden quest.",
    },
    "Rise to Power": {
        "logline": "{name} climbs from nobody to leader of the {faction}, and the climb costs them friends.",
        "beats": [
            "{name} wins a tournament in {place} and catches the elders' eye.",
            "They outmanoeuvre rivals, sometimes unfairly, using {item}.",
            "Crowned leader, {name} must decide whether to declare war on the {rival}.",
        ],
        "ending": "Player choice decides if {name} becomes a wise ruler or the next villain.",
    },
    "Hidden Heir": {
        "logline": "{name} learns they carry the bloodline of the Sun-Crown's last keeper.",
        "beats": [
            "A dying stranger in {place} recognises the mark on {name}'s wrist.",
            "Assassins from both the {faction} and the {rival} close in.",
            "{name} refuses the throne and uses {item} to protect the shard instead.",
        ],
        "ending": "Sets up a sequel hook: another heir exists.",
    },
}
