# 1. run the exe or python file
# 2. type in the name of the ct file (in the dir of the tool btw) hit enter
# 3. then type in your desired output file name and hit enter
# 4. choose json, txt or pymem
# for example if you choose json a ct file that first looked like this...
```xml

<?xml version="1.0" encoding="utf-8"?> <CheatTable CheatEngineTableVersion="46"> <CheatEntries> <CheatEntry> <ID>1</ID> <Description>"fov"</Description> <VariableType>Float</VariableType> <Address>client.dll+12755C</Address> </CheatEntry> <CheatEntry> <ID>2</ID> <Description>"health"</Description> <VariableType>4 Bytes</VariableType> <Address>hw.dll+1282A8C</Address> </CheatEntry> </CheatEntries> <UserdefinedSymbols/> </CheatTable>
```
# would then look like...
```json
[
  {
    "title": "fov",
    "details": {
      "VariableType": "Float",
      "Address": "client.dll+12755C"
    }
  },
  {
    "title": "health",
    "details": {
      "VariableType": "4 Bytes",
      "Address": "hw.dll+1282A8C"
    }
  }
]
```
