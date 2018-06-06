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

    highest_client = tuple()

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
                res['Client'][version] = {
                    "abi": compile_contract(file)['<stdin>:Client']['abi']
                }
                version = get_version(filename)
                if not highest_client or highest_client[0] < version:
                    highest_client = (version, file)

    res['Client'][highest_client[0]]["bin"] = compile_contract(highest_client[1])['<stdin>:Client']['bin']

    with open(settings.contracts_json, 'w') as f:
        json.dump(res, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
