import json
import os
import re
from solc import compile_source

from settings import settings


def get_version(filename):
    try:
        return int(re.findall(r'\d+', filename)[0])
    except IndexError:
        return 0


def compile_contract(filename):
    with open(filename, 'r') as f:
        contract_source_code = f.read()

    compiled_sol = compile_source(contract_source_code)
    return compiled_sol


def main():
    res = {
        "MemoDB": {},
        "Token": {},
        "Client": {},
    }
    contract_dir = os.path.join(os.path.dirname(__file__), 'contracts')

    for filename in os.listdir(contract_dir):
        file = os.path.join(contract_dir, filename)
        if os.path.isfile(file):
            if filename.startswith('MemoDB'):
                version = get_version(filename)
                res['MemoDB'][version] = {
                    "abi": compile_contract(file)['<stdin>:MemoDB']['abi']
                }
            elif filename.startswith('Token'):
                version = get_version(filename)
                res['Token'][version] = {
                    "abi": compile_contract(file)['<stdin>:Token']['abi']
                }
            elif filename.startswith('Client'):
                version = get_version(filename)
                compiled = compile_contract(file)['<stdin>:Client']
                res['Client'][version] = {
                    "abi": compiled['abi'],
                    "bin": compiled['bin']
                }

    res['Token'][0]["address"] = '0x8C6beb352014dA46Ba85B5164f0b95DAEF5375d5'
    res['MemoDB'][0]["address"] = '0x46FDE65ce40E753B08106560E2Bc82eb28715198'

    res['Token'][1000]["address"] = '0xD3E30d3E597ff08Db992c9209d55Eb2711B08Ad8'
    res['MemoDB'][1000]["address"] = '0x7eb9116cd194f4B03959dfb358F846F20127615C'

    with open(settings.contracts_json, 'w') as f:
        json.dump(res, f, sort_keys=True)


if __name__ == '__main__':
    main()
