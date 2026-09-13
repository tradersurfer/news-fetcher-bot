"""
X Profiles to Monitor — add the handles you provide.
Default: Google Search is the primary news source.
X profiles are supplementary for breaking news from companies/CEOs.
"""

# Bitcoin-specific / News
X_PROFILES = [
    # Company / CEO C-Suite (breaking news source)
    "saylor",           # Michael Saylor / Strategy
    "Strategy",         # Strategy (MicroStrategy)
    "Coinbase",         # Coinbase
    "BlackRock",        # BlackRock IBIT
    "Fidelity",         # Fidelity Digital Assets
    "ARKInvest",        # ARK Invest

    # News / Analysis
    "coindesk",         # CoinDesk
    "TheBlock",         # The Block
    "cointelegraph",    # Cointelegraph
    "bitcoinmagazine",  # Bitcoin Magazine

    # Your specific additions
    "geyserfund",       # Geyser Fund
    "freddienew",       # Fredi Neue
    "cakewallet",       # Cake Wallet
    "sethforprivacy",   # Seth For Privacy
    "lnbits",           # LNBits - Lightning News
    "LightningNewsX",   # Lightning News
    "utexo",            # UTXO - Bitcoin payments
    "blocks",           # Block / Jack
    "blockIR",          # Block IR
    "jack",             # Jack Dorsey (no reposts)
    "glxyresearch",     # Galaxy Research
    "ODELLXYZ",         # Odell / Square / CashApp
    "WatcherGuru",      # WatcherGuru
    # Analysts
    "cryptovizart",     # Glassnode
    "ccleffert",        # Punchbowl News
    "LauraEWeiss16",    # Punchbowl News
    "coffeebreak_YT",   # Bitcoin only
    "ZynxBTC",          # Analysis only (manual review)
]

# Profiles that should be logged but NOT auto-posted (manual review)
MANUAL_REVIEW_ONLY = [
    "saifedean",    # Quotes only, never auto-post
    "ZynxBTC",      # Analysis only, run through you first
    "jordanguess",  # Only when Bitcoin/crypto specific
]
