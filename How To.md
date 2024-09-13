# How To Doccument

## Use Scenario

You want to create new Firewall Rule but need informaiton about all possible settings.
#### 1. Use **read** to investigate the settings srtucture **```read(entity_type)```** method.

```python
from sophos_firewall_api import Firewall, EQ, NOT, LIKE

firewall = Firewall(username, password, firewall_ip)

entity_data = firewall.read("FirewallRule")
```
