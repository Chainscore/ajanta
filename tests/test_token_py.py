import unittest
from jam_sdk.runtime import ServiceRunner
from jam_sdk import host
from examples.token import TokenService

class TestTokenService(unittest.TestCase):
    def setUp(self):
        host.reset()
        self.runner = ServiceRunner(TokenService)
        
    def run(self, payload):
        return self.runner.run_refine(payload)
        
    def to_int(self, b):
        return int.from_bytes(b[:8], 'little') if len(b) >= 8 else b.hex()
        
    def test_token(self):
        print('=== Token Test (Python) ===')
        
        # 1. Init
        print(f'Init: {self.run(bytes([0x06])).hex()}')
        
        # 2. Mint 1000 to User 1
        payload = bytes([0x01]) + (1).to_bytes(8, 'little') + (1000).to_bytes(8, 'little')
        print(f'Mint 1000 to User 1: {self.run(payload).hex()}')
        
        # 3. Check Balance of User 1
        payload = bytes([0x03]) + (1).to_bytes(8, 'little')
        print(f'Balance of User 1: {self.to_int(self.run(payload))}')
        
        # 4. Mint 500 to User 100
        payload = bytes([0x01]) + (100).to_bytes(8, 'little') + (500).to_bytes(8, 'little')
        print(f'Mint 500 to User 100: {self.run(payload).hex()}')
        
        # 5. Transfer 200 from User 100 to User 2
        payload = bytes([0x02]) + (2).to_bytes(8, 'little') + (200).to_bytes(8, 'little')
        print(f'Transfer 200 from 100 to 2: {self.run(payload).hex()}')
        
        # 6. Check Balances
        print(f'Balance of User 100: {self.to_int(self.run(bytes([0x03]) + (100).to_bytes(8, "little")))}')
        print(f'Balance of User 2: {self.to_int(self.run(bytes([0x03]) + (2).to_bytes(8, "little")))}')
        
        # 7. Check User Info for User 2
        res = self.run(bytes([0x04]) + (2).to_bytes(8, 'little'))
        if len(res) >= 17:
            joined = int.from_bytes(res[:8], 'little')
            tx_count = int.from_bytes(res[8:16], 'little')
            blocked = res[16]
            print(f'User 2 Info: joined={joined}, tx_count={tx_count}, blocked={blocked}')
        else:
            print(f'User 2 Info Error: {res.hex()}')
            
        # 8. Block User 2
        print(f'Block User 2: {self.run(bytes([0x05]) + (2).to_bytes(8, "little")).hex()}')
        
        # 9. Verify Blocked
        res = self.run(bytes([0x04]) + (2).to_bytes(8, 'little'))
        print(f'User 2 Blocked Status: {res[16]}')

if __name__ == '__main__':
    unittest.main()
