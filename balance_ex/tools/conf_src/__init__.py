"""
Python source of truth for `settings.xml`.

Install deps (for generator + type checking):

    pip install -r balance_ex/tools/requirements.txt

Generate XML:

    python3 balance_ex/tools/generate_settings_xml.py

Bootstrap from an existing XML (one-time):

    python3 balance_ex/tools/convert_settings_xml_to_py.py \
      --in balance_ex/balance_ex/conf/settings.xml \
      --out balance_ex/balance_ex/conf/settings_src/from_xml.py

Then in this file you can switch to:

    from .from_xml import CONFIG

Run pyright (strict) for just this config:

    cd balance_ex/tools
    pyright
"""

from .settings_config import CONFIG


