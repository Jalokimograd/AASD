from json import dumps, loads



neighbors = {"pierwszy": {"path": "122", "name": "sasiad1"}, "drugi": {"path": "864", "name": "sasiad2"}}
path = ["345", "456", "567"]

body = dumps({"neighbors": neighbors, "path": path})

neighbors["trzeci"] = {}
neighbors["trzeci"]["sewastopol"] = {"path": "555", "name": "sasiad3"}

for key, body in neighbors.items():
    print(key)
    print(body)

print("aaa")