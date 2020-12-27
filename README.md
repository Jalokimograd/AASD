# Program na urządzenia mobilne do optymalizacji trasy

## Informacje:
Program powstaje na potrzeby zajęć Agentowe i Aktorowe Systemy Decyzyjne (AASD)
Pisany w pythonie 3.6 na Linuxie ubuntu
System agentowy opiera się na bibliotece SPADE 'https://spade-mas.readthedocs.io/en/latest/readme.html'
Zastosowany serwer XMPP: prosody 'https://prosody.im/'

Docelowa wersja programu zakłada działanie na urządzeniach mobilnych, gdzie urządzenia sąsiednie 
będą wykrywane przy pomocy czujników wbudowanych. 
Aktualna wersja pełni rolę symulacji działania takiego systemu i rolę środowiska (eteru) pełni agent "EnvironmentManager",
który zna położenie każdego urządzenia i sztucznie zapewnia połączenie tylko z sąsiadującymi agentami.
