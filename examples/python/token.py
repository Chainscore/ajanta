from dataclasses import dataclass
from aj_lang.decorators import service, refine, accumulate, on_transfer, structure
from aj_lang.types import U64, U8, Mapping
from aj_lang.host import LOG_INFO

@structure
class UserInfo:
    joined_at: U64
    tx_count: U64
    is_blocked: bool

@service
class TokenService:
    total_supply: U64
    owner: U64
    balances: Mapping[U64, U64]
    users: Mapping[U64, UserInfo]

    @refine
    def refine(self, payload: bytes) -> bytes:
        if len(payload) == 0:
            return b'\xFF'
        
        cmd = payload[0]
        
        # INIT = 0x06
        if cmd == 0x06:
            if self.owner == 0:
                self.owner = 100
                LOG_INFO("Initialized owner to 100")
            return b''

        # MINT = 0x01
        if cmd == 0x01:
            if len(payload) < 17:
                return b'\xFE'
            to = U64.from_bytes(payload[1:9], 'little')
            amount = U64.from_bytes(payload[9:17], 'little')
            
            self.total_supply += amount
            
            self.balances[to] += amount
            
            LOG_INFO("Minted")
            return b''

        # TRANSFER = 0x02
        if cmd == 0x02:
            if len(payload) < 17:
                return b'\xFE'
            sender = 100 # Hardcoded
            to = U64.from_bytes(payload[1:9], 'little')
            amount = U64.from_bytes(payload[9:17], 'little')
            
            u_from = self.users[sender]
            if u_from.is_blocked:
                return b'\xFA'
            
            bal_from = self.balances[sender]
            if bal_from < amount:
                return b'\xFB'
            
            self.balances[sender] -= amount
            self.balances[to] += amount
            
            u_from.tx_count += 1
            self.users[sender] = u_from
            
            u_to = self.users[to]
            if u_to.joined_at == 0:
                u_to.joined_at = 1
            u_to.tx_count += 1
            self.users[to] = u_to
            
            LOG_INFO("Transfer success")
            return b''

        # BALANCE_OF = 0x03
        if cmd == 0x03:
            if len(payload) < 9:
                return b'\xFE'
            who = U64.from_bytes(payload[1:9], 'little')
            bal = self.balances[who]
            return bal

        # GET_USER = 0x04
        if cmd == 0x04:
            if len(payload) < 9:
                return b'\xFE'
            who = U64.from_bytes(payload[1:9], 'little')
            u = self.users[who]
            return u

        # BLOCK_USER = 0x05
        if cmd == 0x05:
            if len(payload) < 9:
                return b'\xFE'
            who = U64.from_bytes(payload[1:9], 'little')
            u = self.users[who]
            u.is_blocked = True
            self.users[who] = u
            LOG_INFO("Blocked user")
            return b''
            
        return b''

    @accumulate
    def accumulate(self, items):
        pass

    @on_transfer
    def on_transfer(self, sender, amount, memo):
        pass
