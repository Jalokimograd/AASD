from spade.template import Template

# zapytanie o sąsiadów innego agenta
REQUEST_NEIGHBORS_LIST: Template = Template(
    metadata=dict(performative="neighbors_list"),
)

# Odebranie propozycji zmiany trasy
PATH_OFFER: Template = Template(
    metadata=dict(performative="path_offer")
)

# Pytanie od innego tubylca czy dany agent nadal jest dostępny (porównywana jest odległośc od siebie)
AVAILABILITY: Template = Template(
    metadata=dict(performative="availability")
)

# Odebranie informacji rozgłoszeniowej o obecności agenta w pobliżu
BROADCAST: Template = Template(
    metadata=dict(performative="broadcast")
)

# ================================================================================================
ACTUALIZE_INFORMATION: Template = Template(
    metadata=dict(performative="environment_actualize")
)

